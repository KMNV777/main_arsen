# ТЗ: Загрузка ресурса в Грузовой Шаттл

| Метаданные | |
|---|---|
| **Проект** | AstroCrop |
| **Фича** | Грузовой Шаттл — аналог поездов в Township |
| **Скоуп документа** | Часть функциональности — загрузка одного ресурса в один cargo‑слот |
| **Аудитория** | Клиентский разработчик |

> Документ описывает только то, что прямо требует бриф: **что видит игрок, на какие кнопки нажимает и что происходит при нехватке ресурса**. Запуск шаттла, кулдаун, награды — вне скоупа.

---

## 1. Что видит игрок

При открытии Экрана Шаттла игрок видит **карточку cargo‑слота** со следующими элементами:

| Элемент | Описание | Источник данных |
|---------|----------|-----------------|
| **Иконка ресурса** | 96×96 px | `ResourceConfig.iconPath` |
| **Название ресурса** | 1 строка, локализовано (например, «Кристалл замёрзшего метана») | `ResourceConfig.locKey` |
| **Сколько нужно** | Крупное число, формат `loaded / required` (например, `3 / 5`) | `slot.loaded`, `slot.required` |
| **Сколько есть у игрока** | Мелкая строка `У тебя: N`. При `N == 0` подсвечивается красным | `playerStock[resourceId]` |
| **Прогресс‑бар** | Заливка `loaded / required` | вычисляется |
| **Кнопка действия** | См. раздел 2 | вычисляется |
| **Бейдж `✓ Готово`** | Появляется поверх карточки при `loaded == required` | вычисляется |

ASCII‑макет карточки:

```
 ┌──────────────────────────────┐
 │       [ icon 96×96 ]         │
 │   Кристалл замёрзшего метана │
 │                              │
 │            3 / 5             │
 │       ▓▓▓▓▓▓░░░░░░           │
 │       У тебя: 2              │
 │                              │
 │      [   Загрузить   ]       │
 └──────────────────────────────┘
```

---

## 2. На какую кнопку нажимает игрок

В карточке слота — **одна кнопка действия**. Её внешний вид и поведение зависят от соотношения `playerStock` и `required − loaded`:

| Стейт кнопки | Условие | Вид | Что делает по тапу |
|--------------|---------|-----|---------------------|
| **Available** | `playerStock ≥ required − loaded` | Зелёная `Загрузить` | Грузит `delta = required − loaded`. Слот → `Done`. |
| **Partial** | `0 < playerStock < required − loaded` | Жёлтая `Загрузить (+N)`, где `N = playerStock` | Грузит `delta = playerStock`. Слот → `Missing`. |
| **Missing** | `playerStock == 0` и `loaded < required` | Серая `Загрузить` (disabled). Рядом — синяя `Купить (N) за 💎 He‑3` | См. раздел 3. |
| **Done** | `loaded == required` | Скрыта; вместо неё бейдж `✓ Готово` | Тап ничего не делает (тултип «Слот заполнен»). |

После любой загрузки склад уменьшается на `delta`, прогресс слота увеличивается на `delta`, карточка перерисовывается синхронно, стейт кнопки пересчитывается.

---

## 3. Что происходит, если ресурса не хватает

Условие: `playerStock == 0` и `loaded < required` (стейт кнопки **Missing**).

1. Кнопка `Загрузить` неактивна (серая). Тап → шейк‑анимация и тултип «Не хватает ресурса. Произведи на ферме или купи за He‑3».
2. Счётчик `У тебя: 0` подсвечен красным.
3. Рядом с серой кнопкой появляется синяя **`Купить (N) за 💎 He‑3`**, где:
   - `N = required − loaded`,
   - `price = N × ResourceConfig.he3PricePerUnit`.
4. Тап `Купить` → диалог подтверждения с двумя кнопками `Отмена` / `Купить`:
   - Если `playerHe3 ≥ price` → на `Купить` атомарно: `playerHe3 −= price`, `slot.loaded = required`. Слот → `Done`.
   - Если `playerHe3 < price` → кнопка `Купить` подменяется на `+ Пополнить`, ведёт в Premium Shop. После пополнения игрок возвращается, может повторить покупку.
5. Тап `Отмена` или закрытие диалога → ничего не списано, прогресс слота сохранён.

**Edge‑case:** пока открыт диалог, склад мог пополниться (фабрика выдала ресурс по таймеру). На закрытии диалога стейт кнопки пересчитывается — он мог уехать из `Missing` в `Available`.

---

## 4. Структуры данных

```ts
type CargoSlot = {
  resourceId: string;
  required: int;        // immutable
  loaded: int;          // 0..required
};

type ResourceConfig = {
  id: string;
  iconPath: string;
  locKey: string;
  he3PricePerUnit: int;
};
```

---

## 5. Псевдокод обработчиков

```pseudo
function onLoadTap(slot):
    if slot.loaded >= slot.required: return
    available = playerStock[slot.resourceId]
    if available <= 0:
        showTooltip("not_enough_resource"); return

    delta = min(available, slot.required - slot.loaded)
    playerStock[slot.resourceId] -= delta
    slot.loaded += delta
    refreshSlotUI(slot)


function onBuyTap(slot):
    missing = slot.required - slot.loaded
    price = missing * ResourceConfig[slot.resourceId].he3PricePerUnit

    if playerHe3 < price:
        openPremiumShop(); return

    showConfirmDialog(price, missing) -> confirmed:
        if not confirmed: return
        // атомарно
        playerHe3 -= price
        slot.loaded = slot.required
        refreshSlotUI(slot)
```
