# 🏜️ Dune - Inteligentny Procesor Danych

**Dune** to zaawansowany system przetwarzania danych, który automatycznie mapuje zadania opisane w języku naturalnym do odpowiednich bibliotek Python, inteligentnie konfiguruje środowisko i wykonuje złożone operacje na danych.

## ✨ **Kluczowe funkcje**

- 🧠 **Inteligentne mapowanie** - Automatyczne wykrywanie bibliotek na podstawie opisu zadania
- 🔧 **Auto-konfiguracja** - Wykrywanie i konfiguracja zmiennych środowiskowych
- 🗣️ **Język naturalny** - Opisuj zadania po polsku, Dune zrozumie
- 📦 **Dynamiczne biblioteki** - Automatyczna instalacja wymaganych pakietów
- 🤖 **LLM Integration** - Mistral 7B do analizy i generowania kodu
- ✅ **Walidacja** - Sprawdzanie środowiska przed i po wykonaniu
- 🐳 **Docker ready** - Kompletne środowisko w kontenerach

## 🚀 **Quick Start**

### **1. Pierwsza instalacja**
```bash
git clone https://github.com/emllm/dune.git
cd dune
make quick-start
```

### **2. Interaktywne uruchomienie (zalecane)**
```bash
make run
```
Zostaniesz poproszony o opisanie zadania, np.:
> *"Pobierz emaile z IMAP i zapisz w folderach według dat"*

### **3. Szybkie zadania**
```bash
make run-quick TASK="Przeanalizuj pliki CSV i wygeneruj raport"
```

## 🧠 **Jak to działa?**

### **Krok 1: Analiza zadania**
```
User: "Pobierz emaile z IMAP i zapisz według dat"
       ↓
Dune: 🔍 Wykryto: email processing
      📚 Mapped to: imaplib, email
      🔧 Potrzebne: IMAP_SERVER, IMAP_USERNAME, IMAP_PASSWORD
```

### **Krok 2: Interaktywna konfiguracja**
```
🔧 KONFIGURACJA: IMAP Email Client
📌 IMAP_SERVER (Adres serwera IMAP): imap.gmail.com
📌 IMAP_USERNAME (auto-wykryto z git): user@gmail.com
📌 IMAP_PASSWORD (Hasło IMAP): ********
💾 Zapisano parametry do .env
```

### **Krok 3: Automatyczne wykonanie**
```
📦 Instalowanie: imaplib2, email-validator
🔍 Walidacja środowiska... ✅
🤖 Generowanie kodu...
🚀 Wykonywanie zadania...
✅ Pobrano 25 emaili do 3 folderów
```

## 📚 **Obsługiwane typy zadań**

| Typ zadania | Przykładowy opis | Biblioteki |
|-------------|------------------|------------|
| **📧 Email** | "Pobierz emaile z IMAP" | `imaplib`, `email` |
| **📊 Dane** | "Przeanalizuj CSV i stwórz wykres" | `pandas`, `matplotlib` |
| **🌐 Web** | "Pobierz dane z API REST" | `requests`, `beautifulsoup4` |
| **🗄️ Bazy** | "Wyeksportuj tabelę do CSV" | `sqlalchemy`, `pandas` |
| **🖼️ Obrazy** | "Zmień rozmiar zdjęć na 800x600" | `Pillow`, `opencv` |
| **📄 Pliki** | "Połącz wszystkie Excel w jeden" | `openpyxl`, `pandas` |

## 🔧 **Tryby uruchomienia**

### **1. Interaktywny (zalecany)**
```bash
make run
# Prowadzi krok po kroku przez proces
```

### **2. Szybki**
```bash
make run-quick TASK="Pobierz emaile z IMAP"
# Automatyczna konfiguracja i wykonanie
```

### **3. Z konfiguracją YAML**
```bash
make config                              # Wygeneruj konfigurację
make run-config CONFIG=configs/task.yaml # Uruchom
```

### **4. Docker**
```bash
make docker-run
# Pełne środowisko z testową skrzynką IMAP
```

## 🛠️ **Dostępne polecenia**

| Polecenie | Opis |
|-----------|------|
| `make run` | Tryb interaktywny |
| `make run-quick TASK="..."` | Szybkie uruchomienie |
| `make config` | Generator konfiguracji |
| `make map` | Interaktywny mapper bibliotek |
| `make discover` | Odkryj dostępne biblioteki |
| `make validate CONFIG=...` | Walidacja konfiguracji |
| `make docker-run` | Uruchomienie w Docker |
| `make demo` | Demo scenariusze |

## 💡 **Przykłady zadań**

### **Email Processing**
```bash
make run-quick TASK="Pobierz wszystkie emaile z IMAP localhost i zapisz w folderach według roku i miesiąca"
```

### **CSV Analysis**
```bash
make run-quick TASK="Przeanalizuj wszystkie pliki CSV w folderze data, połącz je i wygeneruj raport z wykresami"
```

