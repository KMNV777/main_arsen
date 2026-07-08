# Dominion — балансные варианты модификаторов

## Варианты

| # | Файл | Философия | Когда использовать |
|---|------|-----------|-------------------|
| 1 | `variant_1_aggressive.json` | High-risk / high-reward | Паб, соло-фраг |
| 2 | `variant_2_defensive.json` | Low-risk / low-reward | Командная игра, новички |
| 3 | `variant_3_competitive.json` | Симметричный, k≈1.0 | Соревновательный режим |
| 4 | `variant_4_flashpoint.json` | **Burst / situational** | Короткие окна силы, event-триггеры |
| 5 | `dominion_grants_bulwark.json` | **Bulwark / survival** | Броня, резисты, хил — цена в скорости и мобильности |

## Форматы

### Бенчмарк (16 фабрик, один Steam ID)

`variant_*.json` — массив grants для `76561198836236005`, snake_case factory names.

### Per-player (роли + Steam ID)

`dominion_grants_flashpoint.json`, `dominion_grants_bulwark.json` — объект `{ steamId: { role, factories } }`, PascalCase factory names.

## Вариант 4 — Flashpoint

**Идея:** сила приходит короткими всплесками (килл, низкое HP, плент, активка), вне окна — ощутимый дебафф.

| Параметр | Flashpoint vs Competitive |
|----------|---------------------------|
| `active_frames` | 32 (было 64) |
| `cooldown_frames` | 2240–2880 (было 2560–3200) |
| `velocity_modifier` buff | до 1.18–1.25 |
| `damage_scale` debuff | 1.15–1.22 |
| Импланты per-player | **другой набор** (не те же 16) |

### Loadouts по Steam ID (flashpoint)

| Steam ID | Роль | Стиль |
|----------|------|-------|
| `76561199530013153` | boss | Берсерк: килл-щит, спринт после фрага, dash |
| `76561198836236005` | boss | Контроль: краткий инвулн, пост-плент флеш-иммун, гранатный xray |
| `76561198290940309` | mercenary | Саппорт: реген в дыму, хил на дефьюзе, HP при смерти тиммейта |
| `76561198728722755` | mercenary | Энтри: tap damage, скорость, клатч на низком HP |
| `76561198184450067` | mercenary | Пост-плент: урон после плэнта, тихий plant, фейк-шаги |
| `76561198302751753` | mercenary | Снайпер: анти-отдача, защита тела, пистолетный урон |

## Единицы

- `*_frames` — тики сервера (64 tick → 64f ≈ 1 с)
- `velocity_modifier` — множитель скорости (1.0 = база)
- `damage_scale` — множитель урона (>1 = больше получаешь/наносишь)
- `damage_mask` — битовая маска (8 = огонь, 64 = взрыв)
