# Przykładowe konfiguracje zadań

## 1. Pobieranie emaili z IMAP

**Żądanie NLP:**
```
Pobierz wszystkie wiadomości email ze skrzynki IMAP i zapisz je w folderach 
uporządkowanych według roku i miesiąca w formacie skrzynka/rok.miesiąc/*.eml
```

**Wygenerowana konfiguracja:** `configs/email-imap-processor.yaml`

---

## 2. Analiza plików CSV

**Żądanie NLP:**
```
Przeanalizuj wszystkie pliki CSV w folderze data/, połącz je w jeden dataset 
i wygeneruj raport z podstawowymi statystykami
```

**Komenda generowania:**
```bash
python generate_config.py "Przeanalizuj wszystkie pliki CSV w folderze data/, połącz je w jeden dataset i wygeneruj raport z podstawowymi statystykami"
```

---

## 3. Web scraping

**Żądanie NLP:**
```
Pobierz wszystkie artykuły z strony news.com, wyodrębnij tytuły i treść, 
a następnie zapisz w formacie JSON
```

**Komenda:**
```bash
python generate_config.py --template web_scraping "Pobierz artykuły z news.com"
```

---

## 4. Integracja z API

**Żądanie NLP:**
```
Pobierz dane z REST API, przefiltruj według daty i zapisz do bazy danych PostgreSQL
```

---

## 5. Przetwarzanie obrazów

**Żądanie NLP:**
```
Zmień rozmiar wszystkich zdjęć w folderze images/ na 800x600 i zapisz jako JPEG
```

---

## Użycie

### Generowanie konfiguracji:
```bash
# Tryb interaktywny
python generate_config.py --interactive

# Z podanym żądaniem
python generate_config.py "Pobierz emaile z IMAP"

# Z konkretnym szablonem
python generate_config.py --template email_processing "Pobierz emaile"

# Z walidacją
python generate_config.py --validate "Pobierz emaile z IMAP"
```

### Uruchamianie zadań:
```bash
# Z wygenerowaną konfiguracją
python enhanced_run.py --config configs/email-processor.yaml

# Tylko walidacja
python enhanced_run.py --config configs/email-processor.yaml --validate-only

# Określone środowisko
python enhanced_run.py --config configs/email-processor.yaml --environment production
```

### Struktura wygenerowanej konfiguracji:
```yaml
apiVersion: dune.io/v1
kind: TaskConfiguration
metadata:
  name: email-imap-processor
  description: "Pobierz wszystkie wiadomości email..."
  version: "1.0"
  created: "2025-06-21T10:00:00Z"
  tags: [email_processing, auto-generated]

task:
  natural_language: "Pobierz wszystkie wiadomości..."
  requirements: [download_emails, organize_files, connect_imap]
  expected_output:
    type: file_structure
    pattern: "output/skrzynka/{year}.{month}/*.eml"

runtime:
  type: docker
  base_image: python:3.11-slim
  python_packages:
    required: [imaplib2, email-validator, python-dotenv, loguru]
    optional: [beautifulsoup4, chardet]
  environment:
    required: [IMAP_SERVER, IMAP_USERNAME, IMAP_PASSWORD]
    optional: [IMAP_PORT, IMAP_USE_SSL, OUTPUT_DIR]

# ... reszta konfiguracji
```