# 04. Инфраструктура и хостинг

> SVG-рендер: [svg/04-infrastructure.svg](./svg/04-infrastructure.svg)

![Инфраструктура и хостинг](./svg/04-infrastructure.svg)

```mermaid
flowchart TB
    classDef cloud fill:#E3F2FD,stroke:#1976D2,color:#0D47A1,stroke-width:2px
    classDef onprem fill:#FFF3E0,stroke:#E65100,color:#BF360C,stroke-width:2px
    classDef sys fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    classDef test fill:#FFFDE7,stroke:#F9A825,color:#F57F17
    classDef out fill:#FFEBEE,stroke:#C62828,color:#B71C1C
    classDef gpu fill:#F3E5F5,stroke:#6A1B9A,color:#4A148C

    %% QazCloud Koshy
    subgraph QC1["☁️ QazCloud — VDC Koshy"]
        direction TB
        K1["🟢 ИС ABAI<br/>BD abaiprot (PostgreSQL)<br/>+ MySQL SCADA-буферы<br/>CentOS 7 ⚠️ EOL<br/>Docker + Portainer (172.20.102.23)"]:::sys
        K2["🟢 ИС УТО + ИСОТ + Work<br/>Единая платформа ⚠️ SPOF<br/>srv1231602-08 (10.123.16.x)<br/>Ubuntu 24.04"]:::sys
        K3["🟢 Team / KMG Petrochem"]:::sys
        K4["🔴 Электронный архив (ВЫВОД)<br/>10.123.13.12 (1334, 8065)"]:::out
    end

    subgraph GPU["⚡ GPU-кластер ABAI (Koshy?)"]
        G1["5× IBM POWER 9 8335-GTH<br/>+ NVIDIA Tesla V100<br/>~895 ГБ диск, 635 ГБ ОЗУ<br/>ppc64le ⚠️ ограничивает CUDA/Python"]
    end

    %% QazCloud Aqqol
    subgraph QC2["☁️ QazCloud — VDC Aqqol"]
        direction TB
        A1["🟢 САПФИР (Directum RX)<br/>~17 prod-серверов SRV123073-090<br/>Web/HAProxy/TextExtractor/Elastic/<br/>Insarco-монитор/SQL<br/>+ test SRV1230135-145<br/>+ dev SRV1230130-134<br/>+ Trening SRV123091<br/>Win 2019 + Ubuntu 20.04"]:::sys
        A2["🟢 АСДЦ ⚠️ legacy<br/>ODB-DC (172.20.20.21, Win 2012 R2 ⚠️)<br/>OLAP-DC (172.20.20.29, Win 2012 R2 ⚠️)<br/>web-ast-dc (172.20.20.145, Ubuntu 14 ⚠️)<br/>WIN-DC-SRV (172.20.20.146)<br/>srv7058 (Ubuntu 20)"]:::sys
        A3["🟢 СДД<br/>Patroni HA (10.123.13.120)<br/>K8s: master 10.123.13.123 +<br/>4 worker (.121, .122, .124, .125)<br/>GitLab on-prem 10.123.13.129<br/>Grafana+Prom 10.123.13.128<br/>ELK 10.123.13.126/127<br/>Тест: srv154-158 (10.123.15.4-11)"]:::sys
        A4["🟢 ИСУП<br/>SRV5242 (10.123.25.50, App SP)<br/>srv5243 (10.123.25.51, MS SQL)<br/>Win 2019 + SharePoint 2019"]:::sys
        A5["🟢 Интранет SharePoint<br/>SRV5050 (172.22.5.50, 172.22.5.29)<br/>srv5054 (172.22.5.54, MS SQL Always On)<br/>Win Server 2019 Standard<br/>⚠️ Внешние админы KMG DIGITAL"]:::sys
        A6["🟢 BoardMaps<br/>Win Server (IIS + MS SQL + Redis + Vault)<br/>bsd.kmg.kz / bsd-test.kmg.kz"]:::sys
        A7["🟡 Procu / Price (TEST)<br/>price.kmg.kz (10.123.23.194/195)<br/>price2test.kmg.kz (10.123.23.227)<br/>Ubuntu 22.04.5 LTS"]:::test
        A8["🟢 АИСЭМ<br/>srv5201 (172.22.5.201, Ubuntu 20.04)<br/>srv7110 (172.22.7.110, Test)"]:::sys
        A9["🟢 Compliance Control<br/>PROD 172.22.5.167<br/>TEST 10.123.18.58"]:::sys
        A10["🟢 БДА<br/>WAF на доступе к Prod 🛡️"]:::sys
        A11["🟢 Сайт КМГ<br/>www.kmg.kz (172.22.37.30)<br/>kazgpz.kmg.kz (тот же IP)"]:::sys
        A12["🔴 Санау (ВЫВОД)"]:::out
    end

    %% On-Prem
    subgraph OP["🏠 On-Prem"]
        OP1["🟢 Bitrix ANPZ<br/>anpz.kz<br/>On-Prem АНПЗ"]:::sys
        OP2["🟢 ИС УТО ЭМГ<br/>Локальная инфра<br/>АО «Эмбамунайгаз»"]:::sys
        OP3["Портал АО «КазТрансОйл»<br/>Астана, Габдулина 2"]:::sys
        OP4["Мобильное приложение КТО<br/>(proxmox-Pavlodar)"]:::sys
    end

    %% External cloud
    subgraph CL["☁️ Внешний cloud"]
        CL1["🟢 kmg-kumkol.kz<br/>(MySQL 5.7.36)"]:::sys
        CL2["🟢 kpi.kz<br/>(83.97.77.20, MySQL 8.0.30)"]:::sys
    end

    %% Shared services
    subgraph SHARE["🔧 Общие сервисы"]
        SH1["Active Directory КМГ<br/>(LDAP/NTLM/Kerberos/SSO)"]
        SH2["SMTP"]
        SH3["SIEM (подключение всех ИС)"]
        SH4["Антивирус"]
        SH5["Nessus<br/>(KMG\\Nessus Local Access<br/>на ИСУП и Интранете)"]
        SH6["VPN / Checkpoint VPN<br/>(доступ к Prod, без bastion)"]
        SH7["⚠️ MFA — отсутствует<br/>WAF — только БДА<br/>Vault — только BoardMaps<br/>API Gateway — отсутствует"]
    end

    %% ServiceDesk
    subgraph SD["📞 Поддержка"]
        SD1["ServiceDesk: 1444 / 8 800 080 1444"]
        SD2["sms@kmg.kz / sms.kmg.kz / ITSM"]
        SD3["BoardMaps: support@boardmaps.com / 8 800 555 1869"]
    end

    GPU --- K1
    QC1 -.-> SHARE
    QC2 -.-> SHARE
    OP -.-> SHARE
    SHARE -.-> SD
```

