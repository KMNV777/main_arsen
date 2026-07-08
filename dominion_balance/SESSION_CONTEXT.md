# Dominion — контекст сессии (выгрузка)

> Дата: 2026-07-08  
> Ветка: `cursor/dominion-variant-flashpoint-e4b6`  
> PR: https://github.com/KMNV777/main_arsen/pull/41

---

## 1. О проекте

Режим **Dominion** — конфигурация имплантов/модулей для игроков по **Steam ID64**. Каждый игрок получает набор **фабрик** (имплантов), у каждой — **бафф** (плюс) и **дебафф** (минус). Схема risk/reward.

### Формат импорта (`dominion_grants.json`)

```json
{
  "<SteamID64>": {
    "role": "boss" | "mercenary",
    "factories": [
      {
        "factory": "PascalCaseFactoryName",
        "buff": { "name": "ModifierName", "...params" },
        "debuff": { "name": "ModifierName", "...params" }
      },
      { "factory": "FactoryWithDefaultsOnly" }
    ]
  }
}
```

Запись **без** `buff`/`debuff` — дефолтные эффекты из каталога фабрик.

### Единицы и параметры

| Параметр | Значение |
|----------|----------|
| `*_frames` | Тики сервера (64 tick → 64f ≈ 1 с) |
| `velocity_modifier` | Множитель скорости (1.0 = база) |
| `damage_scale` | Множитель урона (>1 = больше) |
| `damage_mask` | Битовая маска (8 = огонь, 64 = взрыв/HE) |
| `max_health_delta` | Изменение max HP |
| `immediate_health_delta` | Изменение текущего HP |
| `armor_value` / `armor_bonus` | Броня |
| `active_frames` / `cooldown_frames` / `lock_frames` | Длительность эффектов |
| `blocked_definition_a/b` | ID weapon definition для блока |
| `apply_for_attacker` / `apply_for_victim` | Направление модификатора |
| `body_only` / `leg_only` | Фильтр зоны попадания |

### Именование модификаторов

- **Дефолтные** — из каталога (`TeammateDeadHealth`, `AimPunch`, …)
- **Balanced\*** — ослабленные/усиленные для competitive-тестов
- **Flashpoint\*** — burst/situational профиль
- **Bulwark\*** — survival/tank профиль

---

## 2. Исходные материалы

### Каталог модификаторов

Файл: `DominionModifiersList.md` (122 фабрики)

Каждая фабрика: дефолтный бафф + дефолтный дебафф + тип реализации (`Velocity`, `MaxHealth`, `AimPunch`, `WeaponBlock`, `BulletMirror`, `SchemaPulse`, …).

Примеры фабрик:

| # | Factory | Бафф | Дебафф |
|---|---------|------|--------|
| 1 | VelocityChip | VulnerableMapHint | VelocityPenalty (−5% скорости) |
| 6 | CreditReaderV1 | TeammateDeadHealth (+30 max HP) | AimPunch (+10%) |
| 24 | DataHackSlowdown | FlashImmunityAfterPlant | PrimaryClipCap (−10% магазин) |
| 36 | ChromoArmorTank | extinguish (cd 1280f) | NoJumpAfterDamage (32f) |
| 42 | EnergyShield | LowHealthHeal (+40 HP) | KillRadarReveal |

### Исходный balanced-конфиг

Файл: `dominion_grants.json` — 6 Steam ID, профиль `Balanced*`.

---

## 3. Steam ID и роли (тестовая группа)

| Steam ID | Роль |
|----------|------|
| `76561199530013153` | boss |
| `76561198836236005` | boss |
| `76561198290940309` | mercenary |
| `76561198728722755` | mercenary |
| `76561198184450067` | mercenary |
| `76561198302751753` | mercenary |

---

## 4. Созданные варианты баланса

### 4.1 Balanced (исходный)

Файл: `dominion_grants.json` (upload)

Философия: competitive-tuned, симметричные `Balanced*` модификаторы.

**Boss 1** (`76561199530013153`): ChromeArmor, BioRegeneration, ZeroFlashProtocol  
**Boss 2** (`76561198836236005`): ChromoArmorTank, DataHackSlowdown, AbsorberBoots  
**Merc 1** (`76561198290940309`): CreditReaderV1, FastNetworkV2, GhostJacketGray  
**Merc 2** (`76561198728722755`): AccuracyZoneV1, VentilationImplant  
**Merc 3** (`76561198184450067`): AntiKineticV1, VisorGridHelmetLed  
**Merc 4** (`76561198302751753`): BioPatchHpV1, MiniRadarV1, VentilationImplant  

---

### 4.2 Flashpoint (burst / situational)

Файл: `dominion_balance/dominion_grants_flashpoint.json`

Философия: короткие окна силы (32f), быстрые кулдауны, event-триггеры (килл, низкое HP, плент). **Другие импланты**, не те же что в Balanced.

| Steam ID | Роль | Стиль | Импланты |
|----------|------|-------|----------|
| `76561199530013153` | boss | Берсерк | AdrenalineChestImplant, FortressChestBlock, KineticAmplifier |
| `76561198836236005` | boss | Контроль зоны | AdaptiveCamouflageGhost, DataHackSlowdown, OracleVisor |
| `76561198290940309` | mercenary | Саппорт | SecondBreathImplant, MedicCargoPants, CreditReaderV1 |
| `76561198728722755` | mercenary | Энтри | LightningReflex, SprinterBioMuscles, AccuracyZoneV1 |
| `76561198184450067` | mercenary | Пост-плент | AntiKineticV1, JumperServo, HackProtocolBomb |
| `76561198302751753` | mercenary | Снайпер | SniperCyberProsthesis, RangefinderV1, PistolReflexV1 |

