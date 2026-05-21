# Архитектура интеграций АО «Эмбамунайгаз»

Документ построен по матрице интеграций и разделу **7.6.1.3 «Текущая карта автоматизации ЭМГ»** (Программа ИТ и цифровизации КМГ, 2025–2028).

---

## 1. Общий ландшафт корпоративных систем

```mermaid
flowchart TB
    subgraph Identity["Идентификация и доступ"]
        AD["Active Directory<br/>(LDAP)"]
    end

    subgraph Security["Информационная безопасность"]
        DLP["Solar Dozor<br/>(DLP)"]
        FW["Forcepoint Web Gateway"]
        FUDOPAM["FUДOPAM<br/>(PAM)"]
    end

    subgraph Docs["Документооборот и архив"]
        Directum["Directum<br/>(СЭД + BPM)"]
        Alfresco["Alfresco ECM"]
        EA["Электронный архив<br/>(Азия-Софт, CMIS)"]
    end

    subgraph Finance["Финансы и планирование"]
        SAP["SAP ERP"]
        SAS["SAS-FM"]
        FC["FC — фин. консолидация"]
        NB["Нацбанк<br/>(курсы валют)"]
        BV["БВУ / банк<br/>(MT940, MT103)"]
        Platts["Platts.com"]
    end

    subgraph HR["Кадры и персонал"]
        UP["ПК «Управление персоналом»"]
        ZUP["1С — зарплата"]
        EPASS["E-Pass"]
    end

    subgraph Ops["Операционные системы"]
        ABAI["ИС ABAI / ИМ<br/>10.32.10.99"]
        ISUTO["ИСУТО"]
        ARGUS["Argus Pro<br/>(GPS-мониторинг)"]
        SP["sPoint"]
        Procu["Procu"]
        AVR["AVR + SAP"]
        KGIS["КГИС"]
        Zhyldyz["Жулдыз"]
    end

    subgraph NSI["НСИ и закупки"]
        ASUNSI["АСУНСИ"]
        ISEZ["ИСЭЗ"]
    end

    AD --> Directum & Alfresco & KGIS & DLP & FUDOPAM & EPASS & Zhyldyz & Procu
    Exchange["Microsoft Exchange"] --> DLP
    FW --> DLP

    SAP <-->|SAP PO / XML| ASUNSI
    SAP <-->|RFC / CSV| SAS
    SAP <-->|XML| ISUTO & SCADA & AVR & EA & Platts
    SAP <-->|SOAP| UP
    SAP <-->|CSV| ZUP & FC & BV & NB & ISEF["ИС ЭСФ"]
    UP <-->|DB functions| UP
    EA <-->|CMIS| EA
    Alfresco --> AD
    Directum --> AD
    Procu --> ASUNSI & ISEZ & AD
    ISUTO <-->|SOAP XML| SAP
    ARGUS -->|REST JSON| ISUTO
    SP -->|REST JSON| KHD["КХД АО НК КМГ"]
    AVR <-->|API XML| SAP

    ABAI -.->|см. раздел 2| Ops
```

**Роль Active Directory:** единый источник учётных записей (логин, UPN, ФИО, e-mail) для Directum, Alfresco, КГИС, DLP, FUDOPAM, E-Pass, Жулдыз, Procu — односторонний LDAP, online, автоматически.

---

## 2. Архитектура ИС ABAI (информационная модель, хост 10.32.10.99)

Центральный контур сбора телеметрии, обогащения данных месторождений и рассылки аналитики. Запуск задач — **cron** + **Django/Celery** + сигналы `post_save`.

