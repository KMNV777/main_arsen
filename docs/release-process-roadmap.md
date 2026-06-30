# Релизный процесс — универсальная дорожная карта

> Датонезависимый фреймворк управления релизом. Описывает **что**, **кто** и **в каком порядке**, без привязки к календарю.  
> Версия процесса: **2.0 (оптимизированная)** — с параллельными потоками и shift-left контролями.

---

## 1. Цели оптимизированного процесса

| Было (классика) | Стало (оптимизация) |
|-----------------|---------------------|
| Security и CVE — в конце, на трансфере | Shift-left: сканирование с первого дня ветки релиза |
| Регресс — монолитный блок | Непрерывный регресс + финальный freeze-прогон |
| UAT → Perf → Security — последовательно | Параллельные потоки на этапе стабилизации |
| Предтрансфер — длинная подготовка «с нуля» | Подготовка prod начинается одновременно с RC |
| Трансфер = big-bang + закрытие CVE | Поэтапный rollout + CVE закрыты до prod |
| Много ручных Gate-meeting | Gate = чеклист + автоматические метрики + короткий sync |

**Ключевой принцип:** каждая фаза имеет **входные критерии (Entry)**, **артефакты** и **выходные критерии (Exit)**. Переход без Exit = No-Go.

---

## 2. Роли и зоны ответственности

| Роль | Аббревиатура | Зона ответственности |
|------|--------------|----------------------|
| **Release Manager** | RM | Сквозная координация, Gate, эскалации, коммуникации |
| **Product Owner** | PO | Scope, приоритеты, UAT sign-off, Release Notes (бизнес) |
| **Tech Lead / Engineering Manager** | TL | Техническое качество, code freeze, архитектурные риски |
| **QA Lead** | QA | Тест-стратегия, тест-план, регресс, quality metrics |
| **DevOps / SRE Lead** | DO | Контуры, CI/CD, деплой, мониторинг, rollback |
| **Security Lead** | SEC | SAST/DAST/SCA, CVE, security sign-off |
| **Support Lead** | SUP | Runbook для L1/L2, обучение, comms для пользователей |
| **Change Manager / CAB** | CAB | Согласование prod-изменений (в регулируемых средах) |

**Обозначения в шагах:**
- **A** (Accountable) — принимает решение, подписывает Gate
- **R** (Responsible) — выполняет работу
- **C** (Consulted) — консультирует, участвует в ревью
- **I** (Informed) — получает статус

---

## 3. Обзор фаз (без дат)

```
┌─────────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────────┐   ┌─────────┐
│  P0         │   │  P1          │   │  P2         │   │  P3          │   │  P4     │
│  Инициация  │──▶│  Стабилиза-  │──▶│  Кандидат   │──▶│  Промышлен-  │──▶│  Пост-  │
│  релиза     │   │  ция         │   │  (RC)       │   │  ный вывод   │   │  релиз  │
└─────────────┘   └──────────────┘   └─────────────┘   └──────────────┘   └─────────┘
      │                  │                  │                  │
   Gate 0            Gate 1             Gate 2             Gate 3
```

| Фаза | Название | Ориентир длительности* | Суть |
|------|----------|------------------------|------|
| **P0** | Инициация релиза | 5–10 р.д. | Scope, ветка, контуры, тест-план |
| **P1** | Стабилизация | 10–16 р.д. | Регресс, фиксы, доводка фичей |
| **P2** | Release Candidate | 10–15 р.д. | Freeze, UAT, perf, security baseline |
| **P3** | Промышленный вывод | 8–14 р.д. | CAB, деплой, валидация prod |
| **P4** | Пострелиз | 5–10 р.д. | Мониторинг, retro, закрытие |

\* Ориентиры для планирования capacity, не жёсткие SLA.

### Параллельные потоки (оптимизация)

На фазах P1–P3 одновременно идут три потока:

```
Поток QA:     [регресс] ──▶ [UAT] ──▶ [prod smoke]
Поток DevOps: [CI/контуры] ──▶ [runbook/CAB] ──▶ [деплой]
Поток SEC:    [shift-left scan] ──▶ [baseline] ──▶ [re-scan prod]
```

---

## 4. Детальная дорожная карта по шагам

---

### Фаза P0 — Инициация релиза

**Цель:** зафиксировать scope, подготовить инфраструктуру и тестовую базу до начала активного тестирования.

**Entry:** backlog релиза согласован, команда выделена.  
**Exit (Gate 0):** scope lock, QA-контур green, тест-план v1.0, security baseline без Critical.

