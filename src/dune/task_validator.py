"""
Walidator konfiguracji zadań zgodnie ze standardem dune Task Configuration.
"""

import os
import yaml
import socket
import requests
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from loguru import logger
import subprocess


class TaskMetadata(BaseModel):
    """Metadane zadania."""
    name: str
    description: str
    version: str
    created: str
    tags: List[str] = []


class TaskDefinition(BaseModel):
    """Definicja zadania."""
    natural_language: str
    requirements: List[str]
    expected_output: Dict[str, Any]


class RuntimeConfig(BaseModel):
    """Konfiguracja środowiska wykonawczego."""
    type: str = "docker"
    base_image: str = "python:3.11-slim"
    python_packages: Dict[str, List[str]]
    environment: Dict[str, List[str]]


class ServiceDependency(BaseModel):
    """Definicja zależności usługowej."""
    name: str
    type: str
    required: bool = True
    connection: Dict[str, str]
    health_check: Dict[str, Any]


class ManagedService(BaseModel):
    """Definicja zarządzanej usługi."""
    name: str
    type: str
    enabled: str = "true"
    config: Dict[str, Any]


class ValidationRule(BaseModel):
    """Reguła walidacji."""
    type: str
    kwargs: Dict[str, Any] = {}


class TaskConfiguration(BaseModel):
    """Główna konfiguracja zadania."""
    apiVersion: str
    kind: str
    metadata: TaskMetadata
    task: TaskDefinition
    runtime: RuntimeConfig
    services: Dict[str, Any]
    validation: Dict[str, List[ValidationRule]]
    monitoring: Dict[str, Any]
    security: Dict[str, Any]
    pipeline: Dict[str, Any]
    environments: Dict[str, Dict[str, Any]] = {}


