#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单演示：保留视频音频
确保视频处理过程中完整保留音频轨道
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airtest.core.api import (
    copy_video_preserve_audio, 
    enhance_video_audio, 
    extract_audio_from_video, 
    get_video_info
)


def simple_audio_demo():
    """简单演示如何保留视频音频"""
    
    print("🎵 视频音频保留演示")
    print("=" * 40)
    
    # 请将您的视频文件路径替换到这里
    input_video = "test_video.mp4"  # 修改为您的视频文件路径
    
    # 检查文件是否存在
    if not os.path.exists(input_video):
        print(f"❌ 视频文件不存在: {input_video}")
        print("请修改脚本中的 input_video 变量为您的视频文件路径")
        return
    
    try:
        # 1. 查看原始视频信息
        print("📋 原始视频信息:")
        original_info = get_video_info(input_video)
        original_duration = original_info.get('duration', 0)
        has_audio = original_info.get('has_audio', False)
        
        print(f"   文件: {input_video}")
        print(f"   时长: {original_duration:.2f} 秒")
        print(f"   音频: {'有' if has_audio else '无'}")
        
        if not has_audio:
            print("   ⚠️  原始视频没有音频轨道")
            return
        
        print()
        
        # 2. 复制视频并保留音频
        print("📋 复制视频（完整保留音频）...")
        
        copied_video = copy_video_preserve_audio(
            input_video,
            preserve_quality=True  # 保持原始质量
        )
        
        print(f"✅ 复制完成!")
        print(f"   输出文件: {copied_video}")
        print()
        
        # 3. 验证结果
        print("🔍 验证结果:")
        copied_info = get_video_info(copied_video)
        copied_duration = copied_info.get('duration', 0)
        copied_has_audio = copied_info.get('has_audio', False)
        
        print(f"   文件: {copied_video}")
        print(f"   时长: {copied_duration:.2f} 秒")
        print(f"   音频: {'有' if copied_has_audio else '无'}")
        print()
        
        # 4. 对比结果
        duration_diff = abs(original_duration - copied_duration)
        
        print("📊 对比结果:")
        print(f"   原始时长: {original_duration:.2f} 秒")
        print(f"   复制时长: {copied_duration:.2f} 秒")
        print(f"   时长差异: {duration_diff:.3f} 秒")
        
        if duration_diff < 0.1:
            print("   ✅ 时长保持一致！")
        else:
            print("   ⚠️  时长有微小差异（正常现象）")
        
        if copied_has_audio:
            print("   ✅ 音频成功保留！")
        else:
            print("   ❌ 音频丢失！")
        
        # 5. 额外功能演示
        print()
        print("🎵 额外功能演示:")
        
        # 提取音频文件
        print("   - 提取音频文件...")
        try:
            audio_file = extract_audio_from_video(input_video, audio_format='mp3')
            audio_size = os.path.getsize(audio_file)
            print(f"     ✅ 音频提取完成: {audio_file}")
            print(f"     📁 音频文件大小: {audio_size / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"     ❌ 音频提取失败: {e}")
        
        # 音频增强（可选）
        print("   - 音频增强（音量提升1.5倍）...")
        try:
            enhanced_video = enhance_video_audio(
                input_video,
                audio_boost=1.5,  # 音量提升1.5倍
                video_quality='medium'
            )
            print(f"     ✅ 音频增强完成: {enhanced_video}")
        except Exception as e:
            print(f"     ❌ 音频增强失败: {e}")
        
        print()
        print("🎉 演示完成！")
        print("您的视频音频已被完整保留。")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        print("请检查:")
        print("1. 视频文件是否存在且可读")
        print("2. 是否安装了 moviepy: pip install moviepy")
        print("3. 输出目录是否有写入权限")
        print("4. 推荐安装 FFmpeg 以获得更好性能")


def interactive_audio_demo():
    """交互式音频保留演示"""
    
    print("🎵 交互式视频音频保留工具")
    print("=" * 40)
    
    while True:
        input_video = input("请输入视频文件路径 (或按 Enter 退出): ").strip()
        
        if not input_video:
            print("👋 再见！")
            break
        
        if not os.path.exists(input_video):
            print(f"❌ 文件不存在: {input_video}")
            continue
        
        try:
            print("\n🔄 分析视频...")
            
            # 显示原始信息
            original_info = get_video_info(input_video)
            has_audio = original_info.get('has_audio', False)
            duration = original_info.get('duration', 0)
            
            print(f"原始信息: {duration:.1f}秒, 音频: {'有' if has_audio else '无'}")
            
            if not has_audio:
                print("⚠️  该视频没有音频轨道")
                continue
            
            # 询问操作类型
            print("\n选择操作:")
            print("1. 复制视频（保留音频）")
            print("2. 增强音频质量")
            print("3. 提取音频文件")
            print("4. 全部操作")
            
            choice = input("请选择 (1-4): ").strip()
            
            if choice == "1":
                # 复制视频
                result = copy_video_preserve_audio(input_video, preserve_quality=True)
                print(f"✅ 复制完成: {result}")
                
            elif choice == "2":
                # 增强音频
                boost = input("音频增益倍数 (默认1.5): ").strip()
                try:
                    boost = float(boost) if boost else 1.5
                except ValueError:
                    boost = 1.5
                
                result = enhance_video_audio(input_video, audio_boost=boost)
                print(f"✅ 音频增强完成: {result}")
                
            elif choice == "3":
                # 提取音频
                format_choice = input("音频格式 (mp3/wav/aac, 默认mp3): ").strip()
                audio_format = format_choice if format_choice in ['mp3', 'wav', 'aac'] else 'mp3'
                
                result = extract_audio_from_video(input_video, audio_format=audio_format)
                print(f"✅ 音频提取完成: {result}")
                
            elif choice == "4":
                # 全部操作
                print("🔄 执行全部操作...")
                
                # 复制视频
                copied = copy_video_preserve_audio(input_video)
                print(f"✅ 视频复制: {copied}")
                
                # 提取音频
                audio = extract_audio_from_video(input_video)
                print(f"✅ 音频提取: {audio}")
                
                # 增强音频
                enhanced = enhance_video_audio(input_video, audio_boost=1.2)
                print(f"✅ 音频增强: {enhanced}")
                
            else:
                print("❌ 无效选择")
                continue
            
            # 验证结果
            if choice in ["1", "2", "4"]:
                print("\n🔍 验证音频保留...")
                result_info = get_video_info(result if choice != "4" else copied)
                result_has_audio = result_info.get('has_audio', False)
                
                if result_has_audio:
                    print("✅ 音频成功保留")
                else:
                    print("❌ 音频可能丢失")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
        
        print("\n" + "-" * 40 + "\n")


def main():
    """主函数"""
    
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
            duration = original_info.get('duration', 0)
            
            print(f"原始信息: {duration:.1f}秒, 音频: {'有' if has_audio else '无'}")
            
            if not has_audio:
                print("⚠️  该视频没有音频轨道")
                return 0
            
            # 复制视频并保留音频
            output_file = copy_video_preserve_audio(input_file, preserve_quality=True)
            
            # 验证结果
            output_info = get_video_info(output_file)
            output_has_audio = output_info.get('has_audio', False)
            output_duration = output_info.get('duration', 0)
            
            print(f"输出信息: {output_duration:.1f}秒, 音频: {'有' if output_has_audio else '无'}")
            
            if output_has_audio:
                print("✅ 音频成功保留")
            else:
                print("❌ 音频可能丢失")
            
            print(f"✅ 完成: {output_file}")
            
            return 0
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return 1
    
    else:
        # 交互模式
        print("使用方法:")
        print("1. 命令行: python simple_audio_demo.py video.mp4")
        print("2. 交互式: 直接运行脚本")
        print("3. 演示模式: 修改脚本中的文件路径")
        print()
        
        choice = input("选择模式 (1=演示, 2=交互, Enter=退出): ").strip()
        
        if choice == "1":
            simple_audio_demo()
        elif choice == "2":
            interactive_audio_demo()
        else:
            print("👋 再见！")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
