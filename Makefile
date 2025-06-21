# Makefile dla projektu Dune
.PHONY: help install setup build run clean test docker-build docker-run config validate
# Project Makefile for emllm (Large Language Model Email Message Language)

# Project name
PROJECT_NAME = emllm

# POETRY environment
POETRY := poetry

# Python paths
PYTHON := $(shell $(POETRY) env info --path)/bin/python
PYTHON_SRC := src/$(PROJECT_NAME)

# Domyślny cel
help:
	@echo "🏜️  Dune - Inteligentny Procesor Danych"
	@echo "======================================="
	@echo ""
	@echo "Dostępne komendy:"
	@echo "  setup              - Pierwsze uruchomienie (instalacja + konfiguracja)"
	@echo "  install            - Instalacja zależności"
	@echo "  run                - Uruchomienie interaktywne"
	@echo "  run-quick TASK=... - Szybkie uruchomienie z zadaniem"
	@echo "  run-config CONFIG=... - Uruchomienie z konfiguracją YAML"
	@echo "  config             - Generator konfiguracji"
	@echo "  map                - Interaktywny mapper bibliotek"
	@echo "  validate CONFIG=... - Walidacja konfiguracji"
	@echo "  docker-build       - Budowanie kontenerów"
	@echo "  docker-run         - Uruchomienie w Docker"
	@echo "  discover           - Odkryj dostępne biblioteki"
	@echo "  test               - Uruchomienie testów"
	@echo "  clean              - Czyszczenie plików tymczasowych"
	@echo ""

# Pierwsze uruchomienie
setup: install create-dirs create-sample-emails
	@echo "✅ Dune został zainicjalizowany!"
	@echo "🚀 Możesz teraz uruchomić: make run lub make docker-run"

# Instalacja zależności
install:
	@echo "📦 Instalowanie zależności Dune..."
	$(POETRY) install --extras all
	@echo "✅ Zależności zainstalowane"

# Tworzenie katalogów
create-dirs:
	@echo "📁 Tworzenie katalogów..."
	mkdir -p docker/mail/testuser@example.com/{cur,new,tmp}
	mkdir -p output logs configs
	@echo "✅ Katalogi utworzone"

# Tworzenie przykładowych emaili
create-sample-emails:
	@echo "📧 Tworzenie przykładowych wiadomości..."
	python setup_test_emails.py
	@echo "✅ Przykładowe wiadomości utworzone"

# Uruchomienie interaktywne
run:
	@echo "🏜️  Uruchamianie Dune w trybie interaktywnym..."
	$(POETRY) run python dune.py --interactive

# Szybkie uruchomienie z zadaniem
run-quick:
	@echo "⚡ Szybkie uruchomienie..."
	@if [ -z "$(TASK)" ]; then \
		echo "❌ Podaj zadanie: make run-quick TASK='Pobierz emaile z IMAP'"; \
		exit 1; \
	fi
	$(POETRY) run python dune.py --quick "$(TASK)" --auto-configure

# Uruchomienie z konfiguracją
run-config:
	@echo "🚀 Uruchamianie z konfiguracją YAML..."
	@if [ -z "$(CONFIG)" ]; then \
		echo "❌ Podaj ścieżkę do konfiguracji: make run-config CONFIG=configs/task.yaml"; \
		exit 1; \
	fi
	$(POETRY) run python dune.py --config $(CONFIG)

# Generator konfiguracji
config:
	@echo "🔧 Generator konfiguracji Dune..."
	$(POETRY) run python generate_config.py --interactive

# Interaktywny mapper bibliotek
map:
	@echo "📚 Interaktywny mapper bibliotek..."
	$(POETRY) run python interactive_dune.py

# Walidacja konfiguracji
validate:
	@echo "🔍 Walidacja konfiguracji..."
	@if [ -z "$(CONFIG)" ]; then \
		echo "❌ Podaj ścieżkę do konfiguracji: make validate CONFIG=configs/task.yaml"; \
		exit 1; \
	fi
	$(POETRY) run python dune.py --config $(CONFIG) --validate-only

