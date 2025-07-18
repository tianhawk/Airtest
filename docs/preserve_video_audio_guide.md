# 保留视频音频指南

## 功能概述

本功能确保在视频处理过程中**完整保留音频轨道**，适用于需要保持原始音频质量和内容的场景。

## 核心特性

- ✅ **完整保留音频**：确保所有音频轨道被完整保留
- ✅ **保持音频质量**：支持无损复制或高质量重编码
- ✅ **音频增强**：可选的音量调节和质量提升
- ✅ **音频提取**：从视频中提取独立的音频文件
- ✅ **格式兼容**：支持多种音频和视频格式

## 快速使用

### 方法1：使用 API 函数

```python
from airtest.core.api import (
    copy_video_preserve_audio, 
    enhance_video_audio, 
    extract_audio_from_video,
    get_video_info
)

# 基本用法 - 复制视频并保留音频
output_path = copy_video_preserve_audio('input_video.mp4')

# 增强音频质量（音量提升1.5倍）
enhanced_video = enhance_video_audio(
    'input_video.mp4', 
    audio_boost=1.5,
    video_quality='high'
)

# 提取音频文件
audio_file = extract_audio_from_video('input_video.mp4', audio_format='mp3')
```

### 方法2：使用命令行工具

```bash
# 处理单个文件
python examples/simple_audio_demo.py your_video.mp4

# 交互式模式
python examples/simple_audio_demo.py

# 完整功能演示
python examples/preserve_video_audio.py
```

## 详细使用示例

### 1. 基本音频保留

```python
from airtest.core.api import copy_video_preserve_audio, get_video_info

# 检查原始视频
original_info = get_video_info("input.mp4")
print(f"原始音频: {'有' if original_info['has_audio'] else '无'}")

# 复制视频并保留音频
output_video = copy_video_preserve_audio(
    "input.mp4",
    "output_with_audio.mp4",
    preserve_quality=True  # 保持原始质量
)

# 验证结果
output_info = get_video_info(output_video)
print(f"输出音频: {'有' if output_info['has_audio'] else '无'}")
```

### 2. 音频质量增强

```python
from airtest.core.api import enhance_video_audio

# 增强音频质量
enhanced_video = enhance_video_audio(
    "input.mp4",
    "enhanced_output.mp4",
    audio_boost=1.2,        # 音量提升20%
    video_quality='high'    # 高质量视频
)

print(f"增强完成: {enhanced_video}")
```

### 3. 音频文件提取

```python
from airtest.core.api import extract_audio_from_video

# 提取为不同格式
mp3_file = extract_audio_from_video("input.mp4", audio_format='mp3')
wav_file = extract_audio_from_video("input.mp4", audio_format='wav')
aac_file = extract_audio_from_video("input.mp4", audio_format='aac')

print(f"MP3: {mp3_file}")
print(f"WAV: {wav_file}")
print(f"AAC: {aac_file}")
```

### 4. 批量处理

```python
import os
from pathlib import Path
from airtest.core.api import copy_video_preserve_audio

def batch_preserve_audio(input_dir, output_dir):
    """批量保留视频音频"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for video_file in input_path.glob('*.mp4'):
        print(f"处理: {video_file.name}")
        
        output_file = output_path / f"{video_file.stem}_with_audio.mp4"
        
        try:
            copy_video_preserve_audio(
                str(video_file),
                str(output_file),
                preserve_quality=True
            )
            print(f"✅ 完成: {output_file.name}")
        except Exception as e:
            print(f"❌ 失败: {e}")

# 使用示例
batch_preserve_audio("input_videos/", "output_videos/")
```

## 技术实现

### FFmpeg 模式（推荐）

#### 无损复制
```bash
ffmpeg -i input.mp4 -c copy -y output.mp4
```
- 复制所有音频和视频流
- 不重新编码，保持原始质量
- 处理速度最快

#### 高质量重编码
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -b:a 192k -y output.mp4
```
- 重新编码但保持高质量
- 可以优化文件大小
- 支持格式转换

#### 音频增强
```bash
ffmpeg -i input.mp4 -c:v libx264 -af "volume=1.5" -c:a aac -y output.mp4
```
- 调节音频音量
- 保持视频质量
- 支持多种音频滤镜

### MoviePy 模式（备选）

```python
import moviepy.editor as mp

