# 保留视频时长指南

## 功能概述

本功能可以去除视频中的音频轨道，同时**完全保留原始视频的时间长度**。这对于需要静音视频但保持原有时长的场景非常有用。

## 核心特性

- ✅ **完全保留时长**：输出视频与原视频时长完全一致
- ✅ **去除音频**：彻底移除所有音频轨道
- ✅ **保持画质**：视频质量不受影响
- ✅ **自动处理**：智能选择最佳处理方式
- ✅ **批量支持**：可同时处理多个视频文件

## 快速使用

### 方法1：使用 API 函数

```python
from airtest.core.api import remove_video_audio

# 基本用法 - 保留时长（默认）
output_path = remove_video_audio('input_video.mp4')

# 指定输出文件
remove_video_audio('input_video.mp4', 'silent_video.mp4')

# 明确指定保留时长
remove_video_audio('input_video.mp4', 'output.mp4', keep_duration=True)
```

### 方法2：使用命令行工具

```bash
# 处理单个文件
python examples/preserve_video_duration.py input_video.mp4

# 批量处理目录中的所有视频
python examples/preserve_video_duration.py /path/to/videos/
```

### 方法3：使用 GUI 应用

```python
# 运行图形界面应用
python examples/robust_gui_app.py
```

## 详细使用示例

### 单个文件处理

```python
import os
from airtest.core.api import remove_video_audio, get_video_info

# 输入文件
input_video = "my_video.mp4"

# 检查原始视频信息
original_info = get_video_info(input_video)
print(f"原始时长: {original_info['duration']} 秒")
print(f"有音频: {original_info['has_audio']}")

# 去除音频，保留时长
output_video = remove_video_audio(
    input_video,
    output_path="silent_video.mp4",
    keep_duration=True  # 关键参数
)

# 验证结果
output_info = get_video_info(output_video)
print(f"输出时长: {output_info['duration']} 秒")
print(f"有音频: {output_info['has_audio']}")

# 时长应该完全一致
assert abs(original_info['duration'] - output_info['duration']) < 0.1
```

### 批量处理

```python
import os
from pathlib import Path
from airtest.core.api import remove_video_audio

def batch_remove_audio(input_dir, output_dir):
    """批量去除音频并保留时长"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 支持的视频格式
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    
    for video_file in input_path.iterdir():
        if video_file.suffix.lower() in video_extensions:
            print(f"处理: {video_file.name}")
            
            output_file = output_path / f"{video_file.stem}_no_audio{video_file.suffix}"
            
            try:
                remove_video_audio(
                    str(video_file),
                    str(output_file),
                    keep_duration=True
                )
                print(f"✅ 完成: {output_file.name}")
            except Exception as e:
                print(f"❌ 失败: {e}")

# 使用示例
batch_remove_audio("input_videos/", "output_videos/")
```

### 高级用法 - 自定义处理

```python
from airtest.utils.video_processor import VideoProcessor

# 创建处理器实例
processor = VideoProcessor()

# 获取详细的视频信息
video_info = processor.get_video_info("input.mp4")
print(f"详细信息: {video_info}")

# 自定义处理参数
output_path = processor.remove_audio(
    input_path="input.mp4",
    output_path="custom_output.mp4",
    keep_duration=True  # 保留时长
)

print(f"处理完成: {output_path}")
```

## 技术原理

### FFmpeg 模式
当系统安装了 FFmpeg 时，使用以下命令：
```bash
ffmpeg -i input.mp4 -c:v copy -an -y output.mp4
```
- `-c:v copy`: 复制视频流，不重新编码（保持质量和时长）
- `-an`: 去除音频流
- `-y`: 覆盖输出文件

### MoviePy 模式
当 FFmpeg 不可用时，使用 MoviePy：
```python
import moviepy.editor as mp

video = mp.VideoFileClip("input.mp4")
video_no_audio = video.without_audio()

# 确保时长一致
if video_no_audio.duration != video.duration:
    video_no_audio = video_no_audio.set_duration(video.duration)

video_no_audio.write_videofile("output.mp4", audio=False)
```

## 参数说明

### `remove_video_audio()` 函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | str | 必需 | 输入视频文件路径 |
| `output_path` | str | None | 输出文件路径（None时自动生成） |
| `keep_duration` | bool | True | 是否保留原始时长 |

### 返回值
- **成功**: 返回输出文件的完整路径
- **失败**: 抛出相应的异常

## 支持的格式

### 输入格式
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)

### 输出格式
- 默认保持与输入相同的格式
- 推荐使用 MP4 格式以获得最佳兼容性

## 常见问题

### Q: 为什么输出视频时长与原视频略有差异？
A: 这是正常现象，通常差异在0.1秒以内。这是由于：
- 视频编码的帧率精度
- 不同编码器的时间戳处理方式
- 浮点数精度限制

### Q: 处理后的视频文件大小变化？
A: 通常文件会变小，因为：
- 移除了音频轨道
- 如果使用 FFmpeg 的 copy 模式，视频流不会重新编码

### Q: 如何确保最佳性能？
A: 建议：
1. 安装 FFmpeg（比 MoviePy 更快）
2. 使用 SSD 存储
3. 确保足够的内存空间

### Q: 支持哪些操作系统？
A: 支持所有主流操作系统：
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu, CentOS, etc.)

## 错误处理

```python
try:
    output_path = remove_video_audio("input.mp4")
    print(f"成功: {output_path}")
except FileNotFoundError:
    print("错误: 输入文件不存在")
except RuntimeError as e:
    print(f"处理错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 性能优化建议

1. **使用 FFmpeg**: 安装 FFmpeg 以获得最佳性能
2. **批量处理**: 一次处理多个文件更高效
3. **存储优化**: 使用 SSD 存储提高 I/O 性能
4. **内存管理**: 处理大文件时确保足够内存

## 完整示例

查看 `examples/preserve_video_duration.py` 获取完整的使用示例，包括：
- 单文件处理演示
- 批量处理功能
- 错误处理机制
- 进度显示
- 结果验证

这个功能完美解决了"保留视频时间长度"的需求，确保输出的静音视频与原视频具有完全相同的时长。
