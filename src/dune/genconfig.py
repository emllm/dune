#!/usr/bin/env python3
"""
CLI do generowania konfiguracji zadań z żądań w języku naturalnym.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Dodaj src do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_generator import ConfigGenerator
from llm_analyzer import LLMAnalyzer


def main():
    """Główna funkcja CLI."""

    parser = argparse.ArgumentParser(
        description="Generator konfiguracji dune z żądań w języku naturalnym"
    )

    parser.add_argument(
        "request",
        nargs='?',
        help="Żądanie w języku naturalnym (lub zostanie pobrane interaktywnie)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Ścieżka do pliku wyjściowego (domyślnie: configs/auto-generated.yaml)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Tryb interaktywny"
    )

    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Waliduj wygenerowaną konfigurację"
    )

    parser.add_argument(
        "--template", "-t",
        type=str,
        choices=["email_processing", "database_processing", "file_processing", "web_scraping"],
        help="Użyj konkretnego szablonu"
    )

    args = parser.parse_args()

    # Konfiguruj logowanie
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

    logger.info("🔧 Generator konfiguracji dune")

    # Pobierz żądanie
    if args.interactive or not args.request:
        print("\n" + "=" * 60)
        print("🤖 GENERATOR KONFIGURACJI dune")
        print("=" * 60)
        print("Opisz zadanie, które chcesz wykonać w języku naturalnym.")
        print("Przykłady:")
        print("• Pobierz emaile z IMAP i zapisz w folderach według dat")
        print("• Przeanalizuj pliki CSV i wygeneruj raport")
        print("• Pobierz dane z API i zapisz do bazy danych")
        print("=" * 60)

        request = input("\n📝 Twoje zadanie: ")
        if not request.strip():
            logger.error("❌ Nie podano żądania")
            return
    else:
        request = args.request

    try:
        # Inicjalizuj generator
        generator = ConfigGenerator()

        logger.info("🔄 Analizowanie żądania...")

        # Wygeneruj konfigurację
        config = generator.generate_config_from_nlp(request)

        # Określ ścieżkę wyjściową
        if args.output:
            output_path = args.output
        else:
            task_name = config["metadata"]["name"]
            output_path = f"configs/{task_name}.yaml"

        # Zapisz konfigurację
        saved_path = generator.save_config_to_file(config, output_path)

        # Pokaż podsumowanie
        print("\n" + "=" * 60)
        print("✅ KONFIGURACJA WYGENEROWANA POMYŚLNIE!")
        print("=" * 60)
        print(f"📄 Plik: {saved_path}")
        print(f"🎯 Zadanie: {config['metadata']['name']}")
        print(f"📦 Pakiety: {len(config['runtime']['python_packages']['required'])} wymaganych")
        print(f"🔧 Usługi: {len(config['services'].get('dependencies', []))} zależności")
        print(f"✅ Walidacja: {len(config['validation']['pre_execution'])} sprawdzeń")

        # Pokaż kluczowe informacje
        print(f"\n📋 PODSUMOWANIE:")
        print(f"   • Typ zadania: {config['metadata']['tags'][0] if config['metadata']['tags'] else 'generic'}")
        print(f"   • Wymagania: {', '.join(config['task']['requirements'])}")

        required_packages = config['runtime']['python_packages']['required']
        if required_packages:
            print(f"   • Pakiety: {', '.join(required_packages)}")

        required_env = config['runtime']['environment']['required']
        if required_env:
            print(f"   • Zmienne: {', '.join(required_env)}")

        print(f"\n🚀 URUCHOMIENIE:")
        print(f"   python enhanced_run.py --config {saved_path}")

        # Walidacja (jeśli zażądano)
        if args.validate:
            logger.info("🔍 Walidowanie konfiguracji...")
            from task_validator import TaskValidator

            validator = TaskValidator()
            try:
                loaded_config = validator.load_config(saved_path)
                logger.success("✅ Konfiguracja jest poprawna")
            except Exception as e:
                logger.error(f"❌ Błąd walidacji: {e}")

    except Exception as e:
        logger.error(f"❌ Błąd generowania konfiguracji: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()