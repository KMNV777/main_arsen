#!/usr/bin/env python3
"""Generate F2F Dominion grants JSON: { SteamID: [ { factory, buff, debuff }, ... ] }."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

# Профиль «ощутимый» — заметные баффы/дебаффы в матче (было ~±5–25, стало ~±15–40)
T = {
    "hp_boss": 40,
    "hp_teammate_death": 35,
    "hp_singular_penalty": -15,
    "armor_pulse": 100,
    "knife_armor": 25,
    "velocity_boss_buff": 1.2,
    "velocity_boss_debuff": 0.78,
    "velocity_low_hp": 1.18,
    "velocity_knife": 1.12,
    "velocity_backpedal": 0.82,
    "velocity_ladder": 2.0,
    "health_threshold_low_hp": 35,
    "health_threshold_silent": 40,
    "damage_plant_body": 1.2,
    "damage_vulnerability": 1.22,
    "damage_leg_resist": 0.6,
    "damage_long_range": 0.88,
    "reload_penalty": 1.18,
    "aim_punch": 1.15,
    "clip_cap_scale": 0.75,
    "heal_amplify": 0.5,
    "mirror_active_frames": 48,
    "mirror_cooldown_frames": 2560,
    "weapon_lock_frames": 3,
    "weapon_locked_velocity": 0.0,
    "no_jump_frames": 48,
    "extinguish_cooldown": 1280,
    "radar_toggle_frames": 12,
    "long_range_distance_scale": 0.55,
}

G = {
    "accuracy_zone_v1": {
        "factory": "accuracy_zone_v1",
        "buff": {
            "name": "accuracy_zone_v1_trigger",
            "health_threshold": T["health_threshold_low_hp"],
            "velocity_modifier": T["velocity_low_hp"],
        },
        "debuff": {
            "name": "reload_primary_attack_penalty",
            "penalty_scale": T["reload_penalty"],
        },
    },
    "anti_kinetic_v1": {
        "factory": "anti_kinetic_v1",
        "buff": {
            "name": "bomb_plant_body_damage",
            "damage_scale": T["damage_plant_body"],
        },
        "debuff": {
            "name": "anti_kinetic_v1_he_vulnerability",
            "damage_scale": T["damage_vulnerability"],
            "apply_for_attacker": False,
            "apply_for_victim": True,
            "damage_mask": 64,
            "body_only": False,
            "leg_only": False,
        },
    },
    "bio_patch_hp_v1": {
        "factory": "bio_patch_hp_v1",
        "buff": {"name": "knife_move_armor", "armor_bonus": T["knife_armor"]},
        "debuff": {
            "name": "bio_patch_hp_v1_fire_vulnerability",
            "damage_scale": T["damage_vulnerability"],
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
            "active_frames": T["mirror_active_frames"],
            "cooldown_frames": T["mirror_cooldown_frames"],
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
            "velocity_modifier": T["velocity_knife"],
        },
        "debuff": {"name": "primary_clip_cap", "max_clip_scale": T["clip_cap_scale"]},
    },
    "accuracy_zone_v1_merc": {
        "factory": "accuracy_zone_v1",
        "buff": {
            "name": "accuracy_zone_v1_trigger",
            "health_threshold": T["health_threshold_low_hp"],
            "velocity_modifier": T["velocity_low_hp"],
        },
        "debuff": {"name": "no_jump_after_damage", "lock_frames": T["no_jump_frames"]},
    },
    "chrome_armor_boss1": {
        "factory": "chrome_armor",
        "buff": {
            "name": "chrome_armor_buff",
            "max_health_delta": T["hp_boss"],
            "immediate_health_delta": T["hp_boss"],
            "ability_name": "armor_pulse_active",
            "armor_value": T["armor_pulse"],
        },
        "debuff": {
            "name": "chrome_armor_debuff",
            "velocity_modifier": T["velocity_boss_buff"],
        },
    },
    "chrome_armor_boss2": {
        "factory": "chrome_armor",
        "buff": {
            "name": "chrome_armor_buff",
            "max_health_delta": T["hp_boss"],
            "immediate_health_delta": T["hp_boss"],
            "ability_name": "armor_pulse_active",
            "armor_value": T["armor_pulse"],
        },
        "debuff": {
            "name": "chrome_armor_debuff",
            "velocity_modifier": T["velocity_boss_debuff"],
        },
    },
    "chrome_repair_v2": {
        "factory": "chrome_repair_v2",
        "buff": {"name": "ability_cooldown_reset", "cooldown_frames": 4480},
        "debuff": {
            "name": "weapon_fire_lock",
            "lock_frames": T["weapon_lock_frames"],
            "locked_velocity_modifier": T["weapon_locked_velocity"],
        },
    },
    "chromo_armor_tank_extinguish": {
        "factory": "chromo_armor_tank",
        "buff": {"name": "extinguish_effect_ability", "cooldown_frames": T["extinguish_cooldown"]},
        "debuff": {
            "name": "ventilation_implant_weapon_block",
            "blocked_definition_a": 2,
            "blocked_definition_b": 64,
        },
    },
    "credit_reader_v1_merc1": {
        "factory": "credit_reader_v1",
        "buff": {"name": "teammate_death_max_health", "max_health_delta": T["hp_teammate_death"]},
        "debuff": {"name": "reload_primary_attack_penalty", "penalty_scale": T["reload_penalty"]},
    },
    "cyber_limb_accuracy": {
        "factory": "cyber_limb_accuracy",
        "buff": {"name": "ladder_climb_velocity", "velocity_modifier": T["velocity_ladder"]},
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
        "buff": {"name": "silent_steps_low_health", "health_threshold": T["health_threshold_silent"]},
        "debuff": {
            "name": "radar_flicker",
            "toggle_frames": T["radar_toggle_frames"],
            "start_hidden": False,
        },
    },
    "ghost_jacket_gray": {
        "factory": "ghost_jacket_gray",
        "buff": {"name": "heal_amplify", "bonus_scale": T["heal_amplify"]},
        "debuff": {"name": "backpedal_velocity_penalty", "velocity_modifier": T["velocity_backpedal"]},
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
            "max_health_delta": T["hp_singular_penalty"],
            "immediate_health_delta": 0,
        },
    },
    "sonar_v2": {
        "factory": "sonar_v2",
        "buff": {"name": "defuse_signal", "sound_name": "Geiger.BeepHigh"},
        "debuff": {
            "name": "long_range_damage_penalty",
            "distance_range_scale": T["long_range_distance_scale"],
            "damage_scale": T["damage_long_range"],
        },
    },
    "ventilation_implant": {
        "factory": "ventilation_implant",
        "buff": {
            "name": "ventilation_implant_leg_resist",
            "damage_scale": T["damage_leg_resist"],
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


def build_export(steam_id: str, role_id: str) -> dict[str, Any]:
    return {steam_id: build_grants(role_id)}


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