# 加载视频（包含音频）
video = mp.VideoFileClip("input.mp4")

# 确保音频被保留
if video.audio is not None:
    # 写入文件，保留音频
    video.write_videofile(
        "output.mp4",
        codec='libx264',
        audio_codec='aac'
    )
else:
    print("原视频没有音频轨道")

video.close()
```

## 参数详解

### `copy_video_preserve_audio()` 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | str | 必需 | 输入视频文件路径 |
| `output_path` | str | None | 输出文件路径（None时自动生成） |
| `preserve_quality` | bool | True | 是否保持原始质量 |

### `enhance_video_audio()` 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | str | 必需 | 输入视频文件路径 |
| `output_path` | str | None | 输出文件路径 |
| `audio_boost` | float | 1.0 | 音频增益倍数 |
| `video_quality` | str | 'high' | 视频质量级别 |

### `extract_audio_from_video()` 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | str | 必需 | 输入视频文件路径 |
| `output_path` | str | None | 输出音频文件路径 |
| `audio_format` | str | 'mp3' | 音频格式 |

## 支持的格式

### 视频格式
- **输入**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **输出**: 默认保持与输入相同，推荐 MP4

### 音频格式
- **MP3**: 通用兼容性最好
- **WAV**: 无损质量，文件较大
- **AAC**: 高质量，文件适中
- **FLAC**: 无损压缩，音质最佳

## 质量设置

### 视频质量级别

| 级别 | CRF值 | 预设 | 适用场景 |
|------|-------|------|----------|
| high | 18 | slow | 最高质量，文件较大 |
| medium | 23 | medium | 平衡质量和大小 |
| low | 28 | fast | 快速处理，文件较小 |

### 音频增益建议

| 倍数 | 效果 | 适用场景 |
|------|------|----------|
| 0.5 | 音量减半 | 音频过大时 |
| 1.0 | 原始音量 | 默认设置 |
| 1.5 | 音量提升50% | 音频偏小时 |
| 2.0 | 音量翻倍 | 音频很小时 |

## 常见问题

### Q: 如何确保音频完整保留？
A: 使用 `preserve_quality=True` 参数，这会使用无损复制模式：
```python
copy_video_preserve_audio("input.mp4", preserve_quality=True)
```

### Q: 处理后音频质量下降怎么办？
A: 
1. 确保安装了 FFmpeg（比 MoviePy 质量更好）
2. 使用 `preserve_quality=True` 进行无损复制
3. 如需重编码，选择高质量设置

### Q: 支持多音轨视频吗？
A: 是的，FFmpeg 模式下会保留所有音轨：
```bash
ffmpeg -i input.mp4 -c copy -y output.mp4  # 保留所有音轨
```

### Q: 如何处理没有音频的视频？
A: 系统会自动检测并提示：
```python
info = get_video_info("video.mp4")
if not info['has_audio']:
    print("该视频没有音频轨道")
```

## 性能优化

### 1. 使用 FFmpeg
```bash
# 安装 FFmpeg
# Windows: 下载并添加到 PATH
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### 2. 选择合适的模式
- **无损复制**: 最快，质量最好
- **高质量重编码**: 平衡速度和质量
- **快速处理**: 最快，质量稍降

### 3. 硬件加速（可选）
```python
# 使用 GPU 加速（需要支持的硬件）
enhance_video_audio(
    "input.mp4",
    video_quality='high'  # 会自动选择最佳编码器
)
```

## 验证音频保留

```python
def verify_audio_preservation(original_path, output_path):
    """验证音频是否被正确保留"""
    
    original_info = get_video_info(original_path)
    output_info = get_video_info(output_path)
    
    original_audio = original_info.get('has_audio', False)
    output_audio = output_info.get('has_audio', False)
    
    if original_audio and output_audio:
        print("✅ 音频成功保留")
        return True
    elif not original_audio:
        print("ℹ️  原始视频无音频")
        return True
    else:
        print("❌ 音频丢失")
        return False

# 使用示例
output = copy_video_preserve_audio("input.mp4")
verify_audio_preservation("input.mp4", output)
```

这个功能完美解决了"保留视频音频"的需求，确保在任何视频处理过程中音频轨道都能被完整保留。
