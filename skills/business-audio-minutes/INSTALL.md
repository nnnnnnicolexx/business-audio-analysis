# Business Audio Minutes 从 0 到 1 安装

本指南假设 Codex 已经安装并可以正常使用。Skill 配置了自动触发：提供录音并说“分析这段录音”即可使用，无需每次输入 Skill 名称。

本页命令均在 `skills/business-audio-minutes` 目录内执行。软件和识别引擎名称仅用于说明安装依赖，不预设任何业务系统或企业环境。

## 目录

- [支持环境](#1-支持环境)
- [准备 Python](#2-准备-python)
- [解压并安装 Skill](#3-解压并安装-skill)
- [配置输出与笔记目录](#4-配置输出与笔记目录)
- [验证安装](#5-验证安装)
- [首次使用](#6-首次使用)
- [模型与质量档位](#7-模型与质量档位)
- [更新与卸载](#8-更新与卸载)

## 1. 支持环境

| 环境 | 本地识别后端 | 说明 |
| --- | --- | --- |
| Apple 芯片 Mac | MLX Whisper | 首选，能够使用 Apple Silicon 加速 |
| Intel Mac | faster-whisper | 使用 CPU 本地识别 |
| Windows | faster-whisper | 支持 CPU；有可用 NVIDIA 环境时自动尝试 CUDA |
| Linux | faster-whisper | 支持 CPU；有可用 NVIDIA 环境时自动尝试 CUDA |

本包的转写脚本不上传音频，也不调用云端识别接口。首次安装需要联网下载 Python 包，首次识别还会下载模型；模型就绪后可在本地识别。Codex 读取转写和附件后如何处理内容，取决于宿主和模型服务配置，因此不能将整条分析流程描述为完全离线。

当前验证基于 Apple Silicon macOS：两种后端均完成过短录音转写。Intel macOS、Windows、Linux 是安装脚本的适配目标，尚未完成对应系统的真机验收；不保证所有系统版本和 CPU 架构均可安装。

本 Skill 不需要启动或维护常驻后台服务。每次分析录音时，Codex 会按需调用隔离的本地 Python 运行环境。

## 2. 准备 Python

建议使用 Python 3.10、3.11 或 3.12。macOS 安装脚本会先尝试使用 Codex 自带的 Python，再检查系统中的 Python，不会因为系统自带 Python 版本较旧而直接失败。

### macOS

先检查：

```bash
python3 --version
```

如果没有 Python，且已经安装 Homebrew，可安装 Python 3.12：

```bash
brew install python@3.12
```

没有 Homebrew 时也可以使用 Python 官网安装包，不必为本 Skill 单独安装包管理器。安装后重新打开终端。

### Windows

先检查：

```powershell
py -3 --version
```

如果没有 Python：

```powershell
winget install -e --id Python.Python.3.12
```

安装后重新打开 PowerShell。

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### Fedora

```bash
sudo dnf install -y python3 python3-pip
```

## 3. 解压并安装 Skill

将仓库压缩包解压，先进入仓库根目录，再进入 Skill 目录：

```text
cd skills/business-audio-minutes
```

Windows PowerShell 也可以使用 `cd skills\business-audio-minutes`。

### macOS / Linux

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
```

安装器会：

1. 将 Skill 安装到 `${CODEX_HOME}/skills/business-audio-minutes`；未设置 `CODEX_HOME` 时使用 `~/.codex/skills/business-audio-minutes`。
2. 在 `${CODEX_HOME}/runtime/business-audio-minutes/.venv` 创建独立 Python 环境；未设置 `CODEX_HOME` 时使用 `~/.codex`。
3. 安装本地识别后端和电子表格读取依赖。
4. 写入个人配置，不复制任何其他人的路径或凭据。
5. 执行环境自检。

安装完成后重启 Codex，使 Skill 列表刷新。

## 4. 配置输出与笔记目录

默认输出目录为：

```text
~/Documents/Codex/business-audio-minutes
```

配置一个可选的本地笔记目录；以下路径只是示例，需要替换为自己的目录：

### macOS / Linux

```bash
python3 scripts/configure.py --publish-dir "$HOME/Documents/meeting-notes"
```

### Windows

```powershell
py -3 scripts\configure.py --publish-dir "$HOME\Documents\meeting-notes"
```

不需要自动同步时保持 `publish_dir` 为空。查看当前配置：

```bash
python3 scripts/configure.py --show
```

Windows 使用 `py -3 scripts\configure.py --show`。配置文件仅保存在本机，不要上传个人配置、录音或分析结果到公共仓库。

## 5. 验证安装

### macOS / Linux

```bash
python3 scripts/doctor.py --strict
```

### Windows

```powershell
py -3 scripts\doctor.py --strict
```

看到 `status: ok` 且存在可用后端即可。

## 6. 首次使用

在 Codex 中上传 `.m4a`、`.mp3`、`.wav`、`.mp4` 等录音文件，然后直接说：

```text
分析这段录音，输出业务调研纪要。
```

也可以附带截图、电子表格和补充说明。Codex 会保留原始转写，并把不确定内容标记为待确认。

## 7. 模型与质量档位

| 档位 | Apple Silicon | 其他平台 | 适用场景 |
| --- | --- | --- | --- |
| `fast` | Whisper Small | Whisper Base | 快速预览、机器资源有限 |
| `balanced` | Large V3 Turbo | Whisper Small | 默认，兼顾质量与资源 |
| `accurate` | Large V3 Turbo | Large V3 Turbo | 重要会议、高配置电脑 |

修改默认档位：

```bash
python3 scripts/configure.py --quality accurate
```

模型首次下载可能需要数百 MB 到约 2 GB 的磁盘空间和稳定网络。

## 8. 更新与卸载

收到新版压缩包后，重新运行安装脚本即可覆盖 Skill 文件并保留个人配置。

卸载时删除配置和运行环境中的相应目录；以下命令适用于未自定义 `CODEX_HOME` 或运行环境路径的 macOS/Linux 安装。自定义过路径时请先运行 `configure.py --show` 核对位置：

```bash
rm -rf ~/.codex/skills/business-audio-minutes
rm -rf ~/.codex/runtime/business-audio-minutes
rm -rf ~/.codex/business-audio-minutes
```

Windows 可删除用户目录下 `.codex\skills\business-audio-minutes`、`.codex\runtime\business-audio-minutes` 和 `.codex\business-audio-minutes`。

遇到模型下载、内存、Windows DLL、CUDA 或低音量问题时，参阅 [references/troubleshooting.md](references/troubleshooting.md)。
