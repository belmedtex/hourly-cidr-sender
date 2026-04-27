import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import sys

# Настройки (вынесены в переменные окружения, но для простоты пока пропишем)
# В GitHub Actions они будут заменены на секреты
URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"
EMAIL_TO = "priborio@yandex.ru"
EMAIL_FROM = "pribor.expert@yandex.ru"
EMAIL_PASSWORD = "sjguxapkndsjibmv"

def download_file():
    try:
        resp = requests.get(URL, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        sys.exit(1)

def send_email(content):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = "WHITE-CIDR-RU список (обновление)"
        body = MIMEText("Актуальный список CIDR во вложении.", "plain")
        msg.attach(body)
        attachment = MIMEApplication(content, Name="WHITE-CIDR-RU-checked.txt")
        attachment["Content-Disposition"] = 'attachment; filename="WHITE-CIDR-RU-checked.txt"'
        msg.attach(attachment)

        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("Письмо успешно отправлено")
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Скачиваю файл...")
    data = download_file()
    print("Отправляю email...")
    send_email(data)
    print("Готово.")
