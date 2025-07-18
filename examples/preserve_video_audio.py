#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
保留视频音频功能 - 确保视频处理后音频完整保留
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airtest.core.api import get_video_info


def copy_video_with_audio(input_path, output_path=None, preserve_quality=True):
    """
    复制视频并完整保留音频
    
    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出视频文件路径
        preserve_quality (bool): 是否保持原始质量
        
    Returns:
        str: 输出文件路径
    """
    import subprocess
    import shutil
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频文件不存在: {input_path}")
    
    # 如果没有指定输出路径，自动生成
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_with_audio{ext}"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 尝试使用 FFmpeg 进行高质量复制
    try:
        if preserve_quality:
            # 使用 FFmpeg 进行无损复制（保留所有音频和视频流）
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c', 'copy',  # 复制所有流，不重新编码
                '-y',  # 覆盖输出文件
                output_path
            ]
        else:
            # 重新编码但保持高质量
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',  # 视频编码器
                '-c:a', 'aac',      # 音频编码器
                '-b:v', '5000k',    # 视频比特率
                '-b:a', '192k',     # 音频比特率
                '-y',
                output_path
            ]
        
        print(f"🔄 使用 FFmpeg 处理视频...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ FFmpeg 处理完成: {output_path}")
            return output_path
        else:
            print(f"⚠️ FFmpeg 处理失败: {result.stderr}")
            raise RuntimeError(f"FFmpeg 失败: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️ FFmpeg 不可用，使用文件复制...")
        
        # 如果 FFmpeg 不可用，直接复制文件
        shutil.copy2(input_path, output_path)
        print(f"✅ 文件复制完成: {output_path}")
        return output_path


def enhance_video_audio(input_path, output_path=None, audio_boost=1.0, video_quality='high'):
    """
    增强视频音频质量
    
    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出视频文件路径
        audio_boost (float): 音频增益倍数 (1.0 = 原始音量)
        video_quality (str): 视频质量 ('high', 'medium', 'low')
        
    Returns:
        str: 输出文件路径
    """
    import subprocess
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频文件不存在: {input_path}")
    
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_enhanced{ext}"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 设置视频质量参数
    quality_settings = {
        'high': {'crf': '18', 'preset': 'slow'},
        'medium': {'crf': '23', 'preset': 'medium'},
        'low': {'crf': '28', 'preset': 'fast'}
    }
    
    settings = quality_settings.get(video_quality, quality_settings['high'])
    
    try:
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-crf', settings['crf'],
            '-preset', settings['preset'],
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_path
        ]
        
        # 如果需要音频增益
        if audio_boost != 1.0:
            # 添加音频滤镜
            volume_filter = f"volume={audio_boost}"
            cmd.insert(-2, '-af')
            cmd.insert(-2, volume_filter)
        
        print(f"🔄 增强视频音频质量...")
        print(f"   音频增益: {audio_boost}x")
        print(f"   视频质量: {video_quality}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ 视频音频增强完成: {output_path}")
            return output_path
        else:
            raise RuntimeError(f"FFmpeg 处理失败: {result.stderr}")
            
    except FileNotFoundError:
        raise RuntimeError("FFmpeg 未安装，无法进行音频增强")


def extract_audio_from_video(input_path, output_path=None, audio_format='mp3'):
    """
    从视频中提取音频文件
    
    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出音频文件路径
        audio_format (str): 音频格式 ('mp3', 'wav', 'aac', 'flac')
        
    Returns:
        str: 输出音频文件路径
    """
    import subprocess
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频文件不存在: {input_path}")
    
    if output_path is None:
        name = os.path.splitext(input_path)[0]
        output_path = f"{name}_audio.{audio_format}"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # 音频编码器映射
        audio_codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac'
        }
        
        codec = audio_codecs.get(audio_format, 'libmp3lame')
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vn',  # 不包含视频
            '-acodec', codec,
            '-ab', '192k',  # 音频比特率
            '-y',
            output_path
        ]
        
        print(f"🎵 提取音频为 {audio_format.upper()} 格式...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ 音频提取完成: {output_path}")
            return output_path
        else:
            raise RuntimeError(f"音频提取失败: {result.stderr}")
            
    except FileNotFoundError:
        raise RuntimeError("FFmpeg 未安装，无法提取音频")


