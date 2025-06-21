"""
Dune - Dynamiczny procesor danych z automatycznym wykrywaniem bibliotek.

Ten moduł zapewnia narzędzia do przetwarzania danych z automatycznym wykrywaniem
i wykorzystaniem odpowiednich bibliotek w zależności od typu danych wejściowych.

Główne komponenty:
- config_generator: Generowanie konfiguracji YAML z żądań w języku naturalnym
- interactive_mapper: Interaktywne mapowanie zadań do bibliotek
- processor_engine: Główny silnik przetwarzania danych
- smart_env_manager: Zarządzanie zmiennymi środowiskowymi
- task_validator: Walidacja konfiguracji zadań
"""

__version__ = "0.1.1"

# Eksport głównych klas i funkcji
from .config_generator import ConfigGenerator
from .interactive_mapper import InteractiveMapper
from .processor_engine import ProcessorEngine
from .smart_env_manager import SmartEnvManager
from .task_validator import TaskValidator

__all__ = [
    'ConfigGenerator',
    'InteractiveMapper',
    'ProcessorEngine',
    'SmartEnvManager',
    'TaskValidator',
    '__version__',
]
