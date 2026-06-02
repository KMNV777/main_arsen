# 06. Сводная матрица информационных систем

| ИС | Сокр. | Стек | Хостинг | Статус | C/I/A | SLA P1 | Код SAW | Лицензия |
|---|---|---|---|---|---|---|---|---|
| ИС «ABAI» | ABAI | Vue 2.7 + Laravel / Django + FastAPI + GeoServer / PostgreSQL + MySQL / Spark+Kafka+Druid | QazCloud Koshy + GPU IBM POWER 9 | 🟢 PROD | 4/4/4 | 30 мин / 8 ч | IS-ABAI-001 | Собственная (КМГ-Инжиниринг / ДПППС) |
| САПФИР | СЭД | C# / IS-Builder / Directum RX / MS SQL+PG+MongoDB | QazCloud Aqqol | 🟢 PROD | — | 15 мин / 2 ч | IS.209.156 | Внешний вендор: Directum |
| АСДЦ | АСДЦ | AngularJS+Knockout+Razor / .NET+PHP / **MS SQL 2014 ⚠️** | QazCloud Aqqol | 🟢 PROD ⚠️ legacy | 3/3/3 | матричный 0,5–2 ч | IS.212.222 | Собственная (ДПППС) |
| СДД | СДД | Golang / React+TS / PG Patroni HA / K8s | QazCloud Aqqol | 🟢 PROD 🛡️ | — | 15 мин / 2 ч | — | Собственная (ДПППС) |
| ИС УТО / УТО ЭМГ | УТО | Vue + Django + PG + MinIO | QazCloud Koshy / Локально ЭМГ | 🟢 PROD | 2/2/2 | 15 мин / 2 ч | — | Собственная (НМА) |
| ИСОТ / ЭНД | HSE | Vue + Django + PG + RabbitMQ + Redis | QazCloud Koshy | 🟢 PROD 🛡️ | 2/2/2 | 15 мин / 2 ч | — | Собственная (ДПППС) |
| Work | Work | Vue + Django REST + asyncio + PG | QazCloud Koshy | 🟢 PROD | — | 15 мин / 2 ч | IS.210.188 | Собственная (ДПППС) |
| Procu / Price | Procu | Vue3 + Django/DRF + PG 17 + MinIO + Celery + Redis | QazCloud Aqqol | 🟡 TEST ⚠️ нет бэкапов | — | 15 мин / 2 ч | — | Собственная (ДПППС) |
| Team (Bitrix24) | Team | Bitrix24 / PHP + MySQL/MariaDB | QazCloud Koshy | 🟢 PROD 🛡️ | ПДн | — | IS.210.187 | Внешний вендор: 1С-Битрикс24 |
| Интранет SharePoint | Интранет | SharePoint 2016/2019 + MS SQL Always On | QazCloud Aqqol | 🟢 PROD | — | — | — | Microsoft SharePoint + MS SQL |
| ИСУП | ИСУП | MS Project Server 2019 + SharePoint 2019 + MS SQL | QazCloud Aqqol | 🟢 PROD | — | 0,5 ч / 2 ч | — | Microsoft Project + SharePoint |
| АИСЭМ | АИСЭМ | React + Node.js + PG + RabbitMQ + Redis | QazCloud Aqqol | 🟢 PROD ⚠️ 1 разработчик | — | 15 мин / 2 ч | IS-212-24 | Собственная (контракт 943617/2024/1, до 31.12.2026, 253,85 млн ₸) |
| Compliance Control | Compli | Angular + .NET + PG + Docker | QazCloud Aqqol | 🟢 PROD | — | 15 мин / 2 ч | — | Собственная (ДПППС) |
| BoardMaps | BM | TS + .NET (C#) + MS SQL + Redis + **Vault** | QazCloud Aqqol | 🟢 PROD 🛡️ | — | — | IS.212.216 | Внешний вендор: ОАО «Дэшборд Системс» |
| БДА | БДА | .NET + PG 11 + **WAF** 🛡️ | QazCloud Aqqol | 🟢 PROD | 2/2/2 | — | IS.211.212 | Собственная |
| Bitrix ANPZ | ANPZ | Bitrix24 / PHP + MySQL | On-Prem АНПЗ | 🟢 PROD | — | — | — | Внешний вендор: 1С-Битрикс24 |
| KMG Petrochem (Bitrix) | Petrochem | Bitrix24 / PHP + MySQL | QazCloud | 🟢 PROD | — | — | — | Внешний вендор: 1С-Битрикс24 |
| КМГ-Кумколь (Bitrix) | KMKL | Bitrix24 / PHP + MySQL | QazCloud | 🟢 PROD | — | — | — | Внешний вендор: 1С-Битрикс24 |
| Сайт КМГ | www.kmg.kz | Bitrix / PHP + MySQL | QazCloud (172.22.37.30) | 🟢 PROD | — | — | — | Собственная на Bitrix |
| Сайт КМГ-Кумколь | kmg-kumkol.kz | Bitrix / PHP + MySQL 5.7.36 + Redis/Memcached | Cloud | 🟢 PROD | — | — | — | Собственная на Bitrix |
| Сайт KPI | kpi.kz | Bitrix / PHP + MySQL 8.0.30 | Cloud (83.97.77.20) | 🟢 PROD | — | — | — | Собственная на Bitrix |
| Сайт КазГПЗ | kazgpz | Bitrix / PHP + MySQL | QazCloud (172.22.37.30) | 🟢 PROD | — | — | — | Собственная на Bitrix |
| Электронный архив | ЭА | FastAPI + React + PG | QazCloud Koshy | 🔴 ВЫВОД (Documentum → собств.) | 2/2/2 | — | IS.211.027 | Собственная |
| Санау | Санау | — | QazCloud Aqqol | 🔴 ВЫВОД | 2/2/2 | — | IS.212.212 | Собственная |
| Бюро пропусков | Бюро | Angular CLI 11.2 + .NET Core + Hangfire + PG 11 + Kafka | — | 🔴 ОТКЛЮЧЕНА (договор расторгнут) | — | — | — | Договор расторгнут |

## Командные роли по системам (PM / TL / DevOps / Бизнес)

| Система | Роли |
|---|---|
| **ABAI** | PM Усманов Н., TL Курмангожин Н., Бизнес Базарбеков Т. |
| **САПФИР** | TL/DevOps Максутбеков А., Бизнес Тылеуов Б.А. (УДО) |
| **АСДЦ** | TL Михалев А.Ю., разработчики Милько Д., Байдуллаев А., аналитик Катаева Д., Бизнес Букобаев Т. |
| **СДД** | TL Дюсембаев И.М. |
| **ИСОТ** | PM Өтеміс Ж., TL/DevOps Нуркин А., Бизнес Оразбеков Ш. |
| **Work** | PM Ахамбаев Р., TL Нұрғалиев А., DevOps Корпетанов К. |
| **Procu/Price** | PM Камбаров А., TL Нуркин А., Бизнес Меткерим А. |
| **АИСЭМ** | PM Калиева К., TL/DevOps Курмангожин Н. |
| **Compliance Control** | PM Давтян Н., разработчик Дюсембаев И. |
| **BoardMaps** | PM Габиден Е.Г., DevOps Корпетанов К.С. |
| **ИСУП / Интранет** | PM Абдрахманова А.Д., DevOps Корпетанов К.С., Бизнес Бекниязов Б. |
| **Электронный архив** | PM Габиден Е.Г., TL Нуркин А.Ж., DevOps Корпетанов К.С. |
| **БДА / Санау** | TL Дюсембаев И.М., DevOps Корпетанов К.С., Support Орынбаев А.Н. |
| **Корп. порталы (Team / ANPZ / Petrochem / КМКЛ)** | PM Ахамбаев Р., TL Нұрғалиев А. |
| **Сайты КМГ / КазГПЗ** | PM Байтулеуова А.Т., DevOps Мәлік М. |

## Каналы поддержки

- **ServiceDesk**: 1444 / 8 800 080 1444 — для большинства систем
- **sms@kmg.kz / ITSM / sms.kmg.kz** — заявочная система
- **BoardMaps (внешний вендор)**: support@boardmaps.com / 8-800-555-1869 (ОАО «Дэшборд Системс»)
- **График**: 8:00–17:30 / 24×7 (большинство), 9:00–18:00 (ИСОТ, Compliance Control)
- **Бюро пропусков**: поддержки нет (договор расторгнут)

## Доменные имена ИС ДПППС

| Поддомен / адрес | Система |
|---|---|
| abai.kmg.kz | ABAI |
| docs.kmg.kz | САПФИР (Directum RX) |
| iis.thkmg.kz | АСДЦ |
| contract.kmg.kz, api.contract.kmg.kz, s3.contract.kmg.kz, gitlab.contract.kmg.kz | СДД |
| hse.kmg.kz, hse2test.kmg.kz | ИСОТ |
| aisem.kmg.kz | АИСЭМ |
| price.kmg.kz, price2test.kmg.kz | Procu/Price |
| work.kmg.kz | Work |
| buro.kmg.kz | Бюро пропусков (отключена) |
| compliance.kmg.kz | Compliance Control |
| bsd.kmg.kz, bsd-test.kmg.kz | BoardMaps |
| pmo.kmg.kz/pwa | ИСУП |
| intranet.kmg.kz, mysite.kmg.kz, msp.kmg.kz | Интранет SharePoint |
| kmg.kz, team.kmg.kz | Team Bitrix |
| anpz.kz | Bitrix ANPZ |
| www.kmg.kz, kmg-kumkol.kz, kpi.kz, kazgpz.kmg.kz | Корп. сайты |

## Репозитории кода

| Репозиторий | Системы |
|---|---|
| **gitkmkl.kmg.kz** (основной GitLab on-prem) | smart-kmg/munaiagyny/hseapp-{backend-django, frontend-vuejs} (ИСОТ); smart-kmg/procu/{front_price, price} (Procu/Price); smart-kmg/e-archive/archive-manager (Электронный архив); smart-kmg/ksb/{www.kmg.kz, kpi, kmg-kumkol.kz} (корпсайты) |
| **gitlab.contract.kmg.kz** (10.123.13.129) — отдельный GitLab для СДД с Registry и Runner | СДД |
| Собственный **Git Extensions** | ABAI |
