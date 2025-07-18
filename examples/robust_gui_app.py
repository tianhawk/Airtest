#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健壮的 GUI 应用程序示例，包含适当的异常处理和优雅退出机制
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import signal
import threading
import traceback
from pathlib import Path


class RobustGUIApp:
    """健壮的 GUI 应用程序基类"""
    
    def __init__(self):
        self.root = None
        self.is_running = False
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """设置信号处理器，优雅处理中断"""
        def signal_handler(signum, frame):
            print(f"\n收到信号 {signum}，正在优雅退出...")
            self.graceful_exit()
        
        # 处理 Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, signal_handler)
        
        # 在 Windows 上处理 Ctrl+Break (SIGBREAK)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, signal_handler)
    
    def create_gui(self):
        """创建 GUI 界面"""
        try:
            self.root = tk.Tk()
            self.root.title("健壮的 GUI 应用程序")
            self.root.geometry("800x600")
            
            # 设置窗口关闭事件处理
            self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
            # 创建主界面
            self.create_widgets()
            
            # 绑定键盘事件
            self.root.bind('<Control-c>', lambda e: self.graceful_exit())
            self.root.bind('<Escape>', lambda e: self.graceful_exit())
            
            return True
            
        except Exception as e:
            print(f"创建 GUI 失败: {e}")
            traceback.print_exc()
            return False
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="视频处理工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件选择
        ttk.Label(main_frame, text="输入视频:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_var, width=50)
        input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # 输出文件选择
        ttk.Label(main_frame, text="输出视频:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        options_frame.columnconfigure(0, weight=1)
        
        self.keep_duration_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保留原视频时长", 
                       variable=self.keep_duration_var).grid(row=0, column=0, sticky=tk.W)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        # 处理按钮
        self.process_button = ttk.Button(button_frame, text="开始处理", 
                                       command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="停止", 
                                    command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        ttk.Button(button_frame, text="退出", command=self.graceful_exit).pack(side=tk.LEFT, padx=5)
        
        # 日志文本框
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择输入视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
            # 自动生成输出文件名
            if not self.output_var.get():
                input_path = Path(filename)
                output_path = input_path.parent / f"{input_path.stem}_no_audio{input_path.suffix}"
                self.output_var.set(str(output_path))
    
    def browse_output_file(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="选择输出视频文件",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 文件", "*.mp4"),
                ("AVI 文件", "*.avi"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.output_var.set(filename)
    
    def log_message(self, message):
        """添加日志消息"""
        if self.root and self.log_text:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
    
    def update_status(self, status):
        """更新状态"""
        if self.root and self.status_var:
            self.status_var.set(status)
            self.root.update_idletasks()
    
    def update_progress(self, value):
        """更新进度条"""
        if self.root and self.progress_var:
            self.progress_var.set(value)
            self.root.update_idletasks()
    
    def start_processing(self):
        """开始处理"""
        input_file = self.input_var.get().strip()
        output_file = self.output_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入视频文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请指定输出视频文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        # 禁用处理按钮，启用停止按钮
        self.process_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 在新线程中处理视频
        self.processing_thread = threading.Thread(
            target=self.process_video_thread,
            args=(input_file, output_file),
            daemon=True
        )
        self.processing_thread.start()
    
    def process_video_thread(self, input_file, output_file):
        """在后台线程中处理视频"""
        try:
            self.update_status("正在处理视频...")
            self.log_message(f"开始处理: {input_file}")
            
            # 这里调用视频处理功能
            # 注意：需要先安装 Airtest 的视频处理功能
            try:
                from airtest.core.api import remove_video_audio
                
                # 模拟进度更新
                for i in range(0, 101, 10):
                    if not self.is_running:
                        break
                    self.update_progress(i)
                    self.log_message(f"处理进度: {i}%")
                    threading.Event().wait(0.5)  # 模拟处理时间
                
                if self.is_running:
                    # 实际的视频处理
                    result = remove_video_audio(
                        input_file, 
                        output_file, 
                        keep_duration=self.keep_duration_var.get()
                    )
                    
                    self.update_progress(100)
                    self.log_message(f"处理完成: {result}")
                    self.update_status("处理完成")
                    
                    # 在主线程中显示完成消息
                    self.root.after(0, lambda: messagebox.showinfo("完成", "视频处理完成！"))
                else:
                    self.log_message("处理已取消")
                    self.update_status("已取消")
                    
            except ImportError:
                self.log_message("错误: 未找到视频处理模块，请确保已安装相关依赖")
                self.update_status("错误: 缺少依赖")
            except Exception as e:
                self.log_message(f"处理错误: {e}")
                self.update_status("处理失败")
                
        except Exception as e:
            self.log_message(f"线程错误: {e}")
            traceback.print_exc()
        finally:
            # 重新启用按钮
            if self.root:
                self.root.after(0, self.reset_buttons)
    
    def reset_buttons(self):
        """重置按钮状态"""
        self.process_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_progress(0)
    
    def stop_processing(self):
        """停止处理"""
        self.is_running = False
        self.log_message("正在停止处理...")
        self.update_status("正在停止...")
    
    def on_window_close(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.graceful_exit()
    
    def graceful_exit(self):
        """优雅退出"""
        print("正在优雅退出...")
        self.is_running = False
        
        # 等待处理线程结束
        if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
            print("等待处理线程结束...")
            self.processing_thread.join(timeout=2)
        
        # 销毁 GUI
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        
        print("程序已退出")
        sys.exit(0)
    
    def run(self):
        """运行应用程序"""
        try:
            if not self.create_gui():
                return False
            
            self.is_running = True
            print("启动 GUI 应用程序...")
            print("按 Ctrl+C 或 Esc 键可以优雅退出")
            
            # 启动主循环
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n收到键盘中断，正在退出...")
            self.graceful_exit()
        except Exception as e:
            print(f"应用程序错误: {e}")
            traceback.print_exc()
            return False
        finally:
            self.is_running = False
        
        return True


def main():
    """主函数"""
    try:
        app = RobustGUIApp()
        success = app.run()
        return 0 if success else 1
    except Exception as e:
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
