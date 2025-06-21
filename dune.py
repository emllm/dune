#!/usr/bin/env python3
"""
Dune Runner - Główny skrypt z interaktywnym mapowaniem i auto-konfiguracją.
"""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Dodaj src do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interactive_mapper import InteractiveMapper
from smart_env_manager import SmartEnvManager
from processor_engine import ProcessorEngine
from llm_analyzer import LLMAnalyzer
from task_validator import TaskValidator
from config_generator import ConfigGenerator


def setup_logging(log_level: str = "INFO"):
    """Konfiguruje system logowania."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )
    logger.add(
        "logs/dune-execution.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level=log_level,
        rotation="10 MB"
    )


def main():
    """Główna funkcja programu."""

    parser = argparse.ArgumentParser(description="Dune - Inteligentny procesor danych")

    # Tryby działania
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Tryb interaktywny z mapowaniem bibliotek"
    )
    mode_group.add_argument(
        "--config", "-c",
        type=str,
        help="Uruchom z plikiem konfiguracji YAML"
    )
    mode_group.add_argument(
        "--quick", "-q",
        type=str,
        help="Szybkie uruchomienie z zadaniem w tekście"
    )

    # Opcje
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Tylko walidacja bez wykonania"
    )
    parser.add_argument(
        "--auto-configure", "-a",
        action="store_true",
        help="Automatyczna konfiguracja środowiska"
    )
    parser.add_argument(
        "--save-config", "-s",
        type=str,
        help="Zapisz wygenerowaną konfigurację do pliku"
    )
    parser.add_argument(
        "--environment", "-e",
        type=str,
        default="development",
        choices=["development", "testing", "production"],
        help="Środowisko uruchomieniowe"
    )
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Poziom logowania"
    )

    args = parser.parse_args()

    # Konfiguracja
    setup_logging(args.log_level)
    load_dotenv()
    os.environ["DUNE_ENVIRONMENT"] = args.environment

    # Utwórz katalogi
    Path("logs").mkdir(exist_ok=True)
    Path("configs").mkdir(exist_ok=True)
    Path(os.getenv("OUTPUT_DIR", "./output")).mkdir(exist_ok=True)

    logger.info("🏜️  Uruchamianie Dune - Inteligentnego Procesora Danych")
    logger.info(f"🔧 Środowisko: {args.environment}")

    try:
        if args.interactive:
            run_interactive_mode(args)
        elif args.config:
            run_config_mode(args)
        elif args.quick:
            run_quick_mode(args)
        else:
            run_default_mode(args)

    except KeyboardInterrupt:
        logger.warning("⚠️  Przerwano przez użytkownika")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)


def run_interactive_mode(args):
    """Uruchamia tryb interaktywny z mapowaniem bibliotek."""

    print("\n" + "=" * 70)
    print("🏜️  DUNE - TRYB INTERAKTYWNY")
    print("=" * 70)
    print("Tryb z automatycznym mapowaniem zadań do bibliotek")
    print("i inteligentną konfiguracją zmiennych środowiskowych.")
    print("=" * 70)

    # Pobierz zadanie od użytkownika
    request = input("\n📝 Opisz zadanie w języku naturalnym: ").strip()

    if not request:
        logger.error("❌ Nie podano zadania")
        return

    # Inicjalizuj komponenty
    mapper = InteractiveMapper()
    env_manager = SmartEnvManager()

    # 1. Mapuj biblioteki
    logger.info("🔍 Mapowanie zadania do bibliotek...")
    libraries = mapper.analyze_task_and_map_libraries(request)

    if not libraries:
        print("❌ Nie znaleziono pasujących bibliotek")
        return

    print(f"\n📚 Znalezione biblioteki ({len(libraries)}):")
    for i, lib in enumerate(libraries, 1):
        print(f"   {i}. {lib.name} ({lib.package})")

    # 2. Interaktywne zbieranie parametrów
    collected_params = {}

    for library in libraries:
        if ask_yes_no(f"\nKonfigurować {library.name}?", default=True):
            params = mapper.interactive_parameter_collection(library)
            collected_params[library.name] = params

    # 3. Wykryj wymagane zmienne środowiskowe
    required_env_vars = []
    optional_env_vars = []

    for library in libraries:
        for param in library.required_params:
            env_var = f"DUNE_{param.upper()}"
            if env_var not in required_env_vars:
                required_env_vars.append(env_var)

        for param in library.optional_params:
            env_var = f"DUNE_{param.upper()}"
            if env_var not in optional_env_vars:
                optional_env_vars.append(env_var)

    # 4. Konfiguruj środowisko
    if required_env_vars or args.auto_configure:
        print(f"\n🔧 Konfiguracja zmiennych środowiskowych...")
        env_vars = env_manager.interactive_env_collection(required_env_vars, optional_env_vars)

        if env_vars and ask_yes_no("Zapisać zmienne do .env?", default=True):
            env_manager.save_to_env_file(env_vars)
            # Przeładuj .env
            load_dotenv()

    # 5. Wygeneruj i zapisz konfigurację
    generator = ConfigGenerator()
    config = generator.generate_config_from_nlp(request)

    # Zaktualizuj konfigurację o zebrane dane
    runtime_config = mapper.generate_runtime_config(libraries, collected_params)
    config["runtime"].update(runtime_config["runtime"])
    config["metadata"]["interactive_mapping"] = {
        "libraries": [lib.name for lib in libraries],
        "collected_parameters": collected_params
    }

    if args.save_config:
        config_path = args.save_config
    else:
        config_path = f"configs/{config['metadata']['name']}.yaml"

    generator.save_config_to_file(config, config_path)

    # 6. Walidacja i wykonanie
    if not args.validate_only:
        if ask_yes_no("Uruchomić zadanie teraz?", default=True):
            execute_task_with_config(config, args)


def run_config_mode(args):
    """Uruchamia z plikiem konfiguracji YAML."""

    logger.info(f"📄 Ładowanie konfiguracji: {args.config}")

    validator = TaskValidator()

    try:
        config = validator.load_config(args.config)
        logger.success(f"✅ Załadowano konfigurację: {config.metadata.name}")
    except Exception as e:
        logger.error(f"❌ Błąd ładowania konfiguracji: {e}")
        return

    # Walidacja środowiska
    if not validate_environment_for_config(config, validator):
        return

    if args.validate_only:
        logger.success("✅ Walidacja zakończona pomyślnie!")
        return

    # Wykonanie zadania
    execute_task_with_config(config, args)


def run_quick_mode(args):
    """Szybki tryb bez interakcji."""

    logger.info(f"⚡ Szybkie uruchomienie: {args.quick}")

    env_manager = SmartEnvManager()

    # Auto-wykryj środowisko
    if args.auto_configure:
        logger.info("🔧 Auto-konfiguracja środowiska...")

        # Podstawowe zmienne dla typowych zadań
        basic_vars = ["DUNE_OUTPUT_DIR", "DUNE_LOG_LEVEL"]
        detected = env_manager.auto_detect_environment_variables(basic_vars)

        if detected:
            env_manager.save_to_env_file(detected)
            load_dotenv()

    # Wygeneruj konfigurację i uruchom
    generator = ConfigGenerator()
    config = generator.generate_config_from_nlp(args.quick)

    execute_task_from_natural_request(args.quick)


def run_default_mode(args):
    """Domyślny tryb uruchomienia."""

    print("\n" + "=" * 60)
    print("🏜️  DUNE - PROCESOR DANYCH")
    print("=" * 60)
    print("Wybierz tryb uruchomienia:")
    print("  1. Interaktywny (mapowanie bibliotek)")
    print("  2. Z konfiguracją YAML")
    print("  3. Szybki (podaj zadanie)")
    print("  4. Legacy (bez konfiguracji)")
    print("=" * 60)

    while True:
        try:
            choice = input("\nWybierz opcję [1-4]: ").strip()

            if choice == "1":
                args.interactive = True
                run_interactive_mode(args)
                break
            elif choice == "2":
                config_path = input("Ścieżka do pliku konfiguracji: ").strip()
                if config_path and Path(config_path).exists():
                    args.config = config_path
                    run_config_mode(args)
                    break
                else:
                    print("❌ Plik nie istnieje")
            elif choice == "3":
                task = input("Opisz zadanie: ").strip()
                if task:
                    args.quick = task
                    run_quick_mode(args)
                    break
                else:
                    print("❌ Nie podano zadania")
            elif choice == "4":
                execute_legacy_task()
                break
            else:
                print("❌ Nieprawidłowy wybór")

        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break


def validate_environment_for_config(config, validator):
    """Waliduje środowisko dla konfiguracji."""

    logger.info("🔍 Walidacja środowiska...")

    if not validator.validate_pre_execution(config):
        logger.error("❌ Walidacja środowiska nie powiodła się")

        for error in validator.errors:
            logger.error(f"   • {error}")

        for warning in validator.warnings:
            logger.warning(f"   • {warning}")

        if validator.errors:
            # Spróbuj auto-naprawić niektóre błędy
            if ask_yes_no("Spróbować auto-naprawić błędy środowiska?"):
                return auto_fix_environment_issues(validator.errors, config)
            else:
                return False

    logger.success("✅ Środowisko prawidłowo skonfigurowane")
    return True


def auto_fix_environment_issues(errors, config):
    """Próbuje automatycznie naprawić błędy środowiska."""

    logger.info("🔧 Próba auto-naprawy błędów środowiska...")

    env_manager = SmartEnvManager()
    fixed_count = 0

    for error in errors:
        if "zmiennej środowiskowej" in error:
            # Wyodrębnij nazwę zmiennej
            import re
            match = re.search(r"zmiennej środowiskowej: (\w+)", error)
            if match:
                var_name = match.group(1)
                logger.info(f"🔧 Próba naprawy {var_name}...")

                # Spróbuj auto-wykryć
                detected = env_manager.auto_detect_environment_variables([var_name])
                if detected.get(var_name):
                    os.environ[var_name] = detected[var_name]
                    logger.success(f"✅ Auto-wykryto {var_name}")
                    fixed_count += 1
                else:
                    # Poproś użytkownika
                    env_vars = env_manager.interactive_env_collection([var_name])
                    if env_vars.get(var_name):
                        os.environ[var_name] = env_vars[var_name]
                        fixed_count += 1

    if fixed_count > 0:
        logger.success(f"✅ Naprawiono {fixed_count} problemów")
        return True

    return False


def execute_task_with_config(config, args):
    """Wykonuje zadanie z konfiguracją."""

    logger.info("🚀 Rozpoczynam wykonanie zadania...")

    # Inicjalizuj komponenty
    llm_analyzer = LLMAnalyzer(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "mistral:7b")
    )

    processor_engine = ProcessorEngine(llm_analyzer)

    try:
        # Wykonaj zadanie
        if hasattr(config, 'task'):
            natural_request = config.task.natural_language
        else:
            natural_request = config["task"]["natural_language"]

        result = processor_engine.process_natural_request(natural_request)

        # Walidacja po wykonaniu
        if hasattr(config, 'validation'):
            validator = TaskValidator()
            if validator.validate_post_execution(config):
                logger.success("✅ Walidacja wyników zakończona pomyślnie")

        # Pokaż wyniki
        show_execution_results(result)

    except Exception as e:
        logger.error(f"❌ Błąd wykonania zadania: {e}")
        raise


def execute_task_from_natural_request(natural_request):
    """Wykonuje zadanie z żądania w języku naturalnym."""

    logger.info(f"📝 Przetwarzanie: {natural_request}")

    llm_analyzer = LLMAnalyzer(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "mistral:7b")
    )

    processor_engine = ProcessorEngine(llm_analyzer)

    try:
        result = processor_engine.process_natural_request(natural_request)
        show_execution_results(result)

    except Exception as e:
        logger.error(f"❌ Błąd przetwarzania: {e}")
        raise


def execute_legacy_task():
    """Wykonuje zadanie w trybie legacy."""

    logger.info("📄 Tryb legacy - podstawowe przetwarzanie emaili")

    # Domyślne zadanie IMAP
    natural_request = """
    Pobierz wszystkie wiadomości email ze skrzynki IMAP i zapisz je w folderach 
    uporządkowanych według roku i miesiąca w formacie skrzynka/rok.miesiąc/*.eml.
    Dane logowania do skrzynki znajdziesz w pliku .env.
    """

    execute_task_from_natural_request(natural_request)


def show_execution_results(result):
    """Pokazuje wyniki wykonania zadania."""

    print("\n" + "=" * 60)
    print("✅ ZADANIE ZAKOŃCZONE POMYŚLNIE!")
    print("=" * 60)

    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, list):
                print(f"📊 {key}: {len(value)} elementów")
                if len(value) <= 5:
                    for item in value:
                        print(f"   • {item}")
                else:
                    for item in value[:3]:
                        print(f"   • {item}")
                    print(f"   ... i {len(value) - 3} więcej")
            else:
                print(f"📊 {key}: {value}")
    else:
        print(f"📊 Wynik: {result}")

    print("=" * 60)


def ask_yes_no(question: str, default: bool = None) -> bool:
    """Zadaje pytanie tak/nie."""

    if default is True:
        prompt = f"{question} [T/n]: "
    elif default is False:
        prompt = f"{question} [t/N]: "
    else:
        prompt = f"{question} [t/n]: "

    while True:
        try:
            answer = input(prompt).strip().lower()

            if not answer and default is not None:
                return default

            if answer in ["t", "tak", "y", "yes", "1", "true"]:
                return True
            elif answer in ["n", "nie", "no", "0", "false"]:
                return False
            else:
                print("Odpowiedz 't' (tak) lub 'n' (nie)")

        except KeyboardInterrupt:
            return False


if __name__ == "__main__":
    main()