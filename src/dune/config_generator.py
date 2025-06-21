"""
Generator konfiguracji YAML na podstawie żądań w języku naturalnym.
"""

import yaml
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger


class ConfigGenerator:
    """Generator konfiguracji zadań na podstawie NLP."""

    def __init__(self, llm_analyzer=None):
        self.llm_analyzer = llm_analyzer
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Ładuje szablony konfiguracji dla różnych typów zadań."""
        return {
            "email_processing": {
                "runtime": {
                    "python_packages": {
                        "required": ["imaplib2", "email-validator", "python-dotenv", "loguru"],
                        "optional": ["beautifulsoup4", "chardet"]
                    },
                    "environment": {
                        "required": ["IMAP_SERVER", "IMAP_USERNAME", "IMAP_PASSWORD"],
                        "optional": ["IMAP_PORT", "IMAP_USE_SSL", "OUTPUT_DIR"]
                    }
                },
                "services": {
                    "dependencies": [{
                        "name": "imap-server",
                        "type": "imap",
                        "required": True,
                        "connection": {
                            "host": "${IMAP_SERVER}",
                            "port": "${IMAP_PORT:-143}",
                            "ssl": "${IMAP_USE_SSL:-false}"
                        },
                        "health_check": {
                            "type": "tcp_connect",
                            "timeout": "10s"
                        }
                    }]
                }
            },

            "database_processing": {
                "runtime": {
                    "python_packages": {
                        "required": ["sqlalchemy", "pandas", "python-dotenv"],
                        "optional": ["psycopg2-binary", "pymysql", "cx_Oracle"]
                    },
                    "environment": {
                        "required": ["DATABASE_URL"],
                        "optional": ["DB_POOL_SIZE", "DB_TIMEOUT"]
                    }
                },
                "services": {
                    "dependencies": [{
                        "name": "database",
                        "type": "sql",
                        "required": True,
                        "connection": {
                            "url": "${DATABASE_URL}"
                        },
                        "health_check": {
                            "type": "sql_query",
                            "query": "SELECT 1",
                            "timeout": "30s"
                        }
                    }]
                }
            },

            "file_processing": {
                "runtime": {
                    "python_packages": {
                        "required": ["pandas", "openpyxl", "python-dotenv"],
                        "optional": ["xlrd", "chardet", "python-magic"]
                    },
                    "environment": {
                        "required": ["INPUT_DIR", "OUTPUT_DIR"],
                        "optional": ["FILE_PATTERN", "ENCODING"]
                    }
                }
            },

            "web_scraping": {
                "runtime": {
                    "python_packages": {
                        "required": ["requests", "beautifulsoup4", "selenium", "python-dotenv"],
                        "optional": ["scrapy", "lxml", "html5lib"]
                    },
                    "environment": {
                        "required": ["TARGET_URL"],
                        "optional": ["USER_AGENT", "REQUEST_DELAY", "PROXY_URL"]
                    }
                }
            }
        }

    def generate_config_from_nlp(self, natural_request: str) -> Dict[str, Any]:
        """Generuje konfigurację YAML na podstawie żądania w języku naturalnym."""

        logger.info("🔄 Analizowanie żądania w celu wygenerowania konfiguracji...")

        # Wykryj typ zadania
        task_type = self._detect_task_type(natural_request)
        logger.info(f"🎯 Wykryty typ zadania: {task_type}")

        # Wyodrębnij wymagania
        requirements = self._extract_requirements(natural_request)

        # Wykryj potrzebne pakiety
        packages = self._detect_required_packages(natural_request, task_type)

        # Wykryj zmienne środowiskowe
        env_vars = self._detect_environment_variables(natural_request, task_type)

        # Wykryj usługi
        services = self._detect_services(natural_request, task_type)

        # Wygeneruj podstawową konfigurację
        config = self._build_base_config(
            natural_request, task_type, requirements,
            packages, env_vars, services
        )

        return config

    def _detect_task_type(self, request: str) -> str:
        """Wykrywa typ zadania na podstawie słów kluczowych."""

        request_lower = request.lower()

        # Mapa słów kluczowych do typów zadań
        keywords_map = {
            "email_processing": ["email", "imap", "pop3", "skrzynka", "wiadomość", "poczta"],
            "database_processing": ["baza danych", "sql", "tabela", "rekord", "zapytanie"],
            "file_processing": ["plik", "csv", "excel", "json", "xml", "folder"],
            "web_scraping": ["strona", "scraping", "pobierz z internetu", "www", "http"],
            "api_processing": ["api", "endpoint", "rest", "json api", "webhook"],
            "data_analysis": ["analiza", "wykres", "statystyki", "raport", "dashboard"]
        }

        # Zlicz dopasowania dla każdego typu
        scores = {}
        for task_type, keywords in keywords_map.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                scores[task_type] = score

        # Zwróć typ z najwyższym wynikiem
        if scores:
            return max(scores, key=scores.get)

        return "generic_processing"

    def _extract_requirements(self, request: str) -> List[str]:
        """Wyodrębnia wymagania funkcjonalne z żądania."""

        requirements = []
        request_lower = request.lower()

        # Mapa wzorców do wymagań
        patterns = {
            r"pobierz.*email|pobierz.*wiadomoś": "download_emails",
            r"zapisz.*folder|organizuj.*folder": "organize_files",
            r"połącz.*imap|łącz.*imap": "connect_imap",
            r"filtruj.*dat|sortuj.*dat": "filter_by_date",
            r"utwórz.*raport|generuj.*raport": "generate_report",
            r"analizuj.*treść": "analyze_content",
            r"wyślij.*email": "send_email",
            r"pobierz.*załącznik": "download_attachments"
        }

        for pattern, requirement in patterns.items():
            if re.search(pattern, request_lower):
                requirements.append(requirement)

        return requirements if requirements else ["process_data"]

    def _detect_required_packages(self, request: str, task_type: str) -> Dict[str, List[str]]:
        """Wykrywa wymagane pakiety Python."""

        # Pobierz bazowe pakiety dla typu zadania
        base_template = self.templates.get(task_type, {})
        packages = base_template.get("runtime", {}).get("python_packages", {
            "required": ["python-dotenv", "loguru"],
            "optional": []
        }).copy()

        request_lower = request.lower()

        # Dodatkowe pakiety na podstawie kontekstu
        additional_packages = {
            "pandas": ["csv", "excel", "dataframe", "tabela"],
            "requests": ["http", "api", "pobierz z internetu"],
            "beautifulsoup4": ["html", "scraping", "parsuj"],
            "sqlalchemy": ["sql", "baza danych"],
            "matplotlib": ["wykres", "chart", "plot"],
            "numpy": ["obliczenia", "matematyka", "array"],
            "opencv-python": ["obraz", "zdjęcie", "cv2"],
            "pillow": ["pil", "image", "grafika"]
        }

        for package, keywords in additional_packages.items():
            if any(keyword in request_lower for keyword in keywords):
                if package not in packages["required"]:
                    packages["optional"].append(package)

        return packages

    def _detect_environment_variables(self, request: str, task_type: str) -> Dict[str, List[str]]:
        """Wykrywa potrzebne zmienne środowiskowe."""

        # Pobierz bazowe zmienne dla typu zadania
        base_template = self.templates.get(task_type, {})
        env_vars = base_template.get("runtime", {}).get("environment", {
            "required": [],
            "optional": ["OUTPUT_DIR"]
        }).copy()

        request_lower = request.lower()

        # Dodatkowe zmienne na podstawie kontekstu
        additional_vars = {
            "API_KEY": ["api", "klucz", "token"],
            "DATABASE_URL": ["baza danych", "sql"],
            "WEBHOOK_URL": ["webhook", "callback"],
            "PROXY_URL": ["proxy", "pośrednik"],
            "TIMEOUT": ["timeout", "czas", "oczekiwanie"]
        }

        for var, keywords in additional_vars.items():
            if any(keyword in request_lower for keyword in keywords):
                if var not in env_vars["required"]:
                    env_vars["optional"].append(var)

        return env_vars

    def _detect_services(self, request: str, task_type: str) -> Dict[str, Any]:
        """Wykrywa wymagane usługi zewnętrzne."""

        # Pobierz bazowe usługi dla typu zadania
        base_template = self.templates.get(task_type, {})
        services = base_template.get("services", {
            "dependencies": [],
            "managed_services": []
        }).copy()

        request_lower = request.lower()

        # Dodatkowe usługi na podstawie kontekstu
        if "redis" in request_lower:
            services["dependencies"].append({
                "name": "redis",
                "type": "cache",
                "required": False,
                "connection": {"host": "${REDIS_HOST:-localhost}", "port": "6379"},
                "health_check": {"type": "tcp_connect", "timeout": "5s"}
            })

        if "elasticsearch" in request_lower:
            services["dependencies"].append({
                "name": "elasticsearch",
                "type": "search",
                "required": False,
                "connection": {"url": "${ELASTICSEARCH_URL:-http://localhost:9200}"},
                "health_check": {"type": "http_get", "endpoint": "/_cluster/health", "timeout": "10s"}
            })

        return services

    def _build_base_config(self, request: str, task_type: str, requirements: List[str],
                           packages: Dict[str, List[str]], env_vars: Dict[str, List[str]],
                           services: Dict[str, Any]) -> Dict[str, Any]:
        """Buduje podstawową konfigurację."""

        # Wygeneruj nazwę zadania
        task_name = self._generate_task_name(request, task_type)

        config = {
            "apiVersion": "dune.io/v1",
            "kind": "TaskConfiguration",
            "metadata": {
                "name": task_name,
                "description": request[:200] + "..." if len(request) > 200 else request,
                "version": "1.0",
                "created": datetime.now().isoformat() + "Z",
                "tags": [task_type, "auto-generated"]
            },
            "task": {
                "natural_language": request,
                "requirements": requirements,
                "expected_output": {
                    "type": "file_structure",
                    "pattern": "output/**/*"
                }
            },
            "runtime": {
                "type": "docker",
                "base_image": "python:3.11-slim",
                "python_packages": packages,
                "environment": env_vars
            },
            "services": services,
            "validation": {
                "pre_execution": [
                    {"type": "service_connectivity",
                     "services": [dep["name"] for dep in services.get("dependencies", []) if dep.get("required")]},
                    {"type": "environment_variables", "required": env_vars.get("required", [])},
                    {"type": "file_permissions", "paths": ["${OUTPUT_DIR:-./output}"],
                     "permissions": ["read", "write"]},
                    {"type": "disk_space", "minimum": "100MB", "path": "${OUTPUT_DIR:-./output}"}
                ],
                "post_execution": [
                    {"type": "output_verification", "expected_files": {"pattern": "output/**/*", "minimum_count": 1}},
                    {"type": "directory_structure", "expected": ["output"]}
                ]
            },
            "monitoring": {
                "logs": {
                    "level": "${LOG_LEVEL:-INFO}",
                    "destinations": [
                        {"type": "file", "path": "logs/task-execution.log"},
                        {"type": "stdout", "format": "json"}
                    ]
                },
                "metrics": [
                    {"name": "execution_time", "type": "histogram", "description": "Czas wykonania zadania"},
                    {"name": "errors_count", "type": "counter", "description": "Liczba błędów"}
                ]
            },
            "security": {
                "network": {
                    "allowed_outbound": ["*:80", "*:443"],
                    "blocked_outbound": ["*:22", "*:3389"]
                },
                "filesystem": {
                    "read_only_paths": ["/etc", "/usr"],
                    "writable_paths": ["${OUTPUT_DIR:-./output}", "/tmp", "logs/"]
                }
            },
            "pipeline": {
                "stages": [
                    {"name": "validation", "type": "validation", "config": {"run_pre_execution_checks": True}},
                    {"name": "environment_setup", "type": "setup",
                     "config": {"install_packages": True, "create_directories": True}},
                    {"name": "llm_analysis", "type": "llm_processing",
                     "config": {"analyze_natural_language": True, "generate_code": True}},
                    {"name": "task_execution", "type": "execution",
                     "config": {"run_generated_code": True, "capture_output": True}},
                    {"name": "post_validation", "type": "validation", "config": {"run_post_execution_checks": True}},
                    {"name": "cleanup", "type": "cleanup", "config": {"remove_temp_files": True}}
                ]
            },
            "environments": {
                "development": {
                    "managed_services_enabled": True,
                    "log_level": "DEBUG",
                    "validation_strict": False
                },
                "testing": {
                    "managed_services_enabled": True,
                    "log_level": "INFO",
                    "validation_strict": True
                },
                "production": {
                    "managed_services_enabled": False,
                    "log_level": "WARNING",
                    "validation_strict": True,
                    "security_enhanced": True
                }
            }
        }

        return config

    def _generate_task_name(self, request: str, task_type: str) -> str:
        """Generuje nazwę zadania na podstawie żądania."""

        # Wyciągnij kluczowe słowa
        words = re.findall(r'\b\w+\b', request.lower())
        key_words = [w for w in words if len(w) > 3 and w not in [
            "jest", "będzie", "oraz", "które", "wszystkie", "danych"
        ]][:3]

        if key_words:
            name = "-".join(key_words)
        else:
            name = task_type.replace("_", "-")

        return f"{name}-processor"

    def save_config_to_file(self, config: Dict[str, Any], filename: str = None) -> str:
        """Zapisuje konfigurację do pliku YAML."""

        if not filename:
            task_name = config["metadata"]["name"]
            filename = f"configs/{task_name}.yaml"

        # Utwórz katalog jeśli nie istnieje
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)

        logger.success(f"✅ Konfiguracja zapisana do: {filename}")
        return filename