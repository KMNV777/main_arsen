#!/usr/bin/env python3
"""Generate F2F Dominion grants JSON: { SteamID: [ { factory, buff, debuff }, ... ] }."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

# Исходные значения из эталонного конфига (КФГ для Арсена)
G = {
    "accuracy_zone_v1": {
        "factory": "accuracy_zone_v1",
        "buff": {
            "name": "accuracy_zone_v1_trigger",
            "health_threshold": 15,
            "velocity_modifier": 1.08,
        },
        "debuff": {
            "name": "reload_primary_attack_penalty",
            "penalty_scale": 1.05,
        },
    },
    "anti_kinetic_v1": {
        "factory": "anti_kinetic_v1",
        "buff": {
            "name": "bomb_plant_body_damage",
            "damage_scale": 1.05,
        },
        "debuff": {
            "name": "anti_kinetic_v1_he_vulnerability",
            "damage_scale": 1.08,
            "apply_for_attacker": False,
            "apply_for_victim": True,
            "damage_mask": 64,
            "body_only": False,
            "leg_only": False,
        },
    },
    "bio_patch_hp_v1": {
        "factory": "bio_patch_hp_v1",
        "buff": {"name": "knife_move_armor", "armor_bonus": 10},
        "debuff": {
            "name": "bio_patch_hp_v1_fire_vulnerability",
            "damage_scale": 1.08,
            "apply_for_attacker": False,
            "apply_for_victim": True,
            "damage_mask": 8,
            "body_only": False,
            "leg_only": False,
        },
    },
    "bio_regeneration_mirror": {
        "factory": "bio_regeneration",
        "buff": {
            "name": "bullet_mirror_active",
            "active_frames": 32,
            "cooldown_frames": 3200,
        },
        "debuff": {
            "name": "reload_click_sound",
            "sound_name": "Buttons.snd15",
        },
    },
    "bio_regeneration_knife_speed": {
        "factory": "bio_regeneration",
        "buff": {
            "name": "bio_regeneration_knife_speed_bonus",
            "velocity_modifier": 1.02,
        },
        "debuff": {"name": "primary_clip_cap", "max_clip_scale": 0.95},
    },
    "accuracy_zone_v1_merc": {
        "factory": "accuracy_zone_v1",
        "buff": {
            "name": "accuracy_zone_v1_trigger",
            "health_threshold": 15,
            "velocity_modifier": 1.08,
        },
        "debuff": {"name": "no_jump_after_damage", "lock_frames": 16},
    },
    "chrome_armor_boss1": {
        "factory": "chrome_armor",
        "buff": {
            "name": "chrome_armor_buff",
            "max_health_delta": 25,
            "immediate_health_delta": 25,
            "ability_name": "armor_pulse_active",
            "armor_value": 60,
        },
        "debuff": {
            "name": "chrome_armor_debuff",
            "velocity_modifier": 1.08,
        },
    },
    "chrome_armor_boss2": {
        "factory": "chrome_armor",
        "buff": {
            "name": "chrome_armor_buff",
            "max_health_delta": 25,
            "immediate_health_delta": 25,
            "ability_name": "armor_pulse_active",
            "armor_value": 60,
        },
        "debuff": {
            "name": "chrome_armor_debuff",
            "velocity_modifier": 0.92,
        },
    },
    "chrome_repair_v2": {
        "factory": "chrome_repair_v2",
        "buff": {"name": "ability_cooldown_reset", "cooldown_frames": 4480},
        "debuff": {
            "name": "weapon_fire_lock",
            "lock_frames": 1,
            "locked_velocity_modifier": 0.5,
        },
    },
    "chromo_armor_tank_extinguish": {
        "factory": "chromo_armor_tank",
        "buff": {"name": "extinguish_effect_ability", "cooldown_frames": 1920},
        "debuff": {
            "name": "ventilation_implant_weapon_block",
            "blocked_definition_a": 2,
            "blocked_definition_b": 64,
        },
    },
    "credit_reader_v1_merc1": {
        "factory": "credit_reader_v1",
        "buff": {"name": "teammate_death_max_health", "max_health_delta": 15},
        "debuff": {"name": "reload_primary_attack_penalty", "penalty_scale": 1.05},
    },
    "cyber_limb_accuracy": {
        "factory": "cyber_limb_accuracy",
        "buff": {"name": "ladder_climb_velocity", "velocity_modifier": 1.5},
        "debuff": {"name": "global_water_step_sound", "sound_name": "Player.Wade"},
    },
    "data_hack_flash": {
        "factory": "data_hack_slowdown",
        "buff": {"name": "flash_immunity_after_bomb_plant"},
        "debuff": {
            "name": "ventilation_implant_weapon_block",
            "blocked_definition_a": 2,
            "blocked_definition_b": 64,
        },
    },
    "fast_network_v2": {
        "factory": "fast_network_v2",
        "buff": {"name": "silent_steps_low_health", "health_threshold": 20},
        "debuff": {
            "name": "radar_flicker",
            "toggle_frames": 32,
            "start_hidden": False,
        },
    },
    "ghost_jacket_gray": {
        "factory": "ghost_jacket_gray",
        "buff": {"name": "heal_amplify", "bonus_scale": 0.25},
        "debuff": {"name": "backpedal_velocity_penalty", "velocity_modifier": 0.96},
    },
    "mini_radar_v1": {
        "factory": "mini_radar_v1",
        "buff": {"name": "mini_radar_v1_round_win_income"},
        "debuff": {"name": "reload_click_sound", "sound_name": "Buttons.snd15"},
    },
    "singular_regen": {
        "factory": "singular_regen",
        "buff": {"name": "singular_regen_active"},
        "debuff": {
            "name": "singular_regen_debuff",
            "max_health_delta": -5,
            "immediate_health_delta": 0,
        },
    },
    "sonar_v2": {
        "factory": "sonar_v2",
        "buff": {"name": "defuse_signal", "sound_name": "Geiger.BeepHigh"},
        "debuff": {
            "name": "long_range_damage_penalty",
            "distance_range_scale": 0.7,
            "damage_scale": 0.95,
        },
    },
    "ventilation_implant": {
        "factory": "ventilation_implant",
        "buff": {
            "name": "ventilation_implant_leg_resist",
            "damage_scale": 0.85,
            "apply_for_attacker": False,
            "apply_for_victim": True,
            "damage_mask": 0,
            "body_only": False,
            "leg_only": True,
        },
        "debuff": {
            "name": "ventilation_implant_weapon_block",
            "blocked_definition_a": 2,
            "blocked_definition_b": 64,
        },
    },
}

ROLE_GRANTS: dict[str, list[str]] = {
    "boss_1": [
        "bio_regeneration_mirror",
        "chrome_armor_boss1",
        "chrome_repair_v2",
        "chromo_armor_tank_extinguish",
        "ventilation_implant",
    ],
    "boss_2": [
        "singular_regen",
        "chrome_armor_boss2",
        "data_hack_flash",
    ],
    "mercenary_1": [
        "credit_reader_v1_merc1",
        "ghost_jacket_gray",
    ],
    "mercenary_2": ["accuracy_zone_v1_merc"],
    "mercenary_3": ["accuracy_zone_v1_merc"],
    "mercenary_4": [
        "bio_patch_hp_v1",
        "bio_regeneration_knife_speed",
        "fast_network_v2",
    ],
    "mercenary_5": [
        "bio_patch_hp_v1",
        "bio_regeneration_knife_speed",
        "fast_network_v2",
        "mini_radar_v1",
    ],
    "shared_global": [
        "cyber_limb_accuracy",
        "sonar_v2",
        "anti_kinetic_v1",
    ],
}


def grant(key: str) -> dict[str, Any]:
    return copy.deepcopy(G[key])


def build_grants(role_id: str) -> list[dict[str, Any]]:
    return [grant(key) for key in ROLE_GRANTS[role_id]]


def dominion_role(role_id: str) -> str:
    return "boss" if role_id.startswith("boss") else "mercenary"


def build_export(steam_id: str, role_id: str) -> dict[str, Any]:
    return {
        steam_id: {
            "role": dominion_role(role_id),
            "factories": build_grants(role_id),
        }
    }


def load_steam_ids(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    out = Path(__file__).parent
    steam_ids = load_steam_ids(out / "steam_ids.json")

    combined: dict[str, Any] = {}
    for role_id, keys in ROLE_GRANTS.items():
        sid = steam_ids[role_id]
        payload = build_export(sid, role_id)
        path = out / f"{role_id}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        combined.update(payload)
        print("wrote", path.name, "->", sid, f"({len(keys)} grants)")

    combined_path = out / "КФГ для Арсена.json"
    combined_path.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("wrote", combined_path.name, f"({len(combined)} players)")


if __name__ == "__main__":
    main()
