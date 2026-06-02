# Исходные dominion JSON

Скопируйте сюда 7 файлов с диска `D:\`:

- `Igor_boss_dominion.json`
- `Aider_boss2.json`
- `roman_marketing_dominion.json`
- `Ilya_dominion.json`
- `fortuna_dominion.json`
- `Valera_dominion.json`
- `arsen_dominion.json`

Затем из каталога `f2f_role_balance`:

```bash
python3 merge_dominion_grants.py
```

Итог: `dominion_grants_combined.json` — все SteamID в одном объекте.

Для **76561198045497938** (Игорь) и **76561198836236006** (Айдер) скрипт выставляет `"role": "boss"`; для остальных — `"mercenary"`.

Формат игрока:

```json
{
  "76561198045497938": {
    "role": "boss",
    "factories": [ { "factory": "...", "buff": { ... }, "debuff": { ... } } ]
  }
}
```

Указать другой каталог (например, WSL `D:`):

```bash
python3 merge_dominion_grants.py --input-dir /mnt/d
```