## Хостинговая матрица

| Площадка | Системы | Особенности |
|---|---|---|
| **QazCloud VDC Koshy** | ABAI, УТО, ИСОТ, Work, Team, KMG Petrochem, Электронный архив | + GPU-кластер IBM POWER 9 для ML (ABAI) |
| **QazCloud VDC Aqqol** | САПФИР, АСДЦ, СДД, Procu/Price, ИСУП, Интранет, BoardMaps, АИСЭМ, Compliance, БДА, Санау, корп. сайт КМГ | Основная масса корпоративных систем |
| **On-Prem АНПЗ** | Bitrix ANPZ (anpz.kz) | Локальная инфра НПЗ |
| **Локальная инфра ЭМГ** | ИС УТО ЭМГ | АО «Эмбамунайгаз» |
| **Внешний cloud** | kmg-kumkol.kz, kpi.kz | Публичные сайты |

## Резервное копирование (по системам)

| Система | Стратегия бэкапа | Риск |
|---|---|---|
| ABAI | pg_dump/WAL → pg-backupVM1/VM2 (172.20.102.253/254) | ⚠️ Бэкапы в окружении Test/QA, нет DR-плана с RTO/RPO, нет автофейловера |
| АСДЦ | vdc-KMG (QazCloud): полные еженедельно + инкрементальные ежедневно | Ретеншн 1 мес |
| Procu/Price | ⚠️ **НЕТ бэкапов** (по паспорту) | Высокий риск утраты |
| ИСОТ | QazCloud: ежедневные инкрем. + еженедельные полные | Ретеншн 1 мес |
| АИСЭМ | Ретеншн 90 дней | — |
| СДД, ИСУП, Интранет, BoardMaps, ЭА, Bitrix-порталы | Еженедельно / регламентно | — |
| Compliance Control | Ежедневно | — |
| БДА, Санау | Еженедельно | — |

## Операционные системы (по реестру)

### Linux
- **Ubuntu 24.04** — единая платформа УТО + ИСОТ + Work (srv1231602-08)
- **Ubuntu 22.04 LTS** — Procu/Price, СДД (srv13120-130 prod, srv154-158 test)
- **Ubuntu 20.04** — АИСЭМ (srv5201/srv7110), часть Directum Insarco (САПФИР), srv7058 (АСДЦ)
- **Ubuntu 14** ⚠️ — web-ast-dc АСДЦ (172.20.20.145) — критическое устаревание
- **CentOS 7** ⚠️ — ИС ABAI (EOL без патчей безопасности и обновлений ядра)

### Windows
- **Win Server 2019 Standard** — САПФИР (~17 серверов SRV123073-090, SRV1230130-145, SharePoint), ИСУП (SRV5242, srv5243), Интранет (SRV5050, srv5054), BoardMaps
- **Win Server 2012 R2** ⚠️ — АСДЦ (ODB-DC 172.20.20.21, OLAP-DC 172.20.20.29, WIN-DC-SRV 172.20.20.146) — устаревшая ОС
