# Эталонный кейс: релиз 14.1

> **Единый документ** — процесс, роли, календарь, чеклисты и оптимизации на примере релиза 14.1.  
> Использовать как шаблон для последующих релизов (14.2, 15.0 и т.д.).

---

## 1. Резюме

| Параметр | Значение |
|----------|----------|
| **Версия** | 14.1 |
| **Ветка** | `release/14.1` |
| **Release Manager** | [ФИО] |
| **Старт подготовки (Gate 0)** | 28.04.2025 |
| **Старт регресса** | 15.05.2025 |
| **Go-Live** | 28.08.2025 |
| **Закрытие релиза (Gate 4)** | 10.09.2025 |
| **Общая длительность** | 92 рабочих дня |
| **Версия процесса** | 2.0 (оптимизированная) |

### Ключевые вехи

| Веха | Дата | Gate |
|------|------|------|
| Подготовка завершена | 14.05.2025 | Gate 0 |
| Регресс завершён | 05.06.2025 | Gate 1 |
| RC принят | 04.07.2025 | Gate 2 |
| Go на пром. вывод | 07.08.2025 | Gate 3 prep |
| Prod stable | 27.08.2025 | Gate 3 |
| Публичный релиз | 28.08.2025 | — |
| Релиз закрыт | 10.09.2025 | Gate 4 |

### Что входит в scope 14.1

| # | Фича / изменение | PO sign-off | QA coverage |
|---|------------------|:-----------:|:-----------:|
| 1 | [Фича 1] | ☐ | ☐ |
| 2 | [Фича 2] | ☐ | ☐ |
| 3 | [Фича 3] | ☐ | ☐ |
| 4 | Bugfix batch | ☐ | ☐ |
| 5 | Tech debt / infra | ☐ | ☐ |

> Заполнить перед Gate 0. Out of scope — только через CR (RM + PO).

---

## 2. Команда и RACI

### 2.1. Назначение ролей (релиз 14.1)

