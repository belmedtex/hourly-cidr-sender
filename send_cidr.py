import requests
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

# Безопасное получение данных из переменных окружения GitHub Secret
EMAIL_FROM = "priborio@yandex.ru"
EMAIL_PASSWORD = "jncsvzsugxqjdyit"
EMAIL_TO = "priborio@yandex.ru"
FILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt"

def download_file():
    """Скачивает файл. В случае ошибки показывает причину и завершает работу."""
    try:
        resp = requests.get(FILE_URL, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"❌ Ошибка скачивания файла: {e}")
        sys.exit(1)

def send_email(file_content):
    """Отправляет письмо через Яндекс. В случае ошибки показывает причину."""
    try:
        # Создаем письмо
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = "Актуальный список CIDR"

        body = MIMEText("Во вложении — свежий белый список CIDR.", "plain")
        msg.attach(body)

        # Создаем вложение
        attachment = MIMEApplication(file_content, Name="WHITE-CIDR-RU-checked.txt")
        attachment["Content-Disposition"] = 'attachment; filename="WHITE-CIDR-RU-checked.txt"'
        msg.attach(attachment)

        # Отправляем письмо через Яндекс
        with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Письмо успешно отправлено!")

    except smtplib.SMTPAuthenticationError:
        print("❌ Ошибка: Яндекс не принял пароль. Проверьте, что вы используете пароль приложения, а не от почты.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Непредвиденная ошибка при отправке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Начинаю работу...")
    file_data = download_file()
    print("📎 Файл скачан. Отправляю письмо...")
    send_email(file_data)
    print("🎉 Готово!")
