#!/bin/bash

echo "🚀 Uruchamianie dune - Procesora Danych"
echo "======================================"

# Sprawdź czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nie jest zainstalowany. Zainstaluj Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose nie jest zainstalowany."
    exit 1
fi

echo "✅ Docker i Docker Compose dostępne"

# Sprawdź czy .env istnieje
if [ ! -f .env ]; then
    echo "❌ Plik .env nie istnieje. Tworzę domyślny..."
    cat > .env << EOF
# Konfiguracja IMAP
IMAP_SERVER=localhost
IMAP_PORT=143
IMAP_USERNAME=testuser@example.com
IMAP_PASSWORD=testpass123
IMAP_USE_SSL=false

# Ścieżka do folderu wyjściowego
OUTPUT_DIR=./output

# Konfiguracja Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Konfiguracja logowania
LOG_LEVEL=INFO
EOF
    echo "✅ Utworzono plik .env z domyślną konfiguracją"
fi

# Utwórz potrzebne foldery
echo "📁 Tworzenie folderów..."
mkdir -p docker/mail/testuser@example.com/{cur,new,tmp}
mkdir -p output
mkdir -p logs

echo "✅ Foldery utworzone"

# Sprawdź czy są przykładowe emaile
if [ ! -d "docker/mail/testuser@example.com/new" ] || [ -z "$(ls -A docker/mail/testuser@example.com/new)" ]; then
    echo "📧 Tworzenie przykładowych wiadomości email..."
    python3 setup_test_emails.py
    echo "✅ Przykładowe wiadomości utworzone"
fi

# Zatrzymaj istniejące kontenery
echo "🛑 Zatrzymywanie istniejących kontenerów..."
docker-compose down

# Zbuduj i uruchom serwisy
echo "🏗️  Budowanie i uruchamianie serwisów..."
docker-compose up --build -d

echo ""
echo "⏳ Oczekiwanie na uruchomienie serwisów..."

# Czekaj na Ollama
echo "🤖 Sprawdzanie Ollama..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama jest gotowa"
        break
    fi
    echo "   Próba $i/30 - czekam na Ollama..."
    sleep 5
done

# Czekaj na serwer pocztowy
echo "📧 Sprawdzanie serwera IMAP..."
for i in {1..20}; do
    if nc -z localhost 143 2>/dev/null; then
        echo "✅ Serwer IMAP jest gotowy"
        break
    fi
    echo "   Próba $i/20 - czekam na IMAP..."
    sleep 3
done

echo ""
echo "🎉 System dune jest gotowy!"
echo ""
echo "📋 Dostępne serwisy:"
echo "   • IMAP Server: localhost:143"
echo "   • Ollama API: http://localhost:11434"
echo "   • Dane logowania: testuser@example.com / testpass123"
echo ""
echo "🏃 Uruchamianie głównego procesora..."
echo "=====================================
"

# Uruchom główny procesor
docker-compose logs -f dune