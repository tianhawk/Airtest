#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单演示：保留视频时长
去除音频但保持原始视频时间长度
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airtest.core.api import remove_video_audio, get_video_info


def simple_demo():
    """简单演示如何保留视频时长"""
    
    print("🎬 视频时长保留演示")
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
        print()
        
        # 2. 去除音频，保留时长
        print("🔇 开始处理...")
        print("   - 去除音频轨道")
        print("   - 保留原始时长")
        
        # 关键调用：keep_duration=True 确保保留时长
        output_video = remove_video_audio(
            input_video,
            keep_duration=True  # 这是关键参数！
        )
        
        print(f"✅ 处理完成!")
        print(f"   输出文件: {output_video}")
        print()
        
        # 3. 验证结果
        print("🔍 验证结果:")
        output_info = get_video_info(output_video)
        output_duration = output_info.get('duration', 0)
        output_has_audio = output_info.get('has_audio', False)
        
        print(f"   文件: {output_video}")
        print(f"   时长: {output_duration:.2f} 秒")
        print(f"   音频: {'有' if output_has_audio else '无'}")
        print()
        
        # 4. 对比结果
        duration_diff = abs(original_duration - output_duration)
        
        print("📊 对比结果:")
        print(f"   原始时长: {original_duration:.2f} 秒")
        print(f"   输出时长: {output_duration:.2f} 秒")
        print(f"   时长差异: {duration_diff:.3f} 秒")
        
        if duration_diff < 0.1:
            print("   ✅ 时长保留成功！")
        else:
            print("   ⚠️  时长有微小差异（正常现象）")
        
        if not output_has_audio:
            print("   ✅ 音频移除成功！")
        else:
            print("   ⚠️  音频可能未完全移除")
        
        print()
        print("🎉 演示完成！")
        print(f"您现在有一个无音频但保持原始时长的视频: {output_video}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        print("请检查:")
        print("1. 视频文件是否存在且可读")
        print("2. 是否安装了 moviepy: pip install moviepy")
        print("3. 输出目录是否有写入权限")


def interactive_demo():
    """交互式演示"""
    
    print("🎬 交互式视频时长保留工具")
    print("=" * 40)
    
    # 获取用户输入
    while True:
        input_video = input("请输入视频文件路径 (或按 Enter 退出): ").strip()
        
        if not input_video:
            print("👋 再见！")
            break
        
        if not os.path.exists(input_video):
            print(f"❌ 文件不存在: {input_video}")
            continue
        
        # 询问输出路径
        output_video = input("输出文件路径 (按 Enter 自动生成): ").strip()
        if not output_video:
            output_video = None
        
        try:
            print("\n🔄 开始处理...")
            
            # 显示原始信息
            original_info = get_video_info(input_video)
            print(f"原始时长: {original_info.get('duration', 0):.2f} 秒")
            
            # 处理视频
            result = remove_video_audio(
                input_video,
                output_video,
                keep_duration=True
            )
            
            # 显示结果
            output_info = get_video_info(result)
            print(f"输出时长: {output_info.get('duration', 0):.2f} 秒")
            print(f"✅ 完成: {result}")
            
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
            original_duration = original_info.get('duration', 0)
            print(f"原始时长: {original_duration:.2f} 秒")
            
            # 处理视频
            output_file = remove_video_audio(input_file, keep_duration=True)
            
            # 验证结果
            output_info = get_video_info(output_file)
            output_duration = output_info.get('duration', 0)
            print(f"输出时长: {output_duration:.2f} 秒")
            
            duration_diff = abs(original_duration - output_duration)
            print(f"时长差异: {duration_diff:.3f} 秒")
            
            print(f"✅ 完成: {output_file}")
            
            return 0
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return 1
    
    else:
        # 交互模式
        print("使用方法:")
        print("1. 命令行: python simple_duration_demo.py video.mp4")
        print("2. 交互式: 直接运行脚本")
        print("3. 演示模式: 修改脚本中的文件路径")
        print()
        
        choice = input("选择模式 (1=演示, 2=交互, Enter=退出): ").strip()
        
        if choice == "1":
            simple_demo()
        elif choice == "2":
            interactive_demo()
        else:
            print("👋 再见！")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
