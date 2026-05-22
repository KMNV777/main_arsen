# F2F — балансные конфиги по ролям

Исходный монолитный конфиг (`dominion_grants` / «КФГ для Арсена») разбит на **отдельные JSON по ролям** согласно распределению баффов и дебаффов.

Числовые значения взяты из tuned-профиля `variant_3_competitive` (ветка `cursor/dominion-balance-variants-61ec`).

## Файлы

| Файл | Роль |
|------|------|
| `boss_1.json` | Босс 1 |
| `boss_2.json` | Босс 2 |
| `mercenary_1.json` … `mercenary_5.json` | Наёмники 1–5 |
| `shared_global.json` | Эффекты без явной роли в ТЗ |
| `КФГ для Арсена.json` | Сводный файл: все роли в одном документе |

Пересобрать: `python3 generate_role_balance.py`

## Распределение эффектов

### Активные способности

| Эффект | Роль | Файл / factory |
|--------|------|----------------|
| Singular Regen | Босс 2 | `singular_regen` |
| Bullet Mirror (F, cooldown) | Босс 1 | `bio_regeneration` |

### HP / броня

| Эффект | Роль | Имя эффекта |
|--------|------|-------------|
| Изменение max HP | Босс 1, 2 | `chrome_armor_buff` |
| Изменение текущего HP | Босс 1, 2 | `immediate_health_delta` |
| Временная броня с ножом | Наёмник 4, 5 | `knife_move_armor` |
| Max HP после смерти тиммейта | Наёмник 1 | `teammate_death_max_health` |

### Скорость / мувмент

| Эффект | Роль | Имя эффекта |
|--------|------|-------------|
| Velocity modifier (−) | Босс 2 | `chrome_armor_debuff` |
| Velocity modifier (+) | Босс 1 | `chrome_armor_velocity_buff` |
| Скорость при low HP | Наёмник 2, 3 | `accuracy_zone_v1_trigger` |
| Скорость с ножом (+) | Наёмник 4, 5 | `bio_regeneration_knife_speed_bonus` |
| Скорость по лестнице | Общие | `ladder_climb_velocity` |
| Замедление назад | Наёмник 1 | `backpedal_velocity_penalty` |
| Нельзя двигаться при стрельбе | Босс 1 | `weapon_fire_lock` |
| Запрет прыжка после урона | Наёмник 2, 3 | `no_jump_after_damage` |

### Звук / stealth

| Эффект | Роль | Имя эффекта |
|--------|------|-------------|
| Тихие шаги при low HP | Наёмник 4, 5 | `silent_steps_low_health` |
| Радар мерцает | Наёмник 4, 5 | `radar_flicker` |
| Звук при дефьюзе | Общие | `defuse_signal` |
| Громкий щелчок перезарядки | Наёмник 5, Босс 1 | `reload_click_sound` |
| Шаги по воде/грязи (карта) | Общие | `global_water_step_sound` |

### Оружие / стрельба

| Эффект | Роль | Имя эффекта |
|--------|------|-------------|
| Блок подбора оружия | Босс 1, 2 | `ventilation_implant_weapon_block` |
| Штраф скорости перезарядки | Наёмник 1 | `reload_primary_attack_penalty` |
| Уменьшение магазина | Наёмник 4, 5 | `primary_clip_cap` |
| Увеличение aim punch | Общие | `aim_punch_scale` |
| Body damage после plant | Общие | `bomb_plant_body_damage` |

### Utility

| Эффект | Роль | Имя эффекта |
|--------|------|-------------|
| Иммунитет к flash после plant | Босс 2 | `flash_immunity_after_bomb_plant` |
| Тушение molotov | Босс 1 | `extinguish_effect_ability` |

## Формат одного файла роли

```jsonc
{
  "_meta": { "role": "boss_1", "displayName": "Босс 1", ... },
  "grants": [
    {
      "factory": "<id импланта>",
      "buff": { "name": "<id эффекта>", ... },
      "debuff": { "name": "<id эффекта>", ... }
    }
  ]
}
```

Для импорта в игру назначьте массив `grants` нужному SteamID / слоту бота той роли, которую он играет.
