import requests
from pprint import pprint
from datetime import date
import json


# Функция получает фото из VK, сортирует их по размеру и возвращает список словарей с информацией о фотографии - кол-во
# лайков, размер и ссылка на фото
def get_photo_vk(user_id, count_photo=5):
    with open("vk_token.txt", "r", encoding="UTF-8") as file:
        vk_token = file.read().strip()
    params = {'owner_id': user_id, 'access_token': vk_token, 'album_id': 'profile',
              'photo_sizes': 1, 'extended': 1, 'v': 5.131}
    response = requests.get("https://api.vk.com/method/photos.get", params=params)
    list_photo_vk = []
    count = 1
    tmp_list_photo = []
    dt_now = date.today()
    for el in response.json()['response']['items']:
        dict_photo = {}
        if count > count_photo:
            break
        if not el['likes']['count'] in tmp_list_photo:
            tmp_list_photo.append(el['likes']['count'])
            dict_photo['file_name'] = el['likes']['count']
        else:
            name_photo = f'{str(el["likes"]["count"])}_{str(dt_now)}'
            tmp_list_photo.append(name_photo)
            dict_photo['file_name'] = name_photo
        sorted_list = sorted(el['sizes'], key=lambda k: k['width'], reverse=True)
        dict_photo['url'] = sorted_list[0]['url']
        dict_photo['size'] = sorted_list[0]['type']
        list_photo_vk.append(dict_photo)
        count += 1
    return list_photo_vk


# Функция создает папку на Я.диске, загружает в неё фотографии и создает json-файл
def upload_photo(token, user_id, name_folder='photo_vk'):
    requests.put('https://cloud-api.yandex.net/' + 'v1/disk/resources/', params={'path': name_folder},
                 headers={'Authorization': f'OAuth {token}'})
    res = get_photo_vk(user_id)
    print(f'Начинается загрузка фотографий. Всего будет загружено - {len(res)} фотографий')
    for dict_photo in res:
        requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                      headers={'Authorization': f'OAuth {token}'},
                      params={'path': f'{name_folder}/{dict_photo["file_name"]}', 'url': dict_photo.pop('url')})
        print(f'Фотография {dict_photo["file_name"]} успешно загружена на Яндекс.Диск в папку {name_folder}')
        with open(f'{dict_photo["file_name"]}.json', "a") as file:
            json.dump(dict_photo, file, ensure_ascii=False, indent=2)
    print('Все фотографии успешно загружены')


def main():
    user_id = input("Введите id пользователя VK: ")
    token = input("Введите token Яндекс.Диска: ")
    upload_photo(token, user_id)


if __name__ == '__main__':
    main()

