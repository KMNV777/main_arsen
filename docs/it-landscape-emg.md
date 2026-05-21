# Общая схема ИТ-ландшафта АО «Эмбамунайгаз»

## Схема (файлы для скачивания)

| Формат | Файл | Для чего |
|--------|------|----------|
| **SVG** | [`it-landscape-emg-general.svg`](it-landscape-emg-general.svg) | Копирование в Word, PowerPoint, Visio, Figma |
| **PNG** | [`it-landscape-emg-general.png`](it-landscape-emg-general.png) | Вставка в презентации, Confluence, печать |

![Общий ИТ-ландшафт ЭМГ](it-landscape-emg-general.png)

---

## Структура ландшафта (слои)

```mermaid
flowchart TB
    subgraph L0["L0 · Организация"]
        KC[КЦ КМГ] --- EMG["АО Эмбамунайгаз"] --- KMGI[КМГИ]
    end

    subgraph L1["L1 · Порталы"]
        Team[Team] --- Intranet[Интранет] --- ISUP[ИСУП] --- CC[Compliance]
    end

    subgraph L2["L2 · Бизнес-приложения"]
        direction LR
        subgraph P[Производство]
            ABAI[ИС ABAI] --- ASDC[АСДЦ]
        end
        subgraph T[Транспорт]
            UTOE[УТО ЭМГ] --- UTO[ИС УТО]
        end
        subgraph F[Финансы]
            SAP[SAP ERP]
        end
        subgraph Z[Закупки]
            Procu[Procu] --- SDD[СДД]
        end
        subgraph D[Документы]
            SAPFIR[САПФИР]
        end
        subgraph H[HSE]
            ISOT[ИСОТ/ЭНД]
        end
    end

    subgraph L3["L3 · Платформа"]
        AD[Active Directory] --- ESB[Шина интеграций] --- KHD[КХД КМГ]
    end

    subgraph L4["L4 · OT · ЭМГ"]
        IM[ИМ 10.32.10.99] --- OPC[OPC/Modbus] --- BI[Аналитика]
    end

    subgraph L5["L5 · ИБ"]
        DLP[Solar Dozor] --- PAM[FUDOPAM]
    end

    EMG --> L2
    ABAI --> IM
    SAP --> ESB
    L2 --> AD
```

---

## Системы по доменам

| Домен | Ключевые ИС |
|-------|-------------|
| **Производство** | ИС ABAI (abai.kmg.kz), АСДЦ, sPoint, Жулдыз, SCADA |
| **Транспорт** | ИС «УТО ЭМГ», ИС «УТО», Argus Pro |
| **Финансы** | SAP ERP, SAS-FM, 1С, AVR, FC, БВУ, Platts |
| **Закупки** | Procu/Price, СДД (contract.kmg.kz), ИСЭЗ, АСУНСИ |
| **Документы** | САПФИР/Directum, Alfresco, электронный архив |
| **Кадры / HSE** | Управление персоналом, E-Pass, ИСОТ/ЭНД (hse.kmg.kz) |
| **ГИС** | КГИС, БДА |
| **Платформа** | Active Directory, шина (SOAP/REST/XML/CSV), КХД КМГ |
| **OT (промысел)** | ИМ/cmv2, OPC DA/UA, Modbus, PostgreSQL/MySQL, аналитика ЭМГ |
| **ИБ** | Solar Dozor, FUDOPAM, Forcepoint, Exchange |
| **Вывод** | Documentum, ИС «Санау» · **Отключена:** buro.kmg.kz |

---

## Связанные материалы

- Детальные интеграции и потоки данных: [`architecture-emg-integrations.md`](architecture-emg-integrations.md)
