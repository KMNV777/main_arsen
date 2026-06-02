# F2F — балансные конфиги по ролям

Формат импорта — **как в `dominion_grants.json`**:

```json
{
  "76561198836236006": {
    "role": "boss",
    "factories": [
      {
        "factory": "accuracy_zone_v1",
        "buff": { "name": "...", ... },
        "debuff": { "name": "...", ... }
      }
    ]
  },
  "76561198836236007": {
    "role": "mercenary",
    "factories": [ ... ]
  }
}
```

**Боссы** (role `boss`): `76561198836236006`, `76561198045497938`. Остальные SteamID — `mercenary`.

Числовые значения взяты из эталонного конфига (ваш пример с `76561198184450067`).

## Steam ID

Соответствие роль → SteamID в `steam_ids.json`. Босс 1 использует ваш ID `76561198184450067`; остальные — заглушки, замените на реальные перед импортом.

## Файлы

| Файл | SteamID (по умолчанию) | Grants |
|------|------------------------|--------|
| `boss_1.json` | 76561198045497938 | 5 |
| `boss_2.json` | 76561198836236006 | 3 |
| `mercenary_1.json` | 76561198836236007 | 2 |
| `mercenary_2.json` | 76561198836236008 | 1 |
| `mercenary_3.json` | 76561198836236009 | 1 |
| `mercenary_4.json` | 76561198836236010 | 3 |
| `mercenary_5.json` | 76561198836236011 | 4 |
| `shared_global.json` | 76561198836236012 | 3 |
| `КФГ для Арсена.json` | все 8 игроков в одном файле | — |

Пересборка: `python3 generate_role_balance.py`

## Объединение 7 файлов с D:\

Скопируйте в `sources/` файлы: `Igor_boss_dominion.json`, `Aider_boss2.json`, `roman_marketing_dominion.json`, `Ilya_dominion.json`, `fortuna_dominion.json`, `Valera_dominion.json`, `arsen_dominion.json`.

```bash
python3 merge_dominion_grants.py
# или: python3 merge_dominion_grants.py --input-dir /mnt/d
```

Результат: **`dominion_grants_combined.json`** — один объект `{ "SteamID": [ ...grants ] }` для импорта.

## Распределение по ролям

См. предыдущую таблицу в PR — эффекты из 16 фабрик эталона разнесены по боссам 1–2 и наёмникам 1–5; общие (лестница, дефьюз, plant damage, вода) — в `shared_global.json`.
