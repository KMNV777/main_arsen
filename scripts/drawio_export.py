# -*- coding: utf-8 -*-
"""Общие настройки draw.io для файлов репозитория (diagrams.net / GitHub)."""

from __future__ import annotations

from drawpyo import File

DRAWIO_HOST = "app.diagrams.net"
DRAWIO_VERSION = "22.1.0"


def configure_drawio_file(f: File) -> File:
    """Метаданные mxfile для открытия в diagrams.net и интеграции с GitHub."""
    f.host = DRAWIO_HOST
    f.version = DRAWIO_VERSION
    f.type = "device"
    return f
