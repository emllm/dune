"""
Analizator LLM do interpretacji żądań w języku naturalnym.
"""

import json
import requests
from typing import Dict, Any
from loguru import logger
from processor_engine import ProcessorConfig


class LLMAnalyzer:
    """Analizator wykorzystujący LLM do interpretacji żądań."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:7b"):
        self.base_url = base_url
        self.model = model
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Sprawdza połączenie z Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                logger.success("Połączenie z Ollama nawiązane")
            else:
                logger.warning("Ollama niedostępna, używanie domyślnych szablonów")
        except requests.RequestException:
            logger.warning("Nie można połączyć się z Ollama, używanie domyślnych szablonów")

    def analyze_request(self, request: str) -> ProcessorConfig:
        """Analizuje żądanie i zwraca konfigurację procesora."""

        # Spróbuj użyć LLM
        try:
            return self._analyze_with_llm(request)
        except Exception as e:
            logger.warning(f"LLM niedostępny ({e}), używanie domyślnego szablonu")
            return self._get_default_imap_processor()

    def _analyze_with_llm(self, request: str) -> ProcessorConfig:
        """Analizuje żądanie za pomocą LLM."""

        prompt = f"""
Przeanalizuj poniższe żądanie i zwróć konfigurację procesora danych w formacie JSON.

Żądanie: {request}

Zwróć odpowiedź w następującym formacie JSON (tylko JSON, bez dodatkowych komentarzy):
{{
    "name": "nazwa_procesora",
    "description": "opis działania",  
    "dependencies": ["lista", "wymaganych", "pakietów"],
    "parameters": {{"parametr": "wartość"}},
    "code_template": "kompletny kod Python do wykonania zadania"
}}

Kod powinien:
1. Wykorzystywać zmienne środowiskowe z prefiksem IMAP_ dla połączenia
2. Zapisywać rezultat w zmiennej 'result' 
3. Używać logger.info() do logowania
4. Tworzyć foldery zgodnie z żądaniem
5. Obsługiwać błędy
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        response_text = result.get("response", "")

        # Wyodrębnij JSON z odpowiedzi
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("Nie znaleziono JSON w odpowiedzi LLM")

        json_text = response_text[json_start:json_end]
        config_data = json.loads(json_text)

        return ProcessorConfig(**config_data)

    def _get_default_imap_processor(self) -> ProcessorConfig:
        """Zwraca domyślny procesor IMAP jako fallback."""

        code_template = '''
import imaplib
import email
import os
from datetime import datetime
from pathlib import Path

# Pobierz dane połączenia z zmiennych środowiskowych
imap_server = os.getenv("IMAP_SERVER", "localhost")
imap_port = int(os.getenv("IMAP_PORT", "143"))
username = os.getenv("IMAP_USERNAME")
password = os.getenv("IMAP_PASSWORD")
use_ssl = os.getenv("IMAP_USE_SSL", "false").lower() == "true"

if not username or not password:
    raise ValueError("Brak danych logowania IMAP w zmiennych środowiskowych")

logger.info(f"Łączenie z serwerem IMAP: {imap_server}:{imap_port}")

# Nawiąż połączenie
if use_ssl:
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
else:
    mail = imaplib.IMAP4(imap_server, imap_port)

mail.login(username, password)
mail.select("inbox")

logger.info("Pobieranie listy wiadomości...")

# Pobierz wszystkie wiadomości
result, data = mail.search(None, "ALL")
email_ids = data[0].split()

downloaded_files = []
base_path = Path(output_dir) / "skrzynka"

logger.info(f"Znaleziono {len(email_ids)} wiadomości")

for i, email_id in enumerate(email_ids):
    try:
        # Pobierz wiadomość
        result, msg_data = mail.fetch(email_id, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)

        # Pobierz datę wiadomości
        date_header = email_message.get("Date")
        if date_header:
            try:
                date_tuple = email.utils.parsedate_tz(date_header)
                if date_tuple:
                    timestamp = email.utils.mktime_tz(date_tuple)
                    msg_date = datetime.fromtimestamp(timestamp)
                else:
                    msg_date = datetime.now()
            except:
                msg_date = datetime.now()
        else:
            msg_date = datetime.now()

        # Utwórz folder rok.miesiąc
        year_month = f"{msg_date.year}.{msg_date.month:02d}"
        folder_path = base_path / year_month
        folder_path.mkdir(parents=True, exist_ok=True)

        # Zapisz plik .eml
        filename = folder_path / f"email_{email_id.decode()}.eml"
        with open(filename, "wb") as f:
            f.write(email_body)

        downloaded_files.append(str(filename))
        logger.info(f"Zapisano: {filename}")

    except Exception as e:
        logger.error(f"Błąd przetwarzania wiadomości {email_id}: {e}")

mail.close()
mail.logout()

result = {
    "status": "completed",
    "downloaded_files": downloaded_files,
    "total_count": len(downloaded_files),
    "folders_created": list(set([str(Path(f).parent) for f in downloaded_files]))
}

logger.success(f"Pobrano {len(downloaded_files)} wiadomości do {len(result['folders_created'])} folderów")
'''

        return ProcessorConfig(
            name="imap_email_downloader",
            description="Pobiera wiadomości email z IMAP i organizuje je w foldery rok.miesiąc",
            dependencies=["imaplib", "email"],
            parameters={},
            code_template=code_template
        )