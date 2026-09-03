# 故障排查

## Doctor 报告运行环境不存在

重新运行 `scripts/install.sh` 或 `scripts/install.ps1`。不要把 Python 包安装到业务项目环境。

## 找不到 Python

安装 Python 3.10 至 3.12，然后重新打开终端。Windows 优先使用 `py -3`，macOS/Linux 优先使用 `python3`。

## 模型下载失败

首次识别需要访问 Hugging Face 下载模型。检查网络、代理和剩余磁盘空间。模型下载中断后可以重新运行本地识别；这不会上传音频。

## 内存不足或速度过慢

将质量档位改为：

```bash
python3 scripts/configure.py --quality fast
```

CPU 机器处理长录音可能接近或超过录音时长。重要会议可在内存更大的机器上使用 `accurate`。

## Windows 出现 DLL 或 CTranslate2 错误

先更新 Windows 和显卡驱动。CPU 使用者可显式传入 `--device cpu`。仍有 DLL 加载错误时安装 Microsoft Visual C++ Redistributable 后重启终端。

## CUDA 不可用

自动模式未检测到可用 CUDA 设备时选择 CPU。如果检测到了设备但驱动或运行库不匹配导致识别失败，显式传入 `--device cpu` 重试。只有本机已有兼容的 NVIDIA 驱动和 CUDA 运行环境时才使用 `--device cuda`；不要为了单次会议临时改系统驱动。

## Apple Silicon 未使用 MLX

执行 `doctor.py --strict` 检查 `mlx_whisper`。若 MLX 安装失败，重新运行安装器；也可以临时指定 `--backend faster` 使用本地 CPU 后端。

## 录音音量很低或出现幻听

先确认原始文件是否真的包含清晰人声。重复的“谢谢大家”、宣传语或无关句子可能是静音段幻听，不能写入纪要。没有可靠改善路径时输出低置信度分析并请用户重新导出录音。

## 笔记目录没有同步

运行 `configure.py --show` 检查 `publish_dir`。目录必须存在或当前用户有权创建。发布是可选步骤，不影响本地纪要生成。
