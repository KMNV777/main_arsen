# Релиз 14.1 — дневной план (QA / DevOps / Security)

> Документ сгенерирован для сквозного управления релизом. Каждый рабочий день содержит чеклисты трёх функций.

## Ключевые вехи

| Веха | Дата |
|------|------|
| Старт регресса | 15.05.2025 |
| Gate 1 (конец регресса) | 05.06.2025 |
| Gate 2 (RC принят) | 04.07.2025 |
| Gate 3 (Go на трансфер) | 07.08.2025 |
| Старт трансфера | 08.08.2025 |
| Gate 4 (конец трансфера) | 27.08.2025 |
| Go-Live | 28.08.2025 |
| Закрытие релиза | 10.09.2025 |

## Условные обозначения

- **P0** — блокер релиза, SLA фикса 24 ч, ретест 1 р.д.
- **P1** — критичный, SLA 48 ч
- **Gate** — формальная точка Go/No-Go с протоколом
- Чеклисты отмечать `[x]` по факту выполнения

## Сводка по фазам

- **Фаза 0** (Подготовка к регрессу): 9 р.д., 28.04.2025 – 14.05.2025
- **Фаза 1** (Регресс и стабилизация): 16 р.д., 15.05.2025 – 05.06.2025
- **Фаза 2** (RC и приёмка): 19 р.д., 06.06.2025 – 04.07.2025
- **Фаза 3** (Предтрансферная готовность): 24 р.д., 07.07.2025 – 07.08.2025
- **Фаза 4** (Трансфер и уязвимости): 14 р.д., 08.08.2025 – 27.08.2025
- **Фаза 5** (Go-Live и пострелиз): 10 р.д., 28.08.2025 – 10.09.2025

---

## Фаза 0: Подготовка к регрессу

**Период:** 28.04.2025 – 14.05.2025 (9 рабочих дней)

### 28.04.2025 — Фаза 0, D01/09: Kick-off подготовки: scope lock и ветка релиза

**QA**
- [ ] Провести ревью scope 14.1 с PO, зафиксировать in/out of scope
- [ ] Сверить тест-план с backlog релиза, выявить пробелы покрытия
- [ ] Подготовить матрицу трассируемости: фича → ТК → owner
- [ ] Согласовать критерии severity (P0–P3) на период регресса

**DevOps**
- [ ] Создать ветку `release/14.1` от стабильного коммита main
- [ ] Настроить CI pipeline для release-ветки (build + unit + lint)
- [ ] Подготовить QA-контур: деплой последнего зелёного билда
- [ ] Зафиксировать версию артефакта (semver/tag) в реестре билдов

**Security**
- [ ] Получить baseline SBOM для целевого билда
- [ ] Согласовать политику: какие CVE блокируют регресс (Critical/High)
- [ ] Запросить список обязательных security-контролов для 14.1

---

### 29.04.2025 — Фаза 0, D02/09: Актуализация тестовой документации

**QA**
- [ ] Обновить/создать ТК по новым фичам 14.1
- [ ] Провести peer-review ТК с аналитиком/PO
- [ ] Подготовить smoke-набор (≤ 2 ч прогона)
- [ ] Подготовить regression suite: приоритет P0-сценариев

**DevOps**
- [ ] Проверить доступность тестовых данных и фикстур в QA
- [ ] Настроить автотесты на release-ветку в CI
- [ ] Проверить секреты/токены QA-контура (rotation, expiry)
- [ ] Задокументировать URL/доступы к QA для команды

**Security**
- [ ] Проверить, что QA-контур не содержит prod-секретов
- [ ] Валидировать политики доступа к тестовым средам (RBAC)
- [ ] Зафиксировать требования к маскированию PII в тест-логах

---

### 30.04.2025 — Фаза 0, D03/09: Готовность тест-плана и окружений

**QA**
- [ ] Финализировать тест-план 14.1 (версия 1.0)
- [ ] Разбить ТК по исполнителям и дням регресса (W1–W3)
- [ ] Подготовить шаблон bug report и SLA на ретест
- [ ] Провести dry-run smoke на QA (пилотный прогон)

**DevOps**
- [ ] Верифицировать parity QA vs staging (версии сервисов, конфиги)
- [ ] Настроить алерты на падение QA-контура в период регресса
- [ ] Подготовить скрипт быстрого redeploy QA из release-ветки
- [ ] Проверить лимиты/квоты CI для параллельных прогонов

**Security**
- [ ] SAST quick-scan release-ветки (информативный, без блокера)
- [ ] Проверить зависимости с известными CVE (предварительный список)
- [ ] Согласовать процесс эскалации security-дефектов в регрессе

---

### 05.05.2025 — Фаза 0, D04/09: Синхронизация после майских праздников

**QA**
- [ ] Актуализировать статус ТК после ревью праздничного периода
- [ ] Провести sync с Dev: список рискованных областей кода
- [ ] Подтвердить готовность smoke и regression наборов
- [ ] Подготовить dashboard метрик регресса (burn-down шаблон)

**DevOps**
- [ ] Redeploy QA с актуальным коммитом release/14.1
- [ ] Проверить health всех зависимостей QA (DB, MQ, cache)
- [ ] Зафиксировать snapshot конфигов QA на старт регресса
- [ ] Подготовить runbook hotfix-деплоя в QA

**Security**
- [ ] Повторный dependency scan после обновления lockfile
- [ ] Проверить audit log доступа к release-репозиторию
- [ ] Подтвердить контакты security on-call на период регресса

---

### 06.05.2025 — Фаза 0, D05/09: Финальная ревизия тест-артефактов

**QA**
- [ ] Sign-off тест-плана от QA Lead
- [ ] Провести walkthrough тест-плана с Dev и PO
- [ ] Зафиксировать entry criteria для старта регресса 15.05
- [ ] Подготовить чеклист Gate 0

**DevOps**
- [ ] Финальный build candidate в QA, тег `14.1-regression-candidate`
- [ ] Проверить артефакт: checksum, подпись, reproducibility
- [ ] Убедиться в rollback QA на предыдущую версию ≤ 15 мин
- [ ] Забронировать окна CI/CD на период регресса

**Security**
- [ ] Подтвердить security entry criteria для Gate 0
- [ ] Проверить отсутствие hardcoded credentials в release-ветке (gitleaks)
- [ ] Задокументировать известные accepted risks (если есть)

---

### 07.05.2025 — Фаза 0, D06/09: Репетиция процессов регресса

**QA**
- [ ] Провести tabletop: сценарий P0-бага в регрессе
- [ ] Отрепетировать процесс ретеста и reopen
- [ ] Проверить интеграцию с bug tracker (workflow, поля)
- [ ] Назначить дежурного QA на daily standup регресса

**DevOps**
- [ ] Репетиция hotfix pipeline: commit → build → QA deploy
- [ ] Проверить время цикла hotfix (target ≤ 4 ч)
- [ ] Настроить уведомления Slack/Teams для падений CI
- [ ] Подготовить capacity plan (параллельные деплои)

**Security**
- [ ] Репетиция эскалации: CVE обнаружен в зависимости mid-regression
- [ ] Проверить SLA security review для hotfix
- [ ] Обновить security contact list в runbook

---

### 12.05.2025 — Фаза 0, D07/09: Стабилизация QA-данных и автотестов

**QA**
- [ ] Заморозить тестовые данные baseline для регресса
- [ ] Прогнать автотесты P0, зафиксировать pass rate baseline
- [ ] Подготовить список flaky-тестов и план стабилизации
- [ ] Сверить автотесты с ручными ТК (нет дублирования пробелов)

**DevOps**
- [ ] Стабилизировать flaky jobs в CI (retry policy, quarantine)
- [ ] Проверить nightly regression job расписание на период 15.05–05.06
- [ ] Backup QA DB / state перед регрессом
- [ ] Документировать restore procedure QA

**Security**
- [ ] Scan тестовых данных на реальный PII (должен быть синтетический)
- [ ] Проверить шифрование backup QA
- [ ] Валидировать network policies QA (нет лишних ingress)

---

### 13.05.2025 — Фаза 0, D08/09: Cross-team readiness review

