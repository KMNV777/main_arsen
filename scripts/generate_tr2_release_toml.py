#!/usr/bin/env python3
"""Generate TR2 release candidate TOML from component definitions."""

from pathlib import Path

REGISTRY = "registry.gazprom-neft.local:5000"
GIT_BASE = "ssh://alm-itsk.gazprom-neft.local:8180/TFS/GPN"
GIT_BRANCH = "release/2026.7.1"
VERSION = "2026.7.1"
REGISTRY_PROJECT_FOLDER = "u250008611"

COMPONENT_TEMPLATE = """
[components.{key}]
name = "{name}"
description = "{description}"
# Имя образа контейнера с компонентом
image = "{image}"
# Версия образа контейнера с компонентом
version = "{version}"
# Путь до GIT репозитория с исходным кодом компонента
git_url = "{git_url}"
# Ветка или тег для GIT репозитория с исходным кодом компонента
git_branch = "{git_branch}"
# В каком регистри располагается или будет располагаться образ контейнера, по умолчанию "registry.gazprom-neft.local:5000"
registry = "{registry}"
# В случае если переносимый компонент не обладает исходным кодом (коробочное или инфраструктурное решение) необходимо указать параметр WITHOUT_SOURCE_CODE установить TRUE. Таким образом проверка исходного кода выполняться не будет. По умолчанию значение параметра FALSE.
without_source_code = "{without_source_code}"
"""

# (image, description, git_project, git_repo_override, without_source_code)
COMPONENTS = [
    ("tr2-authorization", "Авторизация", "tr2", None, False),
    ("tr2-authorization-migrations", "Миграции авторизации", "tr2", "tr2_authorization", False),
    ("tr2-bff", "Backend for Frontend", "tr2", None, False),
    ("tr2-businessaudit", "Бизнес-аудит", "tr2", None, False),
    ("tr2-businessaudit-migrations", "Миграции бизнес-аудита", "tr2", "tr2_businessaudit", False),
    ("tr2-datacollector", "Сборщик данных", "tr2", None, False),
    ("tr2-demechanization", "Демеханизация", "tr2", None, False),
    ("tr2-demechanization-migrations", "Миграции демеханизации", "tr2", "tr2_demechanization", False),
    ("tr2-jobscheduler", "Планировщик задач", "tr2", None, False),
    ("tr2-limitations", "Ограничения", "tr2", None, False),
    ("tr2-mdm", "MDM", "tr2", None, False),
    ("tr2-mdm-integration", "Интеграция MDM", "tr2", None, False),
    ("tr2-mdm-migrations", "Миграции MDM", "tr2", "tr2_mdm", False),
    ("tr2-messagecollector", "Сборщик сообщений", "tr2", None, False),
    ("tr2-opt", "Оптимизация", "tr2", None, False),
    ("tr2-opt-migrations", "Миграции оптимизации", "tr2", "tr2_opt", False),
    ("tr2-postgres-migrations", "Миграции PostgreSQL", "tr2", "tr2_postgres", False),
    ("tr2-pwf", "PWF", "tr2", None, False),
    ("tr2-pwf-migrations", "Миграции PWF", "tr2", "tr2_pwf", False),
    ("tr2-rabbitmq", "RabbitMQ", "tr2", None, True),
    ("tr2-signalr", "SignalR", "tr2", None, False),
    ("tr2-uvch", "УВЧ", "tr2", None, False),
    ("tr2-uvch-migrations", "Миграции УВЧ", "tr2", "tr2_uvch", False),
    ("tr2-uvch-monitoring", "Мониторинг УВЧ", "tr2", None, False),
    ("tr2-uvch-solver", "Решатель УВЧ", "tr2", None, False),
    ("tr2-wellmodel", "Модель скважины", "tr2", None, False),
    ("tr2-wellmodel-migrations", "Миграции модели скважины", "tr2", "tr2_wellmodel", False),
    ("tr2-wellmodel-preprocessor", "Препроцессор модели скважины", "tr2", None, False),
    ("tr2-wellmodel-solver", "Решатель модели скважины", "tr2", None, False),
    ("tr2-nonstationary-solver", "Решатель нестационарной модели", "tr2", None, False),
    ("tr2-frontend", "Frontend", "tr2", None, False),
    ("hdws-fastapi", "HDWS FastAPI", "hdws", None, False),
    ("hdws-worker", "HDWS Worker", "hdws", None, False),
    ("hdsw-worker-periodic", "HDWS Worker Periodic", "hdws", "hdws_worker_periodic", False),
    ("hdsw-redis", "HDWS Redis", "hdws", None, True),
    ("dt-well-migrations", "Миграции DT Well", "dt-well", "dt_well", False),
    ("dt-well-api-service", "DT Well API сервис", "dt-well", None, False),
    ("dt-well-calc-service", "DT Well Calc сервис", "dt-well", None, False),
    ("dt-well-tr-integration-service", "DT Well TR интеграция", "dt-well", None, False),
    ("dt-well-ws-service", "DT Well WS сервис", "dt-well", None, False),
    ("dt-well-frontend", "DT Well Frontend", "dt-well", None, False),
]


def to_repo_name(image: str) -> str:
    return image.replace("-", "_")


def component_key(image: str) -> str:
    return image.replace("-", "_").replace(".", "_")


def build_toml() -> str:
    header = f"""# Описание кандидата
# Окружение: OCP4_PROD (tr2-authorization — OCP_PROD)

# Путь к образам в Nexus. Параметр определяет проектная команда. Используется при сканировании образов контейнеров
registry_project_folder = "{REGISTRY_PROJECT_FOLDER}"

# Раздел определяет версию ПО, которое планируем запуска по шагам оркестратора. И путь до файла где описаны изменения в версии.
[release]
version = "{VERSION}"
releaseDescriptionFile = "CHANGELOG.md"

[components]
"""
    blocks = []
    for image, description, git_project, git_repo_override, without_source_code in COMPONENTS:
        repo = git_repo_override or to_repo_name(image)
        git_url = f"{GIT_BASE}/{git_project}/_git/{repo}"
        blocks.append(
            COMPONENT_TEMPLATE.format(
                key=component_key(image),
                name=image,
                description=description,
                image=image,
                version=VERSION,
                git_url=git_url,
                git_branch=GIT_BRANCH,
                registry=REGISTRY,
                without_source_code=str(without_source_code).lower(),
            ).rstrip()
        )

    return header + "\n".join(blocks) + "\n"


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "U250008611tr2release2026.7.1.toml"
    output.write_text(build_toml(), encoding="utf-8")
    print(f"Written {output} ({len(COMPONENTS)} components)")


if __name__ == "__main__":
    main()
