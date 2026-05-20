# C4-архитектура АО «Эмбамунайгаз» (ЭМГ)

Диаграммы построены по результатам обследования ИТ-ландшафта ЭМГ (верхнеуровневая схема + ответы на уточняющие вопросы).

**Легенда статусов**

| Обозначение | Значение |
|---|---|
| 🟢 | В промышленной эксплуатации |
| 🟡 | Планируется замена / развитие |
| 🔴 | Средство цифровизации отсутствует |
| ☁️ | Размещение в облаке Qazcloud (IaaS, VMware) |
| 🏭 | Размещение в собственном ЦОД |

---

## Level 1 — System Context (Контекстная диаграмма)

Показывает ЭМГ как единую систему в окружении пользователей и внешних систем.

```mermaid
C4Context
    title System Context — АО «Эмбамунайгаз» (ЭМГ)

    Person(prod, "Производственный персонал", "Диспетчеры, инженеры-технологи, геологи, операторы АГЗУ/БКНС")
    Person(corp, "Корпоративные пользователи", "Финансы, бухгалтерия, HR, закупки, юристы, ИТ")
    Person(mgmt, "Руководство", "Оперативное и стратегическое управление добычей")
    Person(ext, "Внешние пользователи", "Контрагенты, партнёры")

    System(emg, "ИТ-ландшафт ЭМГ", "Корпоративные и производственные информационные системы добычи нефти и газа")

    System_Ext(abai, "ИС ABAI", "Централизованная система КМГ: база данных скважин, отчётность, аналитика")
    System_Ext(kmg_cc, "Корпоративный центр КМГ", "SMAX (ITSM), планируемое КХД, корпоративные стандарты")
    System_Ext(kmg_eng, "ТОО КМГ Инжиниринг", "Сопровождение ABAI, Service Desk, интеграция ИСУН")
    System_Ext(qazcloud, "ТОО Qazcloud", "IaaS (VMware), ОЦИБ — мониторинг ИБ 24×7")
    System_Ext(samruk, "Фонд Самрук-Казына", "ИСЭЗ (закупки), портал ИСЗЗ")
    System_Ext(vendors, "Вендоры ПО", "SAP, Schlumberger, Siemens, Autodesk, Oracle и др.")

    Rel(prod, emg, "Ведёт учёт добычи, мониторинг, инженерные расчёты")
    Rel(corp, emg, "Ведёт учёт, документооборот, закупки, HR")
    Rel(mgmt, emg, "Получает отчётность и аналитику")
    Rel(ext, emg, "Использует внешний портал emg.kz")

    Rel(emg, abai, "Передаёт/получает промысловые данные, отчёты", "HTTPS / VPN")
    Rel(emg, kmg_cc, "ITSM-заявки, корпоративная отчётность", "HTTPS")
    Rel(emg, kmg_eng, "Техподдержка ABAI, обмен с ИСУН", "SQL Server / Service Desk")
    Rel(emg, qazcloud, "Размещение ИС, мониторинг ИБ", "IaaS / SOC")
    Rel(emg, samruk, "Закупки, корпоративная отчётность", "HTTPS")
    Rel(emg, vendors, "Лицензии, обновления, поддержка", "Контракт")
    Rel(kmg_eng, abai, "Разработка и сопровождение", "Admin")
```

---

## Level 2 — Container (Контейнерная диаграмма)

Декомпозиция ИТ-ландшафта ЭМГ на прикладные контейнеры и инфраструктурные блоки.

