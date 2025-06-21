"""
Interaktywny mapper zadań do bibliotek z automatycznym odpytywaniem o dane wejściowe.
"""

import os
import sys
import subprocess
import importlib
import inspect
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import json


@dataclass
class LibraryInterface:
    """Definicja interfejsu biblioteki."""
    name: str
    package: str
    main_function: str
    required_params: List[str]
    optional_params: List[str]
    param_types: Dict[str, str]
    param_descriptions: Dict[str, str]
    examples: List[Dict[str, Any]]
    cli_interface: Optional[str] = None


@dataclass
class TaskMapping:
    """Mapowanie zadania do bibliotek."""
    task_keywords: List[str]
    libraries: List[LibraryInterface]
    priority: int = 1


class InteractiveMapper:
    """Interaktywny mapper zadań do bibliotek."""

    def __init__(self):
        self.library_database = self._build_library_database()
        self.task_mappings = self._build_task_mappings()
        self.discovered_interfaces = {}

    def _build_library_database(self) -> Dict[str, LibraryInterface]:
        """Buduje bazę danych dostępnych bibliotek i ich interfejsów."""

        return {
            # Email processing
            "imaplib": LibraryInterface(
                name="IMAP Email Client",
                package="imaplib",
                main_function="IMAP4_SSL",
                required_params=["server", "username", "password"],
                optional_params=["port", "use_ssl", "folder"],
                param_types={
                    "server": "str",
                    "username": "str",
                    "password": "str",
                    "port": "int",
                    "use_ssl": "bool",
                    "folder": "str"
                },
                param_descriptions={
                    "server": "Adres serwera IMAP (np. imap.gmail.com)",
                    "username": "Nazwa użytkownika/email",
                    "password": "Hasło do skrzynki",
                    "port": "Port serwera (143 dla IMAP, 993 dla IMAPS)",
                    "use_ssl": "Czy używać szyfrowania SSL",
                    "folder": "Folder do przetwarzania (domyślnie INBOX)"
                },
                examples=[
                    {
                        "server": "imap.gmail.com",
                        "username": "user@gmail.com",
                        "password": "app_password",
                        "port": 993,
                        "use_ssl": True
                    }
                ]
            ),

            # Database access
            "sqlalchemy": LibraryInterface(
                name="SQL Database Access",
                package="sqlalchemy",
                main_function="create_engine",
                required_params=["database_url"],
                optional_params=["pool_size", "echo", "timeout"],
                param_types={
                    "database_url": "str",
                    "pool_size": "int",
                    "echo": "bool",
                    "timeout": "int"
                },
                param_descriptions={
                    "database_url": "URL połączenia z bazą danych (postgresql://user:pass@host/db)",
                    "pool_size": "Rozmiar puli połączeń",
                    "echo": "Czy logować zapytania SQL",
                    "timeout": "Timeout połączenia w sekundach"
                },
                examples=[
                    {
                        "database_url": "postgresql://user:password@localhost:5432/mydb",
                        "pool_size": 5,
                        "echo": False
                    },
                    {
                        "database_url": "sqlite:///data.db"
                    }
                ]
            ),

            # Web scraping
            "requests": LibraryInterface(
                name="HTTP Client",
                package="requests",
                main_function="get",
                required_params=["url"],
                optional_params=["headers", "timeout", "verify_ssl", "proxies"],
                param_types={
                    "url": "str",
                    "headers": "dict",
                    "timeout": "int",
                    "verify_ssl": "bool",
                    "proxies": "dict"
                },
                param_descriptions={
                    "url": "URL do pobrania",
                    "headers": "Nagłówki HTTP (jako słownik)",
                    "timeout": "Timeout żądania w sekundach",
                    "verify_ssl": "Czy weryfikować certyfikaty SSL",
                    "proxies": "Konfiguracja proxy (jako słownik)"
                },
                examples=[
                    {
                        "url": "https://api.example.com/data",
                        "headers": {"User-Agent": "Dune Bot 1.0"},
                        "timeout": 30
                    }
                ]
            ),

            # File processing
            "pandas": LibraryInterface(
                name="Data Analysis",
                package="pandas",
                main_function="read_csv",
                required_params=["filepath"],
                optional_params=["separator", "encoding", "header_row"],
                param_types={
                    "filepath": "str",
                    "separator": "str",
                    "encoding": "str",
                    "header_row": "int"
                },
                param_descriptions={
                    "filepath": "Ścieżka do pliku CSV",
                    "separator": "Separator kolumn (domyślnie ',')",
                    "encoding": "Kodowanie pliku (np. utf-8, cp1250)",
                    "header_row": "Numer wiersza z nagłówkami (0 = pierwszy wiersz)"
                },
                examples=[
                    {
                        "filepath": "data.csv",
                        "separator": ",",
                        "encoding": "utf-8"
                    }
                ]
            ),

            # Image processing
            "pillow": LibraryInterface(
                name="Image Processing",
                package="Pillow",
                main_function="Image.open",
                required_params=["image_path"],
                optional_params=["output_format", "quality", "resize_dimensions"],
                param_types={
                    "image_path": "str",
                    "output_format": "str",
                    "quality": "int",
                    "resize_dimensions": "tuple"
                },
                param_descriptions={
                    "image_path": "Ścieżka do pliku obrazu",
                    "output_format": "Format wyjściowy (JPEG, PNG, WEBP)",
                    "quality": "Jakość kompresji (1-100 dla JPEG)",
                    "resize_dimensions": "Nowe wymiary jako (width, height)"
                },
                examples=[
                    {
                        "image_path": "input.jpg",
                        "output_format": "JPEG",
                        "quality": 85,
                        "resize_dimensions": (800, 600)
                    }
                ]
            )
        }

    def _build_task_mappings(self) -> List[TaskMapping]:
        """Buduje mapowania zadań do bibliotek."""

        return [
            TaskMapping(
                task_keywords=["email", "imap", "pop3", "skrzynka", "wiadomość", "poczta"],
                libraries=[self.library_database["imaplib"]],
                priority=1
            ),
            TaskMapping(
                task_keywords=["baza danych", "sql", "postgresql", "mysql", "sqlite"],
                libraries=[self.library_database["sqlalchemy"]],
                priority=1
            ),
            TaskMapping(
                task_keywords=["http", "api", "rest", "pobierz", "strona", "url"],
                libraries=[self.library_database["requests"]],
                priority=1
            ),
            TaskMapping(
                task_keywords=["csv", "excel", "pandas", "dataframe", "tabela", "dane"],
                libraries=[self.library_database["pandas"]],
                priority=1
            ),
            TaskMapping(
                task_keywords=["obraz", "zdjęcie", "jpg", "png", "resize", "grafika"],
                libraries=[self.library_database["pillow"]],
                priority=1
            )
        ]

    def analyze_task_and_map_libraries(self, natural_request: str) -> List[LibraryInterface]:
        """Analizuje zadanie i mapuje je do odpowiednich bibliotek."""

        logger.info("🔍 Analizowanie zadania i mapowanie bibliotek...")

        request_lower = natural_request.lower()
        matched_libraries = []

        # Znajdź pasujące mapowania
        for mapping in self.task_mappings:
            score = sum(1 for keyword in mapping.task_keywords
                        if keyword in request_lower)

            if score > 0:
                for library in mapping.libraries:
                    if library not in matched_libraries:
                        matched_libraries.append(library)
                        logger.info(f"📚 Znaleziono bibliotekę: {library.name} (score: {score})")

        # Sortuj według priorytetu
        matched_libraries.sort(key=lambda x: self._get_library_priority(x.name), reverse=True)

        return matched_libraries

    def _get_library_priority(self, library_name: str) -> int:
        """Zwraca priorytet biblioteki."""
        priorities = {
            "IMAP Email Client": 10,
            "SQL Database Access": 9,
            "HTTP Client": 8,
            "Data Analysis": 7,
            "Image Processing": 6
        }
        return priorities.get(library_name, 1)

    def discover_cli_interface(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Odkrywa interfejs CLI biblioteki poprzez analizę kodu."""

        if package_name in self.discovered_interfaces:
            return self.discovered_interfaces[package_name]

        logger.info(f"🔎 Odkrywanie interfejsu CLI dla {package_name}...")

        try:
            # Spróbuj zaimportować pakiet
            module = importlib.import_module(package_name)

            # Sprawdź czy ma CLI
            cli_info = self._analyze_module_for_cli(module)

            if cli_info:
                self.discovered_interfaces[package_name] = cli_info
                logger.success(f"✅ Odkryto interfejs CLI dla {package_name}")
                return cli_info

        except ImportError:
            logger.warning(f"⚠️  Pakiet {package_name} nie jest zainstalowany")
        except Exception as e:
            logger.warning(f"⚠️  Błąd analizy {package_name}: {e}")

        return None

    def _analyze_module_for_cli(self, module) -> Optional[Dict[str, Any]]:
        """Analizuje moduł w poszukiwaniu interfejsu CLI."""

        cli_info = {
            "has_cli": False,
            "main_functions": [],
            "cli_commands": [],
            "parameters": []
        }

        # Sprawdź główne funkcje modułu
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                sig = inspect.signature(obj)
                params = []

                for param_name, param in sig.parameters.items():
                    param_info = {
                        "name": param_name,
                        "type": str(param.annotation) if param.annotation != param.empty else "Any",
                        "default": param.default if param.default != param.empty else None,
                        "required": param.default == param.empty
                    }
                    params.append(param_info)

                cli_info["main_functions"].append({
                    "name": name,
                    "parameters": params,
                    "docstring": obj.__doc__
                })

        if cli_info["main_functions"]:
            cli_info["has_cli"] = True

        return cli_info if cli_info["has_cli"] else None

    def interactive_parameter_collection(self, library: LibraryInterface) -> Dict[str, Any]:
        """Interaktywnie zbiera parametry dla biblioteki."""

        logger.info(f"📝 Zbieranie parametrów dla: {library.name}")
        print(f"\n🔧 KONFIGURACJA: {library.name}")
        print("=" * 50)

        if library.param_descriptions:
            print("📋 Opis biblioteki:")
            for param, desc in library.param_descriptions.items():
                if param in library.required_params:
                    print(f"   • {param} (wymagany): {desc}")
                else:
                    print(f"   • {param} (opcjonalny): {desc}")

        # Pokaż przykłady
        if library.examples:
            print(f"\n💡 Przykład konfiguracji:")
            example = library.examples[0]
            for key, value in example.items():
                print(f"   {key} = {value}")

        print("\n" + "=" * 50)

        collected_params = {}

        # Zbierz wymagane parametry
        for param in library.required_params:
            collected_params[param] = self._collect_single_parameter(
                param, library, required=True
            )

        # Zbierz opcjonalne parametry (zapytaj czy user chce)
        if library.optional_params:
            print(f"\n🔧 Parametry opcjonalne:")
            for param in library.optional_params:
                if self._ask_yes_no(f"Czy chcesz skonfigurować {param}?"):
                    collected_params[param] = self._collect_single_parameter(
                        param, library, required=False
                    )

        return collected_params

    def _collect_single_parameter(self, param_name: str, library: LibraryInterface,
                                  required: bool = True) -> Any:
        """Zbiera pojedynczy parametr."""

        # Sprawdź czy jest w zmiennych środowiskowych
        env_variants = [
            param_name.upper(),
            f"{library.package.upper()}_{param_name.upper()}",
            f"DUNE_{param_name.upper()}"
        ]

        env_value = None
        env_source = None

        for env_var in env_variants:
            env_value = os.getenv(env_var)
            if env_value:
                env_source = env_var
                break

        # Przygotuj prompt
        param_desc = library.param_descriptions.get(param_name, "")
        param_type = library.param_types.get(param_name, "str")

        prompt = f"📌 {param_name}"
        if param_desc:
            prompt += f" ({param_desc})"
        if not required:
            prompt += " [opcjonalny]"

        if env_value:
            prompt += f" [znaleziono w {env_source}: {env_value}]"
            if self._ask_yes_no(f"Użyć wartości z {env_source}?", default=True):
                return self._convert_type(env_value, param_type)

        # Pobierz od użytkownika
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()

                if not user_input and not required:
                    return None

                if not user_input and required:
                    print("❌ Ten parametr jest wymagany!")
                    continue

                return self._convert_type(user_input, param_type)

            except KeyboardInterrupt:
                print("\n⚠️  Przerwano przez użytkownika")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Błąd: {e}. Spróbuj ponownie.")

    def _convert_type(self, value: str, param_type: str) -> Any:
        """Konwertuje wartość do odpowiedniego typu."""

        if param_type == "int":
            return int(value)
        elif param_type == "bool":
            return value.lower() in ["true", "1", "yes", "tak", "y"]
        elif param_type == "float":
            return float(value)
        elif param_type == "list":
            return value.split(",")
        elif param_type == "dict":
            return json.loads(value)
        elif param_type == "tuple" and "," in value:
            return tuple(map(int, value.split(",")))
        else:
            return value

    def _ask_yes_no(self, question: str, default: bool = None) -> bool:
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
                print("\n⚠️  Przerwano przez użytkownika")
                sys.exit(1)

    def generate_runtime_config(self, libraries: List[LibraryInterface],
                                collected_params: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generuje konfigurację runtime na podstawie zebranych danych."""

        # Zbierz wszystkie wymagane pakiety
        packages = {"required": [], "optional": []}
        env_vars = {"required": [], "optional": []}

        for library in libraries:
            packages["required"].append(library.package)

            # Dodaj zmienne środowiskowe na podstawie parametrów
            lib_params = collected_params.get(library.name, {})
            for param_name, value in lib_params.items():
                env_var = f"{library.package.upper()}_{param_name.upper()}"
                if param_name in library.required_params:
                    env_vars["required"].append(env_var)
                else:
                    env_vars["optional"].append(env_var)

        # Usuń duplikaty
        packages["required"] = list(set(packages["required"]))
        packages["optional"] = list(set(packages["optional"]))
        env_vars["required"] = list(set(env_vars["required"]))
        env_vars["optional"] = list(set(env_vars["optional"]))

        return {
            "runtime": {
                "type": "docker",
                "base_image": "python:3.11-slim",
                "python_packages": packages,
                "environment": env_vars
            },
            "collected_parameters": collected_params
        }

    def save_parameters_to_env(self, collected_params: Dict[str, Dict[str, Any]],
                               env_file: str = ".env") -> None:
        """Zapisuje zebrane parametry do pliku .env."""

        logger.info(f"💾 Zapisywanie parametrów do {env_file}")

        # Wczytaj istniejący .env jeśli istnieje
        existing_vars = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        existing_vars[key] = value

        # Dodaj nowe zmienne
        new_vars = {}
        for lib_name, params in collected_params.items():
            for param_name, value in params.items():
                if value is not None:
                    # Kilka wariantów nazwy zmiennej
                    env_var = f"DUNE_{param_name.upper()}"
                    new_vars[env_var] = str(value)

        # Połącz i zapisz
        all_vars = {**existing_vars, **new_vars}

        with open(env_file, 'w') as f:
            f.write("# Dune Configuration\n")
            f.write("# Auto-generated parameters\n\n")

            for key, value in sorted(all_vars.items()):
                f.write(f"{key}={value}\n")

        logger.success(f"✅ Parametry zapisane do {env_file}")
        print(f"\n💾 Zapisano {len(new_vars)} nowych parametrów do {env_file}")

    def run_interactive_mapping(self, natural_request: str) -> Dict[str, Any]:
        """Uruchamia pełny interaktywny proces mapowania."""

        print("\n" + "=" * 60)
        print("🤖 DUNE - INTERAKTYWNY MAPPER BIBLIOTEK")
        print("=" * 60)
        print(f"📝 Zadanie: {natural_request}")
        print("=" * 60)

        # 1. Mapuj biblioteki
        libraries = self.analyze_task_and_map_libraries(natural_request)

        if not libraries:
            print("❌ Nie znaleziono pasujących bibliotek dla tego zadania")
            return {}

        print(f"\n📚 Znalezione biblioteki ({len(libraries)}):")
        for i, lib in enumerate(libraries, 1):
            print(f"   {i}. {lib.name} ({lib.package})")

        # 2. Zbierz parametry dla każdej biblioteki
        collected_params = {}

        for library in libraries:
            if self._ask_yes_no(f"\nKonfigurować {library.name}?", default=True):
                params = self.interactive_parameter_collection(library)
                collected_params[library.name] = params

        # 3. Generuj konfigurację
        runtime_config = self.generate_runtime_config(libraries, collected_params)

        # 4. Zapisz do .env
        if collected_params and self._ask_yes_no("\nZapisać parametry do .env?", default=True):
            self.save_parameters_to_env(collected_params)

        print("\n" + "=" * 60)
        print("✅ MAPOWANIE ZAKOŃCZONE POMYŚLNIE!")
        print("=" * 60)
        print(f"📦 Pakiety do zainstalowania: {len(runtime_config['runtime']['python_packages']['required'])}")
        print(f"🔧 Parametrów zebranych: {sum(len(params) for params in collected_params.values())}")
        print("=" * 60)

        return {
            "libraries": libraries,
            "parameters": collected_params,
            "runtime_config": runtime_config,
            "natural_request": natural_request
        }