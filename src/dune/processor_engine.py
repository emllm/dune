"""
Główny silnik procesora danych z dynamicznym zarządzaniem bibliotekami.
"""

import os
import sys
import subprocess
import importlib
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger
from pydantic import BaseModel


class ProcessorConfig(BaseModel):
    """Konfiguracja procesora danych."""
    name: str
    description: str
    dependencies: List[str]
    parameters: Dict[str, Any]
    code_template: str


class DynamicPackageManager:
    """Menedżer dynamicznego instalowania pakietów."""

    def __init__(self):
        self.installed_packages = set()

    def install_package(self, package_name: str) -> bool:
        """Instaluje pakiet jeśli nie jest zainstalowany."""
        if package_name in self.installed_packages:
            return True

        try:
            logger.info(f"Instalowanie pakietu: {package_name}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.installed_packages.add(package_name)
            logger.success(f"Pakiet {package_name} zainstalowany pomyślnie")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd instalacji pakietu {package_name}: {e}")
            return False

    def import_module(self, module_name: str):
        """Importuje moduł po ewentualnej instalacji."""
        try:
            return importlib.import_module(module_name)
        except ImportError:
            # Spróbuj zainstalować i zaimportować ponownie
            if self.install_package(module_name):
                return importlib.import_module(module_name)
            raise


class ProcessorEngine:
    """Główny silnik procesora danych."""

    def __init__(self, llm_analyzer):
        self.llm_analyzer = llm_analyzer
        self.package_manager = DynamicPackageManager()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(exist_ok=True)

    def process_natural_request(self, request: str) -> Dict[str, Any]:
        """Przetwarza żądanie w języku naturalnym."""

        # 1. Przeanalizuj żądanie za pomocą LLM
        logger.info("Analizowanie żądania za pomocą LLM...")
        processor_config = self.llm_analyzer.analyze_request(request)

        # 2. Zainstaluj wymagane biblioteki
        logger.info("Instalowanie wymaganych bibliotek...")
        for dependency in processor_config.dependencies:
            self.package_manager.install_package(dependency)

        # 3. Wykonaj kod procesora
        logger.info("Wykonywanie procesora danych...")
        return self._execute_processor(processor_config)

    def _execute_processor(self, config: ProcessorConfig) -> Dict[str, Any]:
        """Wykonuje procesor danych na podstawie konfiguracji."""

        # Przygotuj kontekst wykonania
        execution_context = {
            'os': __import__('os'),
            'sys': __import__('sys'),
            'Path': Path,
            'logger': logger,
            'output_dir': str(self.output_dir),
            'package_manager': self.package_manager,
        }

        # Dodaj zmienne środowiskowe
        for key, value in os.environ.items():
            if key.startswith(('IMAP_', 'EMAIL_', 'SMTP_')):
                execution_context[key.lower()] = value

        # Wykonaj kod
        try:
            exec(config.code_template, execution_context)

            # Pobierz wynik z kontekstu
            result = execution_context.get('result', {'status': 'completed'})
            return result

        except Exception as e:
            logger.error(f"Błąd wykonania procesora: {e}")
            raise