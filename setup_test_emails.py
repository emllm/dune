#!/usr/bin/env python3
"""
Skrypt do tworzenia przykładowych wiadomości email w skrzynce testowej.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time


def create_sample_emails():
    """Tworzy przykładowe wiadomości email."""

    # Przykładowe wiadomości z różnymi datami
    sample_emails = [
        {
            "subject": "Testowa wiadomość 1",
            "body": "To jest pierwsza testowa wiadomość email.",
            "date": datetime.now() - timedelta(days=30)
        },
        {
            "subject": "Raport miesięczny",
            "body": "Raport z działalności za ostatni miesiąc.\n\nPozdrawiam,\nSystem",
            "date": datetime.now() - timedelta(days=15)
        },
        {
            "subject": "Przypomnienie o spotkaniu",
            "body": "Przypominam o jutrzejszym spotkaniu o godzinie 10:00.",
            "date": datetime.now() - timedelta(days=5)
        },
        {
            "subject": "Newsletter techniczny",
            "body": "Najnowsze informacje ze świata technologii:\n- AI rozwija się błyskawicznie\n- Nowe frameworki Python",
            "date": datetime.now() - timedelta(days=60)
        },
        {
            "subject": "Aktualna wiadomość",
            "body": "To jest najnowsza wiadomość w skrzynce.",
            "date": datetime.now()
        }
    ]

    return sample_emails


def save_emails_to_maildir(emails, maildir_path):
    """Zapisuje wiadomości bezpośrednio do formatu Maildir."""

    # Utwórz strukturę Maildir
    os.makedirs(f"{maildir_path}/cur", exist_ok=True)
    os.makedirs(f"{maildir_path}/new", exist_ok=True)
    os.makedirs(f"{maildir_path}/tmp", exist_ok=True)

    for i, email_data in enumerate(emails):
        # Utwórz wiadomość
        msg = MIMEMultipart()
        msg["From"] = "sender@example.com"
        msg["To"] = "testuser@example.com"
        msg["Subject"] = email_data["subject"]
        msg["Date"] = email_data["date"].strftime("%a, %d %b %Y %H:%M:%S +0000")

        # Dodaj treść
        body = MIMEText(email_data["body"], "plain", "utf-8")
        msg.attach(body)

        # Wygeneruj unikalną nazwę pliku
        timestamp = int(email_data["date"].timestamp())
        filename = f"{timestamp}.{i}.localhost:2,"

        # Zapisz do folderu new (nowe wiadomości)
        filepath = f"{maildir_path}/new/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(msg.as_string())

        print(f"✅ Utworzono wiadomość: {email_data['subject']}")


def main():
    """Główna funkcja skryptu."""

    print("🔧 Tworzenie przykładowych wiadomości email...")

    # Ścieżka do maildir użytkownika testowego
    maildir_path = "./docker/mail/testuser@example.com"

    # Utwórz przykładowe wiadomości
    emails = create_sample_emails()

    # Zapisz do Maildir
    save_emails_to_maildir(emails, maildir_path)

    print(f"✅ Utworzono {len(emails)} przykładowych wiadomości")
    print(f"📁 Lokalizacja: {maildir_path}")
    print("\n🚀 Teraz możesz uruchomić: docker-compose up")


if __name__ == "__main__":
    main()