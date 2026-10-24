# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name

from __future__ import annotations

import contextlib
import math
import os
from typing import Literal

from nvitop.api import (
    NA,
    GiB,
    NaType,
    Snapshot,
    bytes2human,
    colored,
    set_color,
    timedelta2human,
    ttl_cache,
)
from nvitop.api.host import WINDOWS as IS_WINDOWS
from nvitop.api.host import WINDOWS_SUBSYSTEM_FOR_LINUX
from nvitop.tui.library.host import getuser, hostname
from nvitop.tui.library.widestring import WideString, wcslen


__all__ = [
    'HOSTNAME',
    'IS_SUPERUSER',
    'IS_WINDOWS',
    'IS_WINDOWS_SUBSYSTEM_FOR_LINUX',
    'IS_WSL',
    'LARGE_INTEGER',
    'NA',
    'USERNAME',
    'USER_CONTEXT',
    'GiB',
    'NaType',
    'Snapshot',
    'bytes2human',
    'colored',
    'cut_string',
    'make_bar_chart',
    'set_color',
    'timedelta2human',
    'ttl_cache',
]


USERNAME: str = getuser()

IS_SUPERUSER: bool = False
with contextlib.suppress(AttributeError, OSError):
    if IS_WINDOWS:
        import ctypes

        IS_SUPERUSER = bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    else:
        try:
            IS_SUPERUSER = os.geteuid() == 0
        except AttributeError:
            IS_SUPERUSER = os.getuid() == 0

HOSTNAME: str = hostname()
IS_WINDOWS_SUBSYSTEM_FOR_LINUX = IS_WSL = bool(WINDOWS_SUBSYSTEM_FOR_LINUX)
if IS_WSL:
    HOSTNAME = f'{HOSTNAME} (WSL)'

USER_CONTEXT: str = f'{USERNAME}@{HOSTNAME}'


LARGE_INTEGER: int = 65536


def cut_string(
    s: object,
    maxlen: int,
    padstr: str = '...',
    align: Literal['left', 'right'] = 'left',
) -> str:
    assert align in ('left', 'right')

    if not isinstance(s, str):
        s = str(s)
    s = WideString(s)
    padstr = WideString(padstr)

    if len(s) <= maxlen:
        return str(s)
    if len(padstr) >= maxlen:
        return str(padstr[:maxlen])
    if align == 'left':
        return str(s[: maxlen - len(padstr)] + padstr)
    return str(padstr + s[-(maxlen - len(padstr)) :])


# pylint: disable-next=too-many-arguments
def make_bar_chart(
    prefix: str,
    percent: float | str,
    width: int,
    *,
    extra_text: str = '',
    swap_text: bool = False,
    extra_blank: str = '',
) -> str:
    bar_chart = f'{prefix}: '
    filled = percent != NA and not (isinstance(percent, float) and not math.isfinite(percent))
    if filled:
        if isinstance(percent, str) and percent.endswith('%'):
            percent = percent.replace('%', '')
            percent = float(percent) if '.' in percent else int(percent)
        percentage = max(0.0, min(float(percent) / 100.0, 1.0))
        if isinstance(percent, float) and wcslen(bar_chart) + 9 <= width:
            text = f'{percent:.1f}%'
        else:
            text = f'{min(round(percent), 100):d}%'.replace('100%', 'MAX')  # type: ignore[arg-type]
    else:
        text = 'N/A'
        if (
            extra_text
            and 'N/A' not in extra_text.upper()
            and swap_text
            and wcslen(bar_chart) + wcslen(extra_text) + 2 <= width
        ):
            text, extra_text = extra_text, ''

    tail = text
    if extra_text:
        tail = (
            f'{extra_text} {extra_blank}{text}'
            if swap_text
            else f'{text} {extra_blank}{extra_text}'
        )
    tail = tail.rstrip()
    tail_width = wcslen(tail)
    right_margin = 1
    if wcslen(bar_chart) + tail_width + 2 + right_margin > width:
        tail = text
        tail_width = wcslen(tail)
    if wcslen(bar_chart) + tail_width + 2 + right_margin > width:
        tail = tail[: max(1, width - wcslen(bar_chart) - 2 - right_margin)]
        tail_width = wcslen(tail)

    bar_area = max(1, width - wcslen(bar_chart) - tail_width - 1 - right_margin)
    if filled:
        quotient, remainder = divmod(max(1, round(8 * bar_area * percentage)), 8)
        quotient = min(quotient, bar_area)
        bar = '█' * quotient
        if remainder > 0 and quotient < bar_area:
            bar += ' ▏▎▍▌▋▊▉'[remainder]
    else:
        bar = '░' * bar_area

    used = wcslen(bar_chart) + wcslen(bar)
    padding = max(0, width - right_margin - used - tail_width)
    return f'{bar_chart}{bar}{" " * padding}{tail}{" " * right_margin}'