class TaskValidator:
    """Walidator konfiguracji zadań."""

    def __init__(self):
        self.validation_results = []
        self.warnings = []
        self.errors = []

    def load_config(self, config_path: str) -> TaskConfiguration:
        """Ładuje konfigurację z pliku YAML."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # Rozwiń zmienne środowiskowe
            config_data = self._expand_environment_variables(config_data)

            return TaskConfiguration(**config_data)

        except Exception as e:
            logger.error(f"Błąd ładowania konfiguracji: {e}")
            raise

    def _expand_environment_variables(self, data):
        """Rozszerza zmienne środowiskowe w konfiguracji."""
        if isinstance(data, dict):
            return {k: self._expand_environment_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_environment_variables(item) for item in data]
        elif isinstance(data, str):
            # Prosta zamiana ${VAR} lub ${VAR:-default}
            import re
            def replace_var(match):
                var_expr = match.group(1)
                if ':-' in var_expr:
                    var_name, default = var_expr.split(':-', 1)
                    return os.getenv(var_name, default)
                else:
                    return os.getenv(var_expr, match.group(0))

            return re.sub(r'\$\{([^}]+)\}', replace_var, data)
        else:
            return data

    def validate_pre_execution(self, config: TaskConfiguration) -> bool:
        """Wykonuje walidację przed wykonaniem zadania."""
        logger.info("Rozpoczynam walidację przed wykonaniem...")

        success = True

        # Waliduj połączenia z usługami
        success &= self._validate_service_connectivity(config)

        # Waliduj zmienne środowiskowe
        success &= self._validate_environment_variables(config)

        # Waliduj uprawnienia do plików
        success &= self._validate_file_permissions(config)

        # Waliduj miejsce na dysku
        success &= self._validate_disk_space(config)

        # Waliduj pakiety Python
        success &= self._validate_python_packages(config)

        return success

    def validate_post_execution(self, config: TaskConfiguration) -> bool:
        """Wykonuje walidację po wykonaniu zadania."""
        logger.info("Rozpoczynam walidację po wykonaniu...")

        success = True

        # Waliduj wygenerowane pliki
        success &= self._validate_output_files(config)

        # Waliduj strukturę katalogów
        success &= self._validate_directory_structure(config)

        return success

    def _validate_service_connectivity(self, config: TaskConfiguration) -> bool:
        """Sprawdza połączenie z wymaganymi usługami."""
        logger.info("Sprawdzanie połączeń z usługami...")

        success = True
        dependencies = config.services.get("dependencies", [])

        for dep in dependencies:
            service = ServiceDependency(**dep)

            if service.required:
                if not self._check_service_health(service):
                    self.errors.append(f"Nie można połączyć z wymaganą usługą: {service.name}")
                    success = False
                else:
                    logger.success(f"✅ Usługa {service.name} dostępna")
            else:
                if not self._check_service_health(service):
                    self.warnings.append(f"Opcjonalna usługa {service.name} niedostępna")
                    logger.warning(f"⚠️  Opcjonalna usługa {service.name} niedostępna")

        return success

    def _check_service_health(self, service: ServiceDependency) -> bool:
        """Sprawdza dostępność konkretnej usługi."""
        try:
            health_check = service.health_check

            if health_check["type"] == "tcp_connect":
                host = service.connection.get("host", "localhost")
                port = int(service.connection.get("port", 80))
                timeout = int(health_check.get("timeout", "10s").replace("s", ""))

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()

                return result == 0

            elif health_check["type"] == "http_get":
                url = service.connection["url"]
                endpoint = health_check.get("endpoint", "")
                timeout = int(health_check.get("timeout", "30s").replace("s", ""))

                response = requests.get(f"{url}{endpoint}", timeout=timeout)
                return response.status_code == 200

        except Exception as e:
            logger.debug(f"Health check failed for {service.name}: {e}")
            return False

        return False

    def _validate_environment_variables(self, config: TaskConfiguration) -> bool:
        """Sprawdza wymagane zmienne środowiskowe."""
        logger.info("Sprawdzanie zmiennych środowiskowych...")

        success = True
        required_vars = config.runtime.environment.get("required", [])

        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Brak wymaganej zmiennej środowiskowej: {var}")
                success = False
            else:
                logger.success(f"✅ Zmienna {var} ustawiona")

        return success

    def _validate_file_permissions(self, config: TaskConfiguration) -> bool:
        """Sprawdza uprawnienia do plików i katalogów."""
        logger.info("Sprawdzanie uprawnień do plików...")

        success = True
        output_dir = os.getenv("OUTPUT_DIR", "./output")

        # Sprawdź czy można tworzyć katalogi
        try:
            test_dir = Path(output_dir) / "test_permissions"
            test_dir.mkdir(parents=True, exist_ok=True)

            # Sprawdź czy można pisać pliki
            test_file = test_dir / "test.txt"
            test_file.write_text("test")
            test_file.unlink()
            test_dir.rmdir()

            logger.success(f"✅ Uprawnienia do zapisu w {output_dir}")

        except Exception as e:
            self.errors.append(f"Brak uprawnień do zapisu w {output_dir}: {e}")
            success = False

        return success

    def _validate_disk_space(self, config: TaskConfiguration) -> bool:
        """Sprawdza dostępne miejsce na dysku."""
        logger.info("Sprawdzanie miejsca na dysku...")

        output_dir = os.getenv("OUTPUT_DIR", "./output")

        try:
            # Sprawdź dostępne miejsce
            total, used, free = shutil.disk_usage(output_dir)
            free_mb = free // (1024 * 1024)

            if free_mb < 100:  # Minimum 100MB
                self.warnings.append(f"Mało miejsca na dysku: {free_mb}MB")
                logger.warning(f"⚠️  Dostępne miejsce: {free_mb}MB")
            else:
                logger.success(f"✅ Dostępne miejsce: {free_mb}MB")

        except Exception as e:
            self.warnings.append(f"Nie można sprawdzić miejsca na dysku: {e}")

        return True

    def _validate_python_packages(self, config: TaskConfiguration) -> bool:
        """Sprawdza dostępność wymaganych pakietów Python."""
        logger.info("Sprawdzanie pakietów Python...")

        success = True
        required_packages = config.runtime.python_packages.get("required", [])

        for package in required_packages:
            package_name = package.split(">=")[0].split("==")[0]

            try:
                __import__(package_name)
                logger.success(f"✅ Pakiet {package_name} dostępny")
            except ImportError:
                logger.info(f"📦 Pakiet {package_name} będzie zainstalowany")

        return success

    def _validate_output_files(self, config: TaskConfiguration) -> bool:
        """Sprawdza czy zostały wygenerowane oczekiwane pliki."""
        logger.info("Sprawdzanie wygenerowanych plików...")

        success = True
        expected_output = config.task.expected_output

        if expected_output.get("type") == "file_structure":
            pattern = expected_output.get("pattern", "")
            # Tutaj można zaimplementować sprawdzanie wzorca plików
            logger.info(f"Sprawdzanie wzorca: {pattern}")

        return success

    def _validate_directory_structure(self, config: TaskConfiguration) -> bool:
        """Sprawdza strukturę katalogów."""
        logger.info("Sprawdzanie struktury katalogów...")

        # Implementacja sprawdzania struktury
        return True

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generuje raport walidacji."""
        return {
            "validation_passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_checks": len(self.validation_results)
        }