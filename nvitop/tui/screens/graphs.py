# This file is part of nvitop-zh, based on nvitop.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

from __future__ import annotations

import math
from typing import TYPE_CHECKING, ClassVar

from nvitop.tui.library import NA, Device
from nvitop.tui.screens.base import BaseScreen


if TYPE_CHECKING:
    import curses

    from nvitop.tui.tui import TUI


__all__ = ['GpuGraphsScreen']


class GpuGraphsScreen(BaseScreen):  # pylint: disable=too-many-instance-attributes
    NAME: ClassVar[str] = 'graphs'

    def __init__(self, *, win: curses.window, root: TUI) -> None:
        super().__init__(win, root)
        self.visible = False
        self.focused = False
        self.x = self.y = 0
        self.width = root.width
        self.height = 0
        self._saved: list[tuple[object, int, int]] = []

    def enter(self) -> None:
        self._saved = []
        for device in self.root.main_screen.device_panel.leaf_devices:
            for name in ('memory_percent', 'gpu_utilization'):
                history = getattr(getattr(device, name, None), 'history', None)
                if history is not None:
                    self._saved.append((history, history.width, history.height))

    def leave(self) -> None:
        for history, width, height in self._saved:
            history.width = width
            history.height = height
        self._saved = []

    def update_size(self, termsize: tuple[int, int] | None = None) -> tuple[int, int]:
        n_term_lines, n_term_cols = super().update_size(termsize=termsize)
        self.x, self.y = 0, 0
        self.width = n_term_cols
        self.height = n_term_lines
        return n_term_lines, n_term_cols

    def _cell_geometry(self, device_count: int) -> tuple[int, int, int, int]:
        cols = 4 if self.width >= 120 and device_count > 2 else 2
        rows = max(1, math.ceil(device_count / cols))
        return cols, rows, self.width // cols, max(4, self.height // rows)

    def draw(self) -> None:
        if not self.visible:
            return

        self.color_reset()
        blank = ' ' * (self.width - 1)
        for line_index in range(self.height):
            self.addstr(line_index, 0, blank)

        devices = self.root.main_screen.device_panel.leaf_devices
        if not devices:
            self.addstr(1, 1, ' 未发现可见 GPU / No visible devices found')
            return

        cols, rows, cell_width, cell_height = self._cell_geometry(len(devices))
        cell_height = max(4, self.height // rows)
        graph_height = max(1, (cell_height - 3) // 2)
        graph_width = max(8, cell_width - 4)

        for index, device in enumerate(devices):
            row, col = divmod(index, cols)
            x = col * cell_width
            y = row * cell_height

            memory = getattr(getattr(device, 'memory_percent', None), 'history', None)
            utilization = getattr(getattr(device, 'gpu_utilization', None), 'history', None)
            if memory is None or utilization is None:
                self.addstr(y, x + 1, f'GPU{device.display_index}: 等待数据 / waiting for data')
                continue

            memory.width, memory.height = graph_width, graph_height
            utilization.width, utilization.height = graph_width, graph_height

            memory_value = memory.last_value
            utilization_value = utilization.last_value
            mem_color = Device.color_of(memory_value, type='memory')
            utl_color = Device.color_of(utilization_value, type='gpu')

            mem_text = f'GPU{device.display_index} 显存/MEM {memory_value:.1f}%'
            utl_text = f'GPU{device.display_index} 利用/UTL {utilization_value:.1f}%'

            self.addstr(y, x + 1, mem_text)
            self.color_at(y, x + 1, width=min(len(mem_text), cell_width - 1), fg=mem_color, attr='bold')
            for offset, line in enumerate(memory.graph, start=1):
                if offset > graph_height:
                    break
                self.addstr(y + offset, x + 1, line)
                self.color_at(y + offset, x + 1, width=len(line), fg=mem_color)

            util_y = y + graph_height + 2
            self.addstr(util_y, x + 1, utl_text)
            self.color_at(
                util_y,
                x + 1,
                width=min(len(utl_text), cell_width - 1),
                fg=utl_color,
                attr='bold',
            )
            for offset, line in enumerate(utilization.graph, start=1):
                if offset > graph_height or util_y + offset >= self.y + self.height:
                    break
                self.addstr(util_y + offset, x + 1, line)
                self.color_at(util_y + offset, x + 1, width=len(line), fg=utl_color)

    def press(self, key: int) -> bool:
        self.root.keymaps.use_keymap('graphs')
        return self.root.press(key)