| # | Шаг | A | R | C | Действия | Артефакт |
|---|-----|---|---|---|----------|----------|
| P0.1 | Scope Lock | PO | RM | TL, QA | Зафиксировать in/out of scope. Все change requests — через RM. Опубликовать scope doc. | Scope Document |
| P0.2 | Release Branch | TL | DO | Dev | Создать `release/X.Y`, настроить CI (build, unit, lint). Запретить прямые push без review. | Ветка + green CI |
| P0.3 | Тест-план | QA | QA | PO, TL | Составить тест-план: фичи → ТК → приоритет (P0/P1). Матрица трассируемости. | Test Plan v1.0 |
| P0.4 | Тест-кейсы | QA | QA | PO | Актуализировать/создать ТК. Smoke-набор (≤ 2 ч). Regression suite с приоритетами. | ТК в TMS |
| P0.5 | QA-контур | DO | DO | QA, SEC | Деплой билда в QA. Parity QA ↔ staging. Тестовые данные, секреты, мониторинг. | QA Environment Sheet |
| P0.6 | Security Baseline | SEC | SEC | DO, TL | SBOM, SAST/SCA quick-scan, gitleaks. Политика: Critical = блокер с P0. | Security Baseline Report |
| P0.7 | Kick-off | RM | RM | Все | Согласовать SLA багов, каналы, on-call, календарь Gate. | Kick-off протокол |

**Gate 0 — Go на стабилизацию**

| Критерий | Проверяет |
|----------|-----------|
| Scope зафиксирован, CR-процесс определён | PO, RM |
| Тест-план v1.0 утверждён | QA |
| QA-контур стабилен, smoke green | DO, QA |
| Нет открытых Critical security | SEC |
| CI на release-ветке green | DO |

---

### Фаза P1 — Стабилизация

**Цель:** достичь качества, достаточного для заморозки кода и сборки RC.

**Entry:** Gate 0 пройден.  
**Exit (Gate 1):** P0 = 0, тест-план ≥ 98%, RC-кандидат на staging.

| # | Шаг | A | R | C | Действия | Артефакт |
|---|-----|---|---|---|----------|----------|
| P1.1 | Старт регресса | QA | QA | Dev | Smoke 100% → прогон P0 ТК → P1. Daily burn-down. Bug triage с TL. | Regression Dashboard |
| P1.2 | Bug Fix Loop | TL | Dev | QA | P0: фикс ≤ 24 ч. P1: ≤ 48 ч. Hotfix pipeline ≤ 4 ч (commit → QA). | Bug reports + fix log |
| P1.3 | Ретест фиксов | QA | QA | Dev | Re-test в течение 1 р.д. после фикса. Reopen P0 — эскалация RM. | Retest log |
| P1.4 | Актуализация ТК | QA | QA | PO | Обновлять ТК при изменении поведения. Peer-review с аналитиком. | Актуальные ТК |
| P1.5 | Доводка фичей | PO | Dev | QA | Только баги в scope. Без нового функционала. PO подтверждает acceptance. | Feature sign-off list |
| P1.6 | Shift-left Security | SEC | SEC | Dev | Incremental SAST/SCA на каждый merge. Security defects — отдельный трекер. | Security defect log |
| P1.7 | Weekly Go/No-Go | RM | RM | Все | Статус P0/P1, риски, scope cut при необходимости. | Weekly status (RAG) |
| P1.8 | RC Preparation | DO | DO | TL, QA | Dry-run RC build. Staging deploy rehearsal. Tag freeze-candidate. | RC build candidate |

**Оптимизация P1:**
- Автотесты P0 в CI на каждый merge — ручной регресс только на delta.
- Bug triage 2 раза в день в пиковые дни (не раз в неделю).
- «Stop the line» — при P0 новый функционал не мержится до закрытия.

**Gate 1 — Go на RC**

| Критерий | Проверяет |
|----------|-----------|
| P0 = 0, P1 ≤ 3 (waiver у PO) | QA, PO |
| Тест-план ≥ 98% | QA |
| RC-кандидат на staging, smoke green | DO, QA |
| Security: Critical = 0, High — план закрытия | SEC |

---

### Фаза P2 — Release Candidate

**Цель:** получить подписанный RC, готовый к промышленному выводу.

**Entry:** Gate 1 пройден.  
**Exit (Gate 2):** UAT sign-off, perf в SLO, runbook + rollback проверены, CVE Critical/High = 0.