### **Web Scraping**
```bash
make run-quick TASK="Pobierz tytuły artykułów ze strony news.ycombinator.com i zapisz do JSON"
```

### **Database Export**
```bash
make run-quick TASK="Połącz się z PostgreSQL localhost i wyeksportuj tabelę users do CSV"
```

### **Image Processing**
```bash
make run-quick TASK="Zmień rozmiar wszystkich zdjęć JPG w folderze photos na 800x600 pikseli"
```

## 🔍 **Inteligentne wykrywanie środowiska**

Dune automatycznie wykrywa:

### **📧 Dla emaili:**
- ✅ Serwery IMAP (gmail, outlook, lokalne)
- ✅ Username z konfiguracji Git
- ✅ Porty i SSL na podstawie serwera

### **🗄️ Dla baz danych:**
- ✅ Lokalne bazy (PostgreSQL, MySQL, Redis)
- ✅ Konfiguracje z docker-compose.yml
- ✅ Connection stringi z .env

### **📁 Dla plików:**
- ✅ Katalogi input/output w projekcie
- ✅ Popularne ścieżki systemowe
- ✅ Uprawnienia do zapisu

### **🔧 Dla API:**
- ✅ Klucze z zmiennych środowiskowych
- ✅ Endpointy z plików konfiguracyjnych

## 📄 **Format konfiguracji YAML**

```yaml
apiVersion: dune.io/v1
kind: TaskConfiguration
metadata:
  name: email-processor
  description: "Pobieranie emaili z IMAP"

task:
  natural_language: "Pobierz emaile z IMAP i zapisz według dat"
  requirements: [download_emails, organize_files]

runtime:
  python_packages:
    required: [imaplib2, email-validator]
  environment:
    required: [IMAP_SERVER, IMAP_USERNAME, IMAP_PASSWORD]

services:
  dependencies:
    - name: imap-server
      type: imap
      connection:
        host: "${IMAP_SERVER}"
        port: 993

validation:
  pre_execution:
    - type: service_connectivity
    - type: environment_variables
  post_execution:
    - type: output_verification
```

## 🔧 **Architektura systemu**

```
dune/
├── src/
│   ├── interactive_mapper.py     # Mapowanie zadań do bibliotek
│   ├── smart_env_manager.py      # Inteligentne zarządzanie środowiskiem
│   ├── processor_engine.py       # Silnik przetwarzania
│   ├── llm_analyzer.py          # Analizator LLM
│   ├── task_validator.py        # Walidator zadań
│   └── config_generator.py      # Generator konfiguracji
├── configs/                     # Konfiguracje YAML
├── docker/                      # Środowisko Docker
├── output/                      # Wyniki
├── dune.py                  # Główny skrypt
└── Makefile                     # Polecenia
```

## 🚀 **Demo scenariusze**

```bash
# Sprawdź dostępne demo
make demo

# Konkretne scenariusze
make demo-email    # Przetwarzanie emaili
make demo-csv      # Analiza danych CSV  
make demo-web      # Web scraping
make demo-db       # Operacje na bazie danych
```

## 🔍 **Troubleshooting**

### **Problem: Nie można połączyć z IMAP**
```bash
# Sprawdź konfigurację
make validate CONFIG=configs/email-task.yaml

# Auto-naprawa środowiska
make run --auto-configure
```

### **Problem: Brak bibliotek**
```bash
# Odkryj dostępne biblioteki
make discover

# Auto-instalacja
poetry install --extras all
```

### **Problem: Błędy walidacji**
```bash
# Szczegółowe logi
make run --log-level DEBUG

# Status systemu
make status
```

## 🌟 **Zaawansowane funkcje**

### **1. Własne mapowania bibliotek**
```python
# Dodaj w interactive_mapper.py
TaskMapping(
    task_keywords=["moje", "zadanie"],
    libraries=[custom_library],
    priority=1
)
```

### **2. Niestandardowe zmienne środowiskowe**
```python
# Dodaj w smart_env_manager.py
"MY_VAR": EnvVariable(
    name="MY_VAR",
    description="Moja zmienna",
    type="str",
    required=True,
    auto_detect_methods=["custom_method"]
)
```

### **3. Własne walidatory**
```python
# Dodaj w task_validator.py
def _validate_custom_check(self, config) -> bool:
    # Implementacja sprawdzenia
    return True
```

## 📊 **Monitoring i logi**

```bash
# Logi w czasie rzeczywistym
make logs

# Status systemu
make status

# Szczegółowe informacje
make info
```

## 🤝 **Współpraca z istniejącymi systemami**

### **Protokoły:**
- ✅ IMAP/POP3 (poczta)
- ✅ HTTP/REST (API)
- ✅ SQL (bazy danych)
- ✅ FTP/SFTP (pliki)

### **Formaty danych:**
- ✅ CSV, Excel (tabele)
- ✅ JSON, XML (struktura)
- ✅ Email (EML, MSG)
- ✅ Obrazy (JPEG, PNG, WEBP)

## 🔮 **Roadmap**