Ключевые значения Flashpoint:
- Dash: `active_frames: 24`, `cooldown_frames: 2560`
- Short invuln: `active_frames: 32`, `cooldown_frames: 3840`
- Tap damage: `damage_scale: 1.1`
- Low HP speed: `health_threshold: 22`, `velocity_modifier: 1.18`
- Bomb body damage: `damage_scale: 1.15`
- Recoil resist: `scale: 0.65`

---

### 4.3 Bulwark (survival / tank)

Файл: `dominion_balance/dominion_grants_bulwark.json`

Философия: броня, резисты, хил. Цена — скорость и мобильность.

| Steam ID | Роль | Стиль | Импланты |
|----------|------|-------|----------|
| `76561199530013153` | boss | Танк | ChromeArmor (+35 HP), KevlarAntishockJacket, ChromoArmorTank |
| `76561198836236005` | boss | Анти-огонь | SyndicateJacketLeather, EnergyShield (+35 HP), PhoenixJacket |
| `76561198290940309` | mercenary | Медик | GhostJacketGray, MedicCargoPants, MedicArmorJacket |
| `76561198728722755` | mercenary | Якорь | GladiatorChromeHelmetMetal, VanguardJacketBlue, VentilationImplant |
| `76561198184450067` | mercenary | Ротация | ResistorBoots, RangefinderV1, VisorGridHelmetLed |
| `76561198302751753` | mercenary | Саппорт | BioTriggerAutoHeal, SecondBreathImplant, QuietStepPants |

Ключевые значения Bulwark:
- Boss armor: `max_health_delta: 35`, `armor_value: 80`, `velocity_modifier: 0.88`
- Wallbang resist: `damage_scale: 0.55`
- Molotov resist: `damage_scale: 0.45` (mask 8)
- Heal amplify: `bonus_scale: 0.55`
- AWP body resist: `damage_scale: 0.82`
- Leg resist: `damage_scale: 0.72`

---

### 4.4 Бенчмарк-варианты (16 фабрик, один Steam ID)

Ветка `origin/cursor/dominion-balance-variants-61ec`:

| Файл | Философия |
|------|-----------|
| `variant_1_aggressive.json` | High-risk / high-reward (+50% баффы и дебаффы) |
| `variant_2_defensive.json` | Low-risk / low-reward (мягкие значения) |
| `variant_3_competitive.json` | Симметричный, k≈1.0 |
| `variant_4_flashpoint.json` | Burst (snake_case, массив grants) |

Бенчмарк Steam ID: `76561198836236005`  
Формат: массив `[{ factory, buff, debuff }, ...]` (snake_case factory names).

---

## 5. Файлы в репозитории (текущая ветка)

```
dominion_balance/
├── README.md
├── SESSION_CONTEXT.md          ← этот файл
├── variant_4_flashpoint.json   ← бенчмарк 16 фабрик
├── dominion_grants_flashpoint.json
└── dominion_grants_bulwark.json
```

### Загруженные пользователем файлы (uploads)

```
/home/ubuntu/.cursor/projects/workspace/uploads/
├── DominionModifiersList__12GAeM__3633.md
└── dominion_grants__VHWwje__4ca6.json
```

---

## 6. Сравнение профилей

| Профиль | Фокус | HP босса | Скорость | Урон | Импланты |
|---------|-------|----------|----------|------|----------|
| Balanced | Competitive parity | +20 | −5% | ±8–12% | Исходный набор |
| Flashpoint | Burst windows | — | +10–18% burst | +10–15% burst | Новые, situational |
| Bulwark | Survival | +35 | −12% | −12–45% taken | Tank/heal/resist |
| Aggressive | Pub/fragger | +75 | −25% | ±20–25% | Те же 16, усиленные |
| Defensive | Team/newbie | +25 | −8% | ±5–8% | Те же 16, мягкие |

---

## 7. Как применять

1. Выбрать JSON-файл (`dominion_grants_*.json`)
2. Заменить Steam ID на реальные тестеров при необходимости
3. Импортировать на игровой сервер как `dominion_grants.json`
4. Перезагрузить конфиг (механизм reload не документирован в этом репозитории)

---

## 8. История запросов в сессии

1. **Балансные конфигурации по Steam ID** — выдан исходный `dominion_grants.json` с описанием баффов/дебаффов
2. **Ещё один вариант модификаторов** — создан Flashpoint (variant 4)
3. **В структуре `{ role, factories }`** — переформатирован flashpoint без `_meta`
4. **Ещё один конфиг** — создан Bulwark (survival)
5. **Выгрузка контекста** — этот файл

---

## 9. Полные JSON-конфиги

### 9.1 Balanced (исходный)

См. `dominion_grants__VHWwje__4ca6.json` в uploads.

### 9.2 Flashpoint

См. `dominion_balance/dominion_grants_flashpoint.json`

### 9.3 Bulwark

См. `dominion_balance/dominion_grants_bulwark.json`

---

## 10. Remote-ветки (контекст репозитория)

| Ветка | Содержимое |
|-------|------------|
| `origin/cursor/dominion-balance-variants-61ec` | variant_1/2/3 + README |
| `origin/cursor/f2f-role-balance-json-57d2` | F2F role balance, generate_role_balance.py |
| `origin/cursor/merge-dominion-json-7bd4` | Таблицы фабрик, КФГ для Арсена.json |
| `origin/cursor/gaming-support-knowledge-base-d9a3` | Gaming support docs (не проверено) |

Основная ветка `main` — IT landscape / EMG архитектура, без игрового кода.
