# 03. Потоки интеграций

Все 44+ потока данных из реестра «Поток/Данные», сгруппированные по системам-приёмникам.

> ⚠️ Архитектурный риск: API Gateway, circuit breaker и retry-политики **отсутствуют** во всех системах ДПППС.

> SVG-рендер ключевой схемы (ABAI / SCADA): [svg/03-integrations-abai.svg](./svg/03-integrations-abai.svg)

![Интеграции ABAI](./svg/03-integrations-abai.svg)

## 3.1. Интеграции ИС ABAI

```mermaid
flowchart LR
    classDef ext fill:#FCE4EC,stroke:#C2185B,color:#880E4F
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef buf fill:#FFF8E1,stroke:#F9A825,color:#F57F17

    SCADA["SCADA-серверы ДЗО (ЭМГ)"]:::src
    MEMG["MySQL ЭМГ<br/>(буфер)"]:::buf
    MKTM["MySQL КТМ<br/>(буфер)"]:::buf
    MKMG["MySQL SCADA сервер КМГ<br/>(буфер)"]:::buf
    EGOV["data.egov.kz"]:::ext
    COMM["Commodities-API"]:::ext
    AD["Active Directory КМГ"]:::src
    DARCY["Darcy<br/>(РИГИС)"]:::src
    TLOG["Techlog"]:::src

    ABAI["🟢 ИС ABAI<br/>БД abaiprot (PostgreSQL)<br/>17 модулей"]:::sys

    SCADA -- "dbLink (MySQL→MySQL)<br/>1–30 сек • реал.время" --> MEMG
    MEMG -- "dbLink • ≤5 мин" --> MKTM
    MKTM -- "dbLink • ≤5 мин" --> MKMG
    MKMG -- "dbLink → ETL → PostgreSQL<br/>5–15 мин • ≤15 мин" --> ABAI

    EGOV -- "REST/HTTP без API Gateway<br/>по запросу • 1 сутки" --> ABAI
    COMM -- "REST/HTTP без circuit breaker/retry<br/>раз в сутки" --> ABAI
    AD -- "SSO LDAP • ≤1 мин" --> ABAI
    DARCY -- "API • 1–10 раз в сутки" --> TLOG

    ABAI -- "pg_dump / WAL-репликация<br/>ежедневно • ≤24 ч ⚠️ в Test/QA" --> BACKUP[("pg-backupVM1/VM2<br/>172.20.102.253/254")]
```

## 3.2. Интеграции АСДЦ (analytics)

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef ext fill:#FCE4EC,stroke:#C2185B,color:#880E4F
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef cons fill:#E1F5FE,stroke:#01579B,color:#01579B

    SAP_ANPZ["SAP АНПЗ"]:::src
    ONE_PNHZ["1С ПНХЗ"]:::src
    ONE_PKOP["1С ПКОП"]:::src
    MES_ANPZ["MES Honeywell АНПЗ"]:::src
    MES_PNHZ["MES ПНХЗ"]:::src
    QLIK["QlikSense Кумколь"]:::src
    NB["nationalbank.kz"]:::ext

    ASDC["🟢 АСДЦ<br/>iis.thkmg.kz<br/>MS SQL 2014 + .NET/PHP/AngularJS"]:::sys

    IS["ИШ (НПЗ/ДАЦ)"]:::cons
    KHD["КХД"]:::cons
    KMGD["KMG DATA"]:::cons

    SAP_ANPZ -- "SOAP/XML • каждые 2 ч" --> ASDC
    ONE_PNHZ -- "SOAP/XML • каждые 2 ч" --> ASDC
    ONE_PKOP -- "SOAP/XML • каждые 2 ч" --> ASDC
    MES_ANPZ -- "TCP/IP byte • каждые 15 мин" --> ASDC
    MES_PNHZ -- "TCP/IP byte • каждые 15 мин" --> ASDC
    QLIK -- "TCP/IP • ежедневно" --> ASDC
    NB -- "HTTP/XML • ежедневно" --> ASDC

    ASDC -- "REST API • номера вагонов" --> IS
    ASDC -- "REST API • переработка сырья" --> KHD
    ASDC -- "MS SQL хранимые процедуры" --> KMGD
