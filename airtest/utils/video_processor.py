#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""视频处理工具模块，提供视频编辑功能如去除音频等."""

import os
import sys
import subprocess
import tempfile
from airtest.utils.logger import get_logger

LOGGING = get_logger(__name__)


class VideoProcessor:
    """视频处理器，提供视频编辑功能"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """查找系统中的ffmpeg可执行文件"""
        # 常见的ffmpeg路径
        possible_paths = [
            'ffmpeg',  # 系统PATH中
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            'C:\\ffmpeg\\bin\\ffmpeg.exe',  # Windows常见路径
        ]
        
        for path in possible_paths:
            try:
                # 测试ffmpeg是否可用
                subprocess.run([path, '-version'], 
                             capture_output=True, 
                             check=True, 
                             timeout=10)
                LOGGING.info(f"Found ffmpeg at: {path}")
                return path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        # 如果没找到ffmpeg，尝试使用moviepy作为备选方案
        try:
            import moviepy.editor as mp
            LOGGING.info("Using moviepy as video processor")
            return None  # 表示使用moviepy
        except ImportError:
            raise RuntimeError("Neither ffmpeg nor moviepy is available. Please install one of them.")
    
    def remove_audio(self, input_path, output_path=None, keep_duration=True):
        """
        去除视频中的音频，保留视频时长
        
        Args:
            input_path (str): 输入视频文件路径
            output_path (str, optional): 输出视频文件路径，如果为None则自动生成
            keep_duration (bool): 是否保留原视频时长，默认为True
            
        Returns:
            str: 输出文件路径
            
        Raises:
            FileNotFoundError: 输入文件不存在
            RuntimeError: 视频处理失败
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")
        
        # 如果没有指定输出路径，自动生成
        if output_path is None:
            name, ext = os.path.splitext(input_path)
            output_path = f"{name}_no_audio{ext}"
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if self.ffmpeg_path:
            return self._remove_audio_with_ffmpeg(input_path, output_path, keep_duration)
        else:
            return self._remove_audio_with_moviepy(input_path, output_path, keep_duration)
    
    def _remove_audio_with_ffmpeg(self, input_path, output_path, keep_duration):
        """使用ffmpeg去除音频"""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'copy',  # 复制视频流，不重新编码
                '-an',  # 去除音频流
                '-y',   # 覆盖输出文件
                output_path
            ]
            
            LOGGING.info(f"Running ffmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            LOGGING.info(f"Successfully removed audio from {input_path} -> {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Video processing timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to process video with ffmpeg: {str(e)}")
    
    def _remove_audio_with_moviepy(self, input_path, output_path, keep_duration):
        """使用moviepy去除音频"""
        try:
            import moviepy.editor as mp
            
            LOGGING.info(f"Processing video with moviepy: {input_path}")
            
            # 加载视频
            video = mp.VideoFileClip(input_path)
            
            # 去除音频
            video_no_audio = video.without_audio()
            
            # 如果需要保持时长，确保输出视频时长与原视频相同
            if keep_duration:
                original_duration = video.duration
                if video_no_audio.duration != original_duration:
                    # 如果时长不同，调整到原始时长
                    video_no_audio = video_no_audio.set_duration(original_duration)
            
            # 写入输出文件
            video_no_audio.write_videofile(
                output_path,
                codec='libx264',
                audio=False,
                verbose=False,
                logger=None
            )
            
            # 清理资源
            video.close()
            video_no_audio.close()
            
            LOGGING.info(f"Successfully removed audio from {input_path} -> {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("moviepy is not installed. Please install it with: pip install moviepy")
        except Exception as e:
            raise RuntimeError(f"Failed to process video with moviepy: {str(e)}")
    
    def get_video_info(self, video_path):
        """
        获取视频信息
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            dict: 包含视频信息的字典
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if self.ffmpeg_path:
            return self._get_video_info_with_ffmpeg(video_path)
        else:
            return self._get_video_info_with_moviepy(video_path)
    
    def _get_video_info_with_ffmpeg(self, video_path):
        """使用ffmpeg获取视频信息"""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # ffmpeg将信息输出到stderr
            info_text = result.stderr
            
            # 解析基本信息
            info = {
                'path': video_path,
                'has_audio': 'Audio:' in info_text,
                'has_video': 'Video:' in info_text
            }
            
            # 尝试提取时长
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', info_text)
            if duration_match:
                hours, minutes, seconds = duration_match.groups()
                total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                info['duration'] = total_seconds
            
            return info
            
        except Exception as e:
            LOGGING.warning(f"Failed to get video info with ffmpeg: {str(e)}")
            return {'path': video_path, 'error': str(e)}
    
    def _get_video_info_with_moviepy(self, video_path):
        """使用moviepy获取视频信息"""
        try:
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(video_path)
            
            info = {
                'path': video_path,
                'duration': video.duration,
                'has_video': True,
                'has_audio': video.audio is not None,
                'fps': video.fps,
                'size': video.size
            }
            
            video.close()
            return info
            
        except Exception as e:
            LOGGING.warning(f"Failed to get video info with moviepy: {str(e)}")
            return {'path': video_path, 'error': str(e)}

    def copy_video_with_audio(self, input_path, output_path=None, preserve_quality=True):
        """
        复制视频并完整保留音频

        Args:
            input_path (str): 输入视频文件路径
            output_path (str, optional): 输出视频文件路径
            preserve_quality (bool): 是否保持原始质量

        Returns:
            str: 输出文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")

        if output_path is None:
            name, ext = os.path.splitext(input_path)
            output_path = f"{name}_with_audio{ext}"

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if self.ffmpeg_path:
            return self._copy_video_with_ffmpeg(input_path, output_path, preserve_quality)
        else:
            return self._copy_video_with_moviepy(input_path, output_path, preserve_quality)

    def _copy_video_with_ffmpeg(self, input_path, output_path, preserve_quality):
        """使用 FFmpeg 复制视频并保留音频"""
        try:
            if preserve_quality:
                # 无损复制所有流
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-c', 'copy',  # 复制所有流，不重新编码
                    '-y',
                    output_path
                ]
            else:
                # 重新编码但保持高质量
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-b:v', '5000k',
                    '-b:a', '192k',
                    '-y',
                    output_path
                ]

            LOGGING.info(f"Copying video with audio using ffmpeg: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            LOGGING.info(f"Successfully copied video with audio: {input_path} -> {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Video copying timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to copy video with ffmpeg: {str(e)}")

    def _copy_video_with_moviepy(self, input_path, output_path, preserve_quality):
        """使用 MoviePy 复制视频并保留音频"""
        try:
            import moviepy.editor as mp

            LOGGING.info(f"Copying video with audio using moviepy: {input_path}")

            # 加载视频（包含音频）
            video = mp.VideoFileClip(input_path)

            # 确保音频被保留
            if video.audio is None:
                LOGGING.warning("Input video has no audio track")

            # 写入输出文件，保留音频
            if preserve_quality:
                video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
            else:
                video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate='3000k',
                    audio_bitrate='128k',
                    verbose=False,
                    logger=None
                )

            # 清理资源
            video.close()

            LOGGING.info(f"Successfully copied video with audio: {input_path} -> {output_path}")
            return output_path

        except ImportError:
            raise RuntimeError("moviepy is not installed. Please install it with: pip install moviepy")
        except Exception as e:
            raise RuntimeError(f"Failed to copy video with moviepy: {str(e)}")

    def enhance_video_audio(self, input_path, output_path=None, audio_boost=1.0, video_quality='high'):
        """
        增强视频音频质量

        Args:
            input_path (str): 输入视频文件路径
            output_path (str, optional): 输出视频文件路径
            audio_boost (float): 音频增益倍数
            video_quality (str): 视频质量级别

        Returns:
            str: 输出文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")

        if output_path is None:
            name, ext = os.path.splitext(input_path)
            output_path = f"{name}_enhanced{ext}"

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg is required for audio enhancement")

        return self._enhance_with_ffmpeg(input_path, output_path, audio_boost, video_quality)

    def _enhance_with_ffmpeg(self, input_path, output_path, audio_boost, video_quality):
        """使用 FFmpeg 增强视频音频"""
        try:
            # 视频质量设置
            quality_settings = {
                'high': {'crf': '18', 'preset': 'slow'},
                'medium': {'crf': '23', 'preset': 'medium'},
                'low': {'crf': '28', 'preset': 'fast'}
            }

            settings = quality_settings.get(video_quality, quality_settings['high'])

            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',
                '-crf', settings['crf'],
                '-preset', settings['preset'],
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',
                output_path
            ]

            # 添加音频增益滤镜
            if audio_boost != 1.0:
                volume_filter = f"volume={audio_boost}"
                cmd.insert(-2, '-af')
                cmd.insert(-2, volume_filter)

            LOGGING.info(f"Enhancing video audio: boost={audio_boost}x, quality={video_quality}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            LOGGING.info(f"Successfully enhanced video audio: {input_path} -> {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Video enhancement timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to enhance video with ffmpeg: {str(e)}")

    def extract_audio(self, input_path, output_path=None, audio_format='mp3'):
        """
        从视频中提取音频文件

        Args:
            input_path (str): 输入视频文件路径
            output_path (str, optional): 输出音频文件路径
            audio_format (str): 音频格式

        Returns:
            str: 输出音频文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")

        if output_path is None:
            name = os.path.splitext(input_path)[0]
            output_path = f"{name}_audio.{audio_format}"

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if self.ffmpeg_path:
            return self._extract_audio_with_ffmpeg(input_path, output_path, audio_format)
        else:
            return self._extract_audio_with_moviepy(input_path, output_path, audio_format)

    def _extract_audio_with_ffmpeg(self, input_path, output_path, audio_format):
        """使用 FFmpeg 提取音频"""
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
                self.ffmpeg_path,
                '-i', input_path,
                '-vn',  # 不包含视频
                '-acodec', codec,
                '-ab', '192k',
                '-y',
                output_path
            ]

            LOGGING.info(f"Extracting audio as {audio_format.upper()}: {input_path}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            LOGGING.info(f"Successfully extracted audio: {input_path} -> {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio extraction timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio with ffmpeg: {str(e)}")

    def _extract_audio_with_moviepy(self, input_path, output_path, audio_format):
        """使用 MoviePy 提取音频"""
        try:
            import moviepy.editor as mp

            LOGGING.info(f"Extracting audio with moviepy: {input_path}")

            # 加载视频
            video = mp.VideoFileClip(input_path)

            if video.audio is None:
                raise RuntimeError("Input video has no audio track")

            # 提取音频
            audio = video.audio
            audio.write_audiofile(output_path, verbose=False, logger=None)

            # 清理资源
            audio.close()
            video.close()

            LOGGING.info(f"Successfully extracted audio: {input_path} -> {output_path}")
            return output_path

        except ImportError:
            raise RuntimeError("moviepy is not installed. Please install it with: pip install moviepy")
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio with moviepy: {str(e)}")


# 全局视频处理器实例
_video_processor = None


def get_video_processor():
    """获取全局视频处理器实例"""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor


def remove_video_audio(input_path, output_path=None, keep_duration=True):
    """
    便捷函数：去除视频音频
    
    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出视频文件路径
        keep_duration (bool): 是否保留原视频时长
        
    Returns:
        str: 输出文件路径
    """
    processor = get_video_processor()
    return processor.remove_audio(input_path, output_path, keep_duration)


def get_video_info(video_path):
    """
    便捷函数：获取视频信息

    Args:
        video_path (str): 视频文件路径

    Returns:
        dict: 视频信息
    """
    processor = get_video_processor()
    return processor.get_video_info(video_path)


def copy_video_preserve_audio(input_path, output_path=None, preserve_quality=True):
    """
    复制视频并完整保留音频

    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出视频文件路径
        preserve_quality (bool): 是否保持原始质量

    Returns:
        str: 输出文件路径
    """
    processor = get_video_processor()
    return processor.copy_video_with_audio(input_path, output_path, preserve_quality)


def enhance_video_audio(input_path, output_path=None, audio_boost=1.0, video_quality='high'):
    """
    增强视频音频质量

    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出视频文件路径
        audio_boost (float): 音频增益倍数
        video_quality (str): 视频质量级别

    Returns:
        str: 输出文件路径
    """
    processor = get_video_processor()
    return processor.enhance_video_audio(input_path, output_path, audio_boost, video_quality)


def extract_audio_from_video(input_path, output_path=None, audio_format='mp3'):
    """
    从视频中提取音频文件

    Args:
        input_path (str): 输入视频文件路径
        output_path (str, optional): 输出音频文件路径
        audio_format (str): 音频格式

    Returns:
        str: 输出音频文件路径
    """
    processor = get_video_processor()
    return processor.extract_audio(input_path, output_path, audio_format)
