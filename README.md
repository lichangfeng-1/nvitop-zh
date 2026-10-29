# nvitop-zh

基于 [nvitop](https://github.com/XuehaiPan/nvitop) v1.7.1 的中文增强派生版，当前 v1.0.8。

面向 NVIDIA GPU 的交互式监视器：保留 nvitop 的彩色进度条与进程管理能力，补上 nvtop 常见的频率、PCIe 档位与实时收发速率，并把主界面做成中英双语。

## 与上游的差异

- **中英双语界面**：设备表、主机面板、进程表标题、帮助页与提示信息。
- **设备面板布局**：完整模式恢复“上显存 MEM、下利用率 UTL”两条整宽进度条；紧凑模式两条并排。
- **补齐 nvtop 的信息**：
  - GPU 当前/最大频率（SM 与显存频率）
  - PCIe 档位与实时收发速率，例如 `PCIe3x16 1.1M/439K`
  - 显存带宽利用率、功耗
- **温度**：彩色数字（绿/黄/红），不画进度条。
- **去重**：宽屏已有 UTL 进度条时，表格不再重复显示 GPU-Util；窄屏没有条时保留数字。
- **8 卡实时曲线**：主界面按 `g` 打开八卡视图（宽屏 4×2，窄屏 2×N），每卡显存与利用率各一条；再按 `g` 返回。
- **视频编解码**：频率行第三列显示 `ENC/DEC` 利用率（NVML encoder/decoder）。
- **CPU 与显卡频率**：主机面板显示 CPU 最高核心频率与温度（k10temp）；设备面板补显存频率、SM 频率标签。
- **环境屏中文说明**：按 `e` 查看进程环境时，常见变量（`PATH`、`CUDA_VISIBLE_DEVICES`、`NCCL_*`、`VLLM_*` 等）行尾附中文说明，原 `KEY=VALUE` 内容不变；长值放不下时只显示原行。

## 安装

要求 Python >= 3.8，以及 `nvidia-ml-py`、`psutil`（Windows 额外需要 `windows-curses`）。

### 方式一：源码直接运行

```sh
git clone https://github.com/lichangfeng-1/nvitop-zh.git
cd nvitop-zh
PYTHONPATH=. python3 -m nvitop
```

### 方式二：pip 安装

```sh
pip install .
nvitop-zh
```

> 本项目的 Python 包名仍是 `nvitop`（便于复用上游代码），发行名与唯一命令是 `nvitop-zh`。pip 安装会在当前环境安装同名的 Python 包，若机器上已安装上游 nvitop，建议装在独立虚拟环境。源码方式（`PYTHONPATH=. python3 -m nvitop`）则不会影响系统的 `nvitop` 命令。

## 使用

```sh
nvitop-zh
```

| 按键 | 作用 |
|---|---|
| `g` | 8 卡实时曲线屏；再按返回 |
| `h` / `?` | 帮助 |
| `a` / `f` / `c` | 自动 / 完整 / 紧凑模式 |
| `o` 系列 | 按 GPU、PID、用户、显存等排序 |
| `q` | 退出 |

原 `nvitop` 与 `nvtop` 命令不受影响，可随时对照；屏幕底部还有一行中文使用提示（界面未占满终端时显示）。

## 自适应

- 终端宽度 ≥ 100 列才显示右侧进度条，窄屏只保留表格。
- 终端高度不足时自动从完整模式降为紧凑模式；高度取决于 GPU 数与进程数。

## 已知限制

- 高级屏（`Enter` 进程指标、`t` 树视图）目前保留上游英文；环境屏已支持中文说明。
- 进度条渐变依赖终端 256 色；tmux 或 16 色终端会退化为绿/黄/红三档，功能不受影响。
- 中文列宽按显示宽度计算（`wcslen`），Windows 伪终端预览可能出现宽字符对齐误差，Linux ncursesw 下已验证。

## 许可证

上游 nvitop 采用 **Apache-2.0 AND GPL-3.0-only**。本派生版沿用同一许可，保留上游的 `LICENSE`（Apache-2.0）、`COPYING`（GPL-3.0）与版权声明。

- 上游项目：https://github.com/XuehaiPan/nvitop
- 上游 README 保留为 [README-upstream.md](README-upstream.md)
- 本派生版的修改部分版权归 nvitop-zh contributors，2026。
