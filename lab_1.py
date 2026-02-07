import requests
import matplotlib.pyplot as plt

base_url = 'https://pokeapi.co/api/v2/'
limit = 10
url = f'{base_url}pokemon?limit={limit}'                #https://pokeapi.co/api/v2/pokemon?limit=10

response_1 = requests.get(url)
# print(response.json())

data = []

for i in range(limit):
    url = response_1.json()['results'][i]['url']            # url = f'https://pokeapi.co/api/v2/pokemon/1/'
    response_2 = requests.get(url)
    id = response_2.json()['id']
    name = response_2.json()['name']
    height = response_2.json()['height']
    weight = response_2.json()['weight']
    hp = response_2.json()['stats'][0]['base_stat']
    attack = response_2.json()['stats'][1]['base_stat']
    defense = response_2.json()['stats'][2]['base_stat']
    speed = response_2.json()['stats'][3]['base_stat']
    data.append({"id":id,"name":name,"height":height,"weight":weight,"hp":hp,"attack":attack,"defense":defense,"speed":speed})
# print(data)

def display_graph(x,y,view):
    x_list = []
    y_list = []
    name = []
    for i in data:
        try:
            x_list.append(i[x])
        except:
            print('Заданный параметр X не существует.')
            return
        if y != None:
            try:
                y_list.append(i[y])
            except:
                print('Заданный параметр Y не существует.')
                return
        name.append(i["name"])

    for i in range(limit):
        for j in range(0, limit-i-1):
            if x_list[j] > x_list[j+1]:
                x_list[j], x_list[j+1] = x_list[j+1], x_list[j]
                name[j], name[j+1] = name[j+1], name[j]
                if y != None:
                    y_list[j], y_list[j+1] = y_list[j+1], y_list[j]
                
    
    if view == 1:
        plt.plot(x_list,y_list)
        plt.ylabel(y)
        for i in range(limit):
            plt.text(x_list[i],y_list[i],name[i])
    elif view == 2:
        plt.scatter(x_list,y_list)
        plt.ylabel(y)
        for i in range(limit):
            plt.text(x_list[i],y_list[i],name[i])
    elif view == 3:
        plt.bar(x_list,y_list)
        plt.ylabel(y)
        for i in range(limit):
            plt.text(x_list[i],y_list[i],name[i])
    elif view == 4:
        plt.barh(x_list,y_list)
        plt.ylabel(y)
        for i in range(limit):
            plt.text(y_list[i],x_list[i],name[i])
    elif view == 5:
        plt.hist(x_list)
    elif view == 6:
        plt.pie(x_list, labels=name,autopct='%1.1f%%')
    plt.xlabel(x)
    
    plt.show()

while True:
    view = int(input("""Введите номер графика
1 - Линейный график 
2 - Точечная диаграмма
3 - Столбчатая диаграмма
4 - Горизонтальная столбчатая диаграмма
5 - Гистограмма
6 - Круговая диаграмма
0 - Выход
"""))

    if 0 < view < 5 :
        x = input("""Введите параметр X
Возможные варианты: id, name, height, weight, hp, attack, defense, speed
""")
        y = input("""Введите параметр Y
Возможные варианты: id, name, height, weight, hp, attack, defense, speed
""")
        display_graph(x,y,view)
    elif 4 < view < 7:
        x = input("""Введите параметр
Возможные варианты: id, name, height, weight, hp, attack, defense, speed
""")
        y = None
        display_graph(x,y,view)
    elif view == 0:
        break
    else: print('Ну почти')