| # | Шаг | A | R | C | Действия | Артефакт |
|---|-----|---|---|---|----------|----------|
| P2.1 | Hard Code Freeze | TL | TL | RM, Dev | Только hotfix по approval RM. Dependency updates — только security. | Code Freeze notice |
| P2.2 | RC Build | DO | DO | TL | Tag `X.Y-rc1`. Signed artifacts. Immutable registry. | RC artifact |
| P2.3 | UAT | PO | PO | QA | Бизнес-сценарии на staging. Дефекты UAT — приоритет как P0/P1. | UAT sign-off |
| P2.4 | Performance Test | QA | QA | DO | Нагрузка на staging. Сравнение с предыдущим релизом. SLO не деградировали. | Perf report |
| P2.5 | Security Baseline | SEC | SEC | DO, Dev | Full SAST + DAST + SCA. CVE triage. Critical/High — фикс до Gate 2. | Security Baseline Final |
| P2.6 | RC2 (условно) | RM | DO | QA, SEC | Только если RC1 не прошёл gate. Иначе — пропуск. | RC2 artifact (if needed) |
| P2.7 | Runbook + Rollback | DO | DO | TL, QA | Deploy runbook пошаговый. Rollback drill на pre-prod. RTO задокументирован. | Runbook, Rollback Plan |
| P2.8 | Release Notes | PO | PO | QA, TL | Финальный список изменений, known issues, breaking changes. | Release Notes |
| P2.9 | Pre-transfer Prep ⚡ | DO | DO | CAB, SEC | **Параллельно с UAT:** CAB draft, pre-prod sync, prod dashboards, on-call roster. | CAB packet (draft) |

**Оптимизация P2:**
- UAT, Perf и Security Baseline — **параллельно**, не последовательно.
- CAB и runbook готовятся **с первого дня RC**, а не отдельной фазой.
- RC2 — исключение; цель — one-shot RC.

**Gate 2 — Go на промышленный вывод**

| Критерий | Проверяет |
|----------|-----------|
| UAT sign-off от PO | PO |
| Perf: SLO в норме vs предыдущий релиз | QA, DO |
| Runbook + rollback drill пройден | DO |
| Critical/High CVE = 0 | SEC |
| Release Notes финал | PO |

---

### Фаза P3 — Промышленный вывод

**Цель:** безопасно доставить RC в prod и подтвердить стабильность.

**Entry:** Gate 2 пройден.  
**Exit (Gate 3):** prod stable, post-deploy smoke 100%, change закрыт.

| # | Шаг | A | R | C | Действия | Артефакт |
|---|-----|---|---|---|----------|----------|
| P3.1 | CAB Approval | CAB | RM | DO, SEC | Подача change request: runbook, rollback, RC SHA, security report. | CAB ticket (approved) |
| P3.2 | Pre-prod Validation | QA | QA | DO | Финальный прогон на pre-prod = prod config. Post-deploy smoke script. | Pre-prod sign-off |
| P3.3 | Comms | RM | RM | PO, SUP | T-14, T-7, T-1: внутренние и внешние уведомления. FAQ для поддержки. | Comms log |
| P3.4 | War Room | RM | RM | DO, QA, SEC | Расписание дежурств. Канал связи. Escalation matrix. | War room schedule |
| P3.5 | Prod Deploy | DO | DO | TL, SEC | По runbook: поэтапно (canary / blue-green / rolling — по архитектуре). Checkpoints rollback. | Deploy journal |
| P3.6 | Post-deploy Smoke | QA | QA | DO | Критичные user flows ≤ 30 мин. P0 в prod — немедленная эскалация. | Prod smoke report |
| P3.7 | Security Re-scan | SEC | SEC | DO | Пассивный scan prod surface. SIEM monitoring. Auth/TLS verify. | Post-deploy security check |
| P3.8 | Stability Window | DO | DO | QA, SEC | Мониторинг error rate, latency. Порог: stable 48 ч. | Stability report |

**Оптимизация P3:**
- CVE закрываются **до** prod (на P2), а не на трансфере — фаза «устранение уязвимостей» убрана из критического пути.
- Поэтапный rollout (canary 5% → 25% → 100%) вместо big-bang.
- Feature flags: включение функционала после stable infra.
- Автоматический post-deploy smoke в pipeline.

**Gate 3 — Go-Live / закрытие change**

| Критерий | Проверяет |
|----------|-----------|
| Prod deploy завершён по runbook | DO |
| Post-deploy smoke 100% | QA |
| Prod stable 48 ч (SLO) | DO |
| Нет открытых Critical/High CVE | SEC |
| CAB change закрыт | CAB, RM |

---

### Фаза P4 — Пострелиз

**Цель:** стабилизировать prod, закрыть релиз, извлечь уроки.

**Entry:** Gate 3 пройден.  
**Exit (Gate 4 / закрытие релиза):** нет P0 prod, retro проведена, артефакты архивированы.

