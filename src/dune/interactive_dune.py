#!/usr/bin/env python3
"""
Interaktywny CLI dla systemu Dune - mapowanie zadań do bibliotek.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Dodaj src do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interactive_mapper import InteractiveMapper
from config_generator import ConfigGenerator


def main():
    """Główna funkcja interaktywnego CLI."""

    parser = argparse.ArgumentParser(
        description="Dune Interactive - Mapowanie zadań do bibliotek"
    )

    parser.add_argument(
        "request",
        nargs='?',
        help="Żądanie w języku naturalnym"
    )

    parser.add_argument(
        "--discover", "-d",
        action="store_true",
        help="Odkryj interfejsy zainstalowanych bibliotek"
    )

    parser.add_argument(
        "--save-config", "-s",
        type=str,
        help="Zapisz wygenerowaną konfigurację do pliku"
    )

    parser.add_argument(
        "--auto-install", "-a",
        action="store_true",
        help="Automatycznie zainstaluj wykryte biblioteki"
    )

    args = parser.parse_args()

    # Konfiguruj logowanie
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
        level="INFO"
    )

    try:
        if args.discover:
            run_discovery_mode()
            return

        # Pobierz zadanie
        if not args.request:
            request = get_interactive_request()
        else:
            request = args.request

        if not request:
            logger.error("❌ Nie podano zadania")
            return

        # Uruchom mapowanie
        result = run_interactive_mapping(request, args)

        # Zapisz konfigurację jeśli żądano
        if args.save_config and result:
            save_generated_config(result, args.save_config)

    except KeyboardInterrupt:
        print("\n👋 Do widzenia!")
    except Exception as e:
        logger.error(f"❌ Błąd: {e}")
        sys.exit(1)


def get_interactive_request() -> str:
    """Pobiera zadanie w trybie interaktywnym."""

    print("\n" + "=" * 70)
    print("🏜️  DUNE - INTERAKTYWNY MAPPER BIBLIOTEK")
    print("=" * 70)
    print("Opisz zadanie, które chcesz wykonać w języku naturalnym.")
    print("")
    print("💡 Przykłady:")
    print("   • Pobierz emaile z IMAP i zapisz w folderach według dat")
    print("   • Przeanalizuj pliki CSV i wygeneruj raport z wykresami")
    print("   • Pobierz dane z API REST i zapisz do bazy PostgreSQL")
    print("   • Zmień rozmiar wszystkich zdjęć w folderze na 800x600")
    print("   • Wyślij emaile do listy odbiorców z załącznikami")
    print("=" * 70)

    request = input("\n📝 Twoje zadanie: ").strip()
    return request


def run_discovery_mode():
    """Uruchamia tryb odkrywania bibliotek."""

    print("\n🔍 TRYB ODKRYWANIA BIBLIOTEK")
    print("=" * 40)

    mapper = InteractiveMapper()

    # Lista pakietów do sprawdzenia
    packages_to_check = [
        "requests", "pandas", "sqlalchemy", "beautifulsoup4",
        "selenium", "matplotlib", "numpy", "pillow", "opencv-python",
        "scrapy", "django", "flask", "fastapi"
    ]

    discovered = []

    for package in packages_to_check:
        print(f"🔎 Sprawdzanie {package}...")
        interface = mapper.discover_cli_interface(package)

        if interface:
            discovered.append((package, interface))
            print(f"   ✅ Znaleziono interfejs")
        else:
            print(f"   ❌ Brak interfejsu lub nie zainstalowany")

    print(f"\n📊 PODSUMOWANIE ODKRYCIA")
    print("=" * 40)
    print(f"Sprawdzono: {len(packages_to_check)} pakietów")
    print(f"Odkryto: {len(discovered)} interfejsów")

    if discovered:
        print(f"\n📚 Odkryte biblioteki:")
        for package, interface in discovered:
            func_count = len(interface.get("main_functions", []))
            print(f"   • {package}: {func_count} funkcji głównych")


def run_interactive_mapping(request: str, args) -> dict:
    """Uruchamia interaktywny proces mapowania."""

    mapper = InteractiveMapper()

    # Uruchom mapowanie
    result = mapper.run_interactive_mapping(request)

    if not result:
        return {}

    # Auto-instalacja jeśli żądano
    if args.auto_install and result.get("libraries"):
        install_detected_libraries(result["libraries"])

    # Wygeneruj pełną konfigurację
    config = generate_full_config(result)
    result["full_config"] = config

    return result


def install_detected_libraries(libraries):
    """Automatycznie instaluje wykryte biblioteki."""

    print(f"\n📦 AUTO-INSTALACJA BIBLIOTEK")
    print("=" * 40)

    import subprocess

    for library in libraries:
        package = library.package
        print(f"📦 Instalowanie {package}...")

        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True)
            print(f"   ✅ {package} zainstalowany")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Błąd instalacji {package}: {e}")


def generate_full_config(mapping_result) -> dict:
    """Generuje pełną konfigurację na podstawie mapowania."""

    generator = ConfigGenerator()

    # Wygeneruj bazową konfigurację
    config = generator.generate_config_from_nlp(mapping_result["natural_request"])

    # Zaktualizuj o zebrane parametry
    runtime_config = mapping_result.get("runtime_config", {}).get("runtime", {})
    if runtime_config:
        config["runtime"].update(runtime_config)

    # Dodaj szczegóły zebranych parametrów
    if mapping_result.get("parameters"):
        config["metadata"]["collected_parameters"] = mapping_result["parameters"]

    # Dodaj informacje o użytych bibliotekach
    if mapping_result.get("libraries"):
        library_info = []
        for lib in mapping_result["libraries"]:
            library_info.append({
                "name": lib.name,
                "package": lib.package,
                "main_function": lib.main_function
            })
        config["metadata"]["mapped_libraries"] = library_info

    return config


def save_generated_config(result, filename):
    """Zapisuje wygenerowaną konfigurację do pliku."""

    config = result.get("full_config")
    if not config:
        logger.warning("⚠️  Brak konfiguracji do zapisania")
        return

    generator = ConfigGenerator()
    saved_path = generator.save_config_to_file(config, filename)

    print(f"\n💾 Konfiguracja zapisana do: {saved_path}")


def show_execution_guide(result):
    """Pokazuje przewodnik uruchamiania zadania."""

    if not result:
        return

    print(f"\n🚀 PRZEWODNIK URUCHAMIANIA")
    print("=" * 40)

    # Pokaż wymagane zmienne środowiskowe
    runtime_config = result.get("runtime_config", {}).get("runtime", {})
    required_vars = runtime_config.get("environment", {}).get("required", [])

    if required_vars:
        print(f"🔧 Wymagane zmienne środowiskowe:")
        for var in required_vars:
            print(f"   export {var}=wartość")
        print()

    # Pokaż komendy instalacji
    packages = runtime_config.get("python_packages", {}).get("required", [])
    if packages:
        print(f"📦 Instalacja pakietów:")
        print(f"   pip install {' '.join(packages)}")
        print()

    # Pokaż komendy uruchamiania
    print(f"🚀 Uruchamianie:")
    print(f"   python enhanced_run.py")

    if result.get("full_config"):
        config_name = result["full_config"]["metadata"]["name"]
        print(f"   # lub z konfiguracją:")
        print(f"   python enhanced_run.py --config configs/{config_name}.yaml")


if __name__ == "__main__":
    main()