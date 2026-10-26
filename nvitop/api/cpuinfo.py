# This file is part of the Chinese-enhanced fork of nvitop.
# License: GNU GPL version 3.

"""Linux CPU frequency and temperature helpers."""

# pylint: disable=missing-module-docstring

from __future__ import annotations

import glob
from pathlib import Path

from nvitop.api.caching import ttl_cache
from nvitop.api.utils import NA, NaType


__all__ = ['cpu_frequency', 'cpu_temperature']


def _read_int(path: str) -> int | None:
    try:
        return int(Path(path).read_text(encoding='utf-8').strip())
    except (OSError, ValueError):
        return None


@ttl_cache(ttl=1.0)
def cpu_frequency() -> tuple[float | NaType, float | NaType]:
    """Return (current maximum core, hardware maximum) CPU frequency in MHz, or NA."""
    frequencies = [
        value
        for path in glob.glob('/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq')
        if (value := _read_int(path)) is not None
    ]
    if not frequencies:
        return NA, NA
    current = max(frequencies) / 1000.0
    maximum = _read_int('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq')
    return current, (maximum / 1000.0 if maximum is not None else NA)


@ttl_cache(ttl=1.0)
def cpu_temperature() -> int | NaType:
    """Return the maximum CPU package temperature in Celsius, or NA."""
    for name_path in glob.glob('/sys/class/hwmon/hwmon*/name'):
        try:
            name = Path(name_path).read_text(encoding='utf-8').strip()
        except OSError:
            continue
        if name not in {'k10temp', 'coretemp', 'zenpower'}:
            continue
        base = str(Path(name_path).parent)
        temperatures = [
            value
            for path in glob.glob(base + '/temp*_input')
            if (value := _read_int(path)) is not None
        ]
        if temperatures:
            return round(max(temperatures) / 1000)
    return NA