| # | Шаг | A | R | C | Действия | Артефакт |
|---|-----|---|---|---|----------|----------|
| P4.1 | Enhanced Monitoring | DO | DO | QA, SEC | Усиленный мониторинг 5–10 р.д. Error budget tracking. | Monitoring report |
| P4.2 | Hotfix (только P0) | TL | Dev | QA, DO | P0 prod — hotfix pipeline. P2/P3 → backlog патча X.Y.1. | Hotfix log |
| P4.3 | Support Handoff | SUP | SUP | PO, QA | Known issues, FAQ, эскалации. Обучение L1/L2. | Support playbook |
| P4.4 | Blameless Retro | RM | RM | Все | Метрики: escaped defects, MTTR, gate delays. Action items. | Retro notes |
| P4.5 | Archive & Close | RM | RM | QA, DO, SEC | Архив тестов, сканов, runbook, gate-протоколов. Закрытие релизного тикета. | Release archive |
| P4.6 | Transition to BAU | DO | DO | SEC | Снятие war room. Нормальный on-call. CMDB обновлён. | BAU confirmation |

**Gate 4 — Закрытие релиза**

| Критерий | Проверяет |
|----------|-----------|
| Нет открытых P0 в prod | QA, TL |
| Ретроспектива проведена, action items заведены | RM |
| Все артефакты архивированы | RM |
| Enhanced monitoring снят | DO |

---

## 5. Сводная RACI-матрица

| Процесс | PO | TL | QA | DO | SEC | RM | CAB | SUP |
|---------|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|
| Scope Lock | **A** | C | C | I | I | **R** | I | I |
| Release Branch | I | **A** | I | **R** | C | C | I | I |
| Тест-план / регресс | C | C | **A/R** | C | I | C | I | I |
| Bug Fix | C | **A** | C | I | C | C | I | I |
| Code Freeze | C | **A** | C | C | I | **R** | I | I |
| UAT sign-off | **A/R** | I | C | I | I | C | I | C |
| Performance | I | C | **A/R** | C | I | C | I | I |
| Security scans | I | C | C | C | **A/R** | C | C | I |
| Runbook / Deploy | I | C | C | **A/R** | C | C | C | I |
| CAB | I | I | I | C | C | **R** | **A** | I |
| Go/No-Go Gates | C | C | C | C | C | **A/R** | C | I |
| Comms | C | I | I | I | I | **A** | I | **R** |
| Post-release | C | C | C | **R** | C | **A** | I | **R** |
| Retro | C | C | C | C | C | **A/R** | I | C |

---

## 6. Карта оптимизаций

### 6.1. Убрано из критического пути

| Элемент (было) | Замена (стало) | Эффект |
|----------------|----------------|--------|
| Отдельная фаза «устранение CVE» на трансфере | CVE closure на P1–P2 (shift-left) | −7…14 р.д. на критическом пути |
| Длинная «предтрансферная» подготовка | CAB + runbook параллельно с UAT (P2.9) | −10…15 р.д. |
| Полный регресс на каждый коммит | CI autotests P0 + ручной delta-регресс | −30…40% effort QA |
| RC2 как норма | One-shot RC, RC2 — исключение | −3…5 р.д. |
| Big-bang prod deploy | Canary / feature flags | ↓ риск, ↓ rollback scope |

### 6.2. Добавлено / усилено

| Практика | Где | Зачем |
|----------|-----|-------|
| SBOM + SCA на каждый merge | P0–P1 | Раннее обнаружение CVE |
| Immutable signed artifacts | P2 | Воспроизводимость, безопасность |
| Automated post-deploy smoke | P3 | Быстрая валидация prod |
| Rollback drill до prod | P2 | Снижение RTO |
| Bug burn-down dashboard | P1 | Прозрачность, раннее предупреждение |
| Gate = чеклист + метрики | Все Gate | Меньше meeting overhead |

### 6.3. Ориентир сокращения цикла

```
Классический процесс:     P0(10) + P1(16) + P2(19) + Pre(24) + Transfer(14) + P4(10) ≈ 93 р.д.
Оптимизированный процесс: P0(7)  + P1(12) + P2(12) + P3(10)              + P4(7)  ≈ 48 р.д.
```

*Оценка для типичного mid-size релиза. Фактическая длительность зависит от scope и зрелости CI/CD.*

---

## 7. Quality Gates — единый чеклист

Использовать как шаблон для любого релиза (копировать в тикет RM):

### Gate 0 → P1
- [ ] Scope Document утверждён (PO)
- [ ] Test Plan v1.0 (QA)
- [ ] QA smoke green (QA + DO)
- [ ] Security baseline: Critical = 0 (SEC)
- [ ] CI green на release-ветке (DO)

