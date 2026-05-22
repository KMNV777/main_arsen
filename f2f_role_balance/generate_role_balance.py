#!/usr/bin/env python3
"""Generate F2F Dominion role balance JSON files from distribution spec."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Baseline tuned values (from dominion_balance variant_3_competitive)
BASE = {
    "bullet_mirror_active_frames": 64,
    "bullet_mirror_cooldown_frames": 2560,
    "chrome_max_hp": 40,
    "chrome_immediate_hp": 40,
    "boss_velocity_buff": 1.15,
    "boss_velocity_debuff": 0.88,
    "singular_max_hp_debuff": -10,
    "knife_armor_bonus": 20,
    "knife_speed_bonus": 1.08,
    "low_hp_speed_threshold": 20,
    "low_hp_speed_modifier": 1.15,
    "silent_steps_threshold": 30,
    "clip_cap_scale": 0.9,
    "reload_penalty_scale": 1.12,
    "teammate_death_hp": 25,
    "backpedal_velocity": 0.92,
    "no_jump_lock_frames": 32,
    "weapon_fire_lock_frames": 2,
    "weapon_fire_locked_velocity": 0.25,
    "extinguish_cooldown_frames": 1280,
    "reload_click_sound": "Buttons.snd15",
    "defuse_sound": "Geiger.BeepHigh",
    "water_step_sound": "Player.Wade",
    "ladder_velocity": 1.8,
    "aim_punch_scale": 1.1,
    "plant_body_damage_scale": 1.1,
    "radar_toggle_frames": 24,
}


def meta(role_id: str, display_name: str, description: str) -> dict[str, Any]:
    return {
        "role": role_id,
        "displayName": display_name,
        "description": description,
        "source": "КФГ для Арсена.json (redistributed by role)",
        "balanceProfile": "competitive_tuned",
        "tickRate": 64,
    }


def grant(factory: str, buff: dict[str, Any], debuff: dict[str, Any]) -> dict[str, Any]:
    return {"factory": factory, "buff": buff, "debuff": debuff}


ROLE_CONFIGS: dict[str, dict[str, Any]] = {
    "boss_1": {
        "displayName": "Босс 1",
        "description": "Bullet Mirror, HP+, скорость+, блок стрельбы/оружия, тушение molotov, громкая перезарядка.",
        "grants": [
            grant(
                "bio_regeneration",
                {
                    "name": "bullet_mirror_active",
                    "active_frames": BASE["bullet_mirror_active_frames"],
                    "cooldown_frames": BASE["bullet_mirror_cooldown_frames"],
                },
                {
                    "name": "reload_click_sound",
                    "sound_name": BASE["reload_click_sound"],
                },
            ),
            grant(
                "chrome_armor",
                {
                    "name": "chrome_armor_buff",
                    "max_health_delta": BASE["chrome_max_hp"],
                    "immediate_health_delta": BASE["chrome_immediate_hp"],
                },
                {
                    "name": "chrome_armor_velocity_buff",
                    "velocity_modifier": BASE["boss_velocity_buff"],
                },
            ),
            grant(
                "chrome_repair_v2",
                {
                    "name": "extinguish_effect_ability",
                    "cooldown_frames": BASE["extinguish_cooldown_frames"],
                },
                {
                    "name": "weapon_fire_lock",
                    "lock_frames": BASE["weapon_fire_lock_frames"],
                    "locked_velocity_modifier": BASE["weapon_fire_locked_velocity"],
                },
            ),
            grant(
                "ventilation_implant",
                {
                    "name": "ventilation_implant_leg_resist",
                    "damage_scale": 0.75,
                    "apply_for_attacker": False,
                    "apply_for_victim": True,
                    "damage_mask": 0,
                    "body_only": False,
                    "leg_only": True,
                },
                {
                    "name": "ventilation_implant_weapon_block",
                    "blocked_definition_a": 2,
                    "blocked_definition_b": 64,
                },
            ),
        ],
    },
    "boss_2": {
        "displayName": "Босс 2",
        "description": "Singular Regen, HP+, замедление, блок оружия, иммунитет к flash после plant.",
        "grants": [
            grant(
                "singular_regen",
                {"name": "singular_regen_active"},
                {
                    "name": "singular_regen_debuff",
                    "max_health_delta": BASE["singular_max_hp_debuff"],
                    "immediate_health_delta": 0,
                },
            ),
            grant(
                "chrome_armor",
                {
                    "name": "chrome_armor_buff",
                    "max_health_delta": BASE["chrome_max_hp"],
                    "immediate_health_delta": BASE["chrome_immediate_hp"],
                },
                {
                    "name": "chrome_armor_debuff",
                    "velocity_modifier": BASE["boss_velocity_debuff"],
                },
            ),
            grant(
                "data_hack_slowdown",
                {"name": "flash_immunity_after_bomb_plant"},
                {
                    "name": "ventilation_implant_weapon_block",
                    "blocked_definition_a": 2,
                    "blocked_definition_b": 64,
                },
            ),
        ],
    },
    "mercenary_1": {
        "displayName": "Наёмник 1",
        "description": "HP после смерти союзника, штраф перезарядки, замедление при движении назад.",
        "grants": [
            grant(
                "credit_reader_v1",
                {
                    "name": "teammate_death_max_health",
                    "max_health_delta": BASE["teammate_death_hp"],
                },
                {
                    "name": "reload_primary_attack_penalty",
                    "penalty_scale": BASE["reload_penalty_scale"],
                },
            ),
            grant(
                "ghost_jacket_gray",
                {
                    "name": "heal_amplify",
                    "bonus_scale": 0.4,
                },
                {
                    "name": "backpedal_velocity_penalty",
                    "velocity_modifier": BASE["backpedal_velocity"],
                },
            ),
        ],
    },
    "mercenary_2": {
        "displayName": "Наёмник 2",
        "description": "Скорость при low HP, запрет прыжка после урона.",
        "grants": [
            grant(
                "accuracy_zone_v1",
                {
                    "name": "accuracy_zone_v1_trigger",
                    "health_threshold": BASE["low_hp_speed_threshold"],
                    "velocity_modifier": BASE["low_hp_speed_modifier"],
                },
                {
                    "name": "no_jump_after_damage",
                    "lock_frames": BASE["no_jump_lock_frames"],
                },
            ),
        ],
    },
    "mercenary_3": {
        "displayName": "Наёмник 3",
        "description": "Скорость при low HP, запрет прыжка после урона.",
        "grants": [
            grant(
                "accuracy_zone_v1",
                {
                    "name": "accuracy_zone_v1_trigger",
                    "health_threshold": BASE["low_hp_speed_threshold"],
                    "velocity_modifier": BASE["low_hp_speed_modifier"],
                },
                {
                    "name": "no_jump_after_damage",
                    "lock_frames": BASE["no_jump_lock_frames"],
                },
            ),
        ],
    },
    "mercenary_4": {
        "displayName": "Наёмник 4",
        "description": "Броня с ножом, скорость с ножом, тихие шаги, мерцание радара, уменьшенный магазин.",
        "grants": [
            grant(
                "bio_patch_hp_v1",
                {
                    "name": "knife_move_armor",
                    "armor_bonus": BASE["knife_armor_bonus"],
                },
                {
                    "name": "bio_patch_hp_v1_fire_vulnerability",
                    "damage_scale": 1.12,
                    "apply_for_attacker": False,
                    "apply_for_victim": True,
                    "damage_mask": 8,
                    "body_only": False,
                    "leg_only": False,
                },
            ),
            grant(
                "bio_regeneration",
                {
                    "name": "bio_regeneration_knife_speed_bonus",
                    "velocity_modifier": BASE["knife_speed_bonus"],
                },
                {
                    "name": "primary_clip_cap",
                    "max_clip_scale": BASE["clip_cap_scale"],
                },
            ),
            grant(
                "fast_network_v2",
                {
                    "name": "silent_steps_low_health",
                    "health_threshold": BASE["silent_steps_threshold"],
                },
                {
                    "name": "radar_flicker",
                    "toggle_frames": BASE["radar_toggle_frames"],
                    "start_hidden": False,
                },
            ),
        ],
    },
    "mercenary_5": {
        "displayName": "Наёмник 5",
        "description": "Как наёмник 4 + громкий щелчок при перезарядке.",
        "grants": [
            grant(
                "bio_patch_hp_v1",
                {
                    "name": "knife_move_armor",
                    "armor_bonus": BASE["knife_armor_bonus"],
                },
                {
                    "name": "bio_patch_hp_v1_fire_vulnerability",
                    "damage_scale": 1.12,
                    "apply_for_attacker": False,
                    "apply_for_victim": True,
                    "damage_mask": 8,
                    "body_only": False,
                    "leg_only": False,
                },
            ),
            grant(
                "bio_regeneration",
                {
                    "name": "bio_regeneration_knife_speed_bonus",
                    "velocity_modifier": BASE["knife_speed_bonus"],
                },
                {
                    "name": "primary_clip_cap",
                    "max_clip_scale": BASE["clip_cap_scale"],
                },
            ),
            grant(
                "fast_network_v2",
                {
                    "name": "silent_steps_low_health",
                    "health_threshold": BASE["silent_steps_threshold"],
                },
                {
                    "name": "radar_flicker",
                    "toggle_frames": BASE["radar_toggle_frames"],
                    "start_hidden": False,
                },
            ),
            grant(
                "mini_radar_v1",
                {
                    "name": "mini_radar_v1_round_win_income",
                },
                {
                    "name": "reload_click_sound",
                    "sound_name": BASE["reload_click_sound"],
                },
            ),
        ],
    },
    "shared_global": {
        "displayName": "Общие (без привязки к роли)",
        "description": "Эффекты из ТЗ без явной роли: лестница, дефьюз, вода, aim punch, урон после plant.",
        "grants": [
            grant(
                "cyber_limb_accuracy",
                {
                    "name": "ladder_climb_velocity",
                    "velocity_modifier": BASE["ladder_velocity"],
                },
                {
                    "name": "global_water_step_sound",
                    "sound_name": BASE["water_step_sound"],
                },
            ),
            grant(
                "sonar_v2",
                {
                    "name": "defuse_signal",
                    "sound_name": BASE["defuse_sound"],
                },
                {
                    "name": "long_range_damage_penalty",
                    "distance_range_scale": 0.55,
                    "damage_scale": 0.92,
                },
            ),
            grant(
                "anti_kinetic_v1",
                {
                    "name": "bomb_plant_body_damage",
                    "damage_scale": BASE["plant_body_damage_scale"],
                },
                {
                    "name": "anti_kinetic_v1_he_vulnerability",
                    "damage_scale": 1.12,
                    "apply_for_attacker": False,
                    "apply_for_victim": True,
                    "damage_mask": 64,
                    "body_only": False,
                    "leg_only": False,
                },
            ),
            grant(
                "ghost_jacket_gray",
                {
                    "name": "heal_amplify",
                    "bonus_scale": 0.1,
                },
                {
                    "name": "aim_punch_scale",
                    "scale": BASE["aim_punch_scale"],
                },
            ),
        ],
    },
}


def build_role_file(role_id: str) -> dict[str, Any]:
    cfg = ROLE_CONFIGS[role_id]
    return {
        "_meta": meta(role_id, cfg["displayName"], cfg["description"]),
        "grants": cfg["grants"],
    }


def build_combined() -> dict[str, Any]:
    return {
        "_meta": {
            "name": "КФГ для Арсена — распределение по ролям",
            "format": "f2f_dominion_grants_by_role",
            "roles": list(ROLE_CONFIGS.keys()),
            "note": "Импорт: назначьте grants из каждой секции role на соответствующего игрока/бота.",
        },
        "roles": {role_id: build_role_file(role_id) for role_id in ROLE_CONFIGS},
    }


def main() -> None:
    out = Path(__file__).parent
    for role_id in ROLE_CONFIGS:
        path = out / f"{role_id}.json"
        payload = build_role_file(role_id)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("wrote", path.name)

    combined_path = out / "КФГ для Арсена.json"
    combined_path.write_text(
        json.dumps(build_combined(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("wrote", combined_path.name)


if __name__ == "__main__":
    main()