```mermaid
flowchart TB
    subgraph IM["ИМ / cmv2 — хост 10.32.10.99"]
        Cron["Планировщик cron"]
        Scripts["Скрипты сбора<br/>(OPC, Modbus, DB)"]
        Django["Django-приложение"]
        Celery["Celery workers"]
        LocalDB[("Локальная БД<br/>теги, скважины,<br/>отчёты ПРС")]
    end

    subgraph Sources["Источники данных (поставщики)"]
        PG_ABAI[("PostgreSQL<br/>ИС ABAI")]
        OPC_ISUN["OPC DA — Kepware<br/>192.168.17.186<br/>(ИСУН)"]
        OPC_KOA["OPC DA — реклоузеры КОА<br/>10.32.10.98"]
        OPC_UA["OPC UA — АСУТП/ТМ<br/>172.16.x, 192.168.x"]
        Modbus["Modbus TCP — КУУН<br/>Кайнар, Карсак, Прорва, УАЗ"]
        SDMO[("MySQL SDMO<br/>4 региона Danfoss")]
        KTM[("MySQL KTM<br/>Floboss S600+")]
        KOADB[("MySQL koa-cm<br/>WinCC HDA")]
        EMGDB[("PostgreSQL emg<br/>10.32.10.90<br/>схема emg_skv")]
    end

    subgraph Consumers["Получатели / исходящие интеграции"]
        Analytics["Сервис аналитики ЭМГ<br/>108.181.186.12:8099<br/>POST /tags/update/<br/>POST /wells/update/"]
        Packets["packet_service<br/>10.32.10.90:8951<br/>/packets/recloser"]
        Speech["Распознавание речи<br/>10.32.10.90:8777<br/>/api/audio-recognition/"]
        SMTP["SMTP Gmail<br/>noreply@dlc.kz<br/>уведомления, XLSX"]
    end

    Cron --> Scripts
    Scripts --> LocalDB
    Django --> LocalDB
    Celery --> LocalDB
    Django --> Speech
    Django --> SMTP

    PG_ABAI -->|"SQL read<br/>08:00, 13:30, 18:00"| Scripts
    OPC_ISUN -->|"OPC DA / OpenOPC+Pyro4<br/>:00 PUMP; :01 RVS+GAS"| Scripts
    OPC_KOA -->|"OPC DA<br/>каждые 5 мин"| Scripts
    OPC_UA -->|"opcuа<br/>каждые 5 мин"| Scripts
    Modbus -->|"pymodbus<br/>каждые 7 мин"| Scripts
    SDMO -->|"PyMySQL<br/>:47 hourly; 07:17 daily"| Scripts
    KTM -->|"PyMySQL<br/>вручную"| Scripts
    KOADB <-->|"read + DELETE hda<br/>cron на промысле КОА"| Scripts
    EMGDB <-->|"chrp_well working 0/1<br/>каждые 15 мин"| Scripts

    Scripts --> LocalDB
    LocalDB -->|"REST JSON<br/>каждые 5 мин"| Analytics
    LocalDB -->|"REST JSON<br/>каждые 5 мин"| Packets
```

### 2.1. Потоки данных ABAI (детализация)

| Источник | Протокол / формат | Данные | Частота | Направление |
|----------|-------------------|--------|---------|-------------|
| ИС ABAI (PostgreSQL) | SQL | Фонд скважин, статусы, техрежимы, категории, ремонты | 08:00, 13:30, 18:00 | → ИМ (read) |
| Kepware / ИСУН | OPC DA | PUMP, ISUN_RVS, ISUN_GAS | :00 / :01 (2 ч) | → ИМ |
| КОА реклоузеры | OPC DA | Мощности, токи, U, МТО/МТЗ | 5 мин | → ИМ → packet_service |
| АСУТП/ТМ (12+ OPC UA) | OPC UA | РГС, расходы, насосы, задвижки (ATB, DMB, GRN…) | 5 мин | → ИМ → аналитика |
| Modbus TCP КУУН | Modbus | Расходомеры, скважины УАЗ | 7 мин | → ИМ |
| SDMO (4× MySQL) | SQL | Дисбаланс ЧРП, суточные avg | :47 / 07:17 | → ИМ |
| KTM Floboss | SQL | СИКН 2hours_kto | вручную | → ИМ |
| koa-cm WinCC HDA | SQL | hdadatatable, ABK/KJS | cron КОА | ↔ ИМ |
| emg (ИСУ-ЭМГ) | SQL | chrp_well.working | 15 мин | ↔ ИМ |
| Аналитика ЭМГ | REST JSON | Теги, скважины | 5 мин | ИМ → |
| packet_service | REST JSON | Реклоузеры bd 522/601 | 5 мин | ИМ → |
| Распознавание речи | multipart → JSON | Аудио рапортов ПРС | online | ↔ ИМ |
| SMTP | RFC 5322 | СИЗ, добыча, XLSX-реестры | cron + signals | ИМ → |