### Gate 1 → P2
- [ ] P0 = 0, P1 ≤ 3 с waiver (QA + PO)
- [ ] Тест-план ≥ 98% (QA)
- [ ] RC-кандидат staging smoke green (DO + QA)
- [ ] Security defect log: Critical = 0 (SEC)

### Gate 2 → P3
- [ ] UAT sign-off (PO)
- [ ] Perf report: SLO ok (QA + DO)
- [ ] Runbook + rollback drill (DO)
- [ ] CVE Critical/High = 0 (SEC)
- [ ] Release Notes финал (PO)
- [ ] CAB packet готов (RM + DO)

### Gate 3 → P4
- [ ] Prod deploy по runbook (DO)
- [ ] Post-deploy smoke 100% (QA)
- [ ] Prod stable 48 ч (DO)
- [ ] CAB change closed (CAB)

### Gate 4 → Закрытие
- [ ] P0 prod = 0 (QA + TL)
- [ ] Retro + action items (RM)
- [ ] Артефакты архивированы (RM)
- [ ] BAU restored (DO)

---

## 8. Артефакты релиза (master checklist)

| # | Артефакт | Фаза | Owner |
|---|----------|------|-------|
| 1 | Scope Document | P0 | PO |
| 2 | Test Plan | P0 | QA |
| 3 | Security Baseline Report | P0, P2 | SEC |
| 4 | Regression Dashboard | P1 | QA |
| 5 | RC Artifact (signed) | P2 | DO |
| 6 | UAT Sign-off | P2 | PO |
| 7 | Performance Report | P2 | QA |
| 8 | Runbook + Rollback Plan | P2 | DO |
| 9 | Release Notes | P2 | PO |
| 10 | CAB Ticket | P3 | RM |
| 11 | Deploy Journal | P3 | DO |
| 12 | Prod Smoke Report | P3 | QA |
| 13 | Stability Report | P3–P4 | DO |
| 14 | Support Playbook | P4 | SUP |
| 15 | Retro Notes + Action Items | P4 | RM |
| 16 | Release Archive | P4 | RM |

---

## 9. Метрики процесса (для ретро и улучшений)

| Метрика | Формула / смысл | Целевое значение |
|---------|-----------------|------------------|
| **Release Cycle Time** | Gate 0 → Gate 3 | Тренд на снижение |
| **Regression Efficiency** | Автотесты / (авто + ручные) | ≥ 60% |
| **Escaped Defects** | P0/P1 в prod первые 14 дней | 0 P0 |
| **Gate Slip Rate** | Gate с No-Go / всего Gate | ≤ 20% |
| **Hotfix MTTR** | Время P0 fix в prod | ≤ 4 ч |
| **CVE Lead Time** | Обнаружение → закрытие Critical | ≤ 48 ч |
| **Rollback Readiness** | RTO по drill | ≤ 30 мин |
| **UAT First-Pass Rate** | UAT без RC2 | ≥ 80% |

---

## 10. Антипаттерны (чего избегать)

| Антипаттерн | Почему плохо | Что делать |
|-------------|--------------|------------|
| «CVE закроем на трансфере» | Блокирует prod, сжимает окно | Shift-left, Gate 2 = CVE 0 |
| Scope creep без CR | Раздувает P1, срывает регресс | Жёсткий CR через RM + PO |
| Регресс без приоритетов | Тратим время на P3 раньше P0 | P0 → P1 → P2, строго |
| Gate как формальность | Пропускаем дефекты в prod | Gate = чеклист, No-Go — норма |
| Runbook «написан, не проверен» | Rollback не работает | Обязательный drill на pre-prod |
| Один RC2 за другим | Процесс нестабилен | Анализ root cause, улучшить P1 |
| Big-bang без feature flags | Высокий blast radius | Canary + flags |

---

## 11. Быстрый старт для Release Manager

1. Скопировать **Gate-чеклист** (раздел 7) в тикет релиза.
2. Назначить **A** на каждую фазу (см. RACI).
3. На kick-off (P0.7) согласовать **параллельные потоки** (раздел 3).
4. Включить **shift-left security** с первого дня ветки.
5. Запустить **CAB draft** одновременно с UAT (P2.9), не ждать Gate 2.
6. На каждом Gate — только чеклист + 30-мин sync, не многочасовые совещания.
7. После Gate 4 — retro с метриками (раздел 9) и action items в backlog процесса.

---

*Связанный документ с привязкой к датам (пример релиза 14.1): `release-14.1-daily-plan.md`*
