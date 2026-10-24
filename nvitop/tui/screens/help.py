# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from nvitop.tui.library import Device, MouseEvent, wcslen
from nvitop.tui.screens.base import BaseScreen
from nvitop.version import __version__


if TYPE_CHECKING:
    import curses

    from nvitop.tui.tui import TUI


__all__ = ['HelpScreen']


HELP_TEMPLATE = r"""nvitop-zh {} - 基于 nvitop, (C) Xuehai Pan, 2021-2026.
GNU GPLv3 许可 / Released under the GNU GPLv3 License.

进程类型 / GPU Process Type: C: 计算/Compute, G: 图形/Graphics, X: 混合/Mixed.

设备着色 / Device coloring 按负载强度 / by loading intensity:
  - GPU 利用率 / GPU utilization: 轻 < {:2d}% <= 中 < {:2d}% <= 重.
  - 显存占比 / GPU-MEM percent: 轻 < {:2d}% <= 中 < {:2d}% <= 重.

      a f c: 切换显示模式 / change display mode      h ?: 本帮助 / help
       F5 r: 强制刷新 / force refresh                 q: 退出 / quit

     Arrows: 滚动进程 / scroll process list        Space: 标记/取消 / tag
       Home: 首个进程 / first process               Esc: 清除选择 / clear
        End: 最后进程 / last process       Ctrl-C I: 中断进程 / interrupt
                                                  K: 杀死进程 / kill
   Ctrl-A ^: 滚到最左 / scroll to left              T: 终止进程 / terminate
   Ctrl-E $: 滚到最右 / scroll to right             e: 进程环境 / environment
   PageUp [: 整屏上滚 / screen up                   t: 树状视图 / tree-view
 PageDown ]: 整屏下滚 / screen down            Enter: 进程指标 / metrics

      Wheel: 滚动进程 / scroll list        Shift-Wheel: 横向滚动 / horizontal
        Tab: 滚动进程 / scroll list         Ctrl-Wheel: 快速滚动 / fast ({}x)

      on oN: 按 GPU 排序 / sort by GPU-INDEX
      op oP: 按 PID 排序 / by PID                  ob oB: 按带宽 / by %GMBW
      ou oU: 按用户 / by USER                      oc oC: 按 CPU / by %CPU
      og oG: 按显存 / by GPU-MEM                   om oM: 按内存 / by %MEM
      os oS: 按 SM / by %SM                        ot oT: 按时间 / by TIME
        , .: 选择排序列 / select column               /: 反转排序 / invert order

按任意键返回 / Press any key to return.
"""


class HelpScreen(BaseScreen):  # pylint: disable=too-many-instance-attributes
    NAME: ClassVar[str] = 'help'

    def __init__(self, *, win: curses.window, root: TUI) -> None:
        super().__init__(win, root)

        self.infos: list[str] = (
            HELP_TEMPLATE.format(
                __version__,
                *Device.GPU_UTILIZATION_THRESHOLDS,
                *Device.MEMORY_UTILIZATION_THRESHOLDS,
                MouseEvent.CTRL_SCROLLWHEEL_MULTIPLIER,
            )
            .strip()
            .splitlines()
        )
        self.color_matrix: dict[int, tuple[str | None, str | None]] = {
            9: ('green', 'green'),
            10: ('green', 'green'),
            12: ('cyan', 'yellow'),
            13: ('cyan', 'yellow'),
            14: ('cyan', 'red'),
            15: (None, 'red'),
            16: ('cyan', 'red'),
            **dict.fromkeys(range(17, 20), ('cyan', 'green')),
            **dict.fromkeys(range(21, 23), ('blue', 'blue')),
            **dict.fromkeys(range(24, 29), ('blue', 'blue')),
            29: ('magenta', 'magenta'),
        }
        # Rows whose right-hand action column is colored red are exactly the
        # kill/terminate/interrupt keybindings — the same set ``--readonly`` disables.
        self.readonly_disabled_rows: frozenset[int] = frozenset(
            row for row, (_, right) in self.color_matrix.items() if right == 'red'
        )

        self.x, self.y = root.x, root.y
        self.width: int = max(map(wcslen, self.infos))
        self.height: int = len(self.infos)

    def draw(self) -> None:
        if not self.need_redraw:
            return

        self.color_reset()

        for y, line in enumerate(self.infos, start=self.y):
            self.addstr(y, self.x, line)

        self.color_at(self.y, self.x, width=self.width, fg='cyan', attr='bold')
        self.color_at(self.y + 1, self.x, width=self.width, fg='cyan', attr='bold')

        self.color_at(self.y + self.height - 1, self.x, width=self.width, fg='cyan', attr='bold')

        self.color_at(self.y + 3, self.x, width=17, attr='bold')
        for dx in (18, 30, 43):
            self.color_at(self.y + 3, self.x + dx, width=1, fg='magenta', attr='bold')
        for dx in (21, 33, 48):
            self.color_at(self.y + 3, self.x + dx, width=1, attr='underline')

        self.color_at(self.y + 5, self.x, width=21, attr='bold')
        for dy in (6, 7):
            self.color_at(self.y + dy, self.x + 21, width=5, fg='green', attr='bold | italic')
            self.color_at(self.y + dy, self.x + 36, width=8, fg='yellow', attr='bold | italic')
            self.color_at(self.y + dy, self.x + 54, width=5, fg='red', attr='bold | italic')

        for dy, (left, right) in self.color_matrix.items():
            if left is not None:
                self.color_at(self.y + dy, self.x, width=12, fg=left, attr='bold')
            if right is not None and not (self.root.readonly and dy in self.readonly_disabled_rows):
                self.color_at(self.y + dy, self.x + 39, width=13, fg=right, attr='bold')

        if self.root.readonly:
            for dy in self.readonly_disabled_rows:
                self.color_at(self.y + dy, self.x + 39, width=self.width - 39, attr='dim')

    def press(self, key: int) -> bool:
        self.root.keymaps.use_keymap('help')
        return self.root.press(key)
