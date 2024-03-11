import requests
import os
import json

vk_token = ""  # сервисный ключ от приложения в VK


class VK:

    API_BASE_URL_VK = "https://api.vk.com/method/"

    def __init__(self):
        self.id_user = input("Ввод ID: ")

    def get_profile_photos(self, id_user):
        url = "https://api.vk.com/method/photos.get"
        params = {
            "access_token": vk_token,
            "owner_id": id_user,
            "album_id": "profile",
            "extended": 1,
            "count": 5,
            "v": "5.131",
        }
        response = requests.get(url, params=params)
        photos = response.json()["response"]["items"]
        return photos

    def get_sorted_photos(self, id_user):
        photos = self.get_profile_photos(id_user)
        sorted_photos = sorted(
            photos, key=lambda x: (-x.get("likes", {}).get("count", 0))
        )
        return sorted_photos


class Yandex:

    def __init__(self, ya_token):
        self.token = ya_token

    def folder_creation(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {self.token}",
        }
        params = {"path": f"{folder_name}", "overwrite": "false"}
        response = requests.put(url=url, headers=headers, params=params)
        if response.status_code == 201:
            print("Папка создана")
        else:
            print("Папка уже существует")

    def upload(self, folder_name, num_photos, sorted_photos):
        results = []
        print("Загрузка фотографий на Яндекс.Диск...")
        for _, photo in enumerate(sorted_photos[:num_photos]):
            sizes = photo.get("sizes")
            if sizes:
                max_size = sizes[-1]
                max_url = max_size["url"]
                likes_count = photo.get("likes", {}).get("count", 0)
                photo_date = photo.get("date")
                photo_id = photo.get("id")
                name = f"{likes_count}_{photo_id}_{photo_date}.jpg"
                if os.path.exists(f"{folder_name}/{name}"):
                    print(f"Файл с именем '{name}' уже существует.")
                    continue

                url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"OAuth {self.token}",
                }
                params_upload = {"path": f"{folder_name}/{name}", "url": max_url}
                response = requests.post(url=url, headers=headers, params=params_upload)
                if response.status_code == 202:
                    print(f"Фотография '{name}' загружена на Яндекс.Диск.")
                    results.append({"file_name": name, "size": max_size})

                else:
                    print(
                        f"Ошибка при загрузке '{name}' на Яндекс.Диск: {response.text}"
                    )
                    print(f"HTTP статус: {response.status_code}")

        with open("results.json", "w") as f:
            json.dump(results, f, indent=4)
        print("Загрузка завершена")


downloader = VK()
user_id = downloader.id_user
sorted_photos = downloader.get_sorted_photos(user_id)
ya_token = str(input("Введите ваш токен Яндекс.Диск: "))
folder_name = str(input("Введите имя папки на Яндекс.Диск: "))
uploader = Yandex(ya_token)
uploader.folder_creation(folder_name)
uploader.upload(folder_name, 5, sorted_photos)