```mermaid
C4Container
    title Container Diagram — ИТ-ландшафт ЭМГ

    Person(prod, "Производственный персонал")
    Person(corp, "Корпоративные пользователи")
    Person(mgmt, "Руководство")

    System_Boundary(emg, "АО «Эмбамунайгаз»") {

        Container(portal_ext, "Внешний портал", "Web", "emg.kz — 🟢 публичный портал", "☁️")
        Container(portal_int, "Внутренний портал", "Web", "🔴 отсутствует", "—")

        Container(sap, "SAP ERP", "SAP ECC", "🟢 FI, CO, MM, PM, TOPO, MDM — финансы, бюджет, ТОиР, закупки", "☁️")
        Container(onec, "1С 8.2", "1С:Предприятие", "🟡 Зарплата — планируется замена", "☁️")
        Container(directum, "СЭД Directum", "Directum RX", "🟢 Электронный документооборот", "☁️")
        Container(advanta, "Advanta", "PM-система", "🟢 Управление проектами", "☁️")
        Container(alfresco, "Alfresco", "ECM", "🟢 Цифровое хранилище документов / электронный архив", "☁️")

        Container(ofm, "OFM / Жулдыз", "Schlumberger", "🟢 Анализ эффективности добычи", "☁️")
        Container(situational, "Ситуационный центр", "Web/Dashboard", "🟢 Оперативный мониторинг", "☁️")

        Container(scada, "АСУ ТП / SCADA", "WinCC, DeltaV, СДМО Mirol, WINCC OA", "🟢 Диспетчеризация производственных объектов", "🏭")
        Container(rtdb, "БД реального времени", "Historian", "🟢 Единая база телеметрии (детали не раскрыты)", "🏭")
        Container(monitor, "Производственный мониторинг", "ArgusPro, Wialon, PetroLine, видео, СКУД, АСКУЭ, АСОМИ", "🟢 GPS-транспорт (ArgusPro с 2025), контроль бурения, энергоучёт", "🏭 / ☁️")

        Container(engineering, "Инженерное ПО", "Petrel, tNavigator, Eclipse, Techlog, ArcGIS, Revit, Civil 3D, ЛИРА-САПР", "🟢 Моделирование пласта, проектирование инфраструктуры", "Workstation")

        Container(ib, "Средства ИБ", "Kaspersky EPP, Solar Dozor DLP", "🟢 Защита рабочих станций и предотвращение утечек", "☁️ / 🏭")

        Container(missing_plan, "🔴 Планирование добычи / ГТМ / процессов", "—", "Отсутствует — Excel / ручные процессы")
        Container(missing_analytics, "🔴 Производственная аналитика", "—", "Подбор ГНО, осложнения, заводнение, эффективность ГТМ/ТКРС, ИМ — отсутствуют")
        Container(missing_digital, "🔴 Цифровое месторождение", "—", "Целевая платформа не определена")
        Container(missing_eco, "🔴 Экомониторинг", "—", "Автоматизированный контур отсутствует")
        Container(missing_kpi, "🔴 Стратегические KPI", "—", "Система отсутствует")
        Container(missing_dwh, "🔴 КХД / DWH / BI", "—", "На уровне ЭМГ отсутствует; планируется на уровне КМГ")
        Container(missing_esb, "🔴 ESB / API Gateway", "—", "Интеграции point-to-point, реестр отсутствует")
    }

    System_Ext(abai, "ИС ABAI", "Централизованная система КМГ")
    System_Ext(smax, "SMAX", "ITSM-платформа КМГ — 🟢 с 2023")
    System_Ext(qazcloud, "Qazcloud", "IaaS + ОЦИБ SOC")
    System_Ext(kmg_eng, "КМГ Инжиниринг", "Сопровождение ABAI, ИСУН")
    System_Ext(samruk, "Самрук-Казына", "ИСЭЗ, ИСЗЗ")

    Rel(prod, scada, "Мониторинг и управление", "HMI/SCADA")
    Rel(prod, monitor, "GPS, видео, контроль бурения")
    Rel(prod, engineering, "Моделирование, проектирование")
    Rel(prod, abai, "Ввод данных, отчёты", "Web")
    Rel(corp, sap, "Учёт, закупки, бюджет")
    Rel(corp, onec, "Расчёт зарплаты")
    Rel(corp, directum, "Документооборот")
    Rel(corp, smax, "ITSM-заявки", "Web")
    Rel(mgmt, situational, "Оперативные дашборды")
    Rel(mgmt, ofm, "Анализ добычи")
    Rel(mgmt, missing_plan, "Планирование (вручную)")

    Rel(scada, rtdb, "Телеметрия", "OPC/Modbus")
    Rel(rtdb, abai, "🔴 Поток не подтверждён", "—")
    Rel(scada, sap, "🔴 Поток не подтверждён", "point-to-point")
    Rel(sap, abai, "Обмен данными", "point-to-point")
    Rel(onec, sap, "🔴 Поток не подтверждён", "point-to-point")
    Rel(directum, alfresco, "Архив документов")
    Rel(emg, qazcloud, "Размещение ☁️-контейнеров", "VMware IaaS")
    Rel(ib, qazcloud, "SOC-мониторинг 24×7", "ОЦИБ")
    Rel(kmg_eng, abai, "Сопровождение и развитие")
    Rel(kmg_eng, emg, "ИСУН", "SQL Server")
    Rel(corp, samruk, "Закупки", "ИСЭЗ")
```

