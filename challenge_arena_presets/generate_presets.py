#!/usr/bin/env python3
"""Generate F2F Challenge Arena preset JSON files (export format: common + red + blue)."""

import copy
import json
from pathlib import Path

PISTOLS = [
    "WEAPON_DEAGLE",
    "WEAPON_ELITE",
    "WEAPON_FIVESEVEN",
    "WEAPON_GLOCK",
    "WEAPON_HKP2000",
    "WEAPON_P250",
    "WEAPON_TEC9",
    "WEAPON_CZ75A",
    "WEAPON_REVOLVER",
    "WEAPON_USP_SILENCER",
]
SMG = [
    "WEAPON_MAC10",
    "WEAPON_P90",
    "WEAPON_MP5SD",
    "WEAPON_UMP45",
    "WEAPON_BIZON",
    "WEAPON_MP7",
    "WEAPON_MP9",
]
RIFLES_SNIPERS = [
    "WEAPON_AK47",
    "WEAPON_AUG",
    "WEAPON_AWP",
    "WEAPON_FAMAS",
    "WEAPON_G3SG1",
    "WEAPON_GALILAR",
    "WEAPON_M4A1",
    "WEAPON_M4A1_SILENCER",
    "WEAPON_SCAR20",
    "WEAPON_SG556",
    "WEAPON_SSG08",
]
HEAVY = ["WEAPON_M249", "WEAPON_NEGEV"]
SHOTGUNS = ["WEAPON_XM1014", "WEAPON_MAG7", "WEAPON_NOVA", "WEAPON_SAWEDOFF"]
ALL_GUNS = PISTOLS + SMG + RIFLES_SNIPERS + HEAVY + SHOTGUNS


def team_base():
    return {
        "weaponExcluded": [],
        "defuseKit": "KIT_MODE_DEFAULT",
        "winCondition": {"classic": {"enabled": True}},
        "visuals": {"wallhack": False, "invisiblePlayers": False},
        "physics": {
            "bhop": False,
            "modelSize": {"value": 1, "enabled": False},
            "speedCharacter": {"value": 1, "enabled": False},
            "gravityModifier": {"value": 1, "enabled": False},
        },
        "player": {
            "hitboxes": {"headOnly": False},
            "armor": {
                "availableFromTheStart": False,
                "type": "ARMOR_TYPE_NONE",
            },
            "health": {
                "hpValue": 100,
                "missDamage": {"missHpPercent": 0, "missDamage": False},
            },
        },
        "weapons": {
            "zoom": {"enabled": True},
            "bullets": {"infinityBulletWithReload": False},
            "grenades": {
                "damageModifier": 1,
                "radiusModifier": 1,
                "infinite": {
                    "he": False,
                    "flash": False,
                    "smoke": False,
                    "decoy": False,
                    "molotov": False,
                },
            },
        },
    }


def common_base(
    *,
    round_count,
    round_time,
    warmup=300,
    require_all=True,
    overtime=False,
    start_money=800,
    max_money=16000,
):
    return {
        "warmupTimer": warmup,
        "requireAllParticipants": require_all,
        "tracking": "TRACKING_MODE_POST_GAME",
        "mode": {"classicDefuse": {"enabled": True}},
        "economy": {
            "startMoney": start_money,
            "maxMoney": max_money,
            "overtimeMoney": 12500,
        },
        "rounds": {
            "roundCount": round_count,
            "roundTimeSeconds": round_time,
            "overtime": {
                "enabled": overtime,
                "maxOvertimes": 1,
                "roundsPerOvertime": 6,
            },
        },
    }


def win_condition(consecutive_wins=None):
    wc = {"classic": {"enabled": True}}
    if consecutive_wins:
        wc["consecutive"] = {"winsNeeded": consecutive_wins}
    return wc


def minority(red, **kwargs):
    t = team_base()
    deep_update(t, red)
    deep_update(t, kwargs)
    return t


def majority(blue, **kwargs):
    t = team_base()
    deep_update(t, blue)
    deep_update(t, kwargs)
    return t