```

## 3.3. Интеграции САПФИР (СЭД)

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef gov fill:#FFF3E0,stroke:#E65100,color:#BF360C
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20

    AD["Active Directory КМГ"]:::src
    SMTP["SMTP"]:::src
    ARIO["Directum Ario<br/>(захват из почты/папок)"]:::src
    ESEDO["ЕСЭДО<br/>(СОИ госорганов)"]:::gov

    SAP["🟢 САПФИР<br/>Directum RX<br/>docs.kmg.kz"]:::sys

    AD -- "LDAP • создание объектов домена" --> SAP
    SMTP -- "почтовый агент" --> SAP
    ARIO -- "служба ввода" --> SAP
    SAP <-- "SOAP/XML • каждые 10 мин ⚠️ высокая критичность" --> ESEDO
```

## 3.4. Интеграции СДД (контракты)

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef gov fill:#FFF3E0,stroke:#E65100,color:#BF360C
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef sib fill:#E1F5FE,stroke:#01579B,color:#01579B

    AD["Active Directory КМГ"]:::src
    SMTP["SMTP"]:::src
    TSP["НУЦ РК — TSP"]:::gov
    OCSP["НУЦ РК — OCSP"]:::gov
    SAP4["SAP S/4HANA"]:::src
    ISEZ["ИСЭЗ"]:::sib
    ASR["ASR"]:::sib

    SDD["🟢 СДД<br/>contract.kmg.kz<br/>Patroni HA + K8s"]:::sys
    EA["Электронный архив<br/>10.123.13.12"]:::sib

    AD -- "LDAP • ≤1 мин" --> SDD
    SMTP -- "уведомления" --> SDD
    TSP -- "REST • временная метка ЭЦП" --> SDD
    OCSP -- "REST • проверка отзыва ЭЦП" --> SDD
    SAP4 -- "Business Partner — RFC/REST<br/>ежедневно" --> SDD
    SAP4 -- "АВР (14 полей) — REST<br/>ежедневно" --> SDD
    SDD -- "REST + ЭЦП<br/>подписание АВР" --> ISEZ
    SDD -- "HTTP/JSON<br/>передача данных" --> ASR
    SDD -- "HTTP/JSON • по подписанию • ≤1 ч" --> EA
```

## 3.5. Интеграции HR-кластера (Team / Work)

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef ext fill:#FCE4EC,stroke:#C2185B,color:#880E4F
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20

    AD["Active Directory"]:::src
    ONE["1С Финансы/HR"]:::src
    SAPK["SAP КМГ"]:::src
    QSAM["Qsamruk.kz"]:::ext
    PROCT["Модуль прокторинга"]:::ext

    TEAM["🟢 Team (kmg.kz)<br/>Bitrix24"]:::sys
    WORK["🟢 Work (work.kmg.kz)<br/>Django + Vue"]:::sys
    BANPZ["🟢 Bitrix ANPZ"]:::sys
    IJ["iJanet АНПЗ"]:::src

    AD -- "LDAP • по расписанию" --> TEAM
    ONE -- "API XML/JSON • по регламенту" --> TEAM
    SAPK -- "API XML/JSON • по регламенту" --> TEAM
    TEAM -- "API • отпуска/командировки/АО" --> ONE
    TEAM -- "API • потребности, ДИ" --> WORK

    QSAM -- "редирект регистрация/отклики" --> WORK
    WORK -- "API • резюме, статусы" --> QSAM
    PROCT -- "REST API • тестирование" --> WORK
    TEAM <-- "вакансии / этапы отбора" --> WORK

    AD -- "LDAP" --> BANPZ
    SAPK -- "API XML/JSON" --> BANPZ
    BANPZ -- "API" --> IJ
    BANPZ -- "API" --> WORK
```