---

## Level 2 — Container: слои данных и интеграций

Отдельная декомпозиция данных и интеграционного контура (ключевая проблемная зона обследования).

```mermaid
C4Container
    title Container Diagram — Данные и интеграции ЭМГ

    Person(analyst, "Аналитик / инженер")
    Person(admin, "ИТ-администратор")

    System_Boundary(data, "Контур данных ЭМГ") {

        ContainerDb(abai_db, "Модуль «Базы данных» ABAI", "Oracle / PostgreSQL", "🟢 Скважины, история эксплуатации, добыча/закачка, материалы дела — 6/58 отчётов в продуктиве")
        ContainerDb(abai_aux, "Вспомогательные модули ABAI", "Oracle / PostgreSQL", "🟡 Мониторинг и аналитические расчёты — в доработке")
        ContainerDb(abai_nsi, "ИС АСУ НСИ", "Oracle / PostgreSQL", "🟡 Нормативно-справочная информация — план развития")
        ContainerDb(abai_lab, "Лабораторные данные", "Oracle / PostgreSQL", "🟡 Хранение лабораторных данных")
        ContainerDb(abai_passport, "Паспортизация оборудования", "Oracle / PostgreSQL + SAP PM", "🟡 Паспорта оборудования")

        ContainerDb(sap_db, "БД SAP ERP", "Oracle / HANA", "🟢 Финансы, бюджет, закупки, ТОиР, MDM")
        ContainerDb(onec_db, "БД 1С 8.2", "MS SQL", "🟡 Кадровый и зарплатный контур")
        ContainerDb(alfresco_db, "Alfresco Repository", "PostgreSQL", "🟢 Электронный архив документов")
        ContainerDb(rtdb, "БД реального времени", "Historian", "🟢 Телеметрия SCADA/DCS")

        ContainerDb(tbd_archive, "ТБД (архив)", "Oracle / PostgreSQL", "⚫ Выведена из эксплуатации с IV кв. 2024, архивный режим")

        Container(missing_mdm, "🔴 MDM / Data Office", "—", "Единая модель данных и Data Governance отсутствуют")
        Container(missing_dwh, "🔴 КХД / Data Lake", "—", "Планируется на уровне КМГ, не на уровне ЭМГ")
        Container(missing_esb, "🔴 ESB / API Gateway", "—", "Не внедрена; интеграции point-to-point")
    }

    System_Ext(kmg_eng, "КМГ Инжиниринг", "Разработка и сопровождение ABAI")

    Rel(analyst, abai_db, "Отчёты, аналитика", "Web UI")
    Rel(analyst, sap_db, "Финансовая отчётность", "SAP GUI / Fiori")
    Rel(admin, missing_esb, "🔴 Управление интеграциями отсутствует")

    Rel(rtdb, abai_db, "🔴 Поток SCADA→ABAI не подтверждён", "point-to-point?")
    Rel(sap_db, abai_db, "Обмен промысловыми/финансовыми данными", "point-to-point")
    Rel(onec_db, sap_db, "🔴 Источник истины не определён", "point-to-point?")
    Rel(abai_db, abai_aux, "Расчёты")
    Rel(abai_db, abai_nsi, "НСИ")
    Rel(abai_db, abai_lab, "Лаборатория")
    Rel(abai_db, abai_passport, "Паспортизация")
    Rel(kmg_eng, abai_db, "Сопровождение, доработка 52 отчётов")
    Rel(tbd_archive, abai_db, "Миграция завершена", "IV кв. 2024")
```

---

## Level 3 — Component: ИС ABAI (ключевая система)

Детализация модулей ABAI, доступных ЭМГ (по данным обследования).