# Odkryj dostępne biblioteki
discover:
	@echo "🔍 Odkrywanie dostępnych bibliotek..."
	$(POETRY) run python interactive_dune.py --discover

# Docker - budowanie
docker-build:
	@echo "🏗️  Budowanie kontenerów Dune..."
	docker-compose build --no-cache
	@echo "✅ Kontenery zbudowane"

# Docker - uruchomienie
docker-run: create-sample-emails
	@echo "🏜️  Uruchamianie Dune w Docker..."
	docker-compose up -d
	@echo "⏳ Oczekiwanie na uruchomienie serwisów..."
	@sleep 10
	@echo "🎉 Serwisy uruchomione!"
	@echo "📋 Status serwisów:"
	docker-compose ps
	@echo ""
	@echo "📊 Logi głównego procesora:"
	docker-compose logs -f data-processor

# Zatrzymanie Docker
docker-stop:
	@echo "🛑 Zatrzymywanie kontenerów Dune..."
	docker-compose down
	@echo "✅ Kontenery zatrzymane"

# Testy
test:
	@echo "🧪 Uruchamianie testów Dune..."
	$(POETRY) run pytest tests/ -v
	@echo "✅ Testy zakończone"

# Czyszczenie
clean:
	@echo "🧹 Czyszczenie Dune..."
	rm -rf output/* logs/* __pycache__ .pytest_cache
	rm -rf docker/mail/testuser@example.com/{cur,new,tmp}/*
	docker-compose down --volumes --remove-orphans 2>/dev/null || true
	@echo "✅ Wyczyszczono"

# Status systemu
status:
	@echo "📊 Status systemu Dune:"
	@echo "======================="
	@echo ""
	@echo "📁 Katalogi:"
	@ls -la | grep -E "(output|logs|configs|docker)" || echo "   Brak katalogów"
	@echo ""
	@echo "📧 Przykładowe emaile:"
	@if [ -d "docker/mail/testuser@example.com/new" ]; then \
		echo "   $(shell ls docker/mail/testuser@example.com/new | wc -l) wiadomości"; \
	else \
		echo "   Brak wiadomości (uruchom: make create-sample-emails)"; \
	fi
	@echo ""
	@echo "🐳 Kontenery Docker:"
	@docker-compose ps 2>/dev/null || echo "   Docker Compose nie uruchomiony"
	@echo ""
	@echo "🔧 Konfiguracje:"
	@if [ -d "configs" ] && [ "$(shell ls configs/*.yaml 2>/dev/null | wc -l)" -gt 0 ]; then \
		ls configs/*.yaml 2>/dev/null | head -5; \
		if [ "$(shell ls configs/*.yaml 2>/dev/null | wc -l)" -gt 5 ]; then \
			echo "   ... i $(shell expr $(shell ls configs/*.yaml 2>/dev/null | wc -l) - 5) więcej"; \
		fi \
	else \
		echo "   Brak konfiguracji (uruchom: make config)"; \
	fi

# Przykłady użycia
examples:
	@echo "💡 Przykłady użycia Dune:"
	@echo "========================="
	@echo ""
	@echo "1. Pierwsza instalacja:"
	@echo "   make setup"
	@echo ""
	@echo "2. Tryb interaktywny (zalecany dla nowych użytkowników):"
	@echo "   make run"
	@echo ""
	@echo "3. Szybkie zadania:"
	@echo "   make run-quick TASK='Pobierz emaile z IMAP i zapisz według dat'"
	@echo "   make run-quick TASK='Przeanalizuj pliki CSV i wygeneruj raport'"
	@echo ""
	@echo "4. Z konfiguracją YAML:"
	@echo "   make config                              # Wygeneruj konfigurację"
	@echo "   make run-config CONFIG=configs/task.yaml # Uruchom z konfiguracją"
	@echo ""
	@echo "5. Mapowanie bibliotek:"
	@echo "   make map         # Interaktywny mapper"
	@echo "   make discover    # Odkryj dostępne biblioteki"
	@echo ""
	@echo "6. Docker:"
	@echo "   make docker-run  # Pełne środowisko"
	@echo ""
	@echo "7. Walidacja:"
	@echo "   make validate CONFIG=configs/task.yaml"
	@echo ""

# Demo scenarios
demo:
	@echo "🎬 Demo scenariusze Dune:"
	@echo "========================"
	@echo ""
	@echo "Wybierz demo:"
	@echo "  1. Email processing   - make demo-email"
	@echo "  2. CSV analysis       - make demo-csv"
	@echo "  3. Web scraping       - make demo-web"
	@echo "  4. Database access    - make demo-db"
	@echo ""

demo-email:
	@echo "📧 Demo: Przetwarzanie emaili"
	$(POETRY) run python dune.py --quick "Pobierz wszystkie emaile z IMAP localhost i zapisz w folderach według miesięcy" --auto-configure

demo-csv:
	@echo "📊 Demo: Analiza CSV"
	$(POETRY) run python dune.py --quick "Przeanalizuj pliki CSV w folderze data i wygeneruj raport z wykresami" --auto-configure

demo-web:
	@echo "🌐 Demo: Web scraping"
	$(POETRY) run python dune.py --quick "Pobierz tytuły artykułów ze strony news.ycombinator.com" --auto-configure

demo-db:
	@echo "🗄️  Demo: Baza danych"
	$(POETRY) run python dune.py --quick "Połącz się z bazą PostgreSQL i wyeksportuj tabelę users do CSV" --auto-configure

# Quick start dla nowych użytkowników
quick-start: setup
	@echo ""
	@echo "🎉 DUNE QUICK START ZAKOŃCZONY!"
	@echo "==============================="
	@echo ""
	@echo "🏜️  Witaj w Dune! Twój inteligentny procesor danych jest gotowy."
	@echo ""
	@echo "🚀 Co teraz?"
	@echo "   1. make run          - Tryb interaktywny (polecany)"
	@echo "   2. make examples     - Zobacz przykłady użycia"
	@echo "   3. make demo         - Uruchom demo scenariusze"
	@echo ""
	@echo "💡 Wskazówka: Zacznij od 'make run' i opisz swoje zadanie po polsku!"
	@echo ""

# Informacje o systemie
info:
	@echo "ℹ️  Informacje o systemie Dune:"
	@echo "==============================="
	@echo "Python: $(shell python --version 2>/dev/null || echo 'Nie zainstalowany')"
	@echo "$(POETRY): $(shell $(POETRY) --version 2>/dev/null || echo 'Nie zainstalowany')"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Nie zainstalowany')"
	@echo "Docker Compose: $(shell docker-compose --version 2>/dev/null || echo 'Nie zainstalowany')"
	@echo ""
	@echo "Katalog Dune: $(PWD)"
	@echo "Wielkość output: $(shell du -sh output 2>/dev/null || echo '0B')"
	@echo "Wielkość logs: $(shell du -sh logs 2>/dev/null || echo '0B')"
	@echo "Konfiguracje: $(shell ls configs/*.yaml 2>/dev/null | wc -l || echo '0') plików"

# Build package
.PHONY: build
build:
	$(POETRY) version patch
	$(POETRY) build

# Publish package to PyPI
.PHONY: publish
publish: build
	$(POETRY) publish --no-interaction

# Generate documentation
.PHONY: docs
docs:
	$(PYTHON) -m pdoc --html --output-dir docs .

# Start REST server
.PHONY: start-server
start-server:
	$(PYTHON) -m emllm.cli rest --host 0.0.0.0 --port 8000

# Test message parsing
.PHONY: test-message
test-message:
	$(PYTHON) -m emllm.cli parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test\n\nHello World"

# Run full test suite
.PHONY: test-all
test-all: lint type-check test
	echo "All tests passed!"
