#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from airtest.utils.video_processor import VideoProcessor, remove_video_audio, get_video_info
from airtest.core.api import remove_video_audio as api_remove_video_audio
from airtest.core.api import get_video_info as api_get_video_info


class TestVideoProcessor(unittest.TestCase):
    """视频处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.test_video_path = os.path.join(self.test_dir, "test_video.mp4")
        self.output_video_path = os.path.join(self.test_dir, "output_video.mp4")
        
        # 创建一个模拟的视频文件
        with open(self.test_video_path, 'wb') as f:
            f.write(b'fake video content')
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_video_processor_init(self):
        """测试视频处理器初始化"""
        processor = VideoProcessor()
        self.assertIsInstance(processor, VideoProcessor)
    
    @patch('subprocess.run')
    def test_find_ffmpeg_success(self, mock_run):
        """测试成功找到ffmpeg"""
        mock_run.return_value = MagicMock(returncode=0)
        processor = VideoProcessor()
        self.assertIsNotNone(processor.ffmpeg_path)
    
    @patch('subprocess.run')
    @patch('moviepy.editor')
    def test_find_ffmpeg_fallback_to_moviepy(self, mock_moviepy, mock_run):
        """测试ffmpeg不可用时回退到moviepy"""
        # 模拟ffmpeg不可用
        mock_run.side_effect = FileNotFoundError()
        # 模拟moviepy可用
        mock_moviepy.VideoFileClip = MagicMock()
        
        processor = VideoProcessor()
        self.assertIsNone(processor.ffmpeg_path)
    
    @patch('subprocess.run')
    def test_find_ffmpeg_no_tools_available(self, mock_run):
        """测试既没有ffmpeg也没有moviepy时抛出异常"""
        # 模拟ffmpeg不可用
        mock_run.side_effect = FileNotFoundError()
        
        # 模拟moviepy不可用
        with patch.dict('sys.modules', {'moviepy.editor': None}):
            with self.assertRaises(RuntimeError):
                VideoProcessor()
    
    def test_remove_audio_file_not_found(self):
        """测试输入文件不存在时抛出异常"""
        processor = VideoProcessor()
        with self.assertRaises(FileNotFoundError):
            processor.remove_audio("nonexistent_file.mp4")
    
    @patch('subprocess.run')
    def test_remove_audio_with_ffmpeg_success(self, mock_run):
        """测试使用ffmpeg成功去除音频"""
        # 模拟ffmpeg可用
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        processor = VideoProcessor()
        processor.ffmpeg_path = 'ffmpeg'  # 强制使用ffmpeg
        
        result = processor.remove_audio(self.test_video_path, self.output_video_path)
        self.assertEqual(result, self.output_video_path)
        mock_run.assert_called()
    
    @patch('subprocess.run')
    def test_remove_audio_with_ffmpeg_failure(self, mock_run):
        """测试ffmpeg处理失败"""
        # 模拟ffmpeg失败
        mock_run.return_value = MagicMock(returncode=1, stderr="Error message")
        
        processor = VideoProcessor()
        processor.ffmpeg_path = 'ffmpeg'
        
        with self.assertRaises(RuntimeError):
            processor.remove_audio(self.test_video_path, self.output_video_path)
    
    @patch('moviepy.editor.VideoFileClip')
    def test_remove_audio_with_moviepy_success(self, mock_video_clip):
        """测试使用moviepy成功去除音频"""
        # 模拟moviepy视频对象
        mock_video = MagicMock()
        mock_video.duration = 10.0
        mock_video_no_audio = MagicMock()
        mock_video_no_audio.duration = 10.0
        mock_video.without_audio.return_value = mock_video_no_audio
        mock_video_clip.return_value = mock_video
        
        processor = VideoProcessor()
        processor.ffmpeg_path = None  # 强制使用moviepy
        
        result = processor.remove_audio(self.test_video_path, self.output_video_path)
        self.assertEqual(result, self.output_video_path)
        mock_video.without_audio.assert_called_once()
        mock_video_no_audio.write_videofile.assert_called_once()
    
    def test_auto_generate_output_path(self):
        """测试自动生成输出路径"""
        processor = VideoProcessor()
        
        # 模拟处理方法
        with patch.object(processor, '_remove_audio_with_moviepy') as mock_method:
            mock_method.return_value = "test_output.mp4"
            processor.ffmpeg_path = None
            
            result = processor.remove_audio(self.test_video_path)
            
            # 检查是否调用了处理方法，并且输出路径包含"_no_audio"
            mock_method.assert_called_once()
            args = mock_method.call_args[0]
            self.assertIn("_no_audio", args[1])
    
    @patch('subprocess.run')
    def test_get_video_info_with_ffmpeg(self, mock_run):
        """测试使用ffmpeg获取视频信息"""
        # 模拟ffmpeg输出
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr="Duration: 00:01:30.50, start: 0.000000, bitrate: 1000 kb/s\nVideo: h264\nAudio: aac"
        )
        
        processor = VideoProcessor()
        processor.ffmpeg_path = 'ffmpeg'
        
        info = processor.get_video_info(self.test_video_path)
        
        self.assertIn('path', info)
        self.assertIn('has_audio', info)
        self.assertIn('has_video', info)
        self.assertIn('duration', info)
        self.assertTrue(info['has_audio'])
        self.assertTrue(info['has_video'])
        self.assertAlmostEqual(info['duration'], 90.5, places=1)
    
    @patch('moviepy.editor.VideoFileClip')
    def test_get_video_info_with_moviepy(self, mock_video_clip):
        """测试使用moviepy获取视频信息"""
        # 模拟moviepy视频对象
        mock_video = MagicMock()
        mock_video.duration = 120.0
        mock_video.fps = 30.0
        mock_video.size = (1920, 1080)
        mock_video.audio = MagicMock()  # 有音频
        mock_video_clip.return_value = mock_video
        
        processor = VideoProcessor()
        processor.ffmpeg_path = None
        
        info = processor.get_video_info(self.test_video_path)
        
        self.assertEqual(info['duration'], 120.0)
        self.assertEqual(info['fps'], 30.0)
        self.assertEqual(info['size'], (1920, 1080))
        self.assertTrue(info['has_audio'])
        self.assertTrue(info['has_video'])
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        with patch('airtest.utils.video_processor.get_video_processor') as mock_get_processor:
            mock_processor = MagicMock()
            mock_get_processor.return_value = mock_processor
            
            # 测试remove_video_audio函数
            remove_video_audio("input.mp4", "output.mp4")
            mock_processor.remove_audio.assert_called_with("input.mp4", "output.mp4", True)
            
            # 测试get_video_info函数
            get_video_info("video.mp4")
            mock_processor.get_video_info.assert_called_with("video.mp4")
    
    def test_api_functions(self):
        """测试API函数"""
        with patch('airtest.utils.video_processor.remove_video_audio') as mock_remove:
            with patch('airtest.utils.video_processor.get_video_info') as mock_info:
                # 测试API函数
                api_remove_video_audio("input.mp4", "output.mp4")
                mock_remove.assert_called_with("input.mp4", "output.mp4", True)
                
                api_get_video_info("video.mp4")
                mock_info.assert_called_with("video.mp4")


class TestVideoProcessorIntegration(unittest.TestCase):
    """视频处理器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_output_directory(self):
        """测试自动创建输出目录"""
        processor = VideoProcessor()
        
        # 创建测试输入文件
        input_path = os.path.join(self.test_dir, "input.mp4")
        with open(input_path, 'wb') as f:
            f.write(b'fake video')
        
        # 指定不存在目录中的输出文件
        output_dir = os.path.join(self.test_dir, "new_dir")
        output_path = os.path.join(output_dir, "output.mp4")
        
        # 模拟处理方法
        with patch.object(processor, '_remove_audio_with_moviepy') as mock_method:
            mock_method.return_value = output_path
            processor.ffmpeg_path = None
            
            processor.remove_audio(input_path, output_path)
            
            # 检查目录是否被创建
            self.assertTrue(os.path.exists(output_dir))


if __name__ == '__main__':
    unittest.main()