## 3.6. Интеграции Compliance Control

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef ext fill:#FCE4EC,stroke:#C2185B,color:#880E4F
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20

    KOMPRA["Kompra"]:::ext
    AD["Active Directory"]:::src
    SAP["SAP"]:::src

    CC["🟢 Compliance Control<br/>compliance.kmg.kz<br/>Angular + .NET + PG"]:::sys

    KOMPRA -- "REST/JSON • при заполнении формы" --> CC
    AD -- "REST/JSON • раз в сутки" --> CC
    SAP -- "SOAP/XML • 3 раза в сутки" --> CC
```

## 3.7. Интеграции Procu / Price (ЗАКУПКИ)

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef gov fill:#FFF3E0,stroke:#E65100,color:#BF360C
    classDef sys fill:#FFFDE7,stroke:#F9A825,color:#F57F17

    SAPP["SAP Price"]:::src
    GBDU["ГБД ЮЛ"]:::gov

    PRC["🟡 Procu / Price (ТЕСТ)<br/>price.kmg.kz<br/>Vue3 + Django/DRF + PG 17"]:::sys

    SAPP -- "REST/JSON • по запросу • H" --> PRC
    GBDU -- "REST/JSON • по запросу • L" --> PRC
```

## 3.8. Интеграции ИСУП и Интранета

```mermaid
flowchart LR
    classDef src fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20

    AD["Active Directory<br/>(LDAP/NTLM)"]:::src
    KHD["КХД"]:::src
    SMTP["SMTP"]:::src

    ISUP["🟢 ИСУП<br/>pmo.kmg.kz/pwa<br/>MS Project + SharePoint 2019"]:::sys
    PBI["Power BI<br/>(дашборды)"]:::sys
    INT["🟢 Интранет<br/>SharePoint 2016/2019"]:::sys

    AD -- "LDAP/NTLM • по запросу" --> ISUP
    KHD -- "по запросу • H" --> ISUP
    ISUP -- "автоподгрузка" --> PBI
    SMTP -- "уведомления" --> ISUP

    AD -- "LDAP/NTLM" --> INT
    SMTP -- "уведомления" --> INT
```

## 3.9. Сводная таблица потоков (по реестру документа)

