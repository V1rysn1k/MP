import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from .forms import RegisterForm, ProfileEditForm
from .models import User

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            logger.info("Пользователь %s успешно зарегистрировался с email %s", 
                       user.username, user.email)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            errors = form.errors.as_json()
            logger.warning("Ошибки валидации при регистрации: %s", errors)
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    return render(request, 'home.html')


@login_required
def user_list(request):
    """Список всех пользователей (только для авторизованных)"""
    all_users = User.objects.exclude(pk=request.user.pk)
    my_friends = set(request.user.friends.values_list('pk', flat=True))
    sent_requests = set(request.user.friend_requests.values_list('pk', flat=True))

    users = []
    for u in all_users:
        users.append({
            'user': u,
            'is_friend': u.pk in my_friends,
            'has_sent': u.pk in sent_requests,
        })
    
    logger.debug("Пользователь %s просматривает список пользователей. Найдено: %d", 
                request.user.username, len(users))
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def profile(request, username):
    """Страница профиля"""
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    is_friend = request.user.is_friend(profile_user)
    has_sent = request.user.has_sent_request(profile_user)

    logger.debug("Пользователь %s просматривает профиль %s (владелец: %s, друг: %s)",
                request.user.username, username, is_owner, is_friend)

    if not is_owner and not is_friend:
        return render(request, 'users/profile_private.html', {
            'profile_user': profile_user,
            'has_sent': has_sent,
        })

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'has_sent': has_sent,
    })


@login_required
def profile_edit(request):
    """Редактирование своего профиля"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            # Проверка на аватар ТОЛЬКО если загружен новый файл
            avatar_file = request.FILES.get('avatar')
            
            if avatar_file:
                # Проверяем MIME тип загруженного файла
                if not avatar_file.content_type.startswith('image/'):
                    logger.error("Пользователь %s попытался загрузить не-изображение: %s, тип: %s",
                               request.user.username, avatar_file.name, avatar_file.content_type, exc_info=True)
                    messages.error(request, 'Загруженный файл должен быть изображением!')
                    return render(request, 'users/profile_edit.html', {'form': form})
            
            # Сохраняем форму
            form.save()
            
            # Логирование: успешное редактирование
            if avatar_file:
                logger.info("Пользователь %s обновил свой профиль и загрузил новую аватарку", request.user.username)
            else:
                logger.info("Пользователь %s обновил свой профиль", request.user.username)
            
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile', username=request.user.username)
        else:
            # Логирование: ошибки валидации формы
            logger.warning("Ошибки валидации при редактировании профиля пользователя %s: %s",
                          request.user.username, form.errors.as_json())
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def send_friend_request(request, username):
    """Отправить заявку в друзья"""
    to_user = get_object_or_404(User, username=username)
    
    if to_user == request.user:
        logger.warning("Пользователь %s попытался отправить заявку сам себе", request.user.username)
        messages.warning(request, 'Нельзя отправить заявку самому себе!')
    elif request.user.is_friend(to_user):
        logger.info("Пользователь %s попытался отправить заявку уже другу %s", 
                   request.user.username, to_user.username)
        messages.info(request, f'Вы уже друзья с {to_user.username}!')
    else:
        request.user.friend_requests.add(to_user)
        logger.info("Пользователь %s отправил заявку в друзья пользователю %s", 
                   request.user.username, to_user.username)
        messages.success(request, f'Заявка отправлена пользователю {to_user.username}!')
    
    return redirect('profile', username=to_user.username)


@login_required
def accept_friend_request(request, username):
    """Принять заявку в друзья"""
    from_user = get_object_or_404(User, username=username)
    
    if from_user.has_sent_request(request.user):
        request.user.friends.add(from_user)
        from_user.friends.add(request.user)
        from_user.friend_requests.remove(request.user)
        
        logger.info("Пользователь %s принял заявку в друзья от %s", 
                   request.user.username, from_user.username)
        messages.success(request, f'{from_user.username} теперь ваш друг!')
    else:
        logger.warning("Пользователь %s попытался принять несуществующую заявку от %s",
                      request.user.username, from_user.username)
        messages.warning(request, 'Нет заявки от этого пользователя!')
    
    return redirect('profile', username=request.user.username)


@login_required
def remove_friend(request, username):
    """Удалить из друзей"""
    friend = get_object_or_404(User, username=username)
    
    if request.user.is_friend(friend):
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        
        logger.info("Пользователь %s удалил из друзей пользователя %s", 
                   request.user.username, friend.username)
        messages.success(request, f'{friend.username} удалён из друзей.')
    else:
        logger.warning("Пользователь %s попытался удалить не-друга %s",
                      request.user.username, friend.username)
        messages.warning(request, f'{friend.username} не является вашим другом!')
    
    return redirect('profile', username=request.user.username)


@login_required
def incoming_requests(request):
    """Входящие заявки в друзья"""
    requesters = User.objects.filter(friend_requests=request.user)
    
    logger.debug("Пользователь %s просматривает входящие заявки. Найдено: %d",
                request.user.username, requesters.count())
    return render(request, 'users/incoming_requests.html', {'requesters': requesters})