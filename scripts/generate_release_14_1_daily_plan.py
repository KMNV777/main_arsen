#!/usr/bin/env python3
"""Generate release 14.1 daily plan with QA / DevOps / Security checklists."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "release-14.1-daily-plan.md"

HOLIDAYS = {
    date(2025, 5, 1),
    date(2025, 5, 2),
    date(2025, 5, 8),
    date(2025, 5, 9),
    date(2025, 6, 12),
    date(2025, 6, 13),
}


def workdays(start: date, end: date) -> list[date]:
    days: list[date] = []
    d = start
    while d <= end:
        if d.weekday() < 5 and d not in HOLIDAYS:
            days.append(d)
        d += timedelta(days=1)
    return days


def fmt(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def checklist(items: list[str]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items)


DayPlan = tuple[str, list[str], list[str], list[str]]


PHASE0: list[DayPlan] = [
    (
        "Kick-off подготовки: scope lock и ветка релиза",
        [
            "Провести ревью scope 14.1 с PO, зафиксировать in/out of scope",
            "Сверить тест-план с backlog релиза, выявить пробелы покрытия",
            "Подготовить матрицу трассируемости: фича → ТК → owner",
            "Согласовать критерии severity (P0–P3) на период регресса",
        ],
        [
            "Создать ветку `release/14.1` от стабильного коммита main",
            "Настроить CI pipeline для release-ветки (build + unit + lint)",
            "Подготовить QA-контур: деплой последнего зелёного билда",
            "Зафиксировать версию артефакта (semver/tag) в реестре билдов",
        ],
        [
            "Получить baseline SBOM для целевого билда",
            "Согласовать политику: какие CVE блокируют регресс (Critical/High)",
            "Запросить список обязательных security-контролов для 14.1",
        ],
    ),
    (
        "Актуализация тестовой документации",
        [
            "Обновить/создать ТК по новым фичам 14.1",
            "Провести peer-review ТК с аналитиком/PO",
            "Подготовить smoke-набор (≤ 2 ч прогона)",
            "Подготовить regression suite: приоритет P0-сценариев",
        ],
        [
            "Проверить доступность тестовых данных и фикстур в QA",
            "Настроить автотесты на release-ветку в CI",
            "Проверить секреты/токены QA-контура (rotation, expiry)",
            "Задокументировать URL/доступы к QA для команды",
        ],
        [
            "Проверить, что QA-контур не содержит prod-секретов",
            "Валидировать политики доступа к тестовым средам (RBAC)",
            "Зафиксировать требования к маскированию PII в тест-логах",
        ],
    ),
    (
        "Готовность тест-плана и окружений",
        [
            "Финализировать тест-план 14.1 (версия 1.0)",
            "Разбить ТК по исполнителям и дням регресса (W1–W3)",
            "Подготовить шаблон bug report и SLA на ретест",
            "Провести dry-run smoke на QA (пилотный прогон)",
        ],
        [
            "Верифицировать parity QA vs staging (версии сервисов, конфиги)",
            "Настроить алерты на падение QA-контура в период регресса",
            "Подготовить скрипт быстрого redeploy QA из release-ветки",
            "Проверить лимиты/квоты CI для параллельных прогонов",
        ],
        [
            "SAST quick-scan release-ветки (информативный, без блокера)",
            "Проверить зависимости с известными CVE (предварительный список)",
            "Согласовать процесс эскалации security-дефектов в регрессе",
        ],
    ),
    (
        "Синхронизация после майских праздников",
        [
            "Актуализировать статус ТК после ревью праздничного периода",
            "Провести sync с Dev: список рискованных областей кода",
            "Подтвердить готовность smoke и regression наборов",
            "Подготовить dashboard метрик регресса (burn-down шаблон)",
        ],
        [
            "Redeploy QA с актуальным коммитом release/14.1",
            "Проверить health всех зависимостей QA (DB, MQ, cache)",
            "Зафиксировать snapshot конфигов QA на старт регресса",
            "Подготовить runbook hotfix-деплоя в QA",
        ],
        [
            "Повторный dependency scan после обновления lockfile",
            "Проверить audit log доступа к release-репозиторию",
            "Подтвердить контакты security on-call на период регресса",
        ],
    ),
    (
        "Финальная ревизия тест-артефактов",
        [
            "Sign-off тест-плана от QA Lead",
            "Провести walkthrough тест-плана с Dev и PO",
            "Зафиксировать entry criteria для старта регресса 15.05",
            "Подготовить чеклист Gate 0",
        ],
        [
            "Финальный build candidate в QA, тег `14.1-regression-candidate`",
            "Проверить артефакт: checksum, подпись, reproducibility",
            "Убедиться в rollback QA на предыдущую версию ≤ 15 мин",
            "Забронировать окна CI/CD на период регресса",
        ],
        [
            "Подтвердить security entry criteria для Gate 0",
            "Проверить отсутствие hardcoded credentials в release-ветке (gitleaks)",
            "Задокументировать известные accepted risks (если есть)",
        ],
    ),
    (
        "Репетиция процессов регресса",
        [
            "Провести tabletop: сценарий P0-бага в регрессе",
            "Отрепетировать процесс ретеста и reopen",
            "Проверить интеграцию с bug tracker (workflow, поля)",
            "Назначить дежурного QA на daily standup регресса",
        ],
        [
            "Репетиция hotfix pipeline: commit → build → QA deploy",
            "Проверить время цикла hotfix (target ≤ 4 ч)",
            "Настроить уведомления Slack/Teams для падений CI",
            "Подготовить capacity plan (параллельные деплои)",
        ],
        [
            "Репетиция эскалации: CVE обнаружен в зависимости mid-regression",
            "Проверить SLA security review для hotfix",
            "Обновить security contact list в runbook",
        ],
    ),
    (
        "Стабилизация QA-данных и автотестов",
        [
            "Заморозить тестовые данные baseline для регресса",
            "Прогнать автотесты P0, зафиксировать pass rate baseline",
            "Подготовить список flaky-тестов и план стабилизации",
            "Сверить автотесты с ручными ТК (нет дублирования пробелов)",
        ],
        [
            "Стабилизировать flaky jobs в CI (retry policy, quarantine)",
            "Проверить nightly regression job расписание на период 15.05–05.06",
            "Backup QA DB / state перед регрессом",
            "Документировать restore procedure QA",
        ],
        [
            "Scan тестовых данных на реальный PII (должен быть синтетический)",
            "Проверить шифрование backup QA",
            "Валидировать network policies QA (нет лишних ingress)",
        ],
    ),
    (
        "Cross-team readiness review",
        [
            "Провести readiness review с Dev, PO, Release Manager",
            "Закрыть открытые вопросы по ТК и тест-данным",
            "Подтвердить roster QA на 16 дней регресса",
            "Разослать calendar invites: daily standup 15.05–05.06",
        ],
        [
            "Cross-team readiness: DevOps подтверждает QA green",
            "Проверить on-call ротацию DevOps на регресс",
            "Финальный smoke всех микросервисов 14.1 в QA",
            "Подготовить release dashboard (build, deploy, health)",
        ],
        [
            "Security readiness: подтвердить процесс для регресса",
            "Финальный gitleaks + secret scan release-ветки",
            "Gate 0 pre-check: нет открытых Critical security findings",
        ],
    ),
    (
        "Gate 0 — Go на регресс",
        [
            "Провести Gate 0 meeting, заполнить протокол",
            "Опубликовать стартовый билд и тест-план команде",
            "Разослать kick-off note: правила, SLA, контакты",
            "Подтвердить freeze scope — change только через CAB",
        ],
        [
            "Gate 0: QA-контур стабилен 24+ ч",
            "Зафиксировать build ID для D01 регресса",
            "Включить enhanced monitoring QA на период регресса",
            "Подтвердить hotfix channel (#release-14-1-hotfix)",
        ],
        [
            "Gate 0 sign-off Security: baseline принят",
            "Зафиксировать SBOM v0 в release folder",
            "Передать QA список security-sensitive областей для приоритетного теста",
        ],
    ),
]

PHASE1: list[DayPlan] = [
    (
        "Регресс: старт — smoke и начало прогона",
        [
            "Выполнить smoke-набор на стартовом билде (100%)",
            "Начать прогон P0 ТК (цель дня: ≥ 30% P0)",
            "Заводить баги с severity, steps, logs, build ID",
            "Daily standup: blockers, burn-down",
        ],
        [
            "Подтвердить деплой стартового билда в QA",
            "Мониторинг QA: error rate, latency baseline",
            "Готовность hotfix deploy в течение 4 ч",
            "Логировать все деплои в release journal",
        ],
        [
            "Мониторинг security alerts на QA",
            "Проверить нет аномального трафика/сканирования QA",
            "Быстрый triage если найден security defect в smoke",
        ],
    ),
    (
        "Регресс: продолжение P0",
        [
            "Продолжить P0 ТК (накопительно ≥ 50%)",
            "Ретест закрытых багов вчера (если были фиксы)",
            "Актуализировать ТК при расхождении с фактическим поведением",
            "Triage новых багов с Dev (P0 first)",
        ],
        [
            "Деплой hotfix-билдов по мере готовности",
            "Проверить post-deploy health после каждого hotfix",
            "Обновлять build registry после каждого деплоя",
            "CI: не допускать merge без green checks",
        ],
        [
            "Review security-related багов из вчера",
            "Dependency diff после hotfix — новые CVE?",
            "Документировать security defects в отдельном трекере",
        ],
    ),
    (
        "Регресс W1: основной прогон",
        [
            "Прогон P0 + начало P1 ТК",
            "Цель: ≥ 70% P0 пройдено",
            "Проверить критичные интеграции (API, auth, payments)",
            "Обновить burn-down chart",
        ],
        [
            "Поддерживать QA uptime ≥ 99%",
            "Синхронизировать версии зависимых сервисов",
            "Проверить логирование достаточно для дебага багов",
            "Capacity: параллельные env для QA при необходимости",
        ],
        [
            "Проверить auth/session flows на OWASP top misconfig",
            "Валидировать TLS/certs на QA endpoints",
            "Spot-check логи на утечку sensitive data",
        ],
    ),
    (
        "Регресс W1: интеграции и edge cases",
        [
            "ТК на интеграции и граничные случаи",
            "Exploratory testing по риск-областям от Dev",
            "Ретест P0 фиксов (SLA 1 р.д.)",
            "Начать доводку фичей — regression на changed areas",
        ],
        [
            "Hotfix deploy + DB migration check если есть",
            "Verify rollback одного hotfix на QA (drill)",
            "Мониторинг resource usage QA под нагрузкой тестов",
            "Snapshot QA state EOD для воспроизводимости",
        ],
        [
            "Review RBAC: роли и permissions в новых фичах",
            "Проверить rate limiting на публичных API",
            "Triage security bugs: P0 security = блокер релиза",
        ],
    ),
    (
        "Регресс W1: закрытие недели",
        [
            "Завершить оставшиеся P0 ТК W1",
            "Начать P1 bulk прогон",
            "Weekly mini Go/No-Go: статус P0/P1",
            "Актуализировать ТК по итогам недели",
        ],
        [
            "Weekly infra report: incidents, MTTR",
            "Очистка старых билдов QA (retention policy)",
            "Проверить автотесты nightly — анализ падений",
            "План hotfix окон на W2",
        ],
        [
            "Weekly security sync: открытые security defects",
            "SAST incremental scan на коммиты недели",
            "Обновить risk register",
        ],
    ),
    (
        "Регресс W1 финал / W2 старт",
        [
            "Догнать просроченные P0 ТК",
            "Фокус на P1 + ретест накопленных фиксов",
            "Проверить фичи 14.1 end-to-end user journeys",
            "Документировать known issues (не P0)",
        ],
        [
            "Стабильный билд EOD — tag `14.1-regression-w1`",
            "Проверить миграции applied correctly",
            "Verify feature flags state в QA",
            "Подготовить changelog коммитов W1",
        ],
        [
            "Проверить security fixes из W1 merged",
            "Validate input sanitization на новых формах/API",
            "Проверить CORS/CSP headers если applicable",
        ],
    ),
    (
        "Регресс W2: фиксация P0/P1",
        [
            "Приоритет: все открытые P0 должны быть в работе",
            "Ретест всех P0 фиксов за 24 ч",
            "Продолжить P1 прогон (цель ≥ 50% P1)",
            "Актуализация ТК для изменённых фиксами областей",
        ],
        [
            "Ускоренный hotfix pipeline — target 2–4 ч",
            "Post-deploy automated smoke в CI после hotfix",
            "Мониторинг regression test parallelization",
            "Alert на любой failed deployment",
        ],
        [
            "Security review каждого P0 hotfix (threat check)",
            "Проверить нет bypass auth в фиксах",
            "SCA scan после обновления зависимостей",
        ],
    ),
    (
        "Регресс W2: доводка фичей",
        [
            "Regression на доведённых фичах (full path)",
            "P1 ТК + начало P2 по capacity",
            "Verify fix quality — нет reopen P0",
            "Sync с PO: scope cuts если P0 не закрываются",
        ],
        [
            "Deploy доводок фичей, verify config changes",
            "Проверить backward compatibility settings",
            "Load test light на QA (sanity)",
            "Document config diffs для staging/prod",
        ],
        [
            "Review feature flags security (нет exposed admin)",
            "Audit new API endpoints — auth required?",
            "Check secrets not in env dumps/logs",
        ],
    ),
    (
        "Регресс W2: стабилизация",
        [
            "Цель: P0 open = 0 или с approved waiver",
            "Ретест всех P1 фиксов недели",
            "Пройти тест-план: накопительно ≥ 85%",
            "Подготовить список к Gate 1 mid-check",
        ],
        [
            "Freeze non-critical infra changes в QA",
            "Стабильный билд — минимум деплоев",
            "Verify data integrity после серии фиксов",
            "Backup QA EOD",
        ],
        [
            "Mid-regression security checkpoint",
            "Сверить open security bugs vs gate criteria",
            "Pen-test lite на изменённые endpoints (если есть capacity)",
        ],
    ),
    (
        "Регресс W2: тест-план coverage",
        [
            "Догнать оставшиеся P1 ТК",
            "Exploratory на areas с высоким churn",
            "Ретест regression по fixed modules",
            "Обновить test completion report",
        ],
        [
            "Tag `14.1-regression-w2` на стабильном билде",
            "CI green на release branch обязателен",
            "Подготовить RC branch criteria checklist",
            "Changelog W2 для Release Notes",
        ],
        [
            "DAST scan на QA (scheduled window)",
            "Triage DAST findings — false positive review",
            "Обновить SBOM после W2 merges",
        ],
    ),
    (
        "Регресс W2: pre-Gate 1",
        [
            "Полный ретест всех open P1",
            "Sanity full smoke",
            "Подготовить Gate 1 пакет: metrics, bugs, risks",
            "Confirm test plan ≥ 95% executed",
        ],
        [
            "Pre-Gate 1: QA stable 48h target начинается",
            "Minimize deploys — только P0/P1 blockers",
            "Verify artifact reproducibility",
            "Prepare RC build pipeline parameters",
        ],
        [
            "Pre-Gate 1 security pack: SAST+DAST summary",
            "Confirm zero open Critical security",
            "Document any High with mitigation plan",
        ],
    ),
    (
        "Регресс W2: буфер / догон",
        [
            "Буферный день: закрыть хвосты P1",
            "Финальный ретест спорных багов",
            "Sign-off ТК актуальности от QA owners",
            "Доводка фичей — last mile bugs only",
        ],
        [
            "Буфер: стабилизация, no experimental changes",
            "Final W2 backup QA",
            "RC build dry-run (без публикации)",
            "Staging deploy rehearsal plan",
        ],
        [
            "Буфер: закрыть security findings High",
            "Re-scan после последних фиксов",
            "Security sign-off draft для Gate 1",
        ],
    ),
    (
        "Регресс W3: финальный спринт старт",
        [
            "Финальный прогон оставшихся ТК (100% target)",
            "Full regression на critical paths",
            "Zero tolerance P0 — escalate immediately",
            "Подготовить UAT handoff package",
        ],
        [
            "Подготовить RC1 build environment",
            "Staging parity check начать",
            "Freeze dependency updates (except security)",
            "Document exact commit SHA for RC",
        ],
        [
            "Final security regression checklist start",
            "Verify encryption at rest/transit unchanged",
            "Review admin/privileged flows",
        ],
    ),
    (
        "Регресс W3: финальный ретест",
        [
            "Ретест 100% fixed bugs since D01",
            "Confirm P0=0, P1≤3 (waiver documented)",
            "Final smoke + sanity на freeze candidate",
            "Archive test evidence (screenshots, logs)",
        ],
        [
            "Build RC1 candidate overnight ready",
            "Staging deploy RC1 candidate (evening/next AM)",
            "Smoke automation on RC1",
            "Tag `14.1-rc1-candidate`",
        ],
        [
            "Full SAST on RC1 candidate branch",
            "SCA full scan RC1",
            "Gate 1 security pre-approval package",
        ],
    ),
    (
        "Регресс W3: Gate 1 prep",
        [
            "Финальный отчёт: test plan execution 98%+",
            "Gate 1 checklist complete",
            "Handoff notes для RC phase",
            "Retrospective quick: что улучшить в 14.2",
        ],
        [
            "RC1 deploy to staging",
            "Staging health verification",
            "Rollback staging drill",
            "Release journal: regression complete entry",
        ],
        [
            "Security Gate 1 attendance prepared",
            "Final CVE list for RC1",
            "Sign-off memo draft",
        ],
    ),
    (
        "Gate 1 — завершение регресса",
        [
            "Gate 1 meeting + протокол Go",
            "Freeze test evidence в release folder",
            "Communicate regression complete to stakeholders",
            "Transition checklist to RC phase",
        ],
        [
            "Gate 1: promote build to RC1 official",
            "Lock QA to RC1 SHA",
            "Enable staging monitoring dashboards",
            "Announce code freeze effective next phase",
        ],
        [
            "Gate 1 Security sign-off (или waiver list)",
            "Archive SBOM regression-final",
            "Handoff security watchlist для RC",
        ],
    ),
]

# Phase 2-5: generate with templates + specific milestone days
def phase2_day(idx: int, total: int, d: date) -> DayPlan:
    n = idx + 1
    if n == 1:
        return (
            "Hard Code Freeze + RC1 официальный",
            [
                "Smoke RC1 на staging (100%)",
                "Verify RC1 = Gate 1 approved SHA",
                "Начать UAT smoke с PO",
                "Заморозить ТК — изменения только via CR",
            ],
            [
                "Официальный RC1 tag `14.1-rc1`",
                "Deploy RC1 staging + pre-prod mirror",
                "Disable auto-deploy from release branch без approval",
                "Archive RC1 artifacts (signed)",
            ],
            [
                "RC1 full SAST gate — Critical = 0",
                "SCA gate — no new Critical CVE",
                "Document RC1 security baseline",
            ],
        )
    if n == 2:
        return (
            "UAT старт — бизнес-сценарии",
            [
                "UAT Day 1: critical business flows с PO",
                "Document UAT defects (severity)",
                "Sanity automation on staging",
                "Support PO during UAT sessions",
            ],
            [
                "Staging stability monitoring",
                "UAT support: quick env refresh if needed",
                "Log all UAT environment changes",
                "Prepare hotfix window for UAT blockers",
            ],
            [
                "Monitor UAT access — least privilege",
                "Review UAT data handling",
                "Security standby for UAT escalations",
            ],
        )
    if n in (3, 4):
        return (
            f"UAT продолжение (день {n - 1})",
            [
                "UAT сценарии по test script PO",
                "Ретест UAT blockers (P0/P1)",
                "Regression spot-check после UAT fixes",
                "UAT sign-off progress tracker update",
            ],
            [
                "Deploy UAT fixes to staging only",
                "Maintain staging = RC + approved hotfixes",
                "Daily staging health report",
                "Pre-prod sync if UAT requires",
            ],
            [
                "Review UAT hotfixes security",
                "Incremental scan on UAT fixes",
                "Track security UAT observations",
            ],
        )
    if n == 5:
        return (
            "UAT mid-point review",
            [
                "UAT mid-review с PO: coverage %",
                "Prioritize remaining UAT gaps",
                "Performance sanity scripts run",
                "Update release notes draft",
            ],
            [
                "Staging perf baseline capture",
                "Check autoscaling under UAT load",
                "Infra capacity note for prod",
                "RC1 changelog update",
            ],
            [
                "Mid-UAT security checkpoint",
                "Review access logs staging",
                "Confirm no prod data in UAT",
            ],
        )
    if n in range(6, 10):
        return (
            f"UAT + стабилизация RC (день {n - 5})",
            [
                "Continue UAT + defect retest",
                "Exploratory on payment/auth flows",
                "Automated regression on staging nightly review",
                "P2/P3 triage — defer post-release if ok",
            ],
            [
                "Nightly staging deploy only if hotfix",
                "Monitor error budgets staging",
                "DB migration verify on staging",
                "Document config for prod",
            ],
            [
                "Daily incremental security scan",
                "Triage new CVE in dependencies",
                "Update vulnerability register",
            ],
        )
    if n == 10:
        return (
            "Нагрузочное тестирование — старт",
            [
                "Execute load test plan on staging",
                "Monitor SLO: latency, error rate, throughput",
                "Compare vs 14.0 baseline",
                "Log perf defects",
            ],
            [
                "Load test infra: scale staging appropriately",
                "APM dashboards for load test",
                "Capture infra metrics (CPU, memory, IO)",
                "Ensure no impact on other envs",
            ],
            [
                "Security during load: no auth bypass under stress",
                "Rate limit behavior validation",
                "DDoS protection rules review",
            ],
        )
    if n in range(11, 14):
        return (
            f"Perf + RC стабилизация (день {n - 10})",
            [
                "Perf test analysis + retest fixes",
                "Full regression staging после perf fixes",
                "UAT final scenarios",
                "Prepare RC2 criteria (if needed)",
            ],
            [
                "Tune staging after perf findings",
                "RC2 build prep if RC1 insufficient",
                "Prod-like config validation",
                "Migration timing benchmarks",
            ],
            [
                "Scan RC after perf-related changes",
                "Verify TLS performance config secure",
                "Review cache security headers",
            ],
        )
    if n == 14:
        return (
            "RC2 decision point",
            [
                "RC1 vs RC2 Go/No-Go",
                "If RC2: full smoke RC2",
                "UAT sign-off draft from PO",
                "Finalize test summary report",
            ],
            [
                "Build RC2 if required, tag `14.1-rc2`",
                "Deploy RC2 staging, archive RC1",
                "Update artifact registry",
                "Changelog RC1→RC2",
            ],
            [
                "RC2 full security scan if built",
                "Compare CVE delta RC1→RC2",
                "Security approval RC2",
            ],
        )
    if n in range(15, 19):
        return (
            f"Документация и security baseline (день {n - 14})",
            [
                "Support release notes verification",
                "Final staging regression P0 paths",
                "Sign-off test summary QA Lead",
                "Handoff package для pre-transfer",
            ],
            [
                "Finalize runbook deploy 14.1",
                "Finalize rollback runbook + drill",
                "Pre-prod deploy RC final",
                "Prod deploy rehearsal checklist",
            ],
            [
                "Security baseline scan (SAST+DAST+SCA)",
                "Produce CVE report for transfer phase",
                "Prioritize Critical/High for phase 4",
                "Gate 2 security pre-check",
            ],
        )
    return (
        "Gate 2 — RC принят",
        [
            "Gate 2 meeting: UAT sign-off confirm",
            "QA handoff to pre-transfer checklist",
            "Archive all test artifacts",
            "Communicate RC accepted",
        ],
        [
            "Gate 2: lock RC final SHA `14.1-rc-final`",
            "Pre-prod = RC final, smoke green",
            "CAB packet technical appendix",
            "Freeze RC — only transfer-phase patches",
        ],
        [
            "Gate 2 Security sign-off",
            "Final SBOM `14.1-rc-final`",
            "Transfer-phase vulnerability backlog prioritized",
        ],
    )


def phase3_day(idx: int, d: date) -> DayPlan:
    n = idx + 1
    if n == 1:
        return (
            "Старт предтрансфера: CAB подача",
            [
                "Review pre-transfer QA checklist",
                "Verify RC final staging smoke",
                "Prepare prod validation test suite (post-deploy)",
                "Sync test window с DevOps prod deploy",
            ],
            [
                "Submit CAB / Change Request для prod",
                "Attach runbook, rollback, RC SHA",
                "Define prod maintenance window",
                "Pre-prod final sync with RC",
            ],
            [
                "Attach security baseline report to CAB",
                "List open High CVE with fix ETA",
                "CAB security review slot booked",
            ],
        )
    if n in range(2, 6):
        return (
            f"Pre-prod hardening (день {n})",
            [
                "Execute pre-prod test suite",
                "Validate prod-like data scenarios (anonymized)",
                "Document post-deploy smoke for prod",
                "Train support on known issues",
            ],
            [
                "Pre-prod config parity with prod template",
                "Secrets rotation plan prod (if needed)",
                "DB migration dry-run #1 on prod copy",
                "Network/firewall rules verify prod path",
            ],
            [
                "Pre-prod penetration config review",
                "Verify WAF rules prod",
                "IAM roles prod least-privilege review",
            ],
        )
    if n in range(6, 11):
        return (
            f"Миграции и мониторинг (день {n - 5})",
            [
                "Test migration rollback scenarios (QA/pre-prod)",
                "Define prod smoke ≤ 30 min checklist",
                "Canary test plan if applicable",
                "Support comms T-14 draft review",
            ],
            [
                "Migration dry-run #2 timed",
                "Setup prod release dashboards",
                "Alert thresholds prod (error, latency)",
                "War room bridge + calendar",
            ],
            [
                "Audit prod secrets in vault — no stale",
                "Verify audit logging prod enabled",
                "SIEM alerts for deploy window configured",
            ],
        )
    if n in range(11, 16):
        return (
            f"CAB follow-up и rollback drills (день {n - 10})",
            [
                "Review support playbook 14.1",
                "Finalize prod smoke assignments",
                "Feature flag rollout plan test",
                "Comms T-7 content QA review",
            ],
            [
                "Rollback drill on pre-prod (timed)",
                "Document RTO/RPO actuals",
                "On-call roster finalized",
                "Prod deploy artifact immutability verify",
            ],
            [
                "Security on-call roster transfer phase",
                "Verify incident response playbooks",
                "Patch staging for High CVE (prep)",
            ],
        )
    if n in range(16, 21):
        return (
            f"Финальная готовность (день {n - 15})",
            [
                "Comms T-7 sent, FAQ review",
                "Prod test data / accounts verify",
                "Go/No-Go dry-run agenda",
                "Handoff to transfer phase team",
            ],
            [
                "Prod infra pre-check: capacity, disks, certs",
                "Backup prod pre-deploy snapshot plan",
                "Immutable artifact in prod registry",
                "Deploy automation final test (dry-run)",
            ],
            [
                "CVE remediation sprints planning (phase 4)",
                "Pre-transfer vulnerability assign owners",
                "Security war room prep",
            ],
        )
    if n in range(21, 24):
        return (
            f"Gate 3 preparation (день {n - 20})",
            [
                "Comms T-1 draft",
                "Prod smoke team briefing",
                "Confirm no open P0/P1 on RC",
                "Gate 3 checklist complete",
            ],
            [
                "Final pre-prod smoke RC",
                "Prod window confirmation from CAB",
                "War room tech check",
                "Rollback artifacts staged",
            ],
            [
                "Gate 3 security checklist",
                "Confirm Critical CVE = 0 or explicit waiver",
                "Security briefing transfer team",
            ],
        )
    return (
        "Gate 3 — Go на трансфер 08.08",
        [
            "Gate 3 meeting + Go decision",
            "Publish prod smoke checklist final",
            "Team standby confirm transfer 08.08",
            "Archive pre-transfer evidence",
        ],
        [
            "Gate 3: prod deploy window locked",
            "Final artifact checksum to transfer team",
            "Enable prod enhanced monitoring (standby)",
            "Kick #release-14-1-transfer channel",
        ],
        [
            "Gate 3 Security Go",
            "Distribute prioritized CVE fix list phase 4",
            "Security joins war room 08.08",
        ],
    )


def phase4_day(idx: int, d: date) -> DayPlan:
    n = idx + 1
    if n == 1:
        return (
            "Трансфер D01: pre-prod → prod (этап 1)",
            [
                "Pre-deploy prod smoke baseline (if prod prev version)",
                "Standby war room — QA",
                "Prepare post-deploy smoke scripts",
                "Verify test accounts prod ready",
            ],
            [
                "Execute deploy runbook step 1–N (pre-prod validated)",
                "Prod deploy phase 1 per runbook",
                "Monitor deploy metrics live",
                "Checkpoint: rollback decision point 1",
            ],
            [
                "Security war room active",
                "Monitor SIEM during deploy",
                "Verify no unauthorized deploy activity",
                "Block deploy if Critical CVE unfixed (policy)",
            ],
        )
    if n == 2:
        return (
            "Трансфер D02: prod deploy продолжение",
            [
                "Post-deploy smoke phase 1 (critical paths)",
                "Log any prod anomalies as incidents",
                "Compare prod vs staging behavior",
                "Retest hotfix if deploy patch applied",
            ],
            [
                "Deploy phase 2 services / DB migrations",
                "Migration progress monitoring",
                "Checkpoint rollback 2",
                "Update release journal real-time",
            ],
            [
                "Validate auth flows prod post-deploy",
                "Check cert/TLS post-migration",
                "Scan prod surface (passive) for misconfig",
            ],
        )
    if n in range(3, 6):
        return (
            f"Трансфер D0{n}: стабилизация prod (день {n - 2})",
            [
                "Expanded prod smoke (full checklist)",
                "Monitor user-reported issues channel",
                "Regression prod hotfixes only",
                "Daily prod health report",
            ],
            [
                "Complete remaining deploy steps",
                "Tune prod autoscaling post-deploy",
                "Verify backups post-migration",
                "Hotfix deploy to prod if P0",
            ],
            [
                f"CVE remediation batch {n - 2}: assign + track",
                "Patch Critical/High dependencies",
                "Re-scan after patches",
            ],
        )
    if n == 6:
        return (
            "Трансфер mid-point: security sprint",
            [
                "Prod full smoke regression P0",
                "Verify feature flags prod state",
                "Sign-off prod stable draft",
                "Document prod known issues",
            ],
            [
                "Prod stable 72h checkpoint start",
                "Infra cost/perf post-deploy review",
                "Deploy security patches to prod",
                "Verify checksum prod = RC + approved patches",
            ],
            [
                "Mid-transfer CVE review meeting",
                "Target: Critical = 0 by D12",
                "DAST prod (scheduled, scoped)",
                "Triage DAST prod findings",
            ],
        )
    if n in range(7, 11):
        return (
            f"Уязвимости + стабилизация D0{n} (день {n - 6})",
            [
                "Prod monitoring review daily",
                "Retest security patch regressions",
                "Support patch validation tests",
                "Update prod smoke after patches",
            ],
            [
                "Deploy vulnerability patches prod",
                "Rolling restart if required — runbook",
                "Monitor patch deploy health",
                "Maintain rollback readiness",
            ],
            [
                f"CVE closure sprint day {n - 6}",
                "Verify High CVE closure",
                "SCA/SAST on patch branches",
                "Security sign-off per patch batch",
            ],
        )
    if n in range(11, 14):
        return (
            f"Финал трансфера D0{n} (день {n - 10})",
            [
                "Final prod smoke full suite",
                "Prod stable 48h verification",
                "Gate 4 checklist QA",
                "Prepare Go-Live comms support",
            ],
            [
                "Final prod config freeze",
                "Archive prod deploy logs",
                "Disable enhanced deploy permissions",
                "Prod = release candidate final",
            ],
            [
                "Final security re-scan prod",
                "Critical/High CVE = 0 confirm",
                "Gate 4 security package",
                "Security Go-Live approval draft",
            ],
        )
    return (
        "Gate 4 — Трансфер завершён",
        [
            "Gate 4 meeting QA sign-off",
            "Prod validation complete report",
            "Handoff to Go-Live comms",
            "Archive prod test evidence",
        ],
        [
            "Gate 4: prod stable, deploy complete",
            "Close transfer change ticket",
            "Restore normal change policy",
            "Go-Live deploy confirmation",
        ],
        [
            "Gate 4 Security final sign-off",
            "Publish security release bulletin",
            "Close vulnerability sprint",
        ],
    )


def phase5_day(idx: int, d: date) -> DayPlan:
    n = idx + 1
    if n == 1:
        return (
            "Go-Live D01: публичный релиз 14.1",
            [
                "Execute public release smoke prod",
                "Monitor support tickets first 4h",
                "Verify feature flags public rollout",
                "War room QA first shift",
            ],
            [
                "Enable public feature flags per plan",
                "Publish release announcement trigger",
                "Enhanced monitoring 24h",
                "On-call primary DevOps",
            ],
            [
                "Security monitor first 24h post-release",
                "Watch auth anomaly dashboards",
                "Incident response standby",
            ],
        )
    if n in (2, 3):
        return (
            f"Go-Live D0{n}: усиленный мониторинг",
            [
                "Daily prod health QA report",
                "Triage post-release defects",
                "Smoke on hotfixes if any",
                "Update known issues list",
            ],
            [
                "Review prod metrics vs SLO",
                "Hotfix only P0 prod issues",
                "Capacity adjust if needed",
                "Daily war room summary",
            ],
            [
                "Daily security ops review",
                "Scan for post-release attack patterns",
                "Review prod access anomalies",
            ],
        )
    if n in range(4, 8):
        return (
            f"Стабилизация D0{n} (день {n - 3})",
            [
                "Regression post-release hotfixes",
                "Defer P2/P3 to 14.1.1 if agreed",
                "Support escalation QA",
                "Collect feedback for retro",
            ],
            [
                "Normalize infra to BAU settings",
                "Cleanup temp release resources",
                "Update docs from prod learnings",
                "Patch deploy if needed",
            ],
            [
                "Close remaining Medium CVE if scheduled",
                "Weekly security digest post-release",
                "Update threat model if architecture changed",
            ],
        )
    if n == 8:
        return (
            "Ретроспектива релиза",
            [
                "Blameless retro participation",
                "QA metrics: escaped defects, coverage",
                "Action items для 14.2",
                "Archive final test report",
            ],
            [
                "Retro: deploy MTTR, incidents",
                "Update runbooks from learnings",
                "CI/CD improvements backlog",
                "Close release branch planning",
            ],
            [
                "Retro: security findings timeline",
                "Process improvements security gates",
                "Update security checklist template",
            ],
        )
    if n == 9:
        return (
            "Закрытие релизного тикета",
            [
                "Final QA sign-off release 14.1",
                "Publish test summary archive",
                "Transition bugs to BAU backlog",
                "Release 14.1.1 planning input",
            ],
            [
                "Close infrastructure change records",
                "Tag `14.1` production stable in registry",
                "Merge release branch plan (or maintain)",
                "Resource decommission temp envs",
            ],
            [
                "Final security release sign-off",
                "Archive all scan reports",
                "Compliance evidence package",
            ],
        )
    return (
        "Переход в BAU",
        [
            "Remove enhanced QA monitoring",
            "BAU test cadence restored",
            "Document lessons learned wiki",
            "Celebrate / team recognition",
        ],
        [
            "Disable war room schedules",
            "BAU on-call only",
            "Release 14.1 marked complete in CMDB",
            "Snapshot final prod state documentation",
        ],
        [
            "BAU vulnerability scanning schedule",
            "Close release security project",
            "Handoff to continuous compliance",
        ],
    )


PHASES = [
    ("0", "Подготовка к регрессу", date(2025, 4, 28), date(2025, 5, 14), PHASE0, None),
    ("1", "Регресс и стабилизация", date(2025, 5, 15), date(2025, 6, 5), PHASE1, None),
    ("2", "RC и приёмка", date(2025, 6, 6), date(2025, 7, 4), None, "phase2"),
    ("3", "Предтрансферная готовность", date(2025, 7, 7), date(2025, 8, 7), None, "phase3"),
    ("4", "Трансфер и уязвимости", date(2025, 8, 8), date(2025, 8, 27), None, "phase4"),
    ("5", "Go-Live и пострелиз", date(2025, 8, 28), date(2025, 9, 10), None, "phase5"),
]


def render_day(phase_id: str, phase_name: str, day_num: int, total: int, d: date, plan: DayPlan) -> str:
    goal, qa, devops, sec = plan
    return f"""### {fmt(d)} — Фаза {phase_id}, D{day_num:02d}/{total:02d}: {goal}