---

## 3. Интеграции SAP ERP (хаб предприятия)

```mermaid
flowchart LR
    SAP["SAP ERP"]

    SAP <-->|SAP PO XML| NSI["АСУНСИ"]
    SAP <-->|API XML| UTO["ИСУТО"]
    SAP -->|API XML in| SCADA["SCADA"]
    SAP <-->|API XML| AVR["AVR"]
    SAP <-->|API| EA["Электронный архив"]
    SAP <-->|API| DOC["Documentum"]
    SAP -->|XLSX file| SIZ["СИЗ"]
    SAP -->|CSV| ZP["1С зарплата"]
    SAP -->|CSV| FC["FC консолидация"]
    SAP -->|CSV| HR["Кадры УП"]
    SAP <-->|MT940/103| BANK["БВУ"]
    SAP -->|XML| NB["Нацбанк"]
    SAP <-->|XML| ESF["ИС ЭСФ"]
    SAP -->|API| PL["Platts"]
    SAS["SAS-FM"] -->|RFC .sas7bdat / CSV| SAP
```

---

## 4. Слои архитектуры ABAI (логическое представление)

```mermaid
flowchart TB
    subgraph L1["L1 — Промышленные системы"]
        ISUN["ИСУН"]
        ASUTP["АСУТП / ТМ"]
        KOAP["Промысел КОА"]
        SDMO_P["АСУ ЧРП SDMO"]
        SIKn["СИКН Floboss"]
    end

    subgraph L2["L2 — Шлюзы и протоколы"]
        Kepware["Kepware OPC DA"]
        OPCUA["OPC UA серверы"]
        ModbusGW["Modbus TCP"]
        WinCC["WinCC HDA"]
    end

    subgraph L3["L3 — Интеграционный слой ИМ"]
        ETL["Cron + Python ETL<br/>refresh_views, update_*_tags"]
        API_OUT["REST-клиенты<br/>(аналитика, пакеты)"]
        Notify["SMTP / Celery / Signals"]
    end

    subgraph L4["L4 — Корпоративные сервисы"]
        BI["Аналитика ЭМГ :8099"]
        PKTS["packet_service :8951"]
        ASR["Speech API :8777"]
        Mail["Корп. почта"]
    end

    ISUN --> Kepware --> ETL
    ASUTP --> OPCUA --> ETL
    KOAP --> WinCC --> ETL
    KOAP --> ModbusGW --> ETL
    SDMO_P --> ETL
    SIKn --> ETL

    ETL --> API_OUT --> BI & PKTS
    ETL --> Notify --> Mail
    ETL --> ASR
```

---

## 5. Системы с интеграцией только через AD (без детализации в матрице)

Следующие системы в реестре описаны преимущественно как потребители LDAP-атрибутов: **E-Pass**, **Жулдыз**, **КГИС**, **FUДOPAM**, **Solar Dozor** (дополнительно Exchange, Forcepoint), **Directum**, **Alfresco**.

**ИС ABAI** (п. 3 матрицы) — отдельное описание интеграций вынесено в разделы 2–4 (детализация по п. 12, хост ИМ).

---

## Источники

| Документ | Содержание |
|----------|------------|
| Матрица интеграций (18 систем) | Роли, протоколы, форматы, направление, частота, способ запуска |
| Программа ИТ КМГ 2025–2028, § 7.6.1.3 | Текущая карта автоматизации ЭМГ (контекст) |
