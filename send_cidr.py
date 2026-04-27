import requests
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

EMAIL_FROM = "priborio@yandex.ru"
EMAIL_PASSWORD = "jncsvzsugxqjdyit"  # вставьте сюда
EMAIL_TO = "priborio@yandex.ru"
FILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"

def download_file():
    try:
        resp = requests.get(FILE_URL, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        sys.exit(1)

def send_email(content):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = "CIDR-список"
        msg.attach(MIMEText("Файл во вложении.", "plain"))
        attachment = MIMEApplication(content, Name="WHITE-CIDR-RU-checked.txt")
        attachment["Content-Disposition"] = 'attachment; filename="WHITE-CIDR-RU-checked.txt"'
        msg.attach(attachment)

        # Пробуем порт 587 с STARTTLS
        server = smtplib.SMTP("smtp.yandex.ru", 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print("✅ Письмо отправлено через порт 587")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Запуск...")
    data = download_file()
    send_email(data)