| Роль | Код | Ответственный | Контакт |
|------|-----|---------------|---------|
| Release Manager | RM | [ФИО] | [#release-14-1] |
| Product Owner | PO | [ФИО] | — |
| Tech Lead | TL | [ФИО] | — |
| QA Lead | QA | [ФИО] | — |
| DevOps / SRE Lead | DO | [ФИО] | — |
| Security Lead | SEC | [ФИО] | — |
| Support Lead | SUP | [ФИО] | — |
| CAB | CAB | [ФИО] | — |

**Обозначения:** A — Accountable, R — Responsible, C — Consulted, I — Informed

### 2.2. RACI-матрица

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

---

## 3. Модель процесса (5 фаз)

```
P0 Инициация ──▶ P1 Стабилизация ──▶ P2 RC ──▶ P3 Пром.вывод ──▶ P4 Пострелиз
   28.04          15.05           06.06        07.07           28.08
   Gate 0         Gate 1          Gate 2       Gate 3          Gate 4
```

### Параллельные потоки (оптимизация 14.1)

```
QA:     [регресс 15.05–05.06] ──▶ [UAT 06.06–04.07] ──▶ [prod smoke 08.08–27.08]
DevOps: [CI/QA 28.04–14.05]   ──▶ [runbook+CAB с 06.06] ──▶ [deploy 08.08–27.08]
SEC:    [shift-left с 28.04]   ──▶ [baseline 06.06–04.07] ──▶ [re-scan prod]
```

### Календарь фаз

| Фаза | Период | Р.д. | Gate | Дата Gate |
|------|--------|------|------|-----------|
| **P0** Инициация релиза | 28.04.2025 – 14.05.2025 | 9 | Gate 0 | 14.05.2025 |
| **P1** Стабилизация (регресс) | 15.05.2025 – 05.06.2025 | 16 | Gate 1 | 05.06.2025 |
| **P2** Release Candidate | 06.06.2025 – 04.07.2025 | 19 | Gate 2 | 04.07.2025 |
| **P3** Промышленный вывод | 07.07.2025 – 27.08.2025 | 38 | Gate 3 | 27.08.2025 |
| **P4** Пострелиз | 28.08.2025 – 10.09.2025 | 10 | Gate 4 | 10.09.2025 |

---

## 4. Оптимизация на примере 14.1

### 4.1. Что изменено vs классический план

| Классика (исходный план) | Оптимизация (эталон 14.1) | Эффект |
|--------------------------|---------------------------|--------|
| CVE закрываются на трансфере (14 р.д.) | Shift-left: CVE → Gate 2 (04.07) | Трансфер без блокеров |
| Предтрансфер 24 р.д. отдельно | CAB + runbook с 06.06 (P2.9) | Параллель с UAT |
| Полный ручной регресс | CI autotests P0 + delta-регресс | −30% effort QA |
| Big-bang deploy | Canary 5%→25%→100% + feature flags | ↓ blast radius |
| Gate = долгие meeting | Gate = чеклист + 30 мин sync | ↓ overhead |

### 4.2. SLA и правила

| Правило | Значение |
|---------|----------|
| P0 fix SLA | ≤ 24 ч |
| P1 fix SLA | ≤ 48 ч |
| Hotfix commit → QA | ≤ 4 ч |
| Ретест после фикса | ≤ 1 р.д. |
| Critical CVE | Блокер с Gate 0 |
| High CVE | Блокер с Gate 2 |
| Prod rollback RTO | ≤ 30 мин |
| Prod stable window | 48 ч до Gate 3 |

---

## 5. Детальный план по фазам

### P0 — Scope lock, ветка, тест-план, QA-контур, security baseline

**Период:** 28.04 – 14.05.2025 (9 р.д.)  
**Gate 0:** 14.05.2025

| Шаг | Название | A | R | Действие | Артефакт |
|-----|----------|---|---|----------|----------|
| P0.1 | Scope Lock | PO | RM | Зафиксировать in/out of scope | Scope Document |
| P0.2 | Release Branch | TL | DO | Ветка release/14.1, CI green | Ветка + pipeline |
| P0.3 | Тест-план | QA | QA | Фичи → ТК → P0/P1 | Test Plan v1.0 |
| P0.4 | Тест-кейсы | QA | QA | Smoke ≤2ч, regression suite | ТК в TMS |
| P0.5 | QA-контур | DO | DO | Деплой, parity, данные | QA Environment Sheet |
| P0.6 | Security Baseline | SEC | SEC | SBOM, SAST/SCA, gitleaks | Baseline Report |
| P0.7 | Kick-off | RM | RM | SLA, каналы, on-call | Kick-off протокол |

**Gate 0 — чеклист:**

- [ ] Scope зафиксирован (PO)
- [ ] Test Plan v1.0 (QA)
- [ ] QA smoke green (QA + DO)
- [ ] Critical security = 0 (SEC)
- [ ] CI green (DO)

---

### P1 — Регресс, фиксация багов, ретест, актуализация ТК, доводка фичей

**Период:** 15.05 – 05.06.2025 (16 р.д.)  
**Gate 1:** 05.06.2025

| Шаг | Название | A | R | Действие | Артефакт |
|-----|----------|---|---|----------|----------|
| P1.1 | Старт регресса | QA | QA | Smoke → P0 → P1, burn-down | Regression Dashboard |
| P1.2 | Bug Fix Loop | TL | Dev | P0≤24ч, P1≤48ч, hotfix≤4ч | Bug log |
| P1.3 | Ретест | QA | QA | Re-test за 1 р.д. | Retest log |
| P1.4 | Актуализация ТК | QA | QA | Синхронизация с билдом | Актуальные ТК |
| P1.5 | Доводка фичей | PO | Dev | Только баги в scope | Feature sign-off |
| P1.6 | Shift-left Security | SEC | SEC | SAST/SCA на merge | Security defect log |
| P1.7 | Weekly Go/No-Go | RM | RM | RAG, scope cut | Weekly status |
| P1.8 | RC Prep | DO | DO | Dry-run RC, staging rehearsal | RC candidate |

**Gate 1 — чеклист:**

- [ ] P0 = 0, P1 ≤ 3 waiver (QA + PO)
- [ ] Тест-план ≥ 98% (QA)
- [ ] RC-кандидат staging smoke (DO + QA)
- [ ] Critical security = 0 (SEC)

---

### P2 — Code freeze, RC, UAT, perf, security baseline, runbook

**Период:** 06.06 – 04.07.2025 (19 р.д.)  
**Gate 2:** 04.07.2025

| Шаг | Название | A | R | Действие | Артефакт |
|-----|----------|---|---|----------|----------|
| P2.1 | Code Freeze | TL | TL | Только hotfix via RM | Freeze notice |
| P2.2 | RC Build | DO | DO | Tag 14.1-rc1, signed artifacts | RC artifact |
| P2.3 | UAT | PO | PO | Бизнес-сценарии staging | UAT sign-off |
| P2.4 | Performance | QA | QA | Нагрузка, SLO vs 14.0 | Perf report |
| P2.5 | Security Baseline | SEC | SEC | Full SAST+DAST+SCA | Security Final |
| P2.6 | RC2 (if needed) | RM | DO | Только при fail RC1 | RC2 artifact |
| P2.7 | Runbook + Rollback | DO | DO | Drill на pre-prod | Runbook |
| P2.8 | Release Notes | PO | PO | Changes, known issues | Release Notes |
| P2.9 | Pre-transfer ⚡ | DO | DO | CAB draft ∥ UAT с 06.06 | CAB packet draft |

**Gate 2 — чеклист:**

- [ ] UAT sign-off (PO)
- [ ] Perf SLO ok (QA + DO)
- [ ] Runbook + rollback drill (DO)
- [ ] CVE Critical/High = 0 (SEC)
- [ ] Release Notes финал (PO)

---

### P3 — CAB, pre-prod, prod deploy (canary), стабилизация, Gate 3

**Период:** 07.07 – 27.08.2025 (36 р.д.)  
**Gate 3:** 27.08.2025

| Шаг | Название | A | R | Действие | Артефакт |
|-----|----------|---|---|----------|----------|
| P3.1 | CAB Approval | CAB | RM | Change request approved | CAB ticket |
| P3.2 | Pre-prod Validation | QA | QA | Финальный прогон | Pre-prod sign-off |
| P3.3 | Comms | RM | RM | T-14, T-7, T-1 | Comms log |
| P3.4 | War Room | RM | RM | Дежурства, escalation | War room schedule |
| P3.5 | Prod Deploy | DO | DO | Canary 5→25→100% | Deploy journal |
| P3.6 | Post-deploy Smoke | QA | QA | Critical flows ≤30 мин | Smoke report |
| P3.7 | Security Re-scan | SEC | SEC | SIEM, auth/TLS | Post-deploy check |
| P3.8 | Stability | DO | DO | Stable 48ч | Stability report |

**Gate 3 — чеклист:**

- [ ] Prod deploy по runbook (DO)
- [ ] Post-deploy smoke 100% (QA)
- [ ] Prod stable 48ч (DO)
- [ ] CVE = 0 (SEC)
- [ ] CAB closed (CAB)

---

### P4 — Go-Live, мониторинг, retro, закрытие

**Период:** 28.08 – 10.09.2025 (10 р.д.)  
**Gate 4:** 10.09.2025

| Шаг | Название | A | R | Действие | Артефакт |
|-----|----------|---|---|----------|----------|
| P4.1 | Go-Live | RM | DO | Публичный релиз 28.08 | Go-Live confirm |
| P4.2 | Enhanced Monitoring | DO | DO | 5–10 р.д. усиленный | Monitoring report |
| P4.3 | Hotfix P0 | TL | Dev | Только P0 в prod | Hotfix log |
| P4.4 | Support Handoff | SUP | SUP | FAQ, обучение L1/L2 | Support playbook |
| P4.5 | Retro | RM | RM | Blameless, action items | Retro notes |
| P4.6 | Archive + BAU | RM | RM | Архив, закрытие тикета | Release archive |

**Gate 4 — чеклист:**

- [ ] P0 prod = 0 (QA + TL)
- [ ] Retro проведена (RM)
- [ ] Артефакты архивированы (RM)
- [ ] BAU restored (DO)

---

## 6. Недельный операционный календарь

> Каждая неделя — чеклисты QA, DevOps, Security. Отмечать `[x]` по факту.

### P0 · W1 (28.04 – 30.04) — Scope + ветка + тест-план

**QA**
- [ ] Ревью scope с PO
- [ ] Матрица фича→ТК
- [ ] Согласовать severity P0–P3

**DevOps**
- [ ] Ветка release/14.1
- [ ] CI pipeline green
- [ ] Деплой QA

**Security**
- [ ] SBOM baseline
- [ ] Политика CVE
- [ ] Gitleaks scan

---

### P0 · W2 (05.05 – 08.05) — ТК + контуры

**QA**
- [ ] Smoke-набор ≤2ч
- [ ] Regression suite P0
- [ ] Dry-run smoke

**DevOps**
- [ ] Автотесты на release-ветку
- [ ] QA parity staging
- [ ] Алерты QA

**Security**
- [ ] RBAC тест-сред
- [ ] Нет prod-секретов в QA
- [ ] SAST quick-scan

---

### P0 · W3 (12.05 – 14.05) — Gate 0

**QA**
- [ ] Test Plan v1.0 sign-off
- [ ] Readiness review
- [ ] Kick-off регресса

**DevOps**
- [ ] Tag regression-candidate
- [ ] Hotfix runbook QA
- [ ] Backup QA

**Security**
- [ ] Gate 0 security pack
- [ ] Security on-call list
- [ ] Baseline sign-off

---

### P1 · W1 (15.05 – 23.05) — Старт регресса

**QA**
- [ ] Smoke 100%
- [ ] P0 ТК ≥50%
- [ ] Daily burn-down

**DevOps**
- [ ] Hotfix ≤4ч
- [ ] Deploy journal
- [ ] QA uptime 99%

**Security**
- [ ] Incremental SAST/SCA
- [ ] Security defect tracker
- [ ] RBAC новых фич

---

### P1 · W2 (26.05 – 30.05) — Фиксы + P1

**QA**
- [ ] P0 target = 0
- [ ] P1 прогон ≥50%
- [ ] Ретест фиксов 24ч

**DevOps**
- [ ] Tag 14.1-regression-w1
- [ ] CI green mandatory
- [ ] Snapshot QA EOD

**Security**
- [ ] DAST window QA
- [ ] Mid-regression checkpoint
- [ ] SBOM update

---

### P1 · W3 (02.06 – 05.06) — Gate 1

**QA**
- [ ] Тест-план ≥98%
- [ ] 100% ретест fixed
- [ ] Gate 1 пакет

**DevOps**
- [ ] RC1 candidate staging
- [ ] Rollback rehearsal
- [ ] Code freeze prep

**Security**
- [ ] Full SAST/SCA RC1
- [ ] Critical = 0
- [ ] Gate 1 sign-off

---

### P2 · W1 (06.06 – 13.06) — Code freeze + UAT старт

**QA**
- [ ] RC1 smoke staging
- [ ] UAT Day 1–3 с PO
- [ ] Sanity automation

**DevOps**
- [ ] Tag 14.1-rc1
- [ ] Disable auto-deploy
- [ ] CAB draft старт ⚡

**Security**
- [ ] RC1 SAST gate
- [ ] SCA gate
- [ ] CVE triage

---

### P2 · W2 (16.06 – 20.06) — UAT + Perf параллельно

**QA**
- [ ] UAT продолжение
- [ ] Perf test старт
- [ ] UAT defect retest

**DevOps**
- [ ] Staging stability
- [ ] Pre-prod sync ⚡
- [ ] Prod dashboards ⚡

**Security**
- [ ] Incremental scans
- [ ] UAT hotfix review
- [ ] WAF rules review

---

### P2 · W3 (23.06 – 27.06) — Perf + RC2 decision

**QA**
- [ ] Perf analysis
- [ ] UAT final scenarios
- [ ] RC2 Go/No-Go

**DevOps**
- [ ] Tune staging
- [ ] RC2 build if needed
- [ ] Runbook draft

**Security**
- [ ] Scan after perf fixes
- [ ] CVE delta RC1→RC2
- [ ] Security approval

---

### P2 · W4 (30.06 – 04.07) — Gate 2

**QA**
- [ ] Final staging regression
- [ ] QA summary report
- [ ] Handoff P3

**DevOps**
- [ ] Rollback drill pre-prod
- [ ] Runbook final
- [ ] CAB packet final

**Security**
- [ ] Security baseline final
- [ ] CVE Critical/High = 0
- [ ] Gate 2 sign-off

---

### P3 · W1 (07.07 – 11.07) — CAB + pre-prod

**QA**
- [ ] Pre-prod test suite
- [ ] Prod smoke script
- [ ] Support FAQ review

**DevOps**
- [ ] CAB submit
- [ ] Migration dry-run #1
- [ ] Secrets vault audit

**Security**
- [ ] CAB security appendix
- [ ] IAM prod review
- [ ] SIEM alerts prep

---

### P3 · W2 (14.07 – 18.07) — Миграции + мониторинг

**QA**
- [ ] Migration rollback tests
- [ ] Canary test plan
- [ ] Comms T-14

**DevOps**
- [ ] Dry-run #2 timed
- [ ] War room schedule
- [ ] Alert thresholds

**Security**
- [ ] Audit logging verify
- [ ] Patch High CVE
- [ ] Incident playbooks

---

### P3 · W3 (21.07 – 25.07) — Rollback drill + comms

**QA**
- [ ] Comms T-7
- [ ] Feature flag plan
- [ ] Prod smoke assignments

**DevOps**
- [ ] Rollback drill timed
- [ ] On-call roster
- [ ] Artifact immutability

**Security**
- [ ] Security on-call transfer
- [ ] Pre-deploy CVE check
- [ ] Threat model delta

---

### P3 · W4 (28.07 – 01.08) — Финальная готовность

**QA**
- [ ] Comms T-7 sent
- [ ] Go/No-Go dry-run
- [ ] Gate 3 prep

**DevOps**
- [ ] Prod infra pre-check
- [ ] Backup snapshot plan
- [ ] Deploy automation test

**Security**
- [ ] CVE sprint planning
- [ ] Gate 3 security checklist
- [ ] War room briefing

---

### P3 · W5 (04.08 – 08.08) — Gate 3 + старт деплоя

**QA**
- [ ] Gate 3 meeting
- [ ] Comms T-1
- [ ] War room standby

**DevOps**
- [ ] Gate 3 Go
- [ ] Pre-deploy checklist
- [ ] Deploy phase 1 prod

**Security**
- [ ] Security war room
- [ ] SIEM live
- [ ] Deploy authorization

---

### P3 · W6 (11.08 – 15.08) — Prod deploy + стабилизация

**QA**
- [ ] Post-deploy smoke
- [ ] Prod health daily
- [ ] Hotfix validation

**DevOps**
- [ ] Deploy phase 2–3
- [ ] Canary 5→25%
- [ ] Migration complete

**Security**
- [ ] Auth/TLS verify prod
- [ ] Passive surface scan
- [ ] Patch batch deploy

---

### P3 · W7 (18.08 – 22.08) — Стабильность prod

**QA**
- [ ] Full prod smoke
- [ ] Stable 48h tracking
- [ ] Gate 3 final prep

**DevOps**
- [ ] Config freeze prod
- [ ] Enhanced monitoring
- [ ] Deploy journal close

**Security**
- [ ] Final re-scan
- [ ] CVE = 0 confirm
- [ ] Gate 3 security pack

---

### P3 · W8 (25.08 – 27.08) — Gate 3 закрытие

**QA**
- [ ] Gate 3 QA sign-off
- [ ] Prod validation report
- [ ] Go-Live comms prep

**DevOps**
- [ ] Prod stable confirm
- [ ] CAB change close
- [ ] Go-Live trigger prep

**Security**
- [ ] Gate 3 security final
- [ ] Security bulletin
- [ ] Handoff P4

---

### P4 · W1 (28.08 – 05.09) — Go-Live + мониторинг

**QA**
- [ ] Public release smoke
- [ ] Support ticket triage
- [ ] Known issues update

**DevOps**
- [ ] Feature flags public
- [ ] Enhanced monitoring
- [ ] Hotfix P0 only

**Security**
- [ ] 24h security watch
- [ ] Auth anomaly dashboards
- [ ] Daily sec ops

---

### P4 · W2 (08.09 – 10.09) — Закрытие релиза

**QA**
- [ ] Retro participation
- [ ] Final QA sign-off
- [ ] Archive test report

**DevOps**
- [ ] BAU on-call restore
- [ ] CMDB update
- [ ] Temp env cleanup

**Security**
- [ ] Compliance package
- [ ] Close security project
- [ ] Gate 4 sign-off

---

## 7. Gate-чеклисты (исполняемые)

### Gate 0 — 14.05.2025 · Go на регресс

| # | Критерий | Owner | Статус |
|---|----------|-------|--------|
| 1 | Scope Document утверждён | PO | ☐ |
| 2 | Test Plan v1.0 | QA | ☐ |
| 3 | QA smoke green | QA + DO | ☐ |
| 4 | Security baseline: Critical = 0 | SEC | ☐ |
| 5 | CI green на release/14.1 | DO | ☐ |

**Решение:** ☐ Go  ☐ No-Go  **Подпись RM:** _____________

### Gate 1 — 05.06.2025 · Go на RC

| # | Критерий | Owner | Статус |
|---|----------|-------|--------|
| 1 | P0 = 0 | QA | ☐ |
| 2 | P1 ≤ 3 (waiver) | PO | ☐ |
| 3 | Тест-план ≥ 98% | QA | ☐ |
| 4 | RC-кандидат staging smoke | DO | ☐ |
| 5 | Critical security = 0 | SEC | ☐ |

**Решение:** ☐ Go  ☐ No-Go  **Подпись RM:** _____________

### Gate 2 — 04.07.2025 · Go на пром. вывод

| # | Критерий | Owner | Статус |
|---|----------|-------|--------|
| 1 | UAT sign-off | PO | ☐ |
| 2 | Perf SLO ok vs 14.0 | QA | ☐ |
| 3 | Runbook + rollback drill | DO | ☐ |
| 4 | CVE Critical/High = 0 | SEC | ☐ |
| 5 | Release Notes финал | PO | ☐ |
| 6 | CAB packet готов | RM | ☐ |

**Решение:** ☐ Go  ☐ No-Go  **Подпись RM:** _____________

### Gate 3 — 27.08.2025 · Go-Live / закрытие change

| # | Критерий | Owner | Статус |
|---|----------|-------|--------|
| 1 | Prod deploy по runbook | DO | ☐ |
| 2 | Post-deploy smoke 100% | QA | ☐ |
| 3 | Prod stable 48 ч | DO | ☐ |
| 4 | CVE = 0 | SEC | ☐ |
| 5 | CAB change closed | CAB | ☐ |

**Решение:** ☐ Go  ☐ No-Go  **Подпись RM:** _____________

### Gate 4 — 10.09.2025 · Закрытие релиза

| # | Критерий | Owner | Статус |
|---|----------|-------|--------|
| 1 | P0 prod = 0 | QA + TL | ☐ |
| 2 | Retro + action items | RM | ☐ |
| 3 | Артефакты архивированы | RM | ☐ |
| 4 | BAU restored | DO | ☐ |

**Решение:** ☐ Закрыт  ☐ Не закрыт  **Подпись RM:** _____________

---

## 8. Артефакты релиза 14.1

| # | Артефакт | Фаза | Owner | Срок | Статус |
|---|----------|------|-------|------|--------|
| 1 | Scope Document | P0 | PO | 28.04 | ☐ |
| 2 | Test Plan v1.0 | P0 | QA | 12.05 | ☐ |
| 3 | Security Baseline | P0 | SEC | 14.05 | ☐ |
| 4 | Regression Dashboard | P1 | QA | 15.05+ | ☐ |
| 5 | RC Artifact (14.1-rc1) | P2 | DO | 09.06 | ☐ |
| 6 | UAT Sign-off | P2 | PO | 27.06 | ☐ |
| 7 | Performance Report | P2 | QA | 27.06 | ☐ |
| 8 | Runbook + Rollback | P2 | DO | 03.07 | ☐ |
| 9 | Release Notes | P2 | PO | 04.07 | ☐ |
| 10 | CAB Ticket | P3 | RM | 07.07 | ☐ |
| 11 | Deploy Journal | P3 | DO | 08.08+ | ☐ |
| 12 | Prod Smoke Report | P3 | QA | 27.08 | ☐ |
| 13 | Stability Report | P3 | DO | 27.08 | ☐ |
| 14 | Support Playbook | P4 | SUP | 28.08 | ☐ |
| 15 | Retro Notes | P4 | RM | 08.09 | ☐ |
| 16 | Release Archive | P4 | RM | 10.09 | ☐ |

---

## 9. Метрики релиза 14.1

| Метрика | Цель | Факт |
|---------|------|------|
| Release Cycle Time (Gate 0 → Gate 3) | ≤ 90 р.д. | |
| Regression Efficiency (авто/всего) | ≥ 60% | |
| Escaped Defects P0 (14 дней post) | 0 | |
| Gate Slip Rate | ≤ 20% | |
| Hotfix MTTR (prod P0) | ≤ 4 ч | |
| CVE Lead Time Critical | ≤ 48 ч | |
| Rollback RTO (drill) | ≤ 30 мин | |
| UAT First-Pass (без RC2) | ≥ 80% | |

---

## 10. Риски и антипаттерны

| Риск / антипаттерн | Митигация в 14.1 |
|--------------------|------------------|
| CVE на трансфере | Shift-left: Gate 2 = CVE 0 |
| Scope creep | CR только через RM + PO |
| P0 в конце регресса | Bug triage 2×/день в W2–W3 |
| Rollback не работает | Drill на pre-prod до 04.07 |
| Big-bang deploy | Canary + feature flags |
| Августовские отпуска | On-call ротация до 01.08 |

---

## 11. Шаблон типового рабочего дня

Использовать в дни без отдельной недельной секции:

### [ДД.ММ.ГГГГ] — Фаза [PX], D[NN]: [Фокус дня]

**QA**
- [ ] ...

**DevOps**
- [ ] ...

**Security**
- [ ] ...

**RM end-of-day:**
- [ ] Burn-down обновлён
- [ ] Blockers эскалированы
- [ ] Завтрашние зависимости подтверждены

---

## 12. Быстрый старт (Release Manager)

1. Заполнить таблицу команды (раздел 2.1) и scope (раздел 1).
2. Скопировать Gate-чеклисты (раздел 7) в тикет релиза.
3. На kick-off 28.04 — согласовать параллельные потоки (раздел 3).
4. Еженедельно — сверяться с разделом 6, отмечать чеклисты.
5. На каждом Gate — 30-мин sync + протокол, не многочасовые meeting.
6. После Gate 4 — заполнить метрики (раздел 9) и retro.
7. Архивировать все артефакты (раздел 8) в release folder.

---

*Документ: эталонный кейс релиза 14.1. Версия 1.0. Процесс 2.0 (оптимизированный).*  
*PDF: `docs/release-14.1-reference-case.pdf` — сборка: `./scripts/build_release_14_1_pdf.sh`*