- 🔄 **Workflow engine** - Złożone pipeline'y danych
- 🌐 **Web UI** - Graficzny interfejs użytkownika
- 📊 **Dashboard** - Monitoring w czasie rzeczywistym
- 🔌 **Plugin system** - Rozszerzenia społeczności
- ☁️ **Cloud** - Deployment na AWS/Azure/GCP
- 🤖 **More AI** - GPT-4, Claude, Llama

## 📄 **Licencja**

Apache License - patrz plik LICENSE

---

## 🎯 **Zaczynamy!**

```bash
# Pobierz i zainstaluj
git clone https://github.com/emllm/dune.git
cd dune
make quick-start

# Uruchom pierwszy projekt
make run
```

**Opisz swoje zadanie po polsku, a Dune zajmie się resztą! 🏜️✨**



## 🎉 **Podsumowanie - Dune: Kompletny Inteligentny System**

Stworzyłem dla Ciebie **Dune** - zaawansowany system, który stanowi ewolucję w kierunku prawdziwie inteligentnego przetwarzania danych. Oto kluczowe innowacje:

## 🧠 **Interaktywny Algorytm Mapowania**

### **1. Automatyczne wykrywanie bibliotek**
```python
# System analizuje: "Pobierz emaile z IMAP"
task_keywords=["email", "imap"] → libraries=[imaplib, email]
```

### **2. Inteligentne odpytywanie o parametry**
```python
# Auto-wykrywa z Git, systemów, .env
IMAP_USERNAME = git_config.user.email || system_user@domain
IMAP_SERVER = common_providers || dns_lookup || user_input
```

### **3. CLI Analysis & Interface Discovery**
```python
# Analizuje biblioteki w locie:
discover_cli_interface("requests") → {"main_functions": [...], "parameters": [...]}
```

## 🔧 **Smart Environment Manager**

### **Automatyczne wykrywanie środowiska:**
- ✅ **Git config** → email użytkownika
- ✅ **Docker Compose** → bazy danych  
- ✅ **Network scanning** → dostępne serwisy
- ✅ **File system** → katalogi input/output
- ✅ **Keyring** → zapisane hasła

### **Inteligentna walidacja:**
- ✅ **Regex patterns** dla formatów
- ✅ **Network connectivity** do serwisów
- ✅ **File permissions** i miejsce na dysku
- ✅ **Auto-repair** błędów środowiska

## 🚀 **Przewagi nad konkurencją**

| Funkcja | Airflow | Prefect | **Dune** |
|---------|---------|---------|----------|
| **Natural Language Input** | ❌ | ❌ | ✅ |
| **Auto Library Detection** | ❌ | ❌ | ✅ |
| **Interactive Configuration** | ❌ | ❌ | ✅ |
| **Environment Auto-Discovery** | ❌ | ❌ | ✅ |
| **CLI Interface Analysis** | ❌ | ❌ | ✅ |
| **Zero-config Start** | ❌ | ⚠️ | ✅ |

## 🎯 **Kluczowe scenariusze użycia**

### **Scenario 1: Nowy użytkownik**
```bash
make quick-start
make run
> "Pobierz emaile z mojej skrzynki Gmail"
🔍 Auto-wykryto: user@gmail.com z Git
📚 Mapped: imaplib → IMAP processing  
🔧 Konfiguracja: 3 pytania
✅ Gotowe: 25 emaili w folderach
```

### **Scenario 2: Data Scientist**  
```bash
make run-quick TASK="Przeanalizuj sales.csv i pokaż trendy"
🔍 Wykryto: pandas, matplotlib
📁 Auto-znaleziono: ./data/sales.csv
📊 Wygenerowano: wykresy + raport
```

### **Scenario 3: DevOps**
```bash
make run-quick TASK="Wyeksportuj users z PostgreSQL"
🔍 Wykryto: sqlalchemy
🗄️ Auto-połączono: localhost:5432
💾 Eksport: users.csv (1500 rekordów)
```

## 🏗️ **Architektura Innovation**

### **1. Task-to-Library Mapping Engine**
- **Keyword analysis** → biblioteki
- **Context awareness** → parametry
- **Priority scoring** → najlepsza opcja

### **2. Smart Environment Detection**
- **Multi-source discovery** (git, docker, system)
- **Intelligent fallbacks** → user prompts
- **Auto-validation** → immediate feedback

### **3. Interactive Configuration Flow**
- **Progressive disclosure** → tylko potrzebne parametry
- **Smart defaults** → z auto-detekcji
- **Real-time validation** → błędy od razu

## 📈 **Ready for Production**

```bash
# Development
make run                    # Interactive mode

# Testing  
make validate CONFIG=...    # Full validation

# Production
make docker-run            # Containerized execution
```

## 🔮 **Rozszerzalność**

System został zaprojektowany jako **extensible platform**:

- **Library mappings** → łatwe dodawanie nowych bibliotek
- **Environment detectors** → własne metody wykrywania  
- **Validators** → niestandardowe sprawdzenia
- **Task templates** → gotowe scenariusze