```mermaid
C4Component
    title Component Diagram — ИС ABAI (контекст использования ЭМГ)

    Person(engineer, "Инженер-технолог ЭМГ")
    Person(reporter, "Специалист по отчётности")

    Container_Boundary(abai, "ИС ABAI (централизованная, КМГ)") {

        Component(db_module, "Модуль «Базы данных»", "Java / Web", "🟢 Хранение данных по скважинам: эксплуатация, добыча/закачка, материалы дела")
        Component(reports, "Отчётный модуль", "Web", "🟡 6 форм в продуктиве, 52 в доработке")
        Component(calc, "Аналитические расчёты", "Web", "🟡 Вспомогательный — мониторинг и расчёты")
        Component(nsi, "ИС АСУ НСИ", "Web", "🟡 НСИ — план развития")
        Component(lab, "Лабораторные данные", "Web", "🟡 Хранение лабораторных данных")
        Component(passport, "Паспортизация", "Web + SAP PM", "🟡 Паспорта оборудования")
        Component(gtm, "Анализ ГТМ", "—", "🔴 Отсутствует / не подтверждено")
        Component(gno, "Подбор ГНО", "—", "🔴 Отсутствует")
        Component(waterflood, "Управление заводнением", "—", "🔴 Отсутствует")
        Component(im, "Система ИМ", "—", "🔴 Имитационное моделирование отсутствует")
        Component(support, "Service Desk", "Web", "🟢 Техподдержка через КМГ Инжиниринг")
    }

    System_Ext(kmg_eng, "КМГ Инжиниринг", "Разработка, сопровождение, SLA")
    Container_Ext(sap, "SAP ERP", "SAP ECC", "ТОиР, MDM, финансы")
    Container_Ext(scada, "SCADA/DCS", "WinCC, DeltaV", "Телеметрия")

    Rel(engineer, db_module, "Ввод и просмотр данных")
    Rel(engineer, calc, "Аналитические расчёты")
    Rel(reporter, reports, "Формирование отчётов")
    Rel(reporter, support, "Обращения в поддержку")

    Rel(db_module, reports, "Данные для отчётов")
    Rel(db_module, calc, "Данные для расчётов")
    Rel(db_module, nsi, "Справочники")
    Rel(db_module, lab, "Лабораторные данные")
    Rel(db_module, passport, "Паспортизация")
    Rel(passport, sap, "Интеграция с SAP PM", "point-to-point")
    Rel(scada, db_module, "🔴 Поток не подтверждён")
    Rel(kmg_eng, db_module, "Сопровождение и доработка")
    Rel(kmg_eng, reports, "Разработка 52 отчётных форм")
    Rel(kmg_eng, support, "Обработка заявок")
```

---

## Level 3 — Component: АСУ ТП и производственный мониторинг

```mermaid
C4Component
    title Component Diagram — АСУ ТП и мониторинг (собственный ЦОД)

    Person(operator, "Оператор / диспетчер")
    Person(driver, "Водитель АТС")

    Container_Boundary(ot, "Производственный контур (🏭 собственный ЦОД)") {

        Component(wincc, "SIMATIC WinCC", "SCADA", "🟢 HMI/SCADA")
        Component(deltav, "DCS DeltaV", "DCS", "🟢 Распределённое управление")
        Component(mirol, "СДМО Mirol", "SCADA", "🟢 Диспетчеризация")
        Component(wincc_oa, "Siemens WINCC OA", "SCADA", "🟢 Цифровое месторождение (частично)")
        Component(rtdb, "БД реального времени", "Historian", "🟢 Единая телеметрия")

        Component(askue, "АСКУЭ", "Энергоучёт", "🟢 Учёт электроэнергии")
        Component(petrol, "PetroLine ДЭЛ-140", "Контроль бурения", "🟢 Мониторинг бурения/КРС")
        Component(video, "Видеонаблюдение", "IP-камеры", "🟢 Видеоконтроль объектов")
        Component(skud, "СКУД", "Access Control", "🟢 Контроль доступа")
        Component(asomi, "АСОМИ", "Метрология", "🟢 Управление метрологией")
        Component(argus, "ArgusPro", "GPS-мониторинг", "🟢 Мониторинг автотранспорта (с 2025)")
        Component(wialon, "Wialon", "GPS", "🟢 Дополнительный GPS-контур")
    }

    Container_Ext(abai, "ИС ABAI", "Web", "Промысловые данные")
    Container_Ext(sap, "SAP ERP TOPO", "SAP", "ТОиР оборудования")

    Rel(operator, wincc, "Управление")
    Rel(operator, deltav, "Управление")
    Rel(operator, mirol, "Диспетчеризация")
    Rel(driver, argus, "GPS-трекинг")

    Rel(wincc, rtdb, "Телеметрия")
    Rel(deltav, rtdb, "Телеметрия")
    Rel(mirol, rtdb, "Телеметрия")
    Rel(wincc_oa, rtdb, "Телеметрия")
    Rel(askue, rtdb, "Данные энергоучёта")

    Rel(rtdb, abai, "🔴 Поток не подтверждён", "—")
    Rel(rtdb, sap, "🔴 Поток не подтверждён", "—")
    Rel(petrol, abai, "🔴 Поток не подтверждён", "—")
```