def demonstrate_audio_preservation():
    """演示音频保留功能"""
    
    print("=" * 60)
    print("视频音频保留功能演示")
    print("=" * 60)
    
    # 示例视频文件路径
    input_video = "input_video.mp4"  # 请替换为您的视频文件路径
    
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
        print()
        
        # 2. 复制视频并保留音频
        print("📋 复制视频（保留完整音频）...")
        start_time = time.time()
        
        copied_video = copy_video_with_audio(
            input_video,
            preserve_quality=True  # 保持原始质量
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ 复制完成！耗时: {processing_time:.2f} 秒")
        print(f"📁 输出文件: {copied_video}")
        print()
        
        # 3. 验证复制后的视频信息
        print("🔍 验证复制后的视频信息...")
        copied_info = get_video_info(copied_video)
        
        print(f"复制后视频信息:")
        print(f"  📁 文件路径: {copied_info['path']}")
        print(f"  ⏱️  时长: {copied_info.get('duration', 'N/A')} 秒")
        print(f"  🔊 有音频: {copied_info.get('has_audio', 'N/A')}")
        print(f"  🎬 有视频: {copied_info.get('has_video', 'N/A')}")
        print()
        
        # 4. 比较音频保留情况
        original_has_audio = original_info.get('has_audio', False)
        copied_has_audio = copied_info.get('has_audio', False)
        
        print("🎵 音频保留验证:")
        print(f"  原始音频: {'有' if original_has_audio else '无'}")
        print(f"  复制音频: {'有' if copied_has_audio else '无'}")
        
        if original_has_audio and copied_has_audio:
            print("  ✅ 音频成功保留！")
        elif not original_has_audio:
            print("  ℹ️  原始视频无音频")
        else:
            print("  ⚠️  音频可能丢失")
        
        # 5. 文件大小对比
        original_size = os.path.getsize(input_video)
        copied_size = os.path.getsize(copied_video)
        
        print()
        print("💾 文件大小对比:")
        print(f"  原始文件: {original_size / (1024*1024):.2f} MB")
        print(f"  复制文件: {copied_size / (1024*1024):.2f} MB")
        
        if abs(original_size - copied_size) < original_size * 0.01:  # 1% 误差
            print("  ✅ 文件大小基本一致（高质量保留）")
        else:
            print(f"  ℹ️  文件大小变化: {((copied_size - original_size) / original_size * 100):+.1f}%")
        
        # 6. 可选：提取音频文件
        if original_has_audio:
            print()
            print("🎵 额外功能：提取音频文件...")
            try:
                audio_file = extract_audio_from_video(input_video, audio_format='mp3')
                audio_size = os.path.getsize(audio_file)
                print(f"✅ 音频提取完成: {audio_file}")
                print(f"   音频文件大小: {audio_size / (1024*1024):.2f} MB")
            except Exception as e:
                print(f"⚠️  音频提取失败: {e}")
        
        print()
        print("🎉 音频保留演示完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False


def main():
    """主函数"""
    print("视频音频保留工具")
    print("功能：确保视频处理过程中完整保留音频")
    print()
    
    if len(sys.argv) > 1:
        # 命令行模式
        input_file = sys.argv[1]
        
        if not os.path.exists(input_file):
            print(f"❌ 文件不存在: {input_file}")
            return 1
        
        try:
            print(f"🔄 处理文件: {input_file}")
            
            # 获取原始信息
            original_info = get_video_info(input_file)
            has_audio = original_info.get('has_audio', False)
            
            if not has_audio:
                print("⚠️  原始视频没有音频轨道")
            
            # 复制视频并保留音频
            output_file = copy_video_with_audio(input_file, preserve_quality=True)
            
            # 验证结果
            output_info = get_video_info(output_file)
            output_has_audio = output_info.get('has_audio', False)
            
            print(f"原始音频: {'有' if has_audio else '无'}")
            print(f"输出音频: {'有' if output_has_audio else '无'}")
            
            if has_audio and output_has_audio:
                print("✅ 音频成功保留")
            elif not has_audio:
                print("ℹ️  原始视频无音频")
            else:
                print("⚠️  音频可能丢失")
            
            print(f"✅ 完成: {output_file}")
            
            return 0
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return 1
    
    else:
        # 交互模式
        print("使用方法:")
        print("1. 命令行: python preserve_video_audio.py video.mp4")
        print("2. 演示模式: 将视频文件命名为 'input_video.mp4' 并运行此脚本")
        print()
        
        choice = input("选择模式 (1=演示, Enter=退出): ").strip()
        
        if choice == "1":
            demonstrate_audio_preservation()
        else:
            print("👋 再见！")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
