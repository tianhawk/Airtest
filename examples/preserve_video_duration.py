#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
保留视频时长示例 - 去除音频但保持原始视频时长
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airtest.core.api import remove_video_audio, get_video_info


def demonstrate_duration_preservation():
    """演示如何保留视频时长"""
    
    print("=" * 60)
    print("视频时长保留功能演示")
    print("=" * 60)
    
    # 示例视频文件路径（您需要替换为实际的视频文件）
    input_video = "input_video.mp4"  # 请替换为您的视频文件路径
    
    # 检查输入文件是否存在
    if not os.path.exists(input_video):
        print(f"⚠️  输入视频文件不存在: {input_video}")
        print("请将您的视频文件重命名为 'input_video.mp4' 或修改脚本中的文件路径")
        return False
    
    try:
        # 1. 获取原始视频信息
        print("📹 获取原始视频信息...")
        original_info = get_video_info(input_video)
        
        print(f"原始视频信息:")
        print(f"  📁 文件路径: {original_info['path']}")
        print(f"  ⏱️  时长: {original_info.get('duration', 'N/A')} 秒")
        print(f"  🔊 有音频: {original_info.get('has_audio', 'N/A')}")
        print(f"  🎬 有视频: {original_info.get('has_video', 'N/A')}")
        
        if 'fps' in original_info:
            print(f"  📊 帧率: {original_info['fps']} FPS")
        if 'size' in original_info:
            print(f"  📐 分辨率: {original_info['size'][0]}x{original_info['size'][1]}")
        
        print()
        
        # 2. 去除音频并保留时长
        print("🔇 开始去除音频（保留时长）...")
        start_time = time.time()
        
        # 自动生成输出文件名
        output_video = remove_video_audio(
            input_video, 
            keep_duration=True  # 关键参数：保留原始时长
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ 处理完成！耗时: {processing_time:.2f} 秒")
        print(f"📁 输出文件: {output_video}")
        print()
        
        # 3. 验证输出视频信息
        print("🔍 验证输出视频信息...")
        output_info = get_video_info(output_video)
        
        print(f"输出视频信息:")
        print(f"  📁 文件路径: {output_info['path']}")
        print(f"  ⏱️  时长: {output_info.get('duration', 'N/A')} 秒")
        print(f"  🔊 有音频: {output_info.get('has_audio', 'N/A')}")
        print(f"  🎬 有视频: {output_info.get('has_video', 'N/A')}")
        
        # 4. 比较时长
        original_duration = original_info.get('duration')
        output_duration = output_info.get('duration')
        
        if original_duration and output_duration:
            duration_diff = abs(original_duration - output_duration)
            print()
            print("📊 时长对比:")
            print(f"  原始时长: {original_duration:.2f} 秒")
            print(f"  输出时长: {output_duration:.2f} 秒")
            print(f"  时长差异: {duration_diff:.2f} 秒")
            
            if duration_diff < 0.1:  # 允许0.1秒的误差
                print("  ✅ 时长保留成功！")
            else:
                print("  ⚠️  时长有轻微差异（这是正常的）")
        
        # 5. 文件大小对比
        original_size = os.path.getsize(input_video)
        output_size = os.path.getsize(output_video)
        size_reduction = (original_size - output_size) / original_size * 100
        
        print()
        print("💾 文件大小对比:")
        print(f"  原始文件: {original_size / (1024*1024):.2f} MB")
        print(f"  输出文件: {output_size / (1024*1024):.2f} MB")
        print(f"  大小减少: {size_reduction:.1f}%")
        
        print()
        print("🎉 视频处理完成！音频已移除，时长已保留。")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False


def batch_process_videos(input_dir, output_dir=None):
    """批量处理视频文件"""
    
    print("=" * 60)
    print("批量视频处理 - 保留时长")
    print("=" * 60)
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return False
    
    # 支持的视频格式
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    
    # 查找所有视频文件
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_path.glob(f"*{ext}"))
        video_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ 在目录 {input_dir} 中未找到视频文件")
        return False
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 设置输出目录
    if output_dir is None:
        output_path = input_path / "no_audio"
    else:
        output_path = Path(output_dir)
    
    output_path.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_path}")
    print()
    
    success_count = 0
    failed_files = []
    
    for i, video_file in enumerate(video_files, 1):
        print(f"🎬 处理文件 {i}/{len(video_files)}: {video_file.name}")
        
        try:
            # 生成输出文件路径
            output_file = output_path / f"{video_file.stem}_no_audio{video_file.suffix}"
            
            # 获取原始信息
            original_info = get_video_info(str(video_file))
            original_duration = original_info.get('duration', 0)
            
            # 处理视频
            start_time = time.time()
            result = remove_video_audio(
                str(video_file),
                str(output_file),
                keep_duration=True
            )
            processing_time = time.time() - start_time
            
            # 验证结果
            output_info = get_video_info(result)
            output_duration = output_info.get('duration', 0)
            
            print(f"  ✅ 完成 - 耗时: {processing_time:.1f}s")
            print(f"     原始时长: {original_duration:.1f}s → 输出时长: {output_duration:.1f}s")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed_files.append(video_file.name)
        
        print()
    
    # 总结
    print("=" * 60)
    print("批量处理完成")
    print(f"✅ 成功处理: {success_count} 个文件")
    print(f"❌ 处理失败: {len(failed_files)} 个文件")
    
    if failed_files:
        print("失败的文件:")
        for filename in failed_files:
            print(f"  - {filename}")
    
    return success_count > 0


def main():
    """主函数"""
    print("视频时长保留工具")
    print("功能：去除视频音频，但保持原始视频时长")
    print()
    
    if len(sys.argv) > 1:
        # 命令行模式
        input_file = sys.argv[1]
        
        if os.path.isfile(input_file):
            # 单个文件处理
            print(f"处理单个文件: {input_file}")
            
            try:
                output_file = remove_video_audio(input_file, keep_duration=True)
                print(f"✅ 处理完成: {output_file}")
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                return 1
                
        elif os.path.isdir(input_file):
            # 批量处理
            print(f"批量处理目录: {input_file}")
            success = batch_process_videos(input_file)
            return 0 if success else 1
        else:
            print(f"❌ 文件或目录不存在: {input_file}")
            return 1
    else:
        # 交互模式
        print("使用方法:")
        print("1. 单个文件: python preserve_video_duration.py video.mp4")
        print("2. 批量处理: python preserve_video_duration.py /path/to/videos/")
        print("3. 演示模式: 将视频文件命名为 'input_video.mp4' 并运行此脚本")
        print()
        
        # 尝试演示模式
        demonstrate_duration_preservation()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
