"""
Inteligentny menedżer zmiennych środowiskowych z automatycznym wykrywaniem i validacją.
"""

import os
import re
import json
import subprocess
import platform
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from loguru import logger
from dataclasses import dataclass


@dataclass
class EnvVariable:
    """Definicja zmiennej środowiskowej."""
    name: str
    description: str
    type: str  # str, int, bool, path, url, email
    required: bool
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None
    auto_detect_methods: List[str] = None
    examples: List[str] = None


class SmartEnvManager:
    """Inteligentny menedżer zmiennych środowiskowych."""

    def __init__(self):
        self.env_definitions = self._load_env_definitions()
        self.auto_detected = {}
        self.user_provided = {}

    def _load_env_definitions(self) -> Dict[str, EnvVariable]:
        """Ładuje definicje zmiennych środowiskowych."""

        return {
            # IMAP Configuration
            "IMAP_SERVER": EnvVariable(
                name="IMAP_SERVER",
                description="Adres serwera IMAP (np. imap.gmail.com)",
                type="str",
                required=True,
                validation_pattern=r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                auto_detect_methods=["common_providers", "dns_lookup"],
                examples=["imap.gmail.com", "imap.outlook.com", "mail.company.com"]
            ),

            "IMAP_PORT": EnvVariable(
                name="IMAP_PORT",
                description="Port serwera IMAP",
                type="int",
                required=False,
                default_value="993",
                validation_pattern=r"^(143|993|[1-9]\d{1,4})$",
                examples=["143", "993"]
            ),

            "IMAP_USERNAME": EnvVariable(
                name="IMAP_USERNAME",
                description="Nazwa użytkownika IMAP (zazwyczaj email)",
                type="email",
                required=True,
                validation_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                auto_detect_methods=["git_config", "system_user"],
                examples=["user@gmail.com", "john.doe@company.com"]
            ),

            "IMAP_PASSWORD": EnvVariable(
                name="IMAP_PASSWORD",
                description="Hasło IMAP (lub hasło aplikacji)",
                type="str",
                required=True,
                auto_detect_methods=["keyring", "env_file"]
            ),

            # Database Configuration
            "DATABASE_URL": EnvVariable(
                name="DATABASE_URL",
                description="URL połączenia z bazą danych",
                type="url",
                required=False,
                validation_pattern=r"^(postgresql|mysql|sqlite)://.*",
                auto_detect_methods=["docker_compose", "local_services"],
                examples=[
                    "postgresql://user:pass@localhost:5432/dbname",
                    "sqlite:///data.db",
                    "mysql://user:pass@localhost:3306/dbname"
                ]
            ),

            # API Configuration
            "API_KEY": EnvVariable(
                name="API_KEY",
                description="Klucz API do autoryzacji",
                type="str",
                required=False,
                auto_detect_methods=["env_file", "keyring"]
            ),

            "API_BASE_URL": EnvVariable(
                name="API_BASE_URL",
                description="Bazowy URL API",
                type="url",
                required=False,
                validation_pattern=r"^https?://.*",
                examples=["https://api.example.com", "http://localhost:8000"]
            ),

            # File Paths
            "INPUT_DIR": EnvVariable(
                name="INPUT_DIR",
                description="Katalog z plikami wejściowymi",
                type="path",
                required=False,
                default_value="./input",
                auto_detect_methods=["current_directory", "common_paths"],
                examples=["./data", "/home/user/documents", "C:\\Data"]
            ),

            "OUTPUT_DIR": EnvVariable(
                name="OUTPUT_DIR",
                description="Katalog dla plików wyjściowych",
                type="path",
                required=False,
                default_value="./output",
                auto_detect_methods=["current_directory"],
                examples=["./output", "/tmp/results", "C:\\Results"]
            ),

            # System Configuration
            "LOG_LEVEL": EnvVariable(
                name="LOG_LEVEL",
                description="Poziom logowania",
                type="str",
                required=False,
                default_value="INFO",
                validation_pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
                examples=["DEBUG", "INFO", "WARNING", "ERROR"]
            )
        }

    def auto_detect_environment_variables(self, required_vars: List[str]) -> Dict[str, str]:
        """Automatycznie wykrywa zmienne środowiskowe."""

        logger.info("🔍 Automatyczne wykrywanie zmiennych środowiskowych...")

        detected = {}

        for var_name in required_vars:
            if var_name in self.env_definitions:
                value = self._auto_detect_single_var(self.env_definitions[var_name])
                if value:
                    detected[var_name] = value
                    self.auto_detected[var_name] = value
                    logger.success(f"✅ Auto-wykryto {var_name}: {value}")

        return detected

    def _auto_detect_single_var(self, env_var: EnvVariable) -> Optional[str]:
        """Automatycznie wykrywa pojedynczą zmienną."""

        if not env_var.auto_detect_methods:
            return None

        for method in env_var.auto_detect_methods:
            try:
                value = self._run_detection_method(method, env_var)
                if value and self._validate_env_value(value, env_var):
                    return value
            except Exception as e:
                logger.debug(f"Błąd detekcji {method} dla {env_var.name}: {e}")

        return None

    def _run_detection_method(self, method: str, env_var: EnvVariable) -> Optional[str]:
        """Uruchamia konkretną metodę detekcji."""

        if method == "git_config":
            return self._detect_from_git_config(env_var)
        elif method == "system_user":
            return self._detect_from_system_user(env_var)
        elif method == "common_providers":
            return self._detect_common_providers(env_var)
        elif method == "dns_lookup":
            return self._detect_via_dns(env_var)
        elif method == "docker_compose":
            return self._detect_from_docker_compose(env_var)
        elif method == "local_services":
            return self._detect_local_services(env_var)
        elif method == "current_directory":
            return self._detect_from_current_dir(env_var)
        elif method == "common_paths":
            return self._detect_common_paths(env_var)
        elif method == "env_file":
            return self._detect_from_env_files(env_var)
        elif method == "keyring":
            return self._detect_from_keyring(env_var)

        return None

    def _detect_from_git_config(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z konfiguracji Git."""

        if env_var.type != "email":
            return None

        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return None

    def _detect_from_system_user(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z informacji o użytkowniku systemu."""

        if env_var.type == "email":
            username = os.getenv("USER") or os.getenv("USERNAME")
            if username:
                # Spróbuj utworzyć email na podstawie nazwy użytkownika
                common_domains = ["gmail.com", "outlook.com", "company.com"]
                for domain in common_domains:
                    potential_email = f"{username}@{domain}"
                    if self._validate_env_value(potential_email, env_var):
                        return potential_email

        return None

    def _detect_common_providers(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z listy popularnych dostawców."""

        if env_var.name == "IMAP_SERVER":
            # Lista popularnych serwerów IMAP
            common_servers = [
                "imap.gmail.com",
                "imap.outlook.com",
                "imap.mail.yahoo.com",
                "localhost"
            ]

            # Sprawdź czy któryś jest dostępny
            for server in common_servers:
                if self._test_server_connectivity(server, 993) or self._test_server_connectivity(server, 143):
                    return server

        return None

    def _detect_via_dns(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa przez zapytania DNS."""

        # Implementacja sprawdzania rekordów MX dla domen
        return None

    def _detect_from_docker_compose(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z plików docker-compose."""

        compose_files = ["docker-compose.yml", "docker-compose.yaml"]

        for compose_file in compose_files:
            if Path(compose_file).exists():
                try:
                    import yaml
                    with open(compose_file, 'r') as f:
                        compose_data = yaml.safe_load(f)

                    # Szukaj baz danych w serwisach
                    services = compose_data.get("services", {})
                    for service_name, service_config in services.items():
                        if "postgres" in service_name.lower() or service_config.get("image", "").startswith("postgres"):
                            return f"postgresql://user:password@localhost:5432/dbname"
                        elif "mysql" in service_name.lower() or service_config.get("image", "").startswith("mysql"):
                            return f"mysql://user:password@localhost:3306/dbname"

                except:
                    pass

        return None

    def _detect_local_services(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa lokalne usługi."""

        if env_var.name == "DATABASE_URL":
            # Sprawdź popularne porty baz danych
            db_ports = {
                5432: "postgresql://user:password@localhost:5432/dbname",
                3306: "mysql://user:password@localhost:3306/dbname",
                6379: "redis://localhost:6379"
            }

            for port, url in db_ports.items():
                if self._test_server_connectivity("localhost", port):
                    return url

        return None

    def _detect_from_current_dir(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z bieżącego katalogu."""

        if env_var.type == "path":
            current_dir = Path.cwd()

            if env_var.name == "INPUT_DIR":
                candidates = ["input", "data", "src/data", "inputs"]
            elif env_var.name == "OUTPUT_DIR":
                candidates = ["output", "results", "out", "outputs"]
            else:
                return str(current_dir)

            for candidate in candidates:
                path = current_dir / candidate
                if path.exists():
                    return str(path)

            # Zwróć domyślną wartość względem bieżącego katalogu
            return str(current_dir / env_var.default_value.lstrip("./")) if env_var.default_value else None

        return None

    def _detect_common_paths(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z popularnych ścieżek."""

        if env_var.type == "path":
            if platform.system() == "Windows":
                common_paths = ["C:\\Data", "C:\\Users\\%USERNAME%\\Documents"]
            else:
                common_paths = ["/home/$USER/data", "/tmp", "/var/data"]

            for path_template in common_paths:
                path = os.path.expandvars(path_template)
                if Path(path).exists():
                    return path

        return None

    def _detect_from_env_files(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z istniejących plików .env."""

        env_files = [".env", ".env.local", ".env.example"]

        for env_file in env_files:
            if Path(env_file).exists():
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith(f"{env_var.name}="):
                                value = line.split("=", 1)[1]
                                return value
                except:
                    pass

        return None

    def _detect_from_keyring(self, env_var: EnvVariable) -> Optional[str]:
        """Wykrywa z systemowego keyring."""

        try:
            import keyring
            return keyring.get_password("dune", env_var.name)
        except ImportError:
            return None
        except:
            return None

    def _test_server_connectivity(self, host: str, port: int, timeout: int = 3) -> bool:
        """Testuje połączenie z serwerem."""

        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def _validate_env_value(self, value: str, env_var: EnvVariable) -> bool:
        """Waliduje wartość zmiennej środowiskowej."""

        if not value:
            return False

        # Walidacja przez pattern
        if env_var.validation_pattern:
            if not re.match(env_var.validation_pattern, value):
                return False

        # Walidacja przez typ
        if env_var.type == "int":
            try:
                int(value)
            except ValueError:
                return False
        elif env_var.type == "bool":
            if value.lower() not in ["true", "false", "1", "0", "yes", "no"]:
                return False
        elif env_var.type == "path":
            # Sprawdź czy ścieżka jest sensowna
            if not re.match(r"^[a-zA-Z0-9._/\\-]+$", value):
                return False
        elif env_var.type == "url":
            if not value.startswith(("http://", "https://", "ftp://", "file://")):
                return False

        return True

    def interactive_env_collection(self, required_vars: List[str],
                                   optional_vars: List[str] = None) -> Dict[str, str]:
        """Interaktywnie zbiera zmienne środowiskowe."""

        print(f"\n🔧 KONFIGURACJA ZMIENNYCH ŚRODOWISKOWYCH")
        print("=" * 50)

        # Najpierw spróbuj auto-detekcji
        auto_detected = self.auto_detect_environment_variables(required_vars)

        collected = {}

        # Zbierz wymagane zmienne
        for var_name in required_vars:
            value = self._collect_single_env_var(var_name, auto_detected.get(var_name), required=True)
            if value:
                collected[var_name] = value

        # Zbierz opcjonalne zmienne
        if optional_vars:
            print(f"\n🔧 Zmienne opcjonalne:")
            for var_name in optional_vars:
                if self._ask_yes_no(f"Skonfigurować {var_name}?"):
                    value = self._collect_single_env_var(var_name, auto_detected.get(var_name), required=False)
                    if value:
                        collected[var_name] = value

        return collected

    def _collect_single_env_var(self, var_name: str, auto_value: Optional[str],
                                required: bool = True) -> Optional[str]:
        """Zbiera pojedynczą zmienną środowiskową."""

        env_def = self.env_definitions.get(var_name)
        if not env_def:
            # Stwórz podstawową definicję
            env_def = EnvVariable(var_name, f"Zmienna {var_name}", "str", required)

        # Sprawdź obecną wartość
        current_value = os.getenv(var_name) or auto_value

        prompt = f"📌 {var_name}"
        if env_def.description:
            prompt += f" ({env_def.description})"

        if current_value:
            prompt += f" [obecna: {current_value}]"
        elif env_def.default_value:
            prompt += f" [domyślna: {env_def.default_value}]"

        if not required:
            prompt += " [opcjonalna]"

        # Pokaż przykłady
        if env_def.examples:
            print(f"   💡 Przykłady: {', '.join(env_def.examples[:3])}")

        while True:
            try:
                user_input = input(f"{prompt}: ").strip()

                # Użyj obecnej wartości jeśli nic nie podano
                if not user_input:
                    if current_value:
                        return current_value
                    elif env_def.default_value:
                        return env_def.default_value
                    elif not required:
                        return None
                    else:
                        print("❌ Ta zmienna jest wymagana!")
                        continue

                # Waliduj wartość
                if self._validate_env_value(user_input, env_def):
                    return user_input
                else:
                    print(f"❌ Nieprawidłowa wartość dla {env_def.type}")
                    if env_def.validation_pattern:
                        print(f"   Wzorzec: {env_def.validation_pattern}")
                    continue

            except KeyboardInterrupt:
                print("\n⚠️  Przerwano przez użytkownika")
                return None

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
                return False

    def save_to_env_file(self, env_vars: Dict[str, str], filename: str = ".env") -> None:
        """Zapisuje zmienne do pliku .env."""

        logger.info(f"💾 Zapisywanie zmiennych do {filename}")

        # Wczytaj istniejące zmienne
        existing_vars = {}
        if Path(filename).exists():
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        existing_vars[key] = value

        # Połącz ze nowymi
        all_vars = {**existing_vars, **env_vars}

        # Zapisz
        with open(filename, 'w') as f:
            f.write("# Dune Environment Configuration\n")
            f.write("# Auto-generated and user-provided variables\n\n")

            for key, value in sorted(all_vars.items()):
                f.write(f"{key}={value}\n")

        logger.success(f"✅ Zapisano {len(env_vars)} zmiennych do {filename}")

    def validate_environment(self, required_vars: List[str]) -> Tuple[bool, List[str]]:
        """Waliduje kompletność środowiska."""

        missing_vars = []

        for var_name in required_vars:
            value = os.getenv(var_name)
            if not value:
                missing_vars.append(var_name)
            else:
                env_def = self.env_definitions.get(var_name)
                if env_def and not self._validate_env_value(value, env_def):
                    missing_vars.append(f"{var_name} (nieprawidłowa wartość)")

        return len(missing_vars) == 0, missing_vars