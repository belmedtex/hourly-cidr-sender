import requests
import os
import sys
import urllib.parse

# --- НАСТРОЙКИ ---
# URL файла для скачивания
FILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"
# Путь для сохранения файла на Яндекс.Диске (в корне)
YANDEX_DISK_PATH = "/WHITE-CIDR-RU-checked.txt"
# Токен Яндекс.Диска (берём из GitHub Secrets)
TOKEN = os.environ.get("YANDEX_DISK_TOKEN")
# -----------------

def download_file():
    """Скачивает файл по указанному URL"""
    print(f"📥 Скачиваю файл: {FILE_URL}")
    try:
        resp = requests.get(FILE_URL, timeout=30)
        resp.raise_for_status()
        print(f"✅ Скачано {len(resp.content)} байт")
        return resp.content
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка скачивания: {e}")
        sys.exit(1)

def upload_file_to_yadisk(file_content):
    """Загружает файл на Яндекс.Диск с перезаписью"""
    print("🔑 Авторизуюсь на Яндекс.Диске")
    headers = {"Authorization": f"OAuth {TOKEN}"}
    
    # URL-кодируем путь для безопасной передачи в GET-параметре
    encoded_path = urllib.parse.quote(YANDEX_DISK_PATH)

    # 1. Запрашиваем URL для загрузки с параметром перезаписи
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": encoded_path, "overwrite": "true"}  # overwrite=true – ключевой параметр для замены файла
    try:
        resp = requests.get(upload_url, headers=headers, params=params)
        resp.raise_for_status()
        href = resp.json()["href"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения ссылки для загрузки: {e}")
        if resp.status_code == 409:
            print("   Возможно, проблема с путём или правами доступа.")
        sys.exit(1)

    # 2. Загружаем файл методом PUT по полученному URL
    print(f"📤 Загружаю файл на Яндекс.Диск (с перезаписью) ...")
    try:
        put_resp = requests.put(href, data=file_content, headers={"Content-Type": "application/octet-stream"})
        put_resp.raise_for_status()
        print("✅ Файл успешно загружен и заменён.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке: {e}")
        sys.exit(1)

def ensure_public_link():
    """Гарантирует, что на файл есть публичная ссылка, и возвращает её"""
    print("🔓 Проверяю/опубликовываю файл...")
    headers = {"Authorization": f"OAuth {TOKEN}"}
    encoded_path = urllib.parse.quote(YANDEX_DISK_PATH)

    # Сначала проверяем, опубликован ли файл
    info_url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": encoded_path}
    try:
        info_resp = requests.get(info_url, headers=headers, params=params)
        info_resp.raise_for_status()
        resource_info = info_resp.json()
        public_url = resource_info.get("public_url")
        
        if public_url:
            print(f"♻️  Файл уже опубликован. Использую существующую ссылку.")
            return public_url
        else:
            # Файл не опубликован – публикуем
            print("🆕 Файл ещё не опубликован. Публикую...")
            publish_url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
            pub_resp = requests.put(publish_url, headers=headers, params={"path": encoded_path})
            pub_resp.raise_for_status()
            # После публикации получаем обновлённую информацию о ресурсе
            info_resp2 = requests.get(info_url, headers=headers, params=params)
            info_resp2.raise_for_status()
            public_url = info_resp2.json().get("public_url")
            if not public_url:
                raise Exception("Не удалось получить публичную ссылку после публикации")
            print(f"✅ Файл опубликован.")
            return public_url
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при работе с публичной ссылкой: {e}")
        sys.exit(1)

def get_direct_download_link(public_url):
    """
    Преобразует публичную ссылку (yadi.sk/...) в прямую ссылку для скачивания файла.
    """
    print("🔗 Получаю прямую ссылку для скачивания...")
    # Из публичной ссылки извлекаем ключ (то, что идёт после yadi.sk/d/ или yadi.sk/i/)
    # Например: https://yadi.sk/d/FTb3fLiI49Xt0 -> ключ FTb3fLiI49Xt0
    public_key = public_url.split('/')[-1]
    
    download_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": public_key}
    try:
        resp = requests.get(download_url, params=params)
        resp.raise_for_status()
        direct_link = resp.json().get("href")
        if not direct_link:
            raise Exception("Не удалось получить прямую ссылку")
        print(f"✅ Готово.\n🔗 Ваша постоянная прямая ссылка для скачивания:\n{direct_link}")
        return direct_link
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения прямой ссылки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Не найден токен Яндекс.Диска. Проверьте secret YANDEX_DISK_TOKEN")
        sys.exit(1)

    file_data = download_file()
    upload_file_to_yadisk(file_data)        # Файл загружается с перезаписью
    public_url = ensure_public_link()       # Получаем публичную ссылку (yadi.sk/...)
    direct_link = get_direct_download_link(public_url)  # Превращаем её в прямую ссылку на скачивание
    print("🎉 Скрипт выполнен успешно.")
