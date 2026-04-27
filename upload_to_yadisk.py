import requests
import os
import sys
import time
import urllib.parse

# --- НАСТРОЙКИ ---
FILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"
YANDEX_DISK_PATH = "/WHITE-CIDR-RU-checked.txt"
TOKEN = os.environ.get("YANDEX_DISK_TOKEN")
# -----------------

def download_file():
    print(f"📥 Скачиваю файл: {FILE_URL}")
    try:
        resp = requests.get(FILE_URL, timeout=30)
        resp.raise_for_status()
        print(f"✅ Скачано {len(resp.content)} байт")
        return resp.content
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        sys.exit(1)

def upload_file_to_yadisk(file_content):
    print("🔑 Авторизуюсь на Яндекс.Диске")
    headers = {"Authorization": f"OAuth {TOKEN}"}
    encoded_path = urllib.parse.quote(YANDEX_DISK_PATH)
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": encoded_path, "overwrite": "true"}
    try:
        resp = requests.get(upload_url, headers=headers, params=params)
        resp.raise_for_status()
        href = resp.json()["href"]
    except Exception as e:
        print(f"❌ Ошибка получения ссылки для загрузки: {e}")
        sys.exit(1)

    print(f"📤 Загружаю файл на Яндекс.Диск (с перезаписью) ...")
    try:
        put_resp = requests.put(href, data=file_content, headers={"Content-Type": "application/octet-stream"})
        put_resp.raise_for_status()
        print("✅ Файл успешно загружен и заменён.")
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        sys.exit(1)

def ensure_public_link():
    """Проверяет, опубликован ли файл. Если нет — публикует. Возвращает public_url."""
    print("🔓 Проверяю/опубликовываю файл...")
    headers = {"Authorization": f"OAuth {TOKEN}"}
    encoded_path = urllib.parse.quote(YANDEX_DISK_PATH)

    # Получаем информацию о ресурсе
    info_url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": encoded_path}
    try:
        info_resp = requests.get(info_url, headers=headers, params=params)
        info_resp.raise_for_status()
        resource_info = info_resp.json()
        public_url = resource_info.get("public_url")
        if public_url:
            print(f"♻️  Файл уже опубликован. Публичная ссылка: {public_url}")
            return public_url
        else:
            print("🆕 Файл ещё не опубликован. Публикую...")
            publish_url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
            pub_resp = requests.put(publish_url, headers=headers, params={"path": encoded_path})
            pub_resp.raise_for_status()
            # Небольшая задержка, чтобы API успело обработать публикацию
            time.sleep(2)
            # Повторно получаем информацию, чтобы забрать public_url
            info_resp2 = requests.get(info_url, headers=headers, params=params)
            info_resp2.raise_for_status()
            public_url = info_resp2.json().get("public_url")
            if not public_url:
                raise Exception("Не удалось получить публичную ссылку после публикации")
            print(f"✅ Файл опубликован. Публичная ссылка: {public_url}")
            return public_url
    except Exception as e:
        print(f"❌ Ошибка при работе с публичной ссылкой: {e}")
        sys.exit(1)

def get_direct_download_link(public_url):
    """Преобразует публичную ссылку в прямую ссылку для скачивания файла."""
    print("🔗 Получаю прямую ссылку для скачивания...")
    # API Яндекс.Диска принимает полную public_url в качестве параметра public_key
    download_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": public_url}
    try:
        resp = requests.get(download_url, params=params, timeout=30)
        resp.raise_for_status()
        direct_link = resp.json().get("href")
        if not direct_link:
            raise Exception("В ответе нет поля href")
        print(f"✅ Готово.\n🔗 Ваша постоянная прямая ссылка для скачивания:\n{direct_link}")
        return direct_link
    except requests.exceptions.HTTPError as e:
        print(f"❌ Ошибка HTTP: {e}")
        if resp.status_code == 404:
            print("   Ресурс не найден. Возможно, публикация не удалась или ссылка неверна.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка получения прямой ссылки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Не найден токен Яндекс.Диска. Проверьте secret YANDEX_DISK_TOKEN")
        sys.exit(1)

    file_data = download_file()
    upload_file_to_yadisk(file_data)
    public_url = ensure_public_link()
    direct_link = get_direct_download_link(public_url)
    print("🎉 Скрипт выполнен успешно.")
