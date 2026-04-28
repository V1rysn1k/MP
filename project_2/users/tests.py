import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


# ========== ФИКСТУРЫ ==========

@pytest.fixture
def user(db):
    """Фикстура: обычный пользователь"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def second_user(db):
    """Фикстура: второй пользователь"""
    return User.objects.create_user(
        username='seconduser',
        email='second@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_user(db):
    """Фикстура: для теста fixture_user_created"""
    return User.objects.create_user(
        username='fixture_user',
        email='fixture@example.com',
        password='fixturepass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Фикстура: авторизованный клиент"""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def authenticated_test_user(client, test_user):
    """Фикстура: авторизованный клиент с test_user"""
    client.login(username='fixture_user', password='fixturepass123')
    return client


# ========== ТЕСТЫ С ПАРАМЕТРИЗАЦИЕЙ ==========

@pytest.mark.parametrize('username,email,password1,password2,should_pass', [
    ('newuser', 'new@test.com', 'pass123456', 'pass123456', True),
    ('', 'new@test.com', 'pass123456', 'pass123456', False), 
    ('newuser', 'invalid-email', 'pass123456', 'pass123456', False),  
    ('newuser', 'new@test.com', 'pass123', 'pass123456', False), 
])
@pytest.mark.django_db
def test_registration_parameterized(client, username, email, password1, password2, should_pass):
    """Параметризация: регистрация"""
    data = {'username': username, 'email': email, 'password1': password1, 'password2': password2}
    if not username:
        data.pop('username', None)
    
    response = client.post(reverse('register'), data)
    
    if should_pass:
        assert response.status_code == 302
        assert User.objects.filter(username=username).exists()
    else:
        assert response.status_code == 200
        if username:
            assert not User.objects.filter(username=username).exists()


@pytest.mark.parametrize('username,password,should_succeed', [
    ('testuser', 'testpass123', True),
    ('testuser', 'wrongpass', False),
    ('wronguser', 'testpass123', False),
])
@pytest.mark.django_db
def test_login_parameterized(client, user, username, password, should_succeed):
    """Параметризация: вход"""
    response = client.post(reverse('login'), {'username': username, 'password': password})
    
    if should_succeed:
        assert response.status_code == 302
    else:
        assert response.status_code == 200


@pytest.mark.parametrize('url_name', [
    'user_list',
    'profile_edit',
    'incoming_requests',
])
@pytest.mark.django_db
def test_protected_urls_parameterized(client, url_name):
    """Параметризация: защищенные URL"""
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert 'login' in response.url


# ========== ТЕСТЫ С ФИКСТУРАМИ ==========

@pytest.mark.django_db
def test_fixture_user_created(test_user):
    """Фикстура: создание пользователя"""
    assert test_user.username == 'fixture_user'
    assert test_user.email == 'fixture@example.com'


@pytest.mark.django_db
def test_fixture_second_user_created(second_user):
    """Фикстура: создание второго пользователя"""
    assert second_user.username == 'seconduser'
    assert second_user.email == 'second@example.com'


@pytest.mark.django_db
def test_fixture_authenticated_client(authenticated_client):
    """Фикстура: авторизованный клиент имеет доступ к защищенным страницам"""
    response = authenticated_client.get(reverse('user_list'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_fixture_authenticated_test_user(authenticated_test_user):
    """Фикстура: авторизованный клиент с test_user"""
    response = authenticated_test_user.get(reverse('user_list'))
    assert response.status_code == 200


# ========== ТЕСТЫ ОШИБОК ==========

@pytest.mark.django_db
def test_error_404_nonexistent_profile(authenticated_client):
    """Ошибка 404: несуществующий профиль"""
    response = authenticated_client.get(reverse('profile', args=['nonexistent123']))
    assert response.status_code == 404


@pytest.mark.django_db
def test_error_duplicate_email(client, user):
    """Ошибка: дубликат email"""
    data = {
        'username': 'newuser123',
        'email': user.email,
        'password1': 'pass123456',
        'password2': 'pass123456'
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser123').exists()


@pytest.mark.django_db
def test_error_private_profile_not_accessible(authenticated_client, second_user):
    """Ошибка: приватный профиль не доступен"""
    response = authenticated_client.get(reverse('profile', args=[second_user.username]))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert 'профиль скрыт' in content or 'приват' in content.lower() or 'заявку' in content


@pytest.mark.django_db
def test_error_empty_username(client):
    """Ошибка: пустой username при регистрации"""
    data = {
        'username': '',
        'email': 'test@test.com',
        'password1': 'pass123456',
        'password2': 'pass123456'
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 200
    assert not User.objects.filter(email='test@test.com').exists()


@pytest.mark.django_db
def test_error_invalid_email_format(client):
    """Ошибка: неверный формат email"""
    data = {
        'username': 'newuser',
        'email': 'not-an-email',
        'password1': 'pass123456',
        'password2': 'pass123456'
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()