---

## Level 3 — Component: Корпоративные системы

```mermaid
C4Component
    title Component Diagram — Корпоративный контур ЭМГ

    Person(finance, "Бухгалтер / финансист")
    Person(hr, "HR-специалист")
    Person(procurement, "Специалист по закупкам")
    Person(it, "ИТ-специалист")

    Container_Boundary(corp, "Корпоративные системы (☁️ Qazcloud IaaS)") {

        Component(sap_fi, "SAP FI/CO", "SAP ECC", "🟢 Финансы и бухучёт")
        Component(sap_mm, "SAP MM", "SAP ECC", "🟢 Закупки и снабжение")
        Component(sap_pm, "SAP PM / TOPO", "SAP ECC", "🟢 ТОиР и паспортизация")
        Component(sap_mdm, "SAP MDM", "SAP ECC", "🟡 MDM — план развития")
        Component(sap_budget, "SAP Бюджетирование", "SAP ECC", "🟡 Бюджетирование")

        Component(onec_pay, "1С 8.2 Зарплата", "1С", "🟡 Расчёт зарплаты — план замены")
        Component(directum, "Directum", "Directum RX", "🟢 СЭД")
        Component(alfresco, "Alfresco", "ECM", "🟢 Электронный архив")
        Component(advanta, "Advanta", "PM", "🟢 Управление проектами")
        Component(portal, "Портал emg.kz", "Web", "🟢 Внешний портал")
        Component(kpi, "Система KPI", "—", "🟡 Корпоративный KPI — план развития")
        Component(kontr, "КОНО", "Web", "🟢 Управление контрагентами")
        Component(hrm, "ПК Управления персоналом", "Web", "🟢 Кадровое администрирование")

        Component(kaspersky, "Kaspersky EPP", "Endpoint", "🟢 Антивирус")
        Component(dlp, "Solar Dozor", "DLP", "🟢 Предотвращение утечек")
    }

    System_Ext(smax, "SMAX", "ITSM КМГ")
    System_Ext(samruk, "ИСЭЗ / ИСЗЗ", "Самрук-Казына")
    System_Ext(qazcloud_soc, "ОЦИБ Qazcloud", "SOC 24×7")

    Rel(finance, sap_fi, "Учёт")
    Rel(finance, sap_budget, "Бюджетирование")
    Rel(hr, onec_pay, "Расчёт ЗП")
    Rel(hr, hrm, "Кадры")
    Rel(procurement, sap_mm, "Закупки")
    Rel(procurement, kontr, "Контрагенты")
    Rel(procurement, samruk, "Госзакупки", "ИСЭЗ")
    Rel(it, smax, "ITSM-заявки")

    Rel(directum, alfresco, "Архивирование")
    Rel(sap_pm, sap_mdm, "Данные оборудования")
    Rel(kaspersky, qazcloud_soc, "События ИБ")
    Rel(dlp, qazcloud_soc, "События DLP")
```

---

## Deployment — размещение контейнеров