**QA**
{checklist(qa)}

**DevOps**
{checklist(devops)}

**Security**
{checklist(sec)}

---
"""


def main() -> None:
    lines = [
        "# Релиз 14.1 — дневной план (QA / DevOps / Security)",
        "",
        "> Документ сгенерирован для сквозного управления релизом. Каждый рабочий день содержит чеклисты трёх функций.",
        "",
        "## Ключевые вехи",
        "",
        "| Веха | Дата |",
        "|------|------|",
        "| Старт регресса | 15.05.2025 |",
        "| Gate 1 (конец регресса) | 05.06.2025 |",
        "| Gate 2 (RC принят) | 04.07.2025 |",
        "| Gate 3 (Go на трансфер) | 07.08.2025 |",
        "| Старт трансфера | 08.08.2025 |",
        "| Gate 4 (конец трансфера) | 27.08.2025 |",
        "| Go-Live | 28.08.2025 |",
        "| Закрытие релиза | 10.09.2025 |",
        "",
        "## Условные обозначения",
        "",
        "- **P0** — блокер релиза, SLA фикса 24 ч, ретест 1 р.д.",
        "- **P1** — критичный, SLA 48 ч",
        "- **Gate** — формальная точка Go/No-Go с протоколом",
        "- Чеклисты отмечать `[x]` по факту выполнения",
        "",
        "## Сводка по фазам",
        "",
    ]

    for phase_id, phase_name, start, end, static_plans, dynamic in PHASES:
        days = workdays(start, end)
        lines.append(f"- **Фаза {phase_id}** ({phase_name}): {len(days)} р.д., {fmt(days[0])} – {fmt(days[-1])}")

    lines.extend(["", "---", ""])

    for phase_id, phase_name, start, end, static_plans, dynamic in PHASES:
        days = workdays(start, end)
        lines.append(f"## Фаза {phase_id}: {phase_name}")
        lines.append("")
        lines.append(f"**Период:** {fmt(days[0])} – {fmt(days[-1])} ({len(days)} рабочих дней)")
        lines.append("")

        for i, d in enumerate(days):
            if static_plans:
                plan = static_plans[i] if i < len(static_plans) else static_plans[-1]
            elif dynamic == "phase2":
                plan = phase2_day(i, len(days), d)
            elif dynamic == "phase3":
                plan = phase3_day(i, d)
            elif dynamic == "phase4":
                plan = phase4_day(i, d)
            else:
                plan = phase5_day(i, d)
            lines.append(render_day(phase_id, phase_name, i + 1, len(days), d, plan))

    lines.extend(
        [
            "## Приложение A: Gate-критерии (кратко)",
            "",
            "### Gate 0 → Регресс",
            "- [ ] Тест-план утверждён, smoke green",
            "- [ ] QA-контур стабилен, build tagged",
            "- [ ] Security baseline без Critical",
            "",
            "### Gate 1 → RC",
            "- [ ] P0 = 0, P1 ≤ 3 (waiver documented)",
            "- [ ] Тест-план ≥ 98% выполнен",
            "- [ ] RC1 candidate на staging",
            "",
            "### Gate 2 → Предтрансфер",
            "- [ ] UAT sign-off PO",
            "- [ ] Perf в пределах SLO vs 14.0",
            "- [ ] Runbook + rollback проверены",
            "",
            "### Gate 3 → Трансфер",
            "- [ ] CAB approved",
            "- [ ] Pre-prod smoke green",
            "- [ ] On-call и war room готовы",
            "",
            "### Gate 4 → Go-Live",
            "- [ ] Prod stable 48 ч",
            "- [ ] Critical/High CVE = 0",
            "- [ ] Post-deploy smoke 100%",
            "",
            "### Gate 5 → BAU",
            "- [ ] Нет открытых P0 prod",
            "- [ ] Ретро проведена",
            "- [ ] Артефакты архивированы",
            "",
        ]
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
