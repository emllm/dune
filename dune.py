#!/usr/bin/env python3
"""
Główny skrypt uruchamiający procesor danych z automatycznym wykrywaniem bibliotek.
"""

import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Dodaj src do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dune.processor_engine import ProcessorEngine
from dune.llm_analyzer import LLMAnalyzer


def main():
    """Główna funkcja uruchamiająca system."""

    # Załaduj zmienne środowiskowe
    load_dotenv()

    # Konfiguruj logowanie
    logger.add("logs/processor.log", rotation="1 MB")
    logger.info("Uruchamianie procesora danych...")

    # Inicjalizuj komponenty
    llm_analyzer = LLMAnalyzer(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "mistral:7b")
    )

    processor_engine = ProcessorEngine(llm_analyzer)

    # Przykładowe zadanie w języku naturalnym
    natural_request = """
    Pobierz wszystkie wiadomości email ze skrzynki IMAP i zapisz je w folderach 
    uporządkowanych według roku i miesiąca w formacie skrzynka/rok.miesiąc/*.eml.
    Dane logowania do skrzynki znajdziesz w pliku .env.
    """

    logger.info(f"Przetwarzanie żądania: {natural_request}")

    try:
        # Przeanalizuj żądanie i wykonaj
        result = processor_engine.process_natural_request(natural_request)

        logger.success(f"Zadanie zakończone pomyślnie: {result}")
        print(f"✅ Zadanie zakończone pomyślnie!")
        print(f"📊 Wynik: {result}")

    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania: {e}")
        print(f"❌ Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()