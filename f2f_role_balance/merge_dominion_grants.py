#!/usr/bin/env python3
"""Merge per-player dominion_grants JSON files into one import file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Порядок импорта: боссы, затем наёмники (как в вашем списке на D:)
DEFAULT_SOURCE_FILES = (
    "Igor_boss_dominion.json",
    "Aider_boss2.json",
    "roman_marketing_dominion.json",
    "Ilya_dominion.json",
    "fortuna_dominion.json",
    "Valera_dominion.json",
    "arsen_dominion.json",
)

DEFAULT_OUTPUT = "dominion_grants_combined.json"

BOSS_STEAM_IDS = frozenset({"76561198836236006", "76561198045497938"})


def role_for_steam_id(steam_id: str) -> str:
    return "boss" if steam_id in BOSS_STEAM_IDS else "mercenary"


def normalize_player_entry(
    steam_id: str, entry: Any, *, path: Path | None = None
) -> dict[str, Any]:
    label = f"{path}: " if path else ""
    if isinstance(entry, list):
        factories = entry
        role = role_for_steam_id(steam_id)
    elif isinstance(entry, dict) and "factories" in entry:
        factories = entry["factories"]
        role = entry.get("role", role_for_steam_id(steam_id))
    else:
        raise ValueError(
            f"{label}{steam_id}: ожидается [ grants ] или "
            '{ "role": "...", "factories": [ ... ] }'
        )
    if role not in ("boss", "mercenary"):
        raise ValueError(f"{label}{steam_id}: role должен быть boss или mercenary")
    if not isinstance(factories, list):
        raise ValueError(f"{label}{steam_id}: factories должны быть массивом")
    return {"role": role, "factories": factories}


def load_grants_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: ожидается объект {{ SteamID: player }}")
    out: dict[str, Any] = {}
    for steam_id, entry in data.items():
        if not isinstance(steam_id, str) or not steam_id.isdigit():
            raise ValueError(f"{path}: некорректный SteamID '{steam_id}'")
        out[steam_id] = normalize_player_entry(steam_id, entry, path=path)
    return out


def merge_grants_files(paths: list[Path]) -> dict[str, Any]:
    combined: dict[str, Any] = {}
    for path in paths:
        payload = load_grants_file(path)
        overlap = set(combined) & set(payload)
        if overlap:
            raise ValueError(
                f"{path}: дублирующиеся SteamID {sorted(overlap)} "
                f"(уже заданы в предыдущих файлах)"
            )
        combined.update(payload)
    return dict(sorted(combined.items(), key=lambda item: item[0]))


def resolve_input_dir(raw: str | None, base: Path) -> Path:
    if not raw:
        return base / "sources"
    path = Path(raw)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def collect_inputs(input_dir: Path, names: tuple[str, ...]) -> list[Path]:
    missing = [name for name in names if not (input_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Не найдены файлы в {input_dir}:\n"
            + "\n".join(f"  - {name}" for name in missing)
            + "\n\nСкопируйте JSON с диска D: в эту папку или укажите --input-dir."
        )
    return [input_dir / name for name in names]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Объединить dominion_grants JSON (по одному SteamID на файл) в один."
    )
    parser.add_argument(
        "--input-dir",
        help="Каталог с исходниками (по умолчанию: f2f_role_balance/sources)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Имя итогового файла (по умолчанию: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=list(DEFAULT_SOURCE_FILES),
        help="Список JSON-файлов для слияния (в заданном порядке)",
    )
    args = parser.parse_args(argv)

    base = Path(__file__).resolve().parent
    input_dir = resolve_input_dir(args.input_dir, base)
    paths = collect_inputs(input_dir, tuple(args.files))
    combined = merge_grants_files(paths)

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = base / out_path
    out_path.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"merged {len(paths)} files -> {out_path.name}")
    for sid, player in combined.items():
        print(f"  {sid}: {player['role']}, {len(player['factories'])} factory(ies)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