| № | Поток / Данные | Источник | Приёмник | Технология | Частота | Критичность |
|---|---|---|---|---|---|---|
| 1 | РИГИС | Darcy | Techlog | API | 1–10 раз в сутки | 1 сутки |
| 1.1 | Телеметрия скважин | SCADA ДЗО | MySQL ЭМГ | dbLink | реал.время 1–30 сек | ≤1 мин |
| 1.2 | Телеметрия (буфер) | MySQL ЭМГ | MySQL КТМ | dbLink | по расписанию | ≤5 мин |
| 1.3 | Телеметрия (буфер) | MySQL КТМ | MySQL SCADA КМГ | dbLink | по расписанию | ≤5 мин |
| 1.4 | Телеметрия (загрузка) | MySQL SCADA КМГ | abaiprot (PG) | dbLink → ETL | 5–15 мин | ≤15 мин |
| 2 | Госреестры | data.egov.kz | ABAI Экономика | REST | по запросу | 1 сутки |
| 3 | Котировки сырья | Commodities-API | ABAI Экономика | REST | раз в сутки | 1 сутки |
| 4 | SSO ABAI | AD КМГ | ABAI | LDAP | по запросу | ≤1 мин |
| 5 | Производственные данные между модулями | Модули ABAI | Модули ABAI | общие таблицы/view (PG) | по событию | ≤1 мин |
| 6 | Бэкапы БД ABAI | abaiprot | pg-backupVM1/VM2 ⚠️ | pg_dump / WAL | ежедневно | ≤24 ч |
| 7.1 | Финансовые/произв. АНПЗ | SAP АНПЗ | АСДЦ | SOAP | каждые 2 ч | Высокая |
| 7.2 | Финансовые/произв. ПНХЗ | 1С ПНХЗ | АСДЦ | SOAP/XML | каждые 2 ч | Высокая |
| 7.3 | Финансовые/произв. ПКОП | 1С ПКОП | АСДЦ | SOAP/XML | каждые 2 ч | Высокая |
| 7.4 | MES АНПЗ | MES Honeywell | АСДЦ | TCP/IP byte | каждые 15 мин | Высокая |
| 7.5 | MES ПНХЗ | MES ПНХЗ | АСДЦ | TCP/IP byte | каждые 15 мин | Высокая |
| 7.6 | Аналитика QlikSense | QlikSense Кумколь | АСДЦ | TCP/IP byte | ежедневно | Высокая |
| 7.7 | Курсы валют | nationalbank.kz | АСДЦ | HTTP/XML | ежедневно | Средняя |
| 7.8 | Номера вагонов | АСДЦ | ИШ | REST | по регламенту | Высокая |
| 7.9 | Переработка сырья | АСДЦ | КХД | REST | по регламенту | Высокая |
| 7.10 | Данные АСДЦ | АСДЦ | KMG DATA | MS SQL хранимые процедуры | по регламенту | Высокая |
| 8 | Документооборот с госорганами | САПФИР | ЕСЭДО | SOAP/XML | каждые 10 мин | Высокая |
| 8.1 | Синхронизация пользователей | AD | САПФИР | LDAP | по событию | Высокая |
| 9.1 | Авторизация СДД | AD | СДД | LDAP | по запросу | ≤1 мин |
| 9.2 | TSP метка ЭЦП | НУЦ РК TSP | СДД | REST | при подписании | ≤30 сек |
| 9.3 | OCSP проверка ЭЦП | НУЦ РК OCSP | СДД | REST | при подписании | ≤30 сек |
| 9.4 | Business Partner | SAP S/4HANA | СДД | RFC/REST | ежедневно | 1 сутки |
| 9.5 | АВР 14 полей | SAP S/4HANA | СДД (АВР) | REST | ежедневно | 1 сутки |
| 9.6 | Подписание АВР | СДД | ИСЭЗ | REST + ЭЦП | по запросу | ≤5 мин |
| 9.7 | Договоры → ЭА | СДД | Электронный архив | HTTP/JSON | по событию | ≤1 ч |
| 10.1 | Данные ЮЛ | Kompra | Compliance Control | REST/JSON | при заполнении | Высокая |
| 10.2 | Синхронизация AD | AD | Compliance Control | REST/JSON | раз в сутки | Высокая |
| 10.3 | Финансовые данные | SAP | Compliance Control | SOAP/XML | 3 раза в сутки | Высокая |
| 11 | Договоры SAP↔ЭА | SAP | ЭА (10.123.13.12:1334) | HTTP/JSON | по запросу | Высокая |
| 12.1 | Вакансии Team→Work | Team | Work | API | по событию | Высокая |
| 12.2 | Этапы отбора Work→Team | Work | Team | API | по событию | Высокая |
| 12.3 | Резюме Work→Qsamruk | Work | Qsamruk.kz | API (в разработке) | по событию | Высокая |
| 13.1 | Кадры AD→Team | AD | Team | LDAP | по расписанию | Высокая |
| 13.2 | Финансы 1С→Team | 1С | Team | API XML/JSON | по расписанию | Высокая |
| 13.3 | Заявления Team→1С | Team | 1С | API/выгрузка | по событию | Высокая |
| 13.4 | Bitrix ANPZ→iJanet | Bitrix ANPZ | iJanet АНПЗ | API | по событию | Высокая |
| 14.1 | Аутентификация ИСУП | AD | ИСУП | LDAP/NTLM | по запросу | Высокая |
| 14.2 | Финансовые КХД→ИСУП | КХД | ИСУП | — | по запросу | Высокая |
| 14.3 | Аналитика ИСУП→Power BI | ИСУП | Power BI | автоподгрузка | по запросу | Средняя |
| 15 | ГБД ФЛ↔Бюро (отключено) | ГБД ФЛ через ESB | Бюро пропусков | REST/JSON | при оформлении | Высокая |
| 16 | HikVision↔Бюро (отключено) | HikVision | Бюро пропусков | REST/HTTP | каждые 3 сек | Высокая |