**QA**
- [ ] Провести readiness review с Dev, PO, Release Manager
- [ ] Закрыть открытые вопросы по ТК и тест-данным
- [ ] Подтвердить roster QA на 16 дней регресса
- [ ] Разослать calendar invites: daily standup 15.05–05.06

**DevOps**
- [ ] Cross-team readiness: DevOps подтверждает QA green
- [ ] Проверить on-call ротацию DevOps на регресс
- [ ] Финальный smoke всех микросервисов 14.1 в QA
- [ ] Подготовить release dashboard (build, deploy, health)

**Security**
- [ ] Security readiness: подтвердить процесс для регресса
- [ ] Финальный gitleaks + secret scan release-ветки
- [ ] Gate 0 pre-check: нет открытых Critical security findings

---

### 14.05.2025 — Фаза 0, D09/09: Gate 0 — Go на регресс

**QA**
- [ ] Провести Gate 0 meeting, заполнить протокол
- [ ] Опубликовать стартовый билд и тест-план команде
- [ ] Разослать kick-off note: правила, SLA, контакты
- [ ] Подтвердить freeze scope — change только через CAB

**DevOps**
- [ ] Gate 0: QA-контур стабилен 24+ ч
- [ ] Зафиксировать build ID для D01 регресса
- [ ] Включить enhanced monitoring QA на период регресса
- [ ] Подтвердить hotfix channel (#release-14-1-hotfix)

**Security**
- [ ] Gate 0 sign-off Security: baseline принят
- [ ] Зафиксировать SBOM v0 в release folder
- [ ] Передать QA список security-sensitive областей для приоритетного теста

---

## Фаза 1: Регресс и стабилизация

**Период:** 15.05.2025 – 05.06.2025 (16 рабочих дней)

### 15.05.2025 — Фаза 1, D01/16: Регресс: старт — smoke и начало прогона

**QA**
- [ ] Выполнить smoke-набор на стартовом билде (100%)
- [ ] Начать прогон P0 ТК (цель дня: ≥ 30% P0)
- [ ] Заводить баги с severity, steps, logs, build ID
- [ ] Daily standup: blockers, burn-down

**DevOps**
- [ ] Подтвердить деплой стартового билда в QA
- [ ] Мониторинг QA: error rate, latency baseline
- [ ] Готовность hotfix deploy в течение 4 ч
- [ ] Логировать все деплои в release journal

**Security**
- [ ] Мониторинг security alerts на QA
- [ ] Проверить нет аномального трафика/сканирования QA
- [ ] Быстрый triage если найден security defect в smoke

---

### 16.05.2025 — Фаза 1, D02/16: Регресс: продолжение P0

**QA**
- [ ] Продолжить P0 ТК (накопительно ≥ 50%)
- [ ] Ретест закрытых багов вчера (если были фиксы)
- [ ] Актуализировать ТК при расхождении с фактическим поведением
- [ ] Triage новых багов с Dev (P0 first)

**DevOps**
- [ ] Деплой hotfix-билдов по мере готовности
- [ ] Проверить post-deploy health после каждого hotfix
- [ ] Обновлять build registry после каждого деплоя
- [ ] CI: не допускать merge без green checks

**Security**
- [ ] Review security-related багов из вчера
- [ ] Dependency diff после hotfix — новые CVE?
- [ ] Документировать security defects в отдельном трекере

---

### 19.05.2025 — Фаза 1, D03/16: Регресс W1: основной прогон

**QA**
- [ ] Прогон P0 + начало P1 ТК
- [ ] Цель: ≥ 70% P0 пройдено
- [ ] Проверить критичные интеграции (API, auth, payments)
- [ ] Обновить burn-down chart

**DevOps**
- [ ] Поддерживать QA uptime ≥ 99%
- [ ] Синхронизировать версии зависимых сервисов
- [ ] Проверить логирование достаточно для дебага багов
- [ ] Capacity: параллельные env для QA при необходимости

**Security**
- [ ] Проверить auth/session flows на OWASP top misconfig
- [ ] Валидировать TLS/certs на QA endpoints
- [ ] Spot-check логи на утечку sensitive data

---

### 20.05.2025 — Фаза 1, D04/16: Регресс W1: интеграции и edge cases

**QA**
- [ ] ТК на интеграции и граничные случаи
- [ ] Exploratory testing по риск-областям от Dev
- [ ] Ретест P0 фиксов (SLA 1 р.д.)
- [ ] Начать доводку фичей — regression на changed areas

**DevOps**
- [ ] Hotfix deploy + DB migration check если есть
- [ ] Verify rollback одного hotfix на QA (drill)
- [ ] Мониторинг resource usage QA под нагрузкой тестов
- [ ] Snapshot QA state EOD для воспроизводимости

**Security**
- [ ] Review RBAC: роли и permissions в новых фичах
- [ ] Проверить rate limiting на публичных API
- [ ] Triage security bugs: P0 security = блокер релиза

---

### 21.05.2025 — Фаза 1, D05/16: Регресс W1: закрытие недели

**QA**
- [ ] Завершить оставшиеся P0 ТК W1
- [ ] Начать P1 bulk прогон
- [ ] Weekly mini Go/No-Go: статус P0/P1
- [ ] Актуализировать ТК по итогам недели

**DevOps**
- [ ] Weekly infra report: incidents, MTTR
- [ ] Очистка старых билдов QA (retention policy)
- [ ] Проверить автотесты nightly — анализ падений
- [ ] План hotfix окон на W2

**Security**
- [ ] Weekly security sync: открытые security defects
- [ ] SAST incremental scan на коммиты недели
- [ ] Обновить risk register

---

### 22.05.2025 — Фаза 1, D06/16: Регресс W1 финал / W2 старт

**QA**
- [ ] Догнать просроченные P0 ТК
- [ ] Фокус на P1 + ретест накопленных фиксов
- [ ] Проверить фичи 14.1 end-to-end user journeys
- [ ] Документировать known issues (не P0)

**DevOps**
- [ ] Стабильный билд EOD — tag `14.1-regression-w1`
- [ ] Проверить миграции applied correctly
- [ ] Verify feature flags state в QA
- [ ] Подготовить changelog коммитов W1

**Security**
- [ ] Проверить security fixes из W1 merged
- [ ] Validate input sanitization на новых формах/API
- [ ] Проверить CORS/CSP headers если applicable

---

### 23.05.2025 — Фаза 1, D07/16: Регресс W2: фиксация P0/P1

**QA**
- [ ] Приоритет: все открытые P0 должны быть в работе
- [ ] Ретест всех P0 фиксов за 24 ч
- [ ] Продолжить P1 прогон (цель ≥ 50% P1)
- [ ] Актуализация ТК для изменённых фиксами областей

**DevOps**
- [ ] Ускоренный hotfix pipeline — target 2–4 ч
- [ ] Post-deploy automated smoke в CI после hotfix
- [ ] Мониторинг regression test parallelization
- [ ] Alert на любой failed deployment

**Security**
- [ ] Security review каждого P0 hotfix (threat check)
- [ ] Проверить нет bypass auth в фиксах
- [ ] SCA scan после обновления зависимостей

---

### 26.05.2025 — Фаза 1, D08/16: Регресс W2: доводка фичей

**QA**
- [ ] Regression на доведённых фичах (full path)
- [ ] P1 ТК + начало P2 по capacity
- [ ] Verify fix quality — нет reopen P0
- [ ] Sync с PO: scope cuts если P0 не закрываются

**DevOps**
- [ ] Deploy доводок фичей, verify config changes
- [ ] Проверить backward compatibility settings
- [ ] Load test light на QA (sanity)
- [ ] Document config diffs для staging/prod

**Security**
- [ ] Review feature flags security (нет exposed admin)
- [ ] Audit new API endpoints — auth required?
- [ ] Check secrets not in env dumps/logs

---

### 27.05.2025 — Фаза 1, D09/16: Регресс W2: стабилизация

**QA**
- [ ] Цель: P0 open = 0 или с approved waiver
- [ ] Ретест всех P1 фиксов недели
- [ ] Пройти тест-план: накопительно ≥ 85%
- [ ] Подготовить список к Gate 1 mid-check

**DevOps**
- [ ] Freeze non-critical infra changes в QA
- [ ] Стабильный билд — минимум деплоев
- [ ] Verify data integrity после серии фиксов
- [ ] Backup QA EOD

**Security**
- [ ] Mid-regression security checkpoint
- [ ] Сверить open security bugs vs gate criteria
- [ ] Pen-test lite на изменённые endpoints (если есть capacity)

---

### 28.05.2025 — Фаза 1, D10/16: Регресс W2: тест-план coverage

**QA**
- [ ] Догнать оставшиеся P1 ТК
- [ ] Exploratory на areas с высоким churn
- [ ] Ретест regression по fixed modules
- [ ] Обновить test completion report

**DevOps**
- [ ] Tag `14.1-regression-w2` на стабильном билде
- [ ] CI green на release branch обязателен
- [ ] Подготовить RC branch criteria checklist
- [ ] Changelog W2 для Release Notes

**Security**
- [ ] DAST scan на QA (scheduled window)
- [ ] Triage DAST findings — false positive review
- [ ] Обновить SBOM после W2 merges

---

### 29.05.2025 — Фаза 1, D11/16: Регресс W2: pre-Gate 1

**QA**
- [ ] Полный ретест всех open P1
- [ ] Sanity full smoke
- [ ] Подготовить Gate 1 пакет: metrics, bugs, risks
- [ ] Confirm test plan ≥ 95% executed

**DevOps**
- [ ] Pre-Gate 1: QA stable 48h target начинается
- [ ] Minimize deploys — только P0/P1 blockers
- [ ] Verify artifact reproducibility
- [ ] Prepare RC build pipeline parameters

**Security**
- [ ] Pre-Gate 1 security pack: SAST+DAST summary
- [ ] Confirm zero open Critical security
- [ ] Document any High with mitigation plan

---

### 30.05.2025 — Фаза 1, D12/16: Регресс W2: буфер / догон

**QA**
- [ ] Буферный день: закрыть хвосты P1
- [ ] Финальный ретест спорных багов
- [ ] Sign-off ТК актуальности от QA owners
- [ ] Доводка фичей — last mile bugs only

**DevOps**
- [ ] Буфер: стабилизация, no experimental changes
- [ ] Final W2 backup QA
- [ ] RC build dry-run (без публикации)
- [ ] Staging deploy rehearsal plan

**Security**
- [ ] Буфер: закрыть security findings High
- [ ] Re-scan после последних фиксов
- [ ] Security sign-off draft для Gate 1

---

### 02.06.2025 — Фаза 1, D13/16: Регресс W3: финальный спринт старт

**QA**
- [ ] Финальный прогон оставшихся ТК (100% target)
- [ ] Full regression на critical paths
- [ ] Zero tolerance P0 — escalate immediately
- [ ] Подготовить UAT handoff package

**DevOps**
- [ ] Подготовить RC1 build environment
- [ ] Staging parity check начать
- [ ] Freeze dependency updates (except security)
- [ ] Document exact commit SHA for RC

**Security**
- [ ] Final security regression checklist start
- [ ] Verify encryption at rest/transit unchanged
- [ ] Review admin/privileged flows

---

### 03.06.2025 — Фаза 1, D14/16: Регресс W3: финальный ретест

**QA**
- [ ] Ретест 100% fixed bugs since D01
- [ ] Confirm P0=0, P1≤3 (waiver documented)
- [ ] Final smoke + sanity на freeze candidate
- [ ] Archive test evidence (screenshots, logs)

**DevOps**
- [ ] Build RC1 candidate overnight ready
- [ ] Staging deploy RC1 candidate (evening/next AM)
- [ ] Smoke automation on RC1
- [ ] Tag `14.1-rc1-candidate`

**Security**
- [ ] Full SAST on RC1 candidate branch
- [ ] SCA full scan RC1
- [ ] Gate 1 security pre-approval package

---

### 04.06.2025 — Фаза 1, D15/16: Регресс W3: Gate 1 prep

**QA**
- [ ] Финальный отчёт: test plan execution 98%+
- [ ] Gate 1 checklist complete
- [ ] Handoff notes для RC phase
- [ ] Retrospective quick: что улучшить в 14.2

**DevOps**
- [ ] RC1 deploy to staging
- [ ] Staging health verification
- [ ] Rollback staging drill
- [ ] Release journal: regression complete entry

**Security**
- [ ] Security Gate 1 attendance prepared
- [ ] Final CVE list for RC1
- [ ] Sign-off memo draft

---

### 05.06.2025 — Фаза 1, D16/16: Gate 1 — завершение регресса

**QA**
- [ ] Gate 1 meeting + протокол Go
- [ ] Freeze test evidence в release folder
- [ ] Communicate regression complete to stakeholders
- [ ] Transition checklist to RC phase

**DevOps**
- [ ] Gate 1: promote build to RC1 official
- [ ] Lock QA to RC1 SHA
- [ ] Enable staging monitoring dashboards
- [ ] Announce code freeze effective next phase

**Security**
- [ ] Gate 1 Security sign-off (или waiver list)
- [ ] Archive SBOM regression-final
- [ ] Handoff security watchlist для RC

---

## Фаза 2: RC и приёмка

**Период:** 06.06.2025 – 04.07.2025 (19 рабочих дней)

### 06.06.2025 — Фаза 2, D01/19: Hard Code Freeze + RC1 официальный

**QA**
- [ ] Smoke RC1 на staging (100%)
- [ ] Verify RC1 = Gate 1 approved SHA
- [ ] Начать UAT smoke с PO
- [ ] Заморозить ТК — изменения только via CR

**DevOps**
- [ ] Официальный RC1 tag `14.1-rc1`
- [ ] Deploy RC1 staging + pre-prod mirror
- [ ] Disable auto-deploy from release branch без approval
- [ ] Archive RC1 artifacts (signed)

**Security**
- [ ] RC1 full SAST gate — Critical = 0
- [ ] SCA gate — no new Critical CVE
- [ ] Document RC1 security baseline

---

### 09.06.2025 — Фаза 2, D02/19: UAT старт — бизнес-сценарии

**QA**
- [ ] UAT Day 1: critical business flows с PO
- [ ] Document UAT defects (severity)
- [ ] Sanity automation on staging
- [ ] Support PO during UAT sessions

**DevOps**
- [ ] Staging stability monitoring
- [ ] UAT support: quick env refresh if needed
- [ ] Log all UAT environment changes
- [ ] Prepare hotfix window for UAT blockers

**Security**
- [ ] Monitor UAT access — least privilege
- [ ] Review UAT data handling
- [ ] Security standby for UAT escalations

---

### 10.06.2025 — Фаза 2, D03/19: UAT продолжение (день 2)

**QA**
- [ ] UAT сценарии по test script PO
- [ ] Ретест UAT blockers (P0/P1)
- [ ] Regression spot-check после UAT fixes
- [ ] UAT sign-off progress tracker update

**DevOps**
- [ ] Deploy UAT fixes to staging only
- [ ] Maintain staging = RC + approved hotfixes
- [ ] Daily staging health report
- [ ] Pre-prod sync if UAT requires

**Security**
- [ ] Review UAT hotfixes security
- [ ] Incremental scan on UAT fixes
- [ ] Track security UAT observations

---

### 11.06.2025 — Фаза 2, D04/19: UAT продолжение (день 3)

**QA**
- [ ] UAT сценарии по test script PO
- [ ] Ретест UAT blockers (P0/P1)
- [ ] Regression spot-check после UAT fixes
- [ ] UAT sign-off progress tracker update

**DevOps**
- [ ] Deploy UAT fixes to staging only
- [ ] Maintain staging = RC + approved hotfixes
- [ ] Daily staging health report
- [ ] Pre-prod sync if UAT requires

**Security**
- [ ] Review UAT hotfixes security
- [ ] Incremental scan on UAT fixes
- [ ] Track security UAT observations

---

### 16.06.2025 — Фаза 2, D05/19: UAT mid-point review

**QA**
- [ ] UAT mid-review с PO: coverage %
- [ ] Prioritize remaining UAT gaps
- [ ] Performance sanity scripts run
- [ ] Update release notes draft

**DevOps**
- [ ] Staging perf baseline capture
- [ ] Check autoscaling under UAT load
- [ ] Infra capacity note for prod
- [ ] RC1 changelog update

**Security**
- [ ] Mid-UAT security checkpoint
- [ ] Review access logs staging
- [ ] Confirm no prod data in UAT

---

### 17.06.2025 — Фаза 2, D06/19: UAT + стабилизация RC (день 1)

**QA**
- [ ] Continue UAT + defect retest
- [ ] Exploratory on payment/auth flows
- [ ] Automated regression on staging nightly review
- [ ] P2/P3 triage — defer post-release if ok

**DevOps**
- [ ] Nightly staging deploy only if hotfix
- [ ] Monitor error budgets staging
- [ ] DB migration verify on staging
- [ ] Document config for prod

**Security**
- [ ] Daily incremental security scan
- [ ] Triage new CVE in dependencies
- [ ] Update vulnerability register

---

### 18.06.2025 — Фаза 2, D07/19: UAT + стабилизация RC (день 2)

**QA**
- [ ] Continue UAT + defect retest
- [ ] Exploratory on payment/auth flows
- [ ] Automated regression on staging nightly review
- [ ] P2/P3 triage — defer post-release if ok

**DevOps**
- [ ] Nightly staging deploy only if hotfix
- [ ] Monitor error budgets staging
- [ ] DB migration verify on staging
- [ ] Document config for prod

**Security**
- [ ] Daily incremental security scan
- [ ] Triage new CVE in dependencies
- [ ] Update vulnerability register

---

### 19.06.2025 — Фаза 2, D08/19: UAT + стабилизация RC (день 3)

**QA**
- [ ] Continue UAT + defect retest
- [ ] Exploratory on payment/auth flows
- [ ] Automated regression on staging nightly review
- [ ] P2/P3 triage — defer post-release if ok

**DevOps**
- [ ] Nightly staging deploy only if hotfix
- [ ] Monitor error budgets staging
- [ ] DB migration verify on staging
- [ ] Document config for prod

**Security**
- [ ] Daily incremental security scan
- [ ] Triage new CVE in dependencies
- [ ] Update vulnerability register

---

### 20.06.2025 — Фаза 2, D09/19: UAT + стабилизация RC (день 4)

**QA**
- [ ] Continue UAT + defect retest
- [ ] Exploratory on payment/auth flows
- [ ] Automated regression on staging nightly review
- [ ] P2/P3 triage — defer post-release if ok

**DevOps**
- [ ] Nightly staging deploy only if hotfix
- [ ] Monitor error budgets staging
- [ ] DB migration verify on staging
- [ ] Document config for prod

**Security**
- [ ] Daily incremental security scan
- [ ] Triage new CVE in dependencies
- [ ] Update vulnerability register

---

### 23.06.2025 — Фаза 2, D10/19: Нагрузочное тестирование — старт

**QA**
- [ ] Execute load test plan on staging
- [ ] Monitor SLO: latency, error rate, throughput
- [ ] Compare vs 14.0 baseline
- [ ] Log perf defects

**DevOps**
- [ ] Load test infra: scale staging appropriately
- [ ] APM dashboards for load test
- [ ] Capture infra metrics (CPU, memory, IO)
- [ ] Ensure no impact on other envs

**Security**
- [ ] Security during load: no auth bypass under stress
- [ ] Rate limit behavior validation
- [ ] DDoS protection rules review

---

### 24.06.2025 — Фаза 2, D11/19: Perf + RC стабилизация (день 1)

**QA**
- [ ] Perf test analysis + retest fixes
- [ ] Full regression staging после perf fixes
- [ ] UAT final scenarios
- [ ] Prepare RC2 criteria (if needed)

**DevOps**
- [ ] Tune staging after perf findings
- [ ] RC2 build prep if RC1 insufficient
- [ ] Prod-like config validation
- [ ] Migration timing benchmarks

**Security**
- [ ] Scan RC after perf-related changes
- [ ] Verify TLS performance config secure
- [ ] Review cache security headers

---

### 25.06.2025 — Фаза 2, D12/19: Perf + RC стабилизация (день 2)

**QA**
- [ ] Perf test analysis + retest fixes
- [ ] Full regression staging после perf fixes
- [ ] UAT final scenarios
- [ ] Prepare RC2 criteria (if needed)

**DevOps**
- [ ] Tune staging after perf findings
- [ ] RC2 build prep if RC1 insufficient
- [ ] Prod-like config validation
- [ ] Migration timing benchmarks

**Security**
- [ ] Scan RC after perf-related changes
- [ ] Verify TLS performance config secure
- [ ] Review cache security headers

---

### 26.06.2025 — Фаза 2, D13/19: Perf + RC стабилизация (день 3)

**QA**
- [ ] Perf test analysis + retest fixes
- [ ] Full regression staging после perf fixes
- [ ] UAT final scenarios
- [ ] Prepare RC2 criteria (if needed)

**DevOps**
- [ ] Tune staging after perf findings
- [ ] RC2 build prep if RC1 insufficient
- [ ] Prod-like config validation
- [ ] Migration timing benchmarks

**Security**
- [ ] Scan RC after perf-related changes
- [ ] Verify TLS performance config secure
- [ ] Review cache security headers

---

### 27.06.2025 — Фаза 2, D14/19: RC2 decision point

**QA**
- [ ] RC1 vs RC2 Go/No-Go
- [ ] If RC2: full smoke RC2
- [ ] UAT sign-off draft from PO
- [ ] Finalize test summary report

**DevOps**
- [ ] Build RC2 if required, tag `14.1-rc2`
- [ ] Deploy RC2 staging, archive RC1
- [ ] Update artifact registry
- [ ] Changelog RC1→RC2

**Security**
- [ ] RC2 full security scan if built
- [ ] Compare CVE delta RC1→RC2
- [ ] Security approval RC2

---

### 30.06.2025 — Фаза 2, D15/19: Документация и security baseline (день 1)

**QA**
- [ ] Support release notes verification
- [ ] Final staging regression P0 paths
- [ ] Sign-off test summary QA Lead
- [ ] Handoff package для pre-transfer

**DevOps**
- [ ] Finalize runbook deploy 14.1
- [ ] Finalize rollback runbook + drill
- [ ] Pre-prod deploy RC final
- [ ] Prod deploy rehearsal checklist

**Security**
- [ ] Security baseline scan (SAST+DAST+SCA)
- [ ] Produce CVE report for transfer phase
- [ ] Prioritize Critical/High for phase 4
- [ ] Gate 2 security pre-check

---

### 01.07.2025 — Фаза 2, D16/19: Документация и security baseline (день 2)

**QA**
- [ ] Support release notes verification
- [ ] Final staging regression P0 paths
- [ ] Sign-off test summary QA Lead
- [ ] Handoff package для pre-transfer

**DevOps**
- [ ] Finalize runbook deploy 14.1
- [ ] Finalize rollback runbook + drill
- [ ] Pre-prod deploy RC final
- [ ] Prod deploy rehearsal checklist

**Security**
- [ ] Security baseline scan (SAST+DAST+SCA)
- [ ] Produce CVE report for transfer phase
- [ ] Prioritize Critical/High for phase 4
- [ ] Gate 2 security pre-check

---

### 02.07.2025 — Фаза 2, D17/19: Документация и security baseline (день 3)

**QA**
- [ ] Support release notes verification
- [ ] Final staging regression P0 paths
- [ ] Sign-off test summary QA Lead
- [ ] Handoff package для pre-transfer

**DevOps**
- [ ] Finalize runbook deploy 14.1
- [ ] Finalize rollback runbook + drill
- [ ] Pre-prod deploy RC final
- [ ] Prod deploy rehearsal checklist

**Security**
- [ ] Security baseline scan (SAST+DAST+SCA)
- [ ] Produce CVE report for transfer phase
- [ ] Prioritize Critical/High for phase 4
- [ ] Gate 2 security pre-check

---

### 03.07.2025 — Фаза 2, D18/19: Документация и security baseline (день 4)

**QA**
- [ ] Support release notes verification
- [ ] Final staging regression P0 paths
- [ ] Sign-off test summary QA Lead
- [ ] Handoff package для pre-transfer

**DevOps**
- [ ] Finalize runbook deploy 14.1
- [ ] Finalize rollback runbook + drill
- [ ] Pre-prod deploy RC final
- [ ] Prod deploy rehearsal checklist

**Security**
- [ ] Security baseline scan (SAST+DAST+SCA)
- [ ] Produce CVE report for transfer phase
- [ ] Prioritize Critical/High for phase 4
- [ ] Gate 2 security pre-check

---

### 04.07.2025 — Фаза 2, D19/19: Gate 2 — RC принят

**QA**
- [ ] Gate 2 meeting: UAT sign-off confirm
- [ ] QA handoff to pre-transfer checklist
- [ ] Archive all test artifacts
- [ ] Communicate RC accepted

**DevOps**
- [ ] Gate 2: lock RC final SHA `14.1-rc-final`
- [ ] Pre-prod = RC final, smoke green
- [ ] CAB packet technical appendix
- [ ] Freeze RC — only transfer-phase patches

**Security**
- [ ] Gate 2 Security sign-off
- [ ] Final SBOM `14.1-rc-final`
- [ ] Transfer-phase vulnerability backlog prioritized

---

## Фаза 3: Предтрансферная готовность

**Период:** 07.07.2025 – 07.08.2025 (24 рабочих дней)

### 07.07.2025 — Фаза 3, D01/24: Старт предтрансфера: CAB подача

**QA**
- [ ] Review pre-transfer QA checklist
- [ ] Verify RC final staging smoke
- [ ] Prepare prod validation test suite (post-deploy)
- [ ] Sync test window с DevOps prod deploy

**DevOps**
- [ ] Submit CAB / Change Request для prod
- [ ] Attach runbook, rollback, RC SHA
- [ ] Define prod maintenance window
- [ ] Pre-prod final sync with RC

**Security**
- [ ] Attach security baseline report to CAB
- [ ] List open High CVE with fix ETA
- [ ] CAB security review slot booked

---

### 08.07.2025 — Фаза 3, D02/24: Pre-prod hardening (день 2)

**QA**
- [ ] Execute pre-prod test suite
- [ ] Validate prod-like data scenarios (anonymized)
- [ ] Document post-deploy smoke for prod
- [ ] Train support on known issues

**DevOps**
- [ ] Pre-prod config parity with prod template
- [ ] Secrets rotation plan prod (if needed)
- [ ] DB migration dry-run #1 on prod copy
- [ ] Network/firewall rules verify prod path

**Security**
- [ ] Pre-prod penetration config review
- [ ] Verify WAF rules prod
- [ ] IAM roles prod least-privilege review

---

### 09.07.2025 — Фаза 3, D03/24: Pre-prod hardening (день 3)

**QA**
- [ ] Execute pre-prod test suite
- [ ] Validate prod-like data scenarios (anonymized)
- [ ] Document post-deploy smoke for prod
- [ ] Train support on known issues

**DevOps**
- [ ] Pre-prod config parity with prod template
- [ ] Secrets rotation plan prod (if needed)
- [ ] DB migration dry-run #1 on prod copy
- [ ] Network/firewall rules verify prod path

**Security**
- [ ] Pre-prod penetration config review
- [ ] Verify WAF rules prod
- [ ] IAM roles prod least-privilege review

---

### 10.07.2025 — Фаза 3, D04/24: Pre-prod hardening (день 4)

**QA**
- [ ] Execute pre-prod test suite
- [ ] Validate prod-like data scenarios (anonymized)
- [ ] Document post-deploy smoke for prod
- [ ] Train support on known issues

**DevOps**
- [ ] Pre-prod config parity with prod template
- [ ] Secrets rotation plan prod (if needed)
- [ ] DB migration dry-run #1 on prod copy
- [ ] Network/firewall rules verify prod path

**Security**
- [ ] Pre-prod penetration config review
- [ ] Verify WAF rules prod
- [ ] IAM roles prod least-privilege review

---

### 11.07.2025 — Фаза 3, D05/24: Pre-prod hardening (день 5)

**QA**
- [ ] Execute pre-prod test suite
- [ ] Validate prod-like data scenarios (anonymized)
- [ ] Document post-deploy smoke for prod
- [ ] Train support on known issues

**DevOps**
- [ ] Pre-prod config parity with prod template
- [ ] Secrets rotation plan prod (if needed)
- [ ] DB migration dry-run #1 on prod copy
- [ ] Network/firewall rules verify prod path

**Security**
- [ ] Pre-prod penetration config review
- [ ] Verify WAF rules prod
- [ ] IAM roles prod least-privilege review

---

### 14.07.2025 — Фаза 3, D06/24: Миграции и мониторинг (день 1)

**QA**
- [ ] Test migration rollback scenarios (QA/pre-prod)
- [ ] Define prod smoke ≤ 30 min checklist
- [ ] Canary test plan if applicable
- [ ] Support comms T-14 draft review

**DevOps**
- [ ] Migration dry-run #2 timed
- [ ] Setup prod release dashboards
- [ ] Alert thresholds prod (error, latency)
- [ ] War room bridge + calendar

**Security**
- [ ] Audit prod secrets in vault — no stale
- [ ] Verify audit logging prod enabled
- [ ] SIEM alerts for deploy window configured

---

### 15.07.2025 — Фаза 3, D07/24: Миграции и мониторинг (день 2)

**QA**
- [ ] Test migration rollback scenarios (QA/pre-prod)
- [ ] Define prod smoke ≤ 30 min checklist
- [ ] Canary test plan if applicable
- [ ] Support comms T-14 draft review

**DevOps**
- [ ] Migration dry-run #2 timed
- [ ] Setup prod release dashboards
- [ ] Alert thresholds prod (error, latency)
- [ ] War room bridge + calendar

**Security**
- [ ] Audit prod secrets in vault — no stale
- [ ] Verify audit logging prod enabled
- [ ] SIEM alerts for deploy window configured

---

### 16.07.2025 — Фаза 3, D08/24: Миграции и мониторинг (день 3)

**QA**
- [ ] Test migration rollback scenarios (QA/pre-prod)
- [ ] Define prod smoke ≤ 30 min checklist
- [ ] Canary test plan if applicable
- [ ] Support comms T-14 draft review

**DevOps**
- [ ] Migration dry-run #2 timed
- [ ] Setup prod release dashboards
- [ ] Alert thresholds prod (error, latency)
- [ ] War room bridge + calendar

**Security**
- [ ] Audit prod secrets in vault — no stale
- [ ] Verify audit logging prod enabled
- [ ] SIEM alerts for deploy window configured

---

### 17.07.2025 — Фаза 3, D09/24: Миграции и мониторинг (день 4)

**QA**
- [ ] Test migration rollback scenarios (QA/pre-prod)
- [ ] Define prod smoke ≤ 30 min checklist
- [ ] Canary test plan if applicable
- [ ] Support comms T-14 draft review

**DevOps**
- [ ] Migration dry-run #2 timed
- [ ] Setup prod release dashboards
- [ ] Alert thresholds prod (error, latency)
- [ ] War room bridge + calendar

**Security**
- [ ] Audit prod secrets in vault — no stale
- [ ] Verify audit logging prod enabled
- [ ] SIEM alerts for deploy window configured

---

### 18.07.2025 — Фаза 3, D10/24: Миграции и мониторинг (день 5)

**QA**
- [ ] Test migration rollback scenarios (QA/pre-prod)
- [ ] Define prod smoke ≤ 30 min checklist
- [ ] Canary test plan if applicable
- [ ] Support comms T-14 draft review

**DevOps**
- [ ] Migration dry-run #2 timed
- [ ] Setup prod release dashboards
- [ ] Alert thresholds prod (error, latency)
- [ ] War room bridge + calendar

**Security**
- [ ] Audit prod secrets in vault — no stale
- [ ] Verify audit logging prod enabled
- [ ] SIEM alerts for deploy window configured

---

### 21.07.2025 — Фаза 3, D11/24: CAB follow-up и rollback drills (день 1)

**QA**
- [ ] Review support playbook 14.1
- [ ] Finalize prod smoke assignments
- [ ] Feature flag rollout plan test
- [ ] Comms T-7 content QA review

**DevOps**
- [ ] Rollback drill on pre-prod (timed)
- [ ] Document RTO/RPO actuals
- [ ] On-call roster finalized
- [ ] Prod deploy artifact immutability verify

**Security**
- [ ] Security on-call roster transfer phase
- [ ] Verify incident response playbooks
- [ ] Patch staging for High CVE (prep)

---

### 22.07.2025 — Фаза 3, D12/24: CAB follow-up и rollback drills (день 2)

**QA**
- [ ] Review support playbook 14.1
- [ ] Finalize prod smoke assignments
- [ ] Feature flag rollout plan test
- [ ] Comms T-7 content QA review

**DevOps**
- [ ] Rollback drill on pre-prod (timed)
- [ ] Document RTO/RPO actuals
- [ ] On-call roster finalized
- [ ] Prod deploy artifact immutability verify

**Security**
- [ ] Security on-call roster transfer phase
- [ ] Verify incident response playbooks
- [ ] Patch staging for High CVE (prep)

---

### 23.07.2025 — Фаза 3, D13/24: CAB follow-up и rollback drills (день 3)

**QA**
- [ ] Review support playbook 14.1
- [ ] Finalize prod smoke assignments
- [ ] Feature flag rollout plan test
- [ ] Comms T-7 content QA review

**DevOps**
- [ ] Rollback drill on pre-prod (timed)
- [ ] Document RTO/RPO actuals
- [ ] On-call roster finalized
- [ ] Prod deploy artifact immutability verify

**Security**
- [ ] Security on-call roster transfer phase
- [ ] Verify incident response playbooks
- [ ] Patch staging for High CVE (prep)

---

### 24.07.2025 — Фаза 3, D14/24: CAB follow-up и rollback drills (день 4)

**QA**
- [ ] Review support playbook 14.1
- [ ] Finalize prod smoke assignments
- [ ] Feature flag rollout plan test
- [ ] Comms T-7 content QA review

**DevOps**
- [ ] Rollback drill on pre-prod (timed)
- [ ] Document RTO/RPO actuals
- [ ] On-call roster finalized
- [ ] Prod deploy artifact immutability verify

**Security**
- [ ] Security on-call roster transfer phase
- [ ] Verify incident response playbooks
- [ ] Patch staging for High CVE (prep)

---

### 25.07.2025 — Фаза 3, D15/24: CAB follow-up и rollback drills (день 5)

**QA**
- [ ] Review support playbook 14.1
- [ ] Finalize prod smoke assignments
- [ ] Feature flag rollout plan test
- [ ] Comms T-7 content QA review

**DevOps**
- [ ] Rollback drill on pre-prod (timed)
- [ ] Document RTO/RPO actuals
- [ ] On-call roster finalized
- [ ] Prod deploy artifact immutability verify

**Security**
- [ ] Security on-call roster transfer phase
- [ ] Verify incident response playbooks
- [ ] Patch staging for High CVE (prep)

---

### 28.07.2025 — Фаза 3, D16/24: Финальная готовность (день 1)

**QA**
- [ ] Comms T-7 sent, FAQ review
- [ ] Prod test data / accounts verify
- [ ] Go/No-Go dry-run agenda
- [ ] Handoff to transfer phase team

**DevOps**
- [ ] Prod infra pre-check: capacity, disks, certs
- [ ] Backup prod pre-deploy snapshot plan
- [ ] Immutable artifact in prod registry
- [ ] Deploy automation final test (dry-run)

**Security**
- [ ] CVE remediation sprints planning (phase 4)
- [ ] Pre-transfer vulnerability assign owners
- [ ] Security war room prep

---

### 29.07.2025 — Фаза 3, D17/24: Финальная готовность (день 2)

**QA**
- [ ] Comms T-7 sent, FAQ review
- [ ] Prod test data / accounts verify
- [ ] Go/No-Go dry-run agenda
- [ ] Handoff to transfer phase team

**DevOps**
- [ ] Prod infra pre-check: capacity, disks, certs
- [ ] Backup prod pre-deploy snapshot plan
- [ ] Immutable artifact in prod registry
- [ ] Deploy automation final test (dry-run)

**Security**
- [ ] CVE remediation sprints planning (phase 4)
- [ ] Pre-transfer vulnerability assign owners
- [ ] Security war room prep

---

### 30.07.2025 — Фаза 3, D18/24: Финальная готовность (день 3)

**QA**
- [ ] Comms T-7 sent, FAQ review
- [ ] Prod test data / accounts verify
- [ ] Go/No-Go dry-run agenda
- [ ] Handoff to transfer phase team

**DevOps**
- [ ] Prod infra pre-check: capacity, disks, certs
- [ ] Backup prod pre-deploy snapshot plan
- [ ] Immutable artifact in prod registry
- [ ] Deploy automation final test (dry-run)

**Security**
- [ ] CVE remediation sprints planning (phase 4)
- [ ] Pre-transfer vulnerability assign owners
- [ ] Security war room prep

---

### 31.07.2025 — Фаза 3, D19/24: Финальная готовность (день 4)

**QA**
- [ ] Comms T-7 sent, FAQ review
- [ ] Prod test data / accounts verify
- [ ] Go/No-Go dry-run agenda
- [ ] Handoff to transfer phase team

**DevOps**
- [ ] Prod infra pre-check: capacity, disks, certs
- [ ] Backup prod pre-deploy snapshot plan
- [ ] Immutable artifact in prod registry
- [ ] Deploy automation final test (dry-run)

**Security**
- [ ] CVE remediation sprints planning (phase 4)
- [ ] Pre-transfer vulnerability assign owners
- [ ] Security war room prep

---

### 01.08.2025 — Фаза 3, D20/24: Финальная готовность (день 5)

**QA**
- [ ] Comms T-7 sent, FAQ review
- [ ] Prod test data / accounts verify
- [ ] Go/No-Go dry-run agenda
- [ ] Handoff to transfer phase team

**DevOps**
- [ ] Prod infra pre-check: capacity, disks, certs
- [ ] Backup prod pre-deploy snapshot plan
- [ ] Immutable artifact in prod registry
- [ ] Deploy automation final test (dry-run)

**Security**
- [ ] CVE remediation sprints planning (phase 4)
- [ ] Pre-transfer vulnerability assign owners
- [ ] Security war room prep

---

### 04.08.2025 — Фаза 3, D21/24: Gate 3 preparation (день 1)

**QA**
- [ ] Comms T-1 draft
- [ ] Prod smoke team briefing
- [ ] Confirm no open P0/P1 on RC
- [ ] Gate 3 checklist complete

**DevOps**
- [ ] Final pre-prod smoke RC
- [ ] Prod window confirmation from CAB
- [ ] War room tech check
- [ ] Rollback artifacts staged

**Security**
- [ ] Gate 3 security checklist
- [ ] Confirm Critical CVE = 0 or explicit waiver
- [ ] Security briefing transfer team

---

### 05.08.2025 — Фаза 3, D22/24: Gate 3 preparation (день 2)

**QA**
- [ ] Comms T-1 draft
- [ ] Prod smoke team briefing
- [ ] Confirm no open P0/P1 on RC
- [ ] Gate 3 checklist complete

**DevOps**
- [ ] Final pre-prod smoke RC
- [ ] Prod window confirmation from CAB
- [ ] War room tech check
- [ ] Rollback artifacts staged

**Security**
- [ ] Gate 3 security checklist
- [ ] Confirm Critical CVE = 0 or explicit waiver
- [ ] Security briefing transfer team

---

### 06.08.2025 — Фаза 3, D23/24: Gate 3 preparation (день 3)

**QA**
- [ ] Comms T-1 draft
- [ ] Prod smoke team briefing
- [ ] Confirm no open P0/P1 on RC
- [ ] Gate 3 checklist complete

**DevOps**
- [ ] Final pre-prod smoke RC
- [ ] Prod window confirmation from CAB
- [ ] War room tech check
- [ ] Rollback artifacts staged

**Security**
- [ ] Gate 3 security checklist
- [ ] Confirm Critical CVE = 0 or explicit waiver
- [ ] Security briefing transfer team

---

### 07.08.2025 — Фаза 3, D24/24: Gate 3 — Go на трансфер 08.08

**QA**
- [ ] Gate 3 meeting + Go decision
- [ ] Publish prod smoke checklist final
- [ ] Team standby confirm transfer 08.08
- [ ] Archive pre-transfer evidence

**DevOps**
- [ ] Gate 3: prod deploy window locked
- [ ] Final artifact checksum to transfer team
- [ ] Enable prod enhanced monitoring (standby)
- [ ] Kick #release-14-1-transfer channel

**Security**
- [ ] Gate 3 Security Go
- [ ] Distribute prioritized CVE fix list phase 4
- [ ] Security joins war room 08.08

---

## Фаза 4: Трансфер и уязвимости

**Период:** 08.08.2025 – 27.08.2025 (14 рабочих дней)

### 08.08.2025 — Фаза 4, D01/14: Трансфер D01: pre-prod → prod (этап 1)

**QA**
- [ ] Pre-deploy prod smoke baseline (if prod prev version)
- [ ] Standby war room — QA
- [ ] Prepare post-deploy smoke scripts
- [ ] Verify test accounts prod ready

**DevOps**
- [ ] Execute deploy runbook step 1–N (pre-prod validated)
- [ ] Prod deploy phase 1 per runbook
- [ ] Monitor deploy metrics live
- [ ] Checkpoint: rollback decision point 1

**Security**
- [ ] Security war room active
- [ ] Monitor SIEM during deploy
- [ ] Verify no unauthorized deploy activity
- [ ] Block deploy if Critical CVE unfixed (policy)

---

### 11.08.2025 — Фаза 4, D02/14: Трансфер D02: prod deploy продолжение

**QA**
- [ ] Post-deploy smoke phase 1 (critical paths)
- [ ] Log any prod anomalies as incidents
- [ ] Compare prod vs staging behavior
- [ ] Retest hotfix if deploy patch applied

**DevOps**
- [ ] Deploy phase 2 services / DB migrations
- [ ] Migration progress monitoring
- [ ] Checkpoint rollback 2
- [ ] Update release journal real-time

**Security**
- [ ] Validate auth flows prod post-deploy
- [ ] Check cert/TLS post-migration
- [ ] Scan prod surface (passive) for misconfig

---

### 12.08.2025 — Фаза 4, D03/14: Трансфер D03: стабилизация prod (день 1)

**QA**
- [ ] Expanded prod smoke (full checklist)
- [ ] Monitor user-reported issues channel
- [ ] Regression prod hotfixes only
- [ ] Daily prod health report

**DevOps**
- [ ] Complete remaining deploy steps
- [ ] Tune prod autoscaling post-deploy
- [ ] Verify backups post-migration
- [ ] Hotfix deploy to prod if P0

**Security**
- [ ] CVE remediation batch 1: assign + track
- [ ] Patch Critical/High dependencies
- [ ] Re-scan after patches

---

### 13.08.2025 — Фаза 4, D04/14: Трансфер D04: стабилизация prod (день 2)

**QA**
- [ ] Expanded prod smoke (full checklist)
- [ ] Monitor user-reported issues channel
- [ ] Regression prod hotfixes only
- [ ] Daily prod health report

**DevOps**
- [ ] Complete remaining deploy steps
- [ ] Tune prod autoscaling post-deploy
- [ ] Verify backups post-migration
- [ ] Hotfix deploy to prod if P0

**Security**
- [ ] CVE remediation batch 2: assign + track
- [ ] Patch Critical/High dependencies
- [ ] Re-scan after patches

---

### 14.08.2025 — Фаза 4, D05/14: Трансфер D05: стабилизация prod (день 3)

**QA**
- [ ] Expanded prod smoke (full checklist)
- [ ] Monitor user-reported issues channel
- [ ] Regression prod hotfixes only
- [ ] Daily prod health report

**DevOps**
- [ ] Complete remaining deploy steps
- [ ] Tune prod autoscaling post-deploy
- [ ] Verify backups post-migration
- [ ] Hotfix deploy to prod if P0

**Security**
- [ ] CVE remediation batch 3: assign + track
- [ ] Patch Critical/High dependencies
- [ ] Re-scan after patches

---

### 15.08.2025 — Фаза 4, D06/14: Трансфер mid-point: security sprint

**QA**
- [ ] Prod full smoke regression P0
- [ ] Verify feature flags prod state
- [ ] Sign-off prod stable draft
- [ ] Document prod known issues

**DevOps**
- [ ] Prod stable 72h checkpoint start
- [ ] Infra cost/perf post-deploy review
- [ ] Deploy security patches to prod
- [ ] Verify checksum prod = RC + approved patches

**Security**
- [ ] Mid-transfer CVE review meeting
- [ ] Target: Critical = 0 by D12
- [ ] DAST prod (scheduled, scoped)
- [ ] Triage DAST prod findings

---

### 18.08.2025 — Фаза 4, D07/14: Уязвимости + стабилизация D07 (день 1)

**QA**
- [ ] Prod monitoring review daily
- [ ] Retest security patch regressions
- [ ] Support patch validation tests
- [ ] Update prod smoke after patches

**DevOps**
- [ ] Deploy vulnerability patches prod
- [ ] Rolling restart if required — runbook
- [ ] Monitor patch deploy health
- [ ] Maintain rollback readiness

**Security**
- [ ] CVE closure sprint day 1
- [ ] Verify High CVE closure
- [ ] SCA/SAST on patch branches
- [ ] Security sign-off per patch batch

---

### 19.08.2025 — Фаза 4, D08/14: Уязвимости + стабилизация D08 (день 2)

**QA**
- [ ] Prod monitoring review daily
- [ ] Retest security patch regressions
- [ ] Support patch validation tests
- [ ] Update prod smoke after patches

**DevOps**
- [ ] Deploy vulnerability patches prod
- [ ] Rolling restart if required — runbook
- [ ] Monitor patch deploy health
- [ ] Maintain rollback readiness

**Security**
- [ ] CVE closure sprint day 2
- [ ] Verify High CVE closure
- [ ] SCA/SAST on patch branches
- [ ] Security sign-off per patch batch

---

### 20.08.2025 — Фаза 4, D09/14: Уязвимости + стабилизация D09 (день 3)

**QA**
- [ ] Prod monitoring review daily
- [ ] Retest security patch regressions
- [ ] Support patch validation tests
- [ ] Update prod smoke after patches

**DevOps**
- [ ] Deploy vulnerability patches prod
- [ ] Rolling restart if required — runbook
- [ ] Monitor patch deploy health
- [ ] Maintain rollback readiness

**Security**
- [ ] CVE closure sprint day 3
- [ ] Verify High CVE closure
- [ ] SCA/SAST on patch branches
- [ ] Security sign-off per patch batch

---

### 21.08.2025 — Фаза 4, D10/14: Уязвимости + стабилизация D010 (день 4)

**QA**
- [ ] Prod monitoring review daily
- [ ] Retest security patch regressions
- [ ] Support patch validation tests
- [ ] Update prod smoke after patches

**DevOps**
- [ ] Deploy vulnerability patches prod
- [ ] Rolling restart if required — runbook
- [ ] Monitor patch deploy health
- [ ] Maintain rollback readiness

**Security**
- [ ] CVE closure sprint day 4
- [ ] Verify High CVE closure
- [ ] SCA/SAST on patch branches
- [ ] Security sign-off per patch batch

---

### 22.08.2025 — Фаза 4, D11/14: Финал трансфера D011 (день 1)

**QA**
- [ ] Final prod smoke full suite
- [ ] Prod stable 48h verification
- [ ] Gate 4 checklist QA
- [ ] Prepare Go-Live comms support

**DevOps**
- [ ] Final prod config freeze
- [ ] Archive prod deploy logs
- [ ] Disable enhanced deploy permissions
- [ ] Prod = release candidate final

**Security**
- [ ] Final security re-scan prod
- [ ] Critical/High CVE = 0 confirm
- [ ] Gate 4 security package
- [ ] Security Go-Live approval draft

---

### 25.08.2025 — Фаза 4, D12/14: Финал трансфера D012 (день 2)

**QA**
- [ ] Final prod smoke full suite
- [ ] Prod stable 48h verification
- [ ] Gate 4 checklist QA
- [ ] Prepare Go-Live comms support

**DevOps**
- [ ] Final prod config freeze
- [ ] Archive prod deploy logs
- [ ] Disable enhanced deploy permissions
- [ ] Prod = release candidate final

**Security**
- [ ] Final security re-scan prod
- [ ] Critical/High CVE = 0 confirm
- [ ] Gate 4 security package
- [ ] Security Go-Live approval draft

---

### 26.08.2025 — Фаза 4, D13/14: Финал трансфера D013 (день 3)

**QA**
- [ ] Final prod smoke full suite
- [ ] Prod stable 48h verification
- [ ] Gate 4 checklist QA
- [ ] Prepare Go-Live comms support

**DevOps**
- [ ] Final prod config freeze
- [ ] Archive prod deploy logs
- [ ] Disable enhanced deploy permissions
- [ ] Prod = release candidate final

**Security**
- [ ] Final security re-scan prod
- [ ] Critical/High CVE = 0 confirm
- [ ] Gate 4 security package
- [ ] Security Go-Live approval draft

---

### 27.08.2025 — Фаза 4, D14/14: Gate 4 — Трансфер завершён

**QA**
- [ ] Gate 4 meeting QA sign-off
- [ ] Prod validation complete report
- [ ] Handoff to Go-Live comms
- [ ] Archive prod test evidence

**DevOps**
- [ ] Gate 4: prod stable, deploy complete
- [ ] Close transfer change ticket
- [ ] Restore normal change policy
- [ ] Go-Live deploy confirmation

**Security**
- [ ] Gate 4 Security final sign-off
- [ ] Publish security release bulletin
- [ ] Close vulnerability sprint

---

## Фаза 5: Go-Live и пострелиз

**Период:** 28.08.2025 – 10.09.2025 (10 рабочих дней)

### 28.08.2025 — Фаза 5, D01/10: Go-Live D01: публичный релиз 14.1

**QA**
- [ ] Execute public release smoke prod
- [ ] Monitor support tickets first 4h
- [ ] Verify feature flags public rollout
- [ ] War room QA first shift

**DevOps**
- [ ] Enable public feature flags per plan
- [ ] Publish release announcement trigger
- [ ] Enhanced monitoring 24h
- [ ] On-call primary DevOps

**Security**
- [ ] Security monitor first 24h post-release
- [ ] Watch auth anomaly dashboards
- [ ] Incident response standby

---

### 29.08.2025 — Фаза 5, D02/10: Go-Live D02: усиленный мониторинг

**QA**
- [ ] Daily prod health QA report
- [ ] Triage post-release defects
- [ ] Smoke on hotfixes if any
- [ ] Update known issues list

**DevOps**
- [ ] Review prod metrics vs SLO
- [ ] Hotfix only P0 prod issues
- [ ] Capacity adjust if needed
- [ ] Daily war room summary

**Security**
- [ ] Daily security ops review
- [ ] Scan for post-release attack patterns
- [ ] Review prod access anomalies

---

### 01.09.2025 — Фаза 5, D03/10: Go-Live D03: усиленный мониторинг

**QA**
- [ ] Daily prod health QA report
- [ ] Triage post-release defects
- [ ] Smoke on hotfixes if any
- [ ] Update known issues list

**DevOps**
- [ ] Review prod metrics vs SLO
- [ ] Hotfix only P0 prod issues
- [ ] Capacity adjust if needed
- [ ] Daily war room summary

**Security**
- [ ] Daily security ops review
- [ ] Scan for post-release attack patterns
- [ ] Review prod access anomalies

---

### 02.09.2025 — Фаза 5, D04/10: Стабилизация D04 (день 1)

**QA**
- [ ] Regression post-release hotfixes
- [ ] Defer P2/P3 to 14.1.1 if agreed
- [ ] Support escalation QA
- [ ] Collect feedback for retro

**DevOps**
- [ ] Normalize infra to BAU settings
- [ ] Cleanup temp release resources
- [ ] Update docs from prod learnings
- [ ] Patch deploy if needed

**Security**
- [ ] Close remaining Medium CVE if scheduled
- [ ] Weekly security digest post-release
- [ ] Update threat model if architecture changed

---

### 03.09.2025 — Фаза 5, D05/10: Стабилизация D05 (день 2)

**QA**
- [ ] Regression post-release hotfixes
- [ ] Defer P2/P3 to 14.1.1 if agreed
- [ ] Support escalation QA
- [ ] Collect feedback for retro

**DevOps**
- [ ] Normalize infra to BAU settings
- [ ] Cleanup temp release resources
- [ ] Update docs from prod learnings
- [ ] Patch deploy if needed

**Security**
- [ ] Close remaining Medium CVE if scheduled
- [ ] Weekly security digest post-release
- [ ] Update threat model if architecture changed

---

### 04.09.2025 — Фаза 5, D06/10: Стабилизация D06 (день 3)

**QA**
- [ ] Regression post-release hotfixes
- [ ] Defer P2/P3 to 14.1.1 if agreed
- [ ] Support escalation QA
- [ ] Collect feedback for retro

**DevOps**
- [ ] Normalize infra to BAU settings
- [ ] Cleanup temp release resources
- [ ] Update docs from prod learnings
- [ ] Patch deploy if needed

**Security**
- [ ] Close remaining Medium CVE if scheduled
- [ ] Weekly security digest post-release
- [ ] Update threat model if architecture changed

---

### 05.09.2025 — Фаза 5, D07/10: Стабилизация D07 (день 4)

**QA**
- [ ] Regression post-release hotfixes
- [ ] Defer P2/P3 to 14.1.1 if agreed
- [ ] Support escalation QA
- [ ] Collect feedback for retro

**DevOps**
- [ ] Normalize infra to BAU settings
- [ ] Cleanup temp release resources
- [ ] Update docs from prod learnings
- [ ] Patch deploy if needed

**Security**
- [ ] Close remaining Medium CVE if scheduled
- [ ] Weekly security digest post-release
- [ ] Update threat model if architecture changed

---

### 08.09.2025 — Фаза 5, D08/10: Ретроспектива релиза

**QA**
- [ ] Blameless retro participation
- [ ] QA metrics: escaped defects, coverage
- [ ] Action items для 14.2
- [ ] Archive final test report

**DevOps**
- [ ] Retro: deploy MTTR, incidents
- [ ] Update runbooks from learnings
- [ ] CI/CD improvements backlog
- [ ] Close release branch planning

**Security**
- [ ] Retro: security findings timeline
- [ ] Process improvements security gates
- [ ] Update security checklist template

---

### 09.09.2025 — Фаза 5, D09/10: Закрытие релизного тикета

**QA**
- [ ] Final QA sign-off release 14.1
- [ ] Publish test summary archive
- [ ] Transition bugs to BAU backlog
- [ ] Release 14.1.1 planning input

**DevOps**
- [ ] Close infrastructure change records
- [ ] Tag `14.1` production stable in registry
- [ ] Merge release branch plan (or maintain)
- [ ] Resource decommission temp envs

**Security**
- [ ] Final security release sign-off
- [ ] Archive all scan reports
- [ ] Compliance evidence package

---

### 10.09.2025 — Фаза 5, D10/10: Переход в BAU

**QA**
- [ ] Remove enhanced QA monitoring
- [ ] BAU test cadence restored
- [ ] Document lessons learned wiki
- [ ] Celebrate / team recognition

**DevOps**
- [ ] Disable war room schedules
- [ ] BAU on-call only
- [ ] Release 14.1 marked complete in CMDB
- [ ] Snapshot final prod state documentation

**Security**
- [ ] BAU vulnerability scanning schedule
- [ ] Close release security project
- [ ] Handoff to continuous compliance

---

## Приложение A: Gate-критерии (кратко)

### Gate 0 → Регресс
- [ ] Тест-план утверждён, smoke green
- [ ] QA-контур стабилен, build tagged
- [ ] Security baseline без Critical

### Gate 1 → RC
- [ ] P0 = 0, P1 ≤ 3 (waiver documented)
- [ ] Тест-план ≥ 98% выполнен
- [ ] RC1 candidate на staging

### Gate 2 → Предтрансфер
- [ ] UAT sign-off PO
- [ ] Perf в пределах SLO vs 14.0
- [ ] Runbook + rollback проверены

### Gate 3 → Трансфер
- [ ] CAB approved
- [ ] Pre-prod smoke green
- [ ] On-call и war room готовы

### Gate 4 → Go-Live
- [ ] Prod stable 48 ч
- [ ] Critical/High CVE = 0
- [ ] Post-deploy smoke 100%

### Gate 5 → BAU
- [ ] Нет открытых P0 prod
- [ ] Ретро проведена
- [ ] Артефакты архивированы