```mermaid
C4Deployment
    title Deployment Diagram — размещение систем ЭМГ

    Deployment_Node(qazcloud, "Qazcloud IaaS", "VMware") {
        Deployment_Node(vm_corp, "VM-кластер корпоративных ИС", "Linux / Windows") {
            Container(sap, "SAP ERP", "SAP ECC")
            Container(onec, "1С 8.2", "1С")
            Container(directum, "Directum", "Directum RX")
            Container(alfresco, "Alfresco", "ECM")
            Container(portal, "Портал emg.kz", "Web")
            Container(ofm, "OFM / Жулдыз", "Analytics")
            Container(ib, "Kaspersky + DLP", "Security")
        }
    }

    Deployment_Node(onprem, "Собственный ЦОД ЭМГ", "On-Premise") {
        Deployment_Node(scada_cluster, "Кластер АСУ ТП", "Industrial") {
            Container(wincc, "WinCC", "SCADA")
            Container(deltav, "DeltaV", "DCS")
            Container(mirol, "СДМО Mirol", "SCADA")
            Container(rtdb, "Historian", "RTDB")
        }
        Deployment_Node(monitor_cluster, "Мониторинг", "Mixed") {
            Container(argus, "ArgusPro", "GPS")
            Container(petrol, "PetroLine", "Drilling")
            Container(video, "Видеонаблюдение", "IP")
        }
    }

    Deployment_Node(kmg_cloud, "Инфраструктура КМГ", "Centralized") {
        Container(abai, "ИС ABAI", "Centralized KMG system")
        Container(smax, "SMAX", "ITSM")
    }

    Deployment_Node(kmg_eng, "КМГ Инжиниринг", "Service Provider") {
        Container(support, "Service Desk ABAI", "Support")
    }

    Rel(onprem, qazcloud, "VPN / защищённые каналы", "Production data")
    Rel(qazcloud, kmg_cloud, "Корпоративные интеграции", "HTTPS / VPN")
```

---

## Сводная карта: as-is → целевое состояние

```mermaid
flowchart LR
    classDef green fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    classDef yellow fill:#FFF9C4,stroke:#F9A825,color:#F57F17
    classDef red fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef grey fill:#ECEFF1,stroke:#78909C,color:#37474F

    subgraph ASIS["As-Is (факт)"]
        A1["ABAI — ядро данных"]:::green
        A2["SAP + 1С + Directum"]:::green
        A3["SCADA/DCS в ЦОД"]:::green
        A4["Point-to-point интеграции"]:::yellow
        A5["Нет MDM / Data Office"]:::red
        A6["Нет КХД на уровне ЭМГ"]:::red
        A7["Нет ESB"]:::red
        A8["52/58 отчётов ABAI в разработке"]:::yellow
    end

    subgraph TOBE["To-Be (ожидаемое)"]
        B1["КХД на уровне КМГ"]:::yellow
        B2["ESB / API Gateway"]:::red
        B3["Единая MDM / Data Governance"]:::red
        B4["Цифровое месторождение"]:::red
        B5["Планирование добычи/ГТМ"]:::red
        B6["Производственная аналитика"]:::red
        B7["Полный отчётный контур ABAI"]:::yellow
    end

    A1 --> B7
    A4 --> B2
    A5 --> B3
    A6 --> B1
    A3 --> B4
    A1 --> B5
    A1 --> B6
```

---

## Примечания к диаграммам

1. **ABAI** — централизованная система группы КМГ; ЭМГ использует её как сервис (договор с КМГ Инжиниринг), не владея разработкой.
2. **ТБД** выведена из эксплуатации с IV квартала 2024 г.; данные мигрированы в ABAI.
3. **CityPoint** (GPS, 2021–2024) заменён на **ArgusPro** (промэксплуатация с 2025 г.).
4. **SMAX** (ITSM) — централизованная платформа КМГ, используется с 2023 г. (на верхнеуровневой схеме ошибочно обозначена как отсутствующая).
5. Потоки **SCADA/DCS → ABAI/аналитика** в ответах ЭМГ не раскрыты — на диаграммах помечены как неподтверждённые.
6. **КХД, MDM, ESB** — сознательно вынесены за пределы ЭМГ или отмечены как отсутствующие; развитие ожидается на уровне корпоративного центра КМГ.
