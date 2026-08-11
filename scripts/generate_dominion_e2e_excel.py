#!/usr/bin/env python3
"""Generate Dominion E2E test cases Excel for TestRail / Zephyr / Xray import.

Output:
  docs/qa/Dominion_E2E_TestCases.xlsx

Sheets:
  1. Инструкция — how to import
  2. TestCases — one row per case (summary)
  3. Steps — one row per step (step | expected) — primary import sheet
  4. Сводка — counts by module / priority
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
P0_FILL = PatternFill("solid", fgColor="FFCDD2")
P1_FILL = PatternFill("solid", fgColor="FFE0B2")
P2_FILL = PatternFill("solid", fgColor="FFF9C4")
P3_FILL = PatternFill("solid", fgColor="E8F5E9")
SECTION_FILL = PatternFill("solid", fgColor="D9E2F3")

PRIORITY_FILL = {"P0": P0_FILL, "P1": P1_FILL, "P2": P2_FILL, "P3": P3_FILL}


def style_header(ws, row: int, cols: int, height: int = 28) -> None:
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[row].height = height


def style_row(ws, row: int, cols: int, priority: str | None = None) -> None:
    fill = PRIORITY_FILL.get(priority) if priority else None
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.border = BORDER
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        if fill and c <= 6:
            cell.fill = fill


def set_widths(ws, widths: list[float]) -> None:
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# Test case data
# Each case: (id, module, title, priority, type, preconditions, [(step, expected), ...])
# ---------------------------------------------------------------------------

CASES: list[tuple] = [
    # ===== ADMIN =====
    (
        "TC-ADM-001", "Админка / Dictionary", "Создание definition предмета Dominion",
        "P1", "E2E",
        "Авторизован U-ADMIN. В dictionary нет definition TC_TEST_HELMET_C.",
        [
            ("Открыть Админка → Dictionary → Создать предмет", "Открыта форма создания definition"),
            ("Заполнить: name=TC_TEST_HELMET_C, slot=head, rarity=Common, traits=repairable,sellable, game_code=dominion, base_price=1000, durability_loss=28, buff/debuff тексты", "Поля принимают значения без ошибок валидации"),
            ("Нажать «Сохранить»", "Definition создан; отображается в списке каталога"),
            ("Выполнить Grant предмета тестовому игроку U-F2P-LEAD", "Предмет появляется в GetInventory(game=dominion)"),
        ],
    ),
    (
        "TC-ADM-002", "Админка / Dictionary", "Редактирование tooltip-текста definition",
        "P2", "E2E",
        "Definition «Анти-Крипт (Голова) V1» существует. Игрок U-F2P-LEAD владеет и экипировал предмет.",
        [
            ("В админке изменить описание баффа на TC_UPDATED_BUFF_TEXT", "Изменения сохранены"),
            ("Игроком открыть лобби Dominion и навести курсор на слот «Голова»", "В tooltip отображается TC_UPDATED_BUFF_TEXT"),
            ("Проверить gameplay в матче", "Числовые параметры баффа не изменились"),
        ],
    ),
    (
        "TC-ADM-003", "Админка / Dictionary", "PRO-ограничение на Advanced-предмете",
        "P1", "E2E",
        "Definition Advanced (Boss) с restriction=PRO. Предмет выдан U-F2P-LEAD через Grant.",
        [
            ("U-F2P-LEAD открывает Инвентарь → Dominion", "Предмет отображается с blur и меткой «Требуется PRO»"),
            ("Попытка экипировать предмет", "Экипировка заблокирована; отображается CTA покупки PRO"),
        ],
    ),
    (
        "TC-ADM-004", "Админка / Grant", "Выдача предметов игроку (Grant)",
        "P0", "E2E",
        "Авторизован U-ADMIN. У U-F2P-LEAD пустой инвентарь Dominion. 5 Base-предметов (по слоту). idempotency_key=grant-tc-adm-004-{uuid}.",
        [
            ("Admin → Users → U-F2P-LEAD → Grant Items", "Открыт интерфейс выдачи"),
            ("Выбрать 5 Base-предметов, указать idempotency_key", "Форма заполнена"),
            ("Подтвердить выдачу", "Операция успешна"),
            ("Игроком открыть Инвентарь Dominion", "Все 5 предметов отображаются в инвентаре"),
        ],
    ),
    (
        "TC-ADM-005", "Админка / Grant", "Идемпотентность Grant",
        "P1", "API + E2E",
        "TC-ADM-004 выполнен с idempotency_key=grant-tc-adm-004-001. Зафиксирован stackCount до повтора.",
        [
            ("Повторить Grant с тем же idempotency_key и тем же набором предметов", "HTTP 200, операция no-op"),
            ("Проверить инвентарь игрока", "Количество предметов не изменилось; дубликаты не созданы"),
        ],
    ),
    (
        "TC-ADM-006", "Админка / Баланс", "Настройка стоимости RepairByGold",
        "P2", "E2E",
        "В админ-балансе настроена таблица RepairByGold для Rare. У U-PRO-LEAD сломан Rare-предмет (durability=0), Gold ≥ 10000.",
        [
            ("Админ изменяет стоимость попытки 1 для Rare с 520 на 600 Gold", "Настройка сохранена"),
            ("Игрок открывает Repair UI для сломанного Rare-предмета", "Отображается стоимость 600 Gold, attempt=1"),
            ("Подтвердить ремонт (при успехе)", "Списано 600 Gold"),
        ],
    ),
    (
        "TC-ADM-007", "Админка / Audit", "Audit log операции Grant",
        "P3", "E2E",
        "Логирование админ-операций включено.",
        [
            ("Выполнить Grant предмета игроку", "Операция успешна"),
            ("Открыть Audit log, фильтр по admin_id и операции Grant", "Запись содержит: admin_id, user_id, список items, timestamp"),
        ],
    ),
    (
        "TC-ADM-008", "Админка / Dictionary", "Деактивация definition",
        "P2", "E2E",
        "Definition активен; предмет не экипирован ни у одного игрока в активном лобби.",
        [
            ("Деактивировать definition в админке", "Статус = inactive"),
            ("Игрок открывает Selection UI для соответствующего слота", "Предмет не отображается в списке выбора"),
            ("Проверить инвентарь владельца", "Предмет остаётся у владельца"),
        ],
    ),
    # ===== INVENTORY =====
    (
        "TC-INV-001", "Инвентарь / UI", "Отображение инвентаря Dominion",
        "P0", "E2E",
        "У U-F2P-LEAD есть dominion-предметы и платформенные предметы (game_code=null).",
        [
            ("Авторизоваться как U-F2P-LEAD", "Успешный вход"),
            ("Открыть раздел «Инвентарь»", "Инвентарь загружен"),
            ("Применить фильтр «Dominion» / game=dominion", "Отображаются dominion-предметы + платформенные"),
            ("Проверить группировку", "Предметы сгруппированы по слотам (head, chest, hands, legs, feet)"),
        ],
    ),
    (
        "TC-INV-002", "Инвентарь / Loadout", "Экипировка предмета в слот",
        "P0", "E2E",
        "У игрока есть неэкипированный Base-предмет для слота «Голова». Слот «Голова» пуст.",
        [
            ("Открыть лобби Dominion или экран экипировки", "Слот «Голова» в состоянии Empty (плейсхолдер)"),
            ("Кликнуть на иконку слота «Голова»", "Открыта панель Selection UI со списком доступных предметов"),
            ("Выбрать Base-предмет и подтвердить", "Иконка предмета отображается в слоте; статус = Equipped"),
            ("Открыть Инвентарь", "Предмет остаётся в инвентаре с флагом «экипирован»"),
        ],
    ),
    (
        "TC-INV-003", "Инвентарь / Loadout", "Снятие предмета со слота",
        "P1", "E2E",
        "Слот «Грудь» заполнен экипированным предметом.",
        [
            ("Кликнуть на экипированный слот «Грудь»", "Открыто контекстное меню / панель слота"),
            ("Выбрать «Снять»", "Слот переходит в состояние Empty"),
            ("Проверить Инвентарь", "Предмет присутствует; флаг «экипирован» снят; предмет не удалён"),
        ],
    ),
    (
        "TC-INV-004", "Инвентарь / UI", "Tooltip предмета при наведении",
        "P1", "E2E",
        "Экипирован предмет с buff, debuff и active skill (Boss, слот head).",
        [
            ("Навести курсор на иконку слота", "Открыт tooltip без задержки (данные из локального кеша)"),
            ("Проверить содержимое tooltip", "Отображаются: название, тип (Base/Advanced), buff (зелёный), debuff (красный)"),
            ("Для Boss head-слота", "Отображается описание active skill с привязкой к клавише E"),
        ],
    ),
    (
        "TC-INV-005", "Инвентарь / PRO", "Blur PRO-предмета для F2P-игрока",
        "P0", "E2E",
        "U-F2P-LEAD без PRO-подписки. В инвентаре есть Advanced (PRO) предмет.",
        [
            ("Открыть Инвентарь Dominion", "PRO-предмет отображается с blur"),
            ("Навести курсор на PRO-предмет", "Индикация «Требуется PRO»; попап с кнопкой покупки подписки"),
        ],
    ),
    (
        "TC-INV-006", "Инвентарь / PRO", "Блокировка экипировки PRO-предмета без подписки",
        "P0", "E2E",
        "U-F2P-LEAD без PRO; Advanced-предмет в инвентаре.",
        [
            ("Попытаться экипировать Advanced-предмет", "Операция отклонена"),
            ("Проверить слот", "Слот остаётся Empty или с предыдущим предметом"),
            ("Проверить UI", "Отображается CTA «Купить PRO»"),
        ],
    ),
    (
        "TC-INV-007", "Инвентарь / Durability", "Индикатор прочности в лобби",
        "P1", "E2E",
        "Предмет с durability_current=45% экипирован.",
        [
            ("Открыть лобби Dominion", "Иконка предмета отображает шкалу прочности 45%"),
            ("Сравнить цветовую индикацию", "Цвет соответствует порогу (не критический)"),
        ],
    ),
    (
        "TC-INV-008", "Инвентарь / Durability", "Сломанный предмет (0% прочности)",
        "P0", "E2E",
        "Предмет с durability_current=0 в инвентаре U-F2P-BROKEN.",
        [
            ("Экипировать сломанный предмет", "Экипировка технически возможна"),
            ("Открыть лобби", "Предмет подсвечен как «Сломан»"),
            ("Проверить подсказку", "Текст: для активации баффов требуется ремонт"),
            ("Зайти в матч и проверить эффект", "Баффы/дебаффы предмета не работают"),
        ],
    ),
    (
        "TC-INV-009", "Инвентарь / Sell", "Продажа одного предмета",
        "P1", "E2E",
        "Предмет sellable, не экипирован, не зарезервирован. base_price=1000; sell_ratio=0.08. Баланс Gold зафиксирован.",
        [
            ("Выбрать предмет → «Продать»", "Popup с предпросмотром: «Вы получите 80 Gold»"),
            ("Подтвердить продажу", "Предмет удалён из инвентаря; Gold +80"),
            ("Проверить popup до confirm", "Сумма 80 Gold отображалась до подтверждения"),
        ],
    ),
    (
        "TC-INV-010", "Инвентарь / Sell", "Блокировка продажи экипированного предмета",
        "P1", "E2E",
        "Предмет экипирован в loadout.",
        [
            ("Попытаться продать экипированный предмет", "Операция заблокирована"),
            ("Проверить сообщение", "«Сначала снимите предмет со слота» (или эквивалент)"),
        ],
    ),
    (
        "TC-INV-011", "Инвентарь / Sell", "Массовая продажа предметов",
        "P2", "E2E",
        "В инвентаре ≥3 sellable предмета, не экипированы.",
        [
            ("Включить multi-select, выбрать 3 предмета", "Предметы выделены"),
            ("Нажать «Продать выбранные»", "Popup с суммарным preview Gold"),
            ("Подтвердить", "Все 3 предмета удалены; Gold начислен одной суммой"),
        ],
    ),
    (
        "TC-INV-012", "Инвентарь / Repair", "RepairByGold — успешный ремонт с 1-й попытки",
        "P1", "E2E",
        "Common-предмет (base_price=1000), durability=0. Gold ≥ 520.",
        [
            ("Открыть карточку предмета → «Починить за Gold»", "UI: attempt=1, cost=520 Gold (13%), chance=87%"),
            ("Подтвердить ремонт", "Анимация успеха"),
            ("Проверить состояние", "durability=100%; Gold −520; repair_streak_failed не изменился"),
        ],
    ),
    (
        "TC-INV-013", "Инвентарь / Repair", "RepairByGold — неудачная попытка и рост streak",
        "P1", "E2E",
        "Сломанный Common-предмет; repair_streak_failed=0. Mock/seed для провала попытки.",
        [
            ("Выполнить RepairByGold (attempt 1) — провал", "UI: «Ремонт не удался»; Gold списан"),
            ("Проверить предмет", "durability=0; repair_streak_failed=1"),
            ("Открыть Repair UI повторно", "attempt=2, cost=572 Gold (+10%), chance=74%"),
        ],
    ),
    (
        "TC-INV-014", "Инвентарь / Repair", "Сохранение repair_streak после успешного ремонта",
        "P1", "E2E",
        "Предмет починен со 2-й попытки (1-я неудачная); repair_streak_failed=1.",
        [
            ("Снова износить предмет до durability=0", "Предмет сломан"),
            ("Открыть Repair UI", "Следующий ремонт начинается с attempt=2 (cost/chance 2-й попытки), не с attempt=1"),
        ],
    ),
    (
        "TC-INV-015", "Инвентарь / Repair", "Repair cap после 7 неудачных попыток",
        "P2", "E2E",
        "repair_streak_failed=7 на инстансе предмета.",
        [
            ("Открыть Repair UI", "Cost = 50% от стоимости нового предмета; chance = 9%"),
            ("Выполнить попытку", "repair_streak_failed не превышает 7"),
        ],
    ),
    (
        "TC-INV-016", "Инвентарь / Repair", "RepairByKit — гарантированный ремонт",
        "P1", "E2E",
        "Сломанный Common-предмет (durability=0). Common repair_kit в инвентаре (stackCount ≥ 1).",
        [
            ("Открыть карточку предмета → «Использовать ремкомплект»", "Отображён подходящий kit"),
            ("Подтвердить в popup", "durability=100%; kit stackCount −1; Gold не списан"),
        ],
    ),
    (
        "TC-INV-017", "Инвентарь / Repair", "RepairByKit — несовпадение редкости",
        "P1", "E2E",
        "Сломанный Epic-предмет; Common repair_kit в инвентаре.",
        [
            ("Попытаться применить Common kit к Epic-предмету", "Ошибка rarity mismatch"),
            ("Проверить предмет и kit", "durability=0; kit не потрачен"),
        ],
    ),
    (
        "TC-INV-018", "Инвентарь / Repair", "Блокировка ремонта исправного предмета",
        "P2", "E2E",
        "Предмет с durability > 0.",
        [
            ("Открыть Repair UI", "Кнопки ремонта неактивны или отсутствуют"),
            ("Вызвать RepairByGold через API", "HTTP 400 not broken"),
        ],
    ),
    (
        "TC-INV-019", "Инвентарь / Repair", "RepairByGold при недостатке Gold",
        "P1", "E2E",
        "U-PRO-NOGOLD: сломанный предмет, Gold < стоимости попытки.",
        [
            ("Попытаться RepairByGold", "Ошибка insufficient balance"),
            ("Проверить предмет", "durability=0; repair_streak_failed не увеличился"),
        ],
    ),
    (
        "TC-INV-020", "Инвентарь / Reservation", "Блокировка операций при active reservation",
        "P0", "E2E",
        "Игрок в активном поиске матча; loadout залочен (ValidateAndLockLoadout success).",
        [
            ("Попытаться Sell предмета из loadout", "HTTP 409 reserved; UI: операция заблокирована"),
            ("Попытаться Repair", "HTTP 409 reserved"),
            ("Попытаться Consume", "HTTP 409 reserved"),
        ],
    ),
    (
        "TC-INV-021", "Инвентарь / Grant", "Grant доливка stackable при reservation",
        "P2", "API + E2E",
        "repair_kit (stackable) зарезервирован / активная reservation.",
        [
            ("Выполнить Grant +1 repair_kit тому же пользователю", "Операция успешна"),
            ("Проверить stackCount", "stackCount увеличен на 1"),
        ],
    ),
    (
        "TC-INV-022", "Инвентарь / Durability", "Предупреждение о критическом износе (<10%)",
        "P2", "E2E",
        "Предмет с durability=9%.",
        [
            ("Открыть Инвентарь или постматч-экран", "Отображается: «Внимание: Критический износ! Требуется ремонт»"),
        ],
    ),
    # ===== LOBBY =====
    (
        "TC-LOB-001", "Лобби / Создание", "Создание лобби Mercenary (F2P)",
        "P0", "E2E",
        "U-F2P-LEAD авторизован, не в другом лобби.",
        [
            ("Открыть режим Dominion → «Создать лобби»", "Лобби создано; игрок = лидер"),
            ("Выбрать сторону «Наемники» (Mercenary)", "Отображается 5 слотов карточек игроков"),
            ("Проверить селектор роли", "Активна роль Mercenary"),
        ],
    ),
    (
        "TC-LOB-002", "Лобби / Создание", "Создание лобби Boss (PRO)",
        "P0", "E2E",
        "U-PRO-LEAD с активной PRO-подпиской.",
        [
            ("Создать лобби Dominion → сторона «Боссы»", "Отображается 2 слота карточек"),
            ("Открыть Selection UI для head/chest", "Доступны Advanced-предметы"),
        ],
    ),
    (
        "TC-LOB-003", "Лобби / Роли", "Блокировка роли Boss при группе >2 человек",
        "P0", "E2E",
        "В лобби 3+ игрока.",
        [
            ("Лидер пытается переключить сторону на «Боссы»", "Ошибка: «Максимум 2 игрока для данной роли»"),
            ("Проверить текущую сторону", "Сторона не изменилась"),
        ],
    ),
    (
        "TC-LOB-004", "Лобби / PRO", "Валидация PRO при смене стороны",
        "P0", "E2E",
        "PRO-лидер, в группе есть F2P без подписки; группа из 2 человек.",
        [
            ("Лидер пытается переключить на Boss при F2P в группе без PRO", "Валидация блокирует смену стороны"),
            ("Проверить UI", "Отображается понятное сообщение об ошибке"),
        ],
    ),
    (
        "TC-LOB-005", "Лобби / Настройки", "Выбор карты и региона лидером",
        "P1", "E2E",
        "Лидер в лобби; второй игрок в том же лобби.",
        [
            ("Лидер меняет карту и серверный регион", "Значения сохранены"),
            ("Участник проверяет экран без refresh", "Карта и регион обновились (real-time sync)"),
            ("Проверить индикацию пинга", "Пинг к выбранному региону отображается"),
        ],
    ),
    (
        "TC-LOB-006", "Лобби / Настройки", "Не-лидер не может менять карту/регион",
        "P2", "E2E",
        "U-F2P-MEM — участник, не лидер.",
        [
            ("Участник пытается изменить карту", "Селекторы disabled / недоступны"),
        ],
    ),
    (
        "TC-LOB-007", "Лобби / UI", "Кнопка «Инфо / Правила»",
        "P3", "E2E",
        "Лобби открыто.",
        [
            ("Нажать «Инфо / Правила»", "Открыта модалка с гайдом по режиму"),
            ("Проверить содержимое", "Описаны механики Dominion и клавиши E/F"),
        ],
    ),
    (
        "TC-LOB-008", "Лобби / Ready", "Ready — поиск заблокирован пока не все готовы",
        "P0", "E2E",
        "Лобби из 2 игроков; loadout валиден.",
        [
            ("Участник нажимает «Готов»", "Статус карточки = Ready; счётчик 1/2"),
            ("Лидер нажимает «Поиск» без своего Ready", "Поиск не стартует"),
            ("Лидер нажимает «Готов» → «Поиск»", "Поиск запущен"),
        ],
    ),
    (
        "TC-LOB-009", "Лобби / Поиск", "Старт поиска и ValidateAndLockLoadout",
        "P0", "E2E",
        "Все игроки Ready; loadout валиден (5 слотов, не broken).",
        [
            ("Лидер нажимает «Поиск»", "Кнопка меняется на «Отмена»; таймер ожидания"),
            ("Проверить backend", "ValidateAndLockLoadout вернул valid=true; reservation_key создан"),
            ("Проверить предметы", "Предметы залочены (reserved)"),
        ],
    ),
    (
        "TC-LOB-010", "Лобби / Loadout", "Предупреждение при неполном loadout",
        "P1", "E2E",
        "Заполнено 2 из 5 слотов; все Ready.",
        [
            ("Лидер запускает поиск", "Warning о неполной экипировке"),
            ("Подтвердить поиск", "Поиск стартует (допускается неполный loadout)"),
        ],
    ),
    (
        "TC-LOB-011", "Лобби / Loadout", "Блокировка поиска при сломанном предмете",
        "P0", "E2E",
        "U-F2P-BROKEN с durability=0 хотя бы на 1 слоте; все Ready.",
        [
            ("Лидер запускает поиск", "Поиск не стартует"),
            ("Проверить ошибку", "item_broken_{id}; valid=false; лок не поставлен"),
        ],
    ),
    (
        "TC-LOB-012", "Лобби / Loadout", "Блокировка поиска при дубле слота",
        "P1", "E2E",
        "Два предмета назначены на слот head.",
        [
            ("Запустить поиск", "valid=false; ошибка slot_duplicated_head"),
        ],
    ),
    (
        "TC-LOB-013", "Лобби / Reservation", "Отмена поиска и ReleaseBatch",
        "P0", "E2E",
        "Поиск активен; reservation_key существует.",
        [
            ("Лидер нажимает «Отмена»", "Поиск остановлен; кнопка → «Поиск»"),
            ("Проверить backend", "ReleaseBatch(reservation_key) выполнен"),
            ("Попытаться Sell/Repair предмета", "Операции разрешены"),
        ],
    ),
    (
        "TC-LOB-014", "Лобби / UI", "Блокировка выхода после Ready",
        "P1", "E2E",
        "Игрок нажал «Готов» или поиск активен.",
        [
            ("Проверить кнопку «Выход»", "Кнопка disabled"),
            ("Попытаться покинуть лобби", "Выход невозможен до отмены Ready/поиска"),
        ],
    ),
    (
        "TC-LOB-015", "Лобби / Управление", "Kick участника лидером",
        "P1", "E2E",
        "Лобби 2 игрока; лидер = U-F2P-LEAD.",
        [
            ("Лидер на карточке участника выбирает «Выгнать»", "Участник удалён из лобби"),
            ("У кикнутого игрока", "Отображается экран вне лобби"),
            ("У лидера", "Слот участника пуст; кнопка «Пригласить»"),
        ],
    ),
    (
        "TC-LOB-016", "Лобби / Инвайты", "Инвайт друга в ту же команду",
        "P0", "E2E",
        "U-F2P-LEAD в лобби Mercenary; U-F2P-MEM в друзьях.",
        [
            ("Лидер на пустом слоте → «Пригласить» → выбрать друга", "Инвайт отправлен"),
            ("Друг принимает инвайт", "Друг в лобби в той же команде (Mercenary), что и отправитель"),
        ],
    ),
    (
        "TC-LOB-017", "Лобби / Инвайты", "Инвайт F2P в лобби PRO-хоста (сторона Mercenary)",
        "P0", "E2E",
        "PRO-хост в команде Наемников; F2P друг без PRO.",
        [
            ("PRO-хост отправляет инвайт F2P", "Инвайт доставлен"),
            ("F2P принимает", "Успешный вход в лобби, команда Mercenary"),
            ("PRO-хост пытается перенести команду в Boss", "Операция заблокирована (в команде F2P без PRO)"),
        ],
    ),
    (
        "TC-LOB-018", "Лобби / Инвайты", "Инвайт F2P в команду Боссов — отказ",
        "P0", "E2E",
        "PRO-хост в команде Боссов; F2P друг без PRO.",
        [
            ("PRO-хост отправляет инвайт F2P", "Инвайт доставлен"),
            ("F2P пытается принять", "Ошибка: «Вы не можете присоединиться к лобби в команду Боссов без подписки ПРО»"),
        ],
    ),
    (
        "TC-LOB-019", "Лобби / Sync", "Real-time sync loadout между участниками",
        "P1", "E2E",
        "2 игрока в одном лобби.",
        [
            ("Игрок A меняет предмет в слоте chest", "Изменение применено у A"),
            ("Игрок B наблюдает карточку A без refresh", "Иконка chest обновилась у B в течение 1–2 сек"),
        ],
    ),
    (
        "TC-LOB-020", "Лобби / Loadout", "Selection UI: Base перед Advanced",
        "P2", "E2E",
        "PRO Boss с Base и Advanced предметами в слоте head.",
        [
            ("Открыть Selection UI для head", "Сначала список Base-предметов"),
            ("Прокрутить список", "Затем Advanced-предметы"),
        ],
    ),
    (
        "TC-LOB-021", "Лобби / MM", "Гибкий состав 1 игрок → MM доукомплектация",
        "P1", "E2E",
        "Соло-игрок Mercenary, Ready.",
        [
            ("Запустить поиск в одиночку", "MM добирает команду до 5 Merc + формирует матч 2v5"),
        ],
    ),
    # ===== MATCHMAKING =====
    (
        "TC-MM-001", "MM / Accept", "Accept матча всеми игроками",
        "P0", "E2E",
        "Поиск завершён; матч найден.",
        [
            ("Всем игрокам показан popup подтверждения", "Таймер 15–20 сек; кнопки Accept / Decline"),
            ("Все игроки нажимают «Принять»", "Переход на экран «Общее лобби»"),
        ],
    ),
    (
        "TC-MM-002", "MM / Penalty", "Leaver penalty при не-Accept",
        "P0", "E2E",
        "Матч найден; 1 игрок не нажимает Accept / Decline.",
        [
            ("Дождаться истечения таймера", "Матч отменён для всех"),
            ("Проверить не-Accept игрока", "Временный бан на поиск: 15 / 30 / 120 / 720 мин (по эскалации)"),
            ("Проверить остальных", "Возврат в лобби; бан не применён"),
        ],
    ),
    (
        "TC-MM-003", "MM / Showdown", "Общее лобби — состав 2 Boss + 5 Merc",
        "P0", "E2E",
        "Все Accept; матч 2v5.",
        [
            ("Открыт экран общего лобби", "2 карточки Boss + 5 карточек Merc на каждой стороне"),
            ("Проверить снаряжение", "У каждой карточки 5 иконок слотов"),
        ],
    ),
    (
        "TC-MM-004", "MM / Showdown", "Просмотр снаряжения противника в общем лобби",
        "P1", "E2E",
        "Общее лобби открыто.",
        [
            ("Навести курсор на слот снаряжения противника", "Tooltip: название, buff, debuff, active skill"),
            ("Кликнуть на слот противника", "Selection UI не открывается (только просмотр)"),
        ],
    ),
    (
        "TC-MM-005", "MM / Showdown", "Автоконнект через 30 секунд",
        "P1", "E2E",
        "Общее лобби открыто.",
        [
            ("На экране общего лобби дождаться 30 сек", "Таймер отсчитывается"),
            ("По истечении таймера", "Автоматическое подключение к CS2 серверу"),
        ],
    ),
    (
        "TC-MM-006", "MM / Reservation", "Резервация предметов на время матча",
        "P0", "E2E",
        "Матч начался; loadout залочен.",
        [
            ("Во время матча попытаться Sell предмета из loadout", "HTTP 409 reserved"),
        ],
    ),
    # ===== IN-GAME =====
    (
        "TC-GAME-001", "In-Game / Loadout", "Применение loadout в матче",
        "P0", "Game E2E",
        "Полный валидный loadout (5 слотов, durability > 0).",
        [
            ("Зайти в CS2 матч Dominion", "Матч загружен"),
            ("Проверить passive-эффект (smoke: Стелс-Подошва V1)", "Бесшумное приземление работает"),
            ("Проверить Status Bar", "Иконки активных пассивок в нижней части экрана"),
        ],
    ),
    (
        "TC-GAME-002", "In-Game / Durability", "Сломанный предмет не даёт эффекта in-game",
        "P0", "Game E2E",
        "Экипирован предмет durability=0 (dev override / тестовый матч).",
        [
            ("Зайти в матч", "Предмет визуально «сломан»"),
            ("Проверить бафф предмета", "Эффект не срабатывает"),
        ],
    ),
    (
        "TC-GAME-003", "In-Game / Skills", "Active skill E (слот Голова)",
        "P0", "Game E2E",
        "Boss с «Нейро-Сборщик Геликс» (E); КД=20с.",
        [
            ("Нажать E в бою", "Скилл активирован: HP/броня врагов над головами"),
            ("Проверить HUD", "Иконка E затенена; CD-индикатор заполняется"),
            ("Нажать E до окончания CD", "Скилл не активируется повторно"),
        ],
    ),
    (
        "TC-GAME-004", "In-Game / Skills", "Active skill F (слот Грудь/Скелет)",
        "P0", "Game E2E",
        "Boss с «Био-Резерв Zetta» (F); КД=25с.",
        [
            ("Нажать F в бою", "+50 брони мгновенно"),
            ("Проверить HUD", "Иконка F на CD ~25с"),
        ],
    ),
    (
        "TC-GAME-005", "In-Game / Buffs", "Passive trigger — Анти-Крипт V1",
        "P1", "Game E2E",
        "Mercenary с Анти-Крипт V1 в слоте head.",
        [
            ("Опустошить магазин основного оружия", "Автоматический пинг ближайшего врага на карте"),
        ],
    ),
    (
        "TC-GAME-006", "In-Game / Debuffs", "Debuff weapon block — Рефлекс Молния",
        "P1", "Game E2E",
        "Boss с «Рефлекс Молния» (запрет Molotov/Incendiary).",
        [
            ("Открыть buy menu", "Зажигательные гранаты и Молотов недоступны для покупки"),
        ],
    ),
    (
        "TC-GAME-007", "In-Game / Skills", "Chrome Repair V2 — сброс CD скилла E",
        "P2", "Game E2E",
        "Boss с Chrome Repair V2 (F) и active E на CD.",
        [
            ("Использовать E → дождаться CD", "E на перезарядке"),
            ("Нажать F (Chrome Repair V2)", "CD скилла E сброшен; F уходит на CD 50с"),
        ],
    ),
    # ===== WEAR / POSTMATCH =====
    (
        "TC-WEAR-001", "Postmatch / Durability", "Износ после штатного завершения матча",
        "P0", "E2E",
        "Common-предмет durability=95%; матч завершён штатно.",
        [
            ("Завершить матч", "Редирект на экран итогов платформы"),
            ("Проверить блок прочности", "Нотификация: 95% → 67% (износ 28 за матч для Common)"),
            ("Проверить backend", "ApplyMatchWear идемпотентен по match_id"),
        ],
    ),
    (
        "TC-WEAR-002", "Postmatch / Penalty", "Ливер — износ + бан на поиск",
        "P0", "E2E",
        "Матч в процессе; durability до лива зафиксирован.",
        [
            ("Игрок добровольно покидает матч до конца", "Матч прерван для игрока"),
            ("Проверить прочность", "Износ списан как за обычный матч"),
            ("Попытаться начать поиск", "Бан на поиск: 15/30/120/720 мин"),
        ],
    ),
    (
        "TC-WEAR-003", "Postmatch / Durability", "Crash сервера — износ не списывается",
        "P0", "E2E",
        "Матч отменён системой / crash сервера; durability до матча зафиксирован.",
        [
            ("Симулировать crash/cancel матча", "Игрок возвращён на платформу"),
            ("Проверить прочность всех 5 предметов", "Значения без изменений"),
        ],
    ),
    (
        "TC-WEAR-004", "Postmatch / Stats", "Постматч — блок статистики",
        "P1", "E2E",
        "Матч завершён; Boss использовал E/F.",
        [
            ("Открыть экран итогов", "Блок «Статистика» отображается"),
            ("Проверить стандартные метрики", "K/D/A, ADR"),
            ("Проверить Dominion stats", "Кол-во использований E/F; поглощённый урон (Boss) / урон по Boss (Merc)"),
        ],
    ),
    (
        "TC-WEAR-005", "Postmatch / Rewards", "Постматч — блок наград",
        "P1", "E2E",
        "Матч завершён штатно.",
        [
            ("Открыть экран итогов", "Блок «Награды» отображается (приоритетный)"),
            ("Проверить начисления", "XP и Gold отображены"),
            ("Проверить квесты", "Прогресс daily quest обновлён"),
        ],
    ),
    (
        "TC-WEAR-006", "Postmatch / Repair", "Кнопка «Починить всё» с постматча",
        "P2", "E2E",
        "≥2 предмета с durability=0 после матча.",
        [
            ("На экране итогов нажать «Починить всё»", "Переход в flow массового ремонта"),
        ],
    ),
    # ===== FULL FLOWS =====
    (
        "TC-FULL-001", "E2E / Full Flow", "Happy Path — F2P Mercenary (полный цикл)",
        "P0", "E2E",
        "U-F2P-LEAD; пустой инвентарь; admin доступен.",
        [
            ("Admin Grant 5 Base-предметов", "Предметы в инвентаре"),
            ("Экипировать все 5 слотов", "Loadout полный"),
            ("Создать лобби Mercenary → Ready → Поиск", "Поиск запущен; reservation active"),
            ("Accept матча → Общее лобби 30с", "Коннект к CS2"),
            ("Сыграть матч до конца", "Матч завершён"),
            ("Экран итогов: stats + wear", "Износ списан; награды начислены"),
            ("Repair kit → снова в поиск", "Цикл повторяется без ошибок"),
        ],
    ),
    (
        "TC-FULL-002", "E2E / Full Flow", "Happy Path — PRO Boss duo",
        "P0", "E2E",
        "U-PRO-LEAD + U-PRO-MEM; Advanced loadout с E/F.",
        [
            ("Создать лобби Boss (2 игрока)", "2 слота Boss"),
            ("Экипировать Advanced head (E) + chest (F)", "Loadout валиден"),
            ("Поиск → Accept → Матч", "Матч 2v5"),
            ("Использовать E и F в бою", "Скиллы работают; CD отображаются"),
            ("Постматч → RepairByGold → Sell дубликата", "Economy flow без ошибок"),
        ],
    ),
    (
        "TC-FULL-003", "E2E / Invites", "Инвайт cross-subscription (PRO Merc + F2P)",
        "P0", "E2E",
        "PRO-хост и F2P друг доступны.",
        [
            ("PRO-хост создаёт лобби Mercenary", "Лобби создано"),
            ("Инвайт F2P друга → друг принимает", "F2P в команде Mercenary"),
            ("Попытка сменить сторону на Boss", "Заблокировано"),
            ("Поиск → матч → постматч", "Полный цикл успешен"),
        ],
    ),
    (
        "TC-FULL-004", "E2E / Reservation", "Reservation lifecycle",
        "P0", "E2E",
        "Валидный loadout; поиск доступен.",
        [
            ("Поиск → lock active", "Sell/Repair заблокированы"),
            ("Отмена поиска → ReleaseBatch", "Lock снят; операции доступны"),
            ("Repair предмета → повторный поиск", "Lock снова active"),
            ("Полный матч → завершение", "Lock снят после матча"),
        ],
    ),
    # ===== NEGATIVE =====
    (
        "TC-NEG-001", "Negative / Reservation", "ValidateAndLock — 1 невалидный игрок блокирует всё лобби",
        "P1", "E2E",
        "Лобби 5 игроков; у 1 игрока broken item.",
        [
            ("Лидер запускает поиск", "valid=false для всего лобби"),
            ("Проверить reservation", "Лок не поставлен ни на одного игрока"),
        ],
    ),
    (
        "TC-NEG-002", "Negative / Reservation", "Повторный ReleaseBatch — idempotent",
        "P2", "API",
        "Reservation уже снята.",
        [
            ("ReleaseBatch(reservation_key)", "Успех"),
            ("Повторить ReleaseBatch с тем же key", "No-op; без ошибки"),
        ],
    ),
    (
        "TC-NEG-003", "Negative / PRO", "PRO подписка истекла mid-lobby",
        "P1", "E2E",
        "PRO-игрок с Advanced equipped; подписка истекает (симуляция).",
        [
            ("Запустить поиск / старт матча", "Валидация: ошибка или force unequip Advanced"),
            ("Проверить UI", "Понятное сообщение пользователю"),
        ],
    ),
    (
        "TC-NEG-004", "Negative / Wear", "Дубль ApplyMatchWear по match_id",
        "P1", "API",
        "match.finished может прийти дважды.",
        [
            ("Отправить match.finished дважды с одним match_id", "Износ применён 1 раз (dedup)"),
        ],
    ),
    # ===== ITEM SMOKE =====
    (
        "TC-ITEM-HEAD-001", "Items / Голова", "Нейро-Сборщик Геликс (Rare, Active E)",
        "P1", "Game E2E",
        "Boss PRO; предмет в инвентаре.",
        [
            ("Экипировать; проверить tooltip", "Active E, КД 20с, debuff: +20% урон от падения"),
            ("В матче нажать E", "HP/броня врагов над головами; CD 20с"),
        ],
    ),
    (
        "TC-ITEM-CHEST-001", "Items / Грудь", "Био-Резерв Zetta (Rare, Active F)",
        "P1", "Game E2E",
        "Boss PRO; предмет в инвентаре.",
        [
            ("Экипировать; tooltip", "Active F, КД 25с, +50 брони"),
            ("В матче нажать F", "Броня +50; CD 25с"),
        ],
    ),
    (
        "TC-ITEM-HANDS-001", "Items / Кисти", "Перчатки Маркер-Пыль (Legendary)",
        "P2", "Game E2E",
        "Предмет в инвентаре.",
        [
            ("Экипировать; tooltip", "Passive: HE отключает скиллы Boss на 5с"),
            ("Бросить HE в Boss", "Активные скиллы Boss недоступны 5с"),
        ],
    ),
    (
        "TC-ITEM-LEGS-001", "Items / Ноги", "Брюки Ghost Серая (Legendary)",
        "P2", "Game E2E",
        "Предмет в инвентаре.",
        [
            ("Экипировать; tooltip", "Anti-Tagging 100% при беге"),
            ("Получить попадание при беге", "Скорость не снижается (tagging)"),
        ],
    ),
    (
        "TC-ITEM-FEET-001", "Items / Ступни", "Стелс-Подошва V1 (Common)",
        "P1", "Game E2E",
        "F2P; предмет в инвентаре.",
        [
            ("Экипировать F2P; tooltip", "Silent landing passive"),
            ("Прыжок с высоты", "Звук приземления отсутствует"),
        ],
    ),
    (
        "TC-ITEM-WEAR-001", "Items / Durability", "Износ по редкости (Common vs Legendary)",
        "P2", "E2E",
        "Common и Legendary предметы на 100% durability.",
        [
            ("Матч с Common-предметом (100%)", "Износ −28% → 72%"),
            ("Матч с Legendary-предметом (100%)", "Износ −11% → 89%"),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Workbook builders
# ---------------------------------------------------------------------------

def build_instructions(ws) -> None:
    ws.title = "Инструкция"
    set_widths(ws, [28, 95])
    rows = [
        ("Параметр", "Значение"),
        ("Проект", "Dominion — E2E тест-кейсы"),
        ("Версия", "1.0 / 07.08.2026"),
        ("Out of scope", "NFT"),
        ("", ""),
        ("Лист TestCases", "Одна строка = один тест-кейс (сводка). Колонка Steps_Combined — все шаги в одной ячейке."),
        ("Лист Steps", "Одна строка = один шаг. Формат: Шаг | Ожидаемый результат. Основной лист для импорта."),
        ("Лист Сводка", "Количество кейсов по модулям и приоритетам."),
        ("", ""),
        ("Импорт TestRail", "Используйте CSV/Excel import: Case ID → Title → Section (Module) → Priority → Preconditions → Steps (Action + Expected)."),
        ("Импорт Zephyr / Xray", "Лист Steps: Case ID + Step # + Action + Expected Result."),
        ("Приоритеты", "P0 Blocker | P1 Critical | P2 Major | P3 Minor"),
        ("Статус (колонка)", "Not Run / Pass / Fail / Blocked — для ручного прогона"),
        ("", ""),
        ("Тестовые аккаунты", "U-PRO-LEAD, U-PRO-MEM, U-F2P-LEAD, U-F2P-MEM, U-F2P-BROKEN, U-F2P-MIXED, U-PRO-NOGOLD, U-ADMIN, U-SUPPORT"),
        ("Пересборка", "python3 scripts/generate_dominion_e2e_excel.py"),
    ]
    for i, (a, b) in enumerate(rows, 1):
        ws.cell(i, 1, a)
        ws.cell(i, 2, b)
        ws.cell(i, 1).border = BORDER
        ws.cell(i, 2).border = BORDER
        ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(i, 2).alignment = Alignment(wrap_text=True, vertical="top")
    style_header(ws, 1, 2)


def _steps_combined(steps: list[tuple[str, str]]) -> str:
    parts = []
    for i, (action, expected) in enumerate(steps, 1):
        parts.append(f"{i}. {action}\n   → {expected}")
    return "\n".join(parts)


def build_test_cases(ws) -> None:
    ws.title = "TestCases"
    headers = [
        "Case ID",
        "Module",
        "Title",
        "Priority",
        "Type",
        "Preconditions",
        "Steps Count",
        "Steps_Combined",
        "Status",
        "Assignee",
        "Comment",
        "Automation",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header(ws, 1, len(headers))
    set_widths(ws, [16, 24, 48, 10, 12, 50, 10, 70, 12, 14, 30, 12])

    status_dv = DataValidation(type="list", formula1='"Not Run,Pass,Fail,Blocked"', allow_blank=True)
    auto_dv = DataValidation(type="list", formula1='"Manual,To Automate,Automated"', allow_blank=True)
    ws.add_data_validation(status_dv)
    ws.add_data_validation(auto_dv)

    for i, (cid, module, title, priority, typ, pre, steps) in enumerate(CASES, 2):
        ws.cell(i, 1, cid)
        ws.cell(i, 2, module)
        ws.cell(i, 3, title)
        ws.cell(i, 4, priority)
        ws.cell(i, 5, typ)
        ws.cell(i, 6, pre)
        ws.cell(i, 7, len(steps))
        ws.cell(i, 8, _steps_combined(steps))
        ws.cell(i, 9, "Not Run")
        ws.cell(i, 10, "")
        ws.cell(i, 11, "")
        ws.cell(i, 12, "Manual")
        style_row(ws, i, len(headers), priority)
        ws.row_dimensions[i].height = max(45, 18 * len(steps))

    last = 1 + len(CASES)
    status_dv.add(f"I2:I{last}")
    auto_dv.add(f"L2:L{last}")
    ws.auto_filter.ref = f"A1:L{last}"
    ws.freeze_panes = "A2"


def build_steps(ws) -> None:
    """Primary import sheet: one row = one step | expected."""
    ws.title = "Steps"
    headers = [
        "Case ID",
        "Module",
        "Title",
        "Priority",
        "Type",
        "Preconditions",
        "Step #",
        "Step (Action)",
        "Expected Result",
        "Status",
        "Comment",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    style_header(ws, 1, len(headers))
    set_widths(ws, [16, 24, 42, 10, 12, 40, 8, 55, 55, 12, 28])

    status_dv = DataValidation(type="list", formula1='"Not Run,Pass,Fail,Blocked"', allow_blank=True)
    ws.add_data_validation(status_dv)

    row = 2
    for cid, module, title, priority, typ, pre, steps in CASES:
        for step_no, (action, expected) in enumerate(steps, 1):
            ws.cell(row, 1, cid)
            ws.cell(row, 2, module)
            ws.cell(row, 3, title)
            ws.cell(row, 4, priority)
            ws.cell(row, 5, typ)
            ws.cell(row, 6, pre if step_no == 1 else "")
            ws.cell(row, 7, step_no)
            ws.cell(row, 8, action)
            ws.cell(row, 9, expected)
            ws.cell(row, 10, "Not Run")
            ws.cell(row, 11, "")
            style_row(ws, row, len(headers), priority)
            row += 1

    last = row - 1
    status_dv.add(f"J2:J{last}")
    ws.auto_filter.ref = f"A1:K{last}"
    ws.freeze_panes = "A2"


def build_summary(ws) -> None:
    ws.title = "Сводка"
    set_widths(ws, [28, 12, 12, 12, 12, 12])

    ws.cell(1, 1, "Модуль")
    for c, h in enumerate(["Всего", "P0", "P1", "P2", "P3"], 2):
        ws.cell(1, c, h)
    style_header(ws, 1, 6)

    by_module: dict[str, dict[str, int]] = {}
    for cid, module, title, priority, typ, pre, steps in CASES:
        root = module.split(" / ")[0] if " / " in module else module
        # group by prefix
        if cid.startswith("TC-ADM"):
            root = "Админка"
        elif cid.startswith("TC-INV"):
            root = "Инвентарь"
        elif cid.startswith("TC-LOB"):
            root = "Лобби"
        elif cid.startswith("TC-MM"):
            root = "Матчмейкинг"
        elif cid.startswith("TC-GAME"):
            root = "In-Game"
        elif cid.startswith("TC-WEAR"):
            root = "Постматч"
        elif cid.startswith("TC-FULL"):
            root = "Сквозные"
        elif cid.startswith("TC-NEG"):
            root = "Негативные"
        elif cid.startswith("TC-ITEM"):
            root = "Предметы (smoke)"
        bucket = by_module.setdefault(root, {"Всего": 0, "P0": 0, "P1": 0, "P2": 0, "P3": 0})
        bucket["Всего"] += 1
        bucket[priority] += 1

    order = [
        "Админка", "Инвентарь", "Лобби", "Матчмейкинг", "In-Game",
        "Постматч", "Сквозные", "Негативные", "Предметы (smoke)",
    ]
    r = 2
    totals = {"Всего": 0, "P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for name in order:
        data = by_module.get(name)
        if not data:
            continue
        ws.cell(r, 1, name)
        for c, key in enumerate(["Всего", "P0", "P1", "P2", "P3"], 2):
            ws.cell(r, c, data[key])
            totals[key] += data[key]
        style_row(ws, r, 6)
        r += 1

    ws.cell(r, 1, "ИТОГО")
    ws.cell(r, 1).font = Font(bold=True)
    for c, key in enumerate(["Всего", "P0", "P1", "P2", "P3"], 2):
        ws.cell(r, c, totals[key])
        ws.cell(r, c).font = Font(bold=True)
    style_row(ws, r, 6)
    ws.cell(r, 1).fill = SECTION_FILL

    r += 2
    ws.cell(r, 1, "Всего шагов (лист Steps)")
    total_steps = sum(len(c[6]) for c in CASES)
    ws.cell(r, 2, total_steps)
    style_row(ws, r, 2)

    r += 2
    ws.cell(r, 1, "NFT")
    ws.cell(r, 2, "Out of scope")


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "docs" / "qa" / "Dominion_E2E_TestCases.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    # reuse first sheet
    build_instructions(wb.active)
    build_test_cases(wb.create_sheet())
    build_steps(wb.create_sheet())
    build_summary(wb.create_sheet())

    wb.save(out)
    n_cases = len(CASES)
    n_steps = sum(len(c[6]) for c in CASES)
    print(f"Wrote {out}")
    print(f"Cases: {n_cases} | Steps: {n_steps}")


if __name__ == "__main__":
    main()