def deep_update(base, patch):
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_update(base[k], v)
        else:
            base[k] = v


def exclude_all_except(*keep):
    keep_set = set(keep)
    return [w for w in ALL_GUNS if w not in keep_set]


def preset(name, format_label, common, red, blue, *, consecutive_wins=None):
    c = copy.deepcopy(common)
    if consecutive_wins:
        red = copy.deepcopy(red)
        blue = copy.deepcopy(blue)
        red["winCondition"] = win_condition(consecutive_wins)
        blue["winCondition"] = win_condition(consecutive_wins)
    return {
        "_preset": {
            "name": name,
            "format": format_label,
            "minoritySide": "red",
            "majoritySide": "blue",
            "importHint": "F2F Challenge Arena → Импорт настроек. red = меньшинство, blue = большинство.",
        },
        "common": c,
        "red": red,
        "blue": blue,
    }


PRESETS = [
    preset(
        "1 vs 5 — Опытный против пятёрки",
        "1v5",
        common_base(round_count=16, round_time=115, max_money=32000),
        minority(
            {
                "player": {
                    "health": {"hpValue": 200},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "modelSize": {"value": 0.9, "enabled": True},
                    "speedCharacter": {"value": 1.25, "enabled": True},
                },
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "grenades": {
                        "infinite": {"flash": True, "smoke": True}
                    }
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 100}},
                "weaponExcluded": RIFLES_SNIPERS + HEAVY + SHOTGUNS,
                "weapons": {
                    "grenades": {"infinite": {"decoy": True}}
                },
            }
        ),
        consecutive_wins=3,
    ),
    preset(
        "1 vs 10 — Спецназовец против отряда",
        "1v10",
        common_base(round_count=12, round_time=130, max_money=64000),
        minority(
            {
                "player": {
                    "health": {"hpValue": 400},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "modelSize": {"value": 0.85, "enabled": True},
                    "speedCharacter": {"value": 1.35, "enabled": True},
                },
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "bullets": {"infinityBulletWithReload": True},
                    "grenades": {
                        "infinite": {"flash": True, "smoke": True, "he": True}
                    },
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 80}},
                "weaponExcluded": exclude_all_except(*PISTOLS, "WEAPON_KNIFE"),
            }
        ),
        consecutive_wins=2,
    ),
    preset(
        "1 vs 20 — Action-герой",
        "1v20",
        common_base(
            round_count=10,
            round_time=150,
            start_money=200,
            max_money=99999,
        ),
        minority(
            {
                "player": {
                    "health": {"hpValue": 700},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "bhop": True,
                    "modelSize": {"value": 0.8, "enabled": True},
                    "speedCharacter": {"value": 1.45, "enabled": True},
                    "gravityModifier": {"value": 0.9, "enabled": True},
                },
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "bullets": {"infinityBulletWithReload": True},
                    "grenades": {
                        "radiusModifier": 1.5,
                        "infinite": {"flash": True, "smoke": True, "he": True},
                    },
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 60}},
                "weaponExcluded": exclude_all_except("WEAPON_GLOCK", "WEAPON_KNIFE"),
            }
        ),
        consecutive_wins=2,
    ),
    preset(
        "1 vs 30 — Boss mode",
        "1v30",
        common_base(
            round_count=8,
            round_time=180,
            start_money=100,
            max_money=99999,
        ),
        minority(
            {
                "player": {
                    "health": {"hpValue": 1200},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "bhop": True,
                    "modelSize": {"value": 0.75, "enabled": True},
                    "speedCharacter": {"value": 1.5, "enabled": True},
                    "gravityModifier": {"value": 0.85, "enabled": True},
                },
                "visuals": {"wallhack": True},
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "bullets": {"infinityBulletWithReload": True},
                    "grenades": {
                        "damageModifier": 1.5,
                        "radiusModifier": 2,
                        "infinite": {
                            "he": True,
                            "flash": True,
                            "smoke": True,
                            "decoy": True,
                            "molotov": True,
                        },
                    },
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 50}},
                "weaponExcluded": exclude_all_except("WEAPON_KNIFE"),
            }
        ),
        consecutive_wins=2,
    ),
    preset(
        "2 vs 10 — Дуэт против отряда",
        "2v10",
        common_base(round_count=16, round_time=115, max_money=32000),
        minority(
            {
                "player": {
                    "health": {"hpValue": 300},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "modelSize": {"value": 0.9, "enabled": True},
                    "speedCharacter": {"value": 1.3, "enabled": True},
                },
                "weapons": {
                    "grenades": {
                        "infinite": {"flash": True, "smoke": True}
                    }
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 100}},
                "weaponExcluded": RIFLES_SNIPERS + HEAVY + SHOTGUNS,
                "weapons": {
                    "grenades": {"infinite": {"decoy": True}}
                },
            }
        ),
        consecutive_wins=3,
    ),
    preset(
        "2 vs 30 — Два героя",
        "2v30",
        common_base(
            round_count=10,
            round_time=160,
            start_money=200,
            max_money=99999,
        ),
        minority(
            {
                "player": {
                    "health": {"hpValue": 900},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "bhop": True,
                    "modelSize": {"value": 0.8, "enabled": True},
                    "speedCharacter": {"value": 1.45, "enabled": True},
                    "gravityModifier": {"value": 0.9, "enabled": True},
                },
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "bullets": {"infinityBulletWithReload": True},
                    "grenades": {
                        "radiusModifier": 1.5,
                        "infinite": {
                            "he": True,
                            "flash": True,
                            "smoke": True,
                            "decoy": True,
                            "molotov": True,
                        },
                    },
                },
            }
        ),
        majority(
            {
                "player": {"health": {"hpValue": 60}},
                "weaponExcluded": exclude_all_except("WEAPON_GLOCK", "WEAPON_KNIFE"),
                "weapons": {
                    "grenades": {
                        "infinite": {
                            "he": False,
                            "flash": False,
                            "smoke": False,
                            "decoy": False,
                            "molotov": False,
                        }
                    }
                },
            }
        ),
        consecutive_wins=2,
    ),
    preset(
        "2 vs 33 — Финальный босс ×2",
        "2v33",
        common_base(
            round_count=7,
            round_time=200,
            start_money=100,
            max_money=99999,
        ),
        minority(
            {
                "player": {
                    "health": {"hpValue": 1300},
                    "armor": {
                        "availableFromTheStart": True,
                        "type": "ARMOR_TYPE_VEST_HELMET",
                    },
                },
                "physics": {
                    "bhop": True,
                    "modelSize": {"value": 0.75, "enabled": True},
                    "speedCharacter": {"value": 1.5, "enabled": True},
                    "gravityModifier": {"value": 0.85, "enabled": True},
                },
                "visuals": {"wallhack": True},
                "defuseKit": "KIT_MODE_START_WITH",
                "weapons": {
                    "bullets": {"infinityBulletWithReload": True},
                    "grenades": {
                        "damageModifier": 2,
                        "radiusModifier": 2,
                        "infinite": {
                            "he": True,
                            "flash": True,
                            "smoke": True,
                            "decoy": True,
                            "molotov": True,
                        },
                    },
                },
            }
        ),
        majority(
            {
                "player": {
                    "health": {"hpValue": 50},
                    "hitboxes": {"headOnly": True},
                },
                "weaponExcluded": exclude_all_except("WEAPON_KNIFE"),
            }
        ),
        consecutive_wins=2,
    ),
]

FILENAMES = {
    "1v5": "ЧА - 1vs5.json",
    "1v10": "ЧА - 1vs10.json",
    "1v20": "ЧА - 1vs20.json",
    "1v30": "ЧА - 1 большой.json",
    "2v10": "ЧА - 2vs10.json",
    "2v30": "ЧА - 2vs30.json",
    "2v33": "ЧА - 2vs33.json",
}


def main():
    out_dir = Path(__file__).parent
    for p in PRESETS:
        fmt = p["_preset"]["format"]
        path = out_dir / FILENAMES[fmt]
        with path.open("w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
