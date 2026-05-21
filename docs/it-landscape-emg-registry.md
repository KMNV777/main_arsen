# Реестр ИС и интеграций (матрица интеграций ЭМГ)

Источник: официальная матрица интеграций (19 позиций).

| № | Система | Интегрируется с | Тип / формат | Направление |
|---|---------|-----------------|--------------|-------------|
| 2 | **Directum** (СЭД) | Active Directory | LDAP | → AD |
| 3 | **ИС ABAI** | — (см. ИМ №12) | — | — |
| 4 | **Solar Dozor** (DLP) | Exchange, Forcepoint Web Gateway | BCC, ICAP | ← почта, ← веб |
| 5 | **FUDOPAM** (PAM) | Active Directory | LDAP | → AD |
| 6 | **E-Pass** | Active Directory | LDAP | → AD |
| 7 | **Argus Pro** (GPS) | — (→ ИС УТО) | REST JSON | → УТО |
| 8 | **1С** (зарплата) | SAP ERP | CSV, файловый обмен | ← SAP |
| 9 | **SAS-FM** | SAP BW, SAP R/3 | RFC, .sas7bdat, CSV | → SAP |
| 10 | **Жулдыз** | Active Directory | LDAP | → AD |
| 11 | **sPoint** | КХД АО НК КМГ | API JSON | → КХД |
| 12 | **ИМ** (10.32.10.99) | OPC DA/UA, Modbus, MySQL, PostgreSQL, REST, SMTP | см. ниже | OT-хаб |
| 13 | **ПК «Управление персоналом»** | SAP ERP | DB functions | ↔ SAP |
| 14 | **SAP ERP** | АСУНСИ, ИСУТО, SCADA, AVR, ЭА, Documentum, банк, FC, Platts, ИСЭСФ, 1С, кадры | XML, CSV, MT940/103, API | Хаб |
| 15 | **ИС УТО** | SAP ERP | SOAP XML | ↔ SAP |
| 16 | **Alfresco** (ЭА) | Active Directory | LDAP | → AD |
| 17 | **КГИС** | Active Directory | LDAP | → AD |
| 18 | **Procu** | АСУНСИ, ИСЭЗ, AD | API JSON | ↔ |
| 19 | **AVR+** | SAP ERP | API XML | ↔ SAP |

## ИМ (№12) — детализация интеграций

| Контрагент | Данные | Протокол | Частота |
|------------|--------|----------|---------|
| ИС ABAI (PostgreSQL) | Фонд скважин, статусы, ремонты | SQL | 08:00, 13:30, 18:00 |
| Kepware / ИСУН (192.168.17.186) | PUMP, ISUN_RVS, ISUN_GAS | OPC DA | 1 ч / 2 ч |
| КОА реклоузеры (10.32.10.98) | Мощности, токи, МТО/МТЗ | OPC DA | 5 мин |
| OPC UA (АСУТП/ТМ, 12+ серверов) | Телеметрия месторождений | OPC UA | 5 мин |
| Modbus TCP (КУУН) | Расходомеры, скважины | Modbus | 7 мин |
| SDMO Danfoss (4× MySQL) | Дисбаланс ЧРП | SQL | :47 / 07:17 |
| KTM Floboss | СИКН 2hours_kto | SQL | вручную |
| koa-cm WinCC HDA | HDA ABK/KJS | SQL | cron КОА |
| ИСУ-ЭМГ PostgreSQL (10.32.10.90) | chrp_well.working | SQL | 15 мин |
| Аналитика ЭМГ (:8099) | Теги, скважины | REST JSON | 5 мин |
| packet_service (:8951) | Реклоузеры | REST JSON | 5 мин |
| Распознавание речи (:8777) | Аудио ПРС | multipart | online |
| SMTP Gmail | Уведомления, XLSX | SMTP | cron + events |

## SAP ERP (№14) — основные связи

| Контрагент | Данные |
|------------|--------|
| Нацбанк | Курсы валют (XML) |
| ИС ЭСФ | Счета-фактуры |
| БВУ | Выписки MT940/103 |
| Кадры / УП | Табельные номера |
| 1С | Суммы ЗП |
| FC | Фин. консолидация |
| ИС УТО | Объекты, транспорт |
| SCADA | Оборудование |
| АСУНСИ | НСИ (SAP PO XML) |
| AVR | Акты работ |
| ЭА / Documentum | Договоры, архив |
| Platts | Котировки нефти |
| СИЗ | XLSX файл |
