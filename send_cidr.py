import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

# --- Конфигурация из переменных окружения (GitHub Secrets) ---
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO", "pribor.expert@yandex.ru")
FILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"

def download_file():
    resp = requests.get(FILE_URL, timeout=30)
    resp.raise_for_status()
    return resp.content

def send_email(content):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = "WHITE-CIDR-RU список (автоматическое обновление)"
    body = MIMEText("Файл обновлён. Во вложении актуальный список CIDR.", "plain")
    msg.attach(body)

    attachment = MIMEApplication(content, Name="WHITE-CIDR-RU-checked.txt")
    attachment["Content-Disposition"] = 'attachment; filename="WHITE-CIDR-RU-checked.txt"'
    msg.attach(attachment)

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def main():
    print("Скачиваю файл...")
    data = download_file()
    print("Отправляю email...")
    send_email(data)
    print("Готово!")

if __name__ == "__main__":
    main()
