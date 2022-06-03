import json
import time
from pprint import pprint
import requests


class VK:
    url_ = 'https://api.vk.com/method/'
    photo_names = []
    rez_list = []

    def __init__(self, user_id, ver_= 5.131):
        self.user_id = user_id
        self.vk_token = open('tokens.txt').readlines()[4].strip('\n')
        self.params = {'access_token': self.vk_token,
                       'v': ver_}

    def get_photo_user(self, count_, rev_=0):
        url_get_photo_user = self.url_ + 'photos.get'
        params_get_photo_user = {'owner_id': self.user_id,
                                 'album_id': 'profile',
                                 'rev': rev_,
                                 'extended': '1',
                                 'photo_sizes': 1,
                                 'offset': count_,
                                 'count': 1
                                 }

        resp = requests.get(url_get_photo_user, params={**self.params, **params_get_photo_user})
        resp.raise_for_status()

        if 'error' in resp.json():
            if 100 == resp.json()['error']['error_code']:
                print('ERROR - Такого User ID не существует')
                exit()
            else:
                print(f'ERROR - "{resp.json()["""error"""]["""error_code"""]}": "{resp.json()["""error"""]["""error_msg"""]}"')
                exit()
        if count_ >= int(resp.json()['response']['count']):
            print('Фото закончились')
            exit()
        else:
            pprint(f'*** [RESPONSE] <{resp.status_code}> - путь к файлу получен успешно')
            return resp.json()

    def get_photo_name(self):
        self.link_ = self.get_photo_user(count_)['response']['items'][0]
        self.likes_ = self.link_['likes']['count']
        self.date_ = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime(self.link_['date']))
        self.href_ = self.link_['sizes'][-1]['url']
        self.format_ = self.href_.split('/')[-1].split('.')[1].split('?')[0]
        self.file_name_ = f'{self.likes_}.{self.format_}'
        self.size = self.link_['sizes'][-1]['type']

        if self.file_name_ in self.photo_names:
            self.file_name_ = f' {self.likes_}_{self.date_}.{self.format_}'
        self.photo_names += [self.file_name_]


    def create_json(self):
        dict_ = {}
        dict_['file_name'] = self.file_name_
        dict_['size'] = self.size
        self.rez_list.append(dict_)
        with open('logs.json', 'w') as file_:
            json.dump(self.rez_list, file_)


class YaDisk:
    url_ = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

    def __init__(self):
        self.ya_token = open('tokens.txt').readlines()[1].strip('\n')
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'OAuth {self.ya_token}'
                        }

    def upload_photo_from_internet(self, path_, name_):
        href_ = path_
        full_path_ = f'/img/{name_}'
        params = {'url': href_,
                  'path': full_path_
                  }
        self.response = requests.post(url=self.url_, params=params, headers=self.headers)
        self.response.raise_for_status()
        if self.response.status_code == 202:
            print(f'[RESPONSE]<{self.response.status_code}> -  загрузка файла выполнена успешно - **{name_}** ')
            print()
        else:
            print(f'[RESPONSE]<{self.response.status_code}> -  загрузка файла не удалась - **{name_}** ')
            print()

if __name__ == '__main__':
    try:
        count_ = 0
        vk_ = VK(int(input('Введите ID пользователя: ')))
        ya_ = YaDisk()
        photos = input('Введите количество фото для выгрузки с ВК на Яндекс.Диск: ')
        if photos:
            photos = int(photos)
            if photos <= 0:
                print('Ну, как хотите!')
        else:
            photos = 5
        for i in range(photos):
            time.sleep(0.35)
            vk_.get_photo_name()
            ya_.upload_photo_from_internet(vk_.href_, vk_.file_name_)
            vk_.create_json()  # Подготовка JSON результирующего файла
            count_ += 1
    except IndexError as ind_err:
        pprint(f'ERROR - {ind_err}')
    except ValueError as err:
        pprint(f'ERROR - Данные должны быть целым числом - {err}')
    except Exception as err:
        pprint(f'ERROR - {err}')
