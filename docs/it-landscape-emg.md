# Общая схема ИТ-ландшафта АО «Эмбамунайгаз»

Собрано из:
- **Матрицы интеграций** (19 ИС) — реестр и протоколы
- **Матрицы КЦ – ЭМГ – КМГИ** — охват по организациям
- **Программы ИТ КМГ 2025–2028** (§ 7.6.1.3)

---

## Файлы схемы

| Формат | Файл |
|--------|------|
| **draw.io** | [`drawio/it-landscape-emg-general.drawio`](drawio/it-landscape-emg-general.drawio) — редактируемая схема (diagrams.net) |
| **SVG** | [`svg/06-it-landscape-general.svg`](svg/06-it-landscape-general.svg) — для Word / PowerPoint / Figma |
| **Все draw.io** | [`drawio/README.md`](drawio/README.md) |
| **Все SVG** | [`svg/README.md`](svg/README.md) — полный набор схем из architecture-emg-integrations |
| **PNG** | [`it-landscape-emg-general.png`](it-landscape-emg-general.png) — предпросмотр |
| **Реестр 19 ИС** | [`it-landscape-emg-registry.md`](it-landscape-emg-registry.md) — таблица интеграций |
| **Потоки ABAI/ИМ** | [`architecture-emg-integrations.md`](architecture-emg-integrations.md) |

![Общий ИТ-ландшафт ЭМГ](it-landscape-emg-general.png)

---

## Общая схема (19 систем + SAP-хаб)

```mermaid
flowchart TB
    subgraph L0["L0 · Организация"]
        KC[КЦ КМГ] --- EMG["Эмбамунайгаз"] --- KMGI[КМГИ]
    end

    subgraph L3["L3 · Платформа"]
        AD[Active Directory]
        SAP["SAP ERP №14"]
        ESB["Шина XML/CSV/SOAP"]
        KHD[КХД КМГ]
        ASUNSI[АСУНСИ]
    end

    subgraph L2["L2 · Реестр ИС — матрица интеграций"]
        D2["№2 Directum"]
        D3["№3 ABAI"]
        D4["№4 Solar Dozor"]
        D5["№5 FUDOPAM"]
        D6["№6 E-Pass"]
        D7["№7 Argus Pro"]
        D8["№8 1С"]
        D9["№9 SAS-FM"]
        D10["№10 Жулдыз"]
        D11["№11 sPoint"]
        D12["№12 ИМ"]
        D13["№13 Упр.персоналом"]
        D15["№15 ИС УТО"]
        D16["№16 Alfresco"]
        D17["№17 КГИС"]
        D18["№18 Procu"]
        D19["№19 AVR+"]
    end

    subgraph L4["L4 · OT — интеграции ИМ №12"]
        OPC[OPC DA/UA]
        MB[Modbus]
        DB[(MySQL/PG)]
        SVC[Аналитика · packet · Speech · SMTP]
    end

    subgraph L5["L5 · ИБ"]
        EX[Exchange]
        FP[Forcepoint]
    end

    EMG --> D3 & D12
    D3 --> D12
    D12 --> OPC & MB & DB --> SVC
    D2 & D5 & D6 & D10 & D16 & D17 & D18 --> AD
    D4 --> EX & FP
    D9 & D8 & D13 & D15 & D19 --> SAP
    D11 --> KHD
    D18 --> ASUNSI
    D7 --> D15
    SAP --> ESB
```

---

## Реестр 19 информационных систем

| № | Система | Роль в ландшафте |
|---|---------|------------------|
| 2 | Directum | СЭД, документооборот → AD |
| 3 | ИС ABAI | Производство, abai.kmg.kz → ИМ |
| 4 | Solar Dozor | DLP ← Exchange, Forcepoint |
| 5 | FUDOPAM | PAM → AD |
| 6 | E-Pass | Пропуска → AD |
| 7 | Argus Pro | GPS-мониторинг → ИС УТО |
| 8 | 1С | Зарплата ← SAP |
| 9 | SAS-FM | Фин. планирование → SAP |
| 10 | Жулдыз | Мониторинг месторождения → AD |
| 11 | sPoint | Наряды-допуски → КХД |
| **12** | **ИМ (10.32.10.99)** | **OT-хаб: OPC, Modbus, БД, REST** |
| 13 | Управление персоналом | Кадры ↔ SAP |
| 14 | **SAP ERP** | **Центральный хаб интеграций** |
| 15 | ИС УТО | Транспорт ↔ SAP |
| 16 | Alfresco | ECM → AD |
| 17 | КГИС | ГИС → AD |
| 18 | Procu | Закупки ↔ АСУНСИ, ИСЭЗ |
| 19 | AVR+ | Акты работ ↔ SAP |

---

## Корпоративный контур КМГ (дополнение к матрице)

| ИС | URL | ЭМГ |
|----|-----|:---:|
| САПФИР / Directum | docs.kmg.kz | ✓ |
| АСДЦ | iis.thkmg.kz | ✓ |
| ИС УТО ЭМГ | — | ✓ |
| ИСОТ/ЭНД | hse.kmg.kz | ✓ |
| Team, Интранет, ИСУП, Compliance | kmg.kz, intranet… | ✓ |
| Documentum, Санау | — | **ВЫВОД** |

---

## Как читать схему

1. **SAP ERP (№14)** — центр финансовых и кадровых интеграций.
2. **ИМ (№12)** — центр промысловой телеметрии (связан с ABAI №3).
3. **Active Directory** — идентификация для Directum, Alfresco, КГИС, Procu, E-Pass, Жулдыз, FUDOPAM.
4. Детальные протоколы, cron и IP — в [`it-landscape-emg-registry.md`](it-landscape-emg-registry.md) и [`architecture-emg-integrations.md`](architecture-emg-integrations.md).
