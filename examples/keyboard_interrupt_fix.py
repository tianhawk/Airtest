#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复 KeyboardInterrupt 错误的通用解决方案
适用于 tkinter GUI 应用程序
"""

import tkinter as tk
import signal
import sys
import atexit
import threading
from functools import wraps


class KeyboardInterruptHandler:
    """键盘中断处理器"""
    
    def __init__(self):
        self.original_sigint = None
        self.root = None
        self.is_shutting_down = False
        
    def setup(self, root):
        """设置中断处理"""
        self.root = root
        
        # 保存原始的 SIGINT 处理器
        self.original_sigint = signal.signal(signal.SIGINT, self._signal_handler)
        
        # 设置窗口关闭协议
        if hasattr(root, 'protocol'):
            root.protocol("WM_DELETE_WINDOW", self.graceful_shutdown)
        
        # 注册退出处理器
        atexit.register(self.cleanup)
        
        # 绑定键盘快捷键
        if hasattr(root, 'bind_all'):
            root.bind_all('<Control-c>', lambda e: self.graceful_shutdown())
            root.bind_all('<Control-q>', lambda e: self.graceful_shutdown())
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，正在安全退出...")
        self.graceful_shutdown()
    
    def graceful_shutdown(self):
        """优雅关闭"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        print("正在安全关闭应用程序...")
        
        try:
            if self.root:
                # 停止主循环
                self.root.quit()
                # 销毁窗口
                self.root.destroy()
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
        
        # 退出程序
        sys.exit(0)
    
    def cleanup(self):
        """清理资源"""
        if self.original_sigint:
            signal.signal(signal.SIGINT, self.original_sigint)


def safe_mainloop(root, handler=None):
    """安全的主循环包装器"""
    if handler is None:
        handler = KeyboardInterruptHandler()
    
    try:
        handler.setup(root)
        print("启动应用程序... (按 Ctrl+C 安全退出)")
        root.mainloop()
    except KeyboardInterrupt:
        print("\n收到键盘中断")
        handler.graceful_shutdown()
    except Exception as e:
        print(f"主循环错误: {e}")
        handler.graceful_shutdown()
    finally:
        handler.cleanup()


def keyboard_interrupt_safe(func):
    """装饰器：使函数对键盘中断安全"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print(f"\n函数 {func.__name__} 被键盘中断")
            sys.exit(0)
        except Exception as e:
            print(f"函数 {func.__name__} 出错: {e}")
            raise
    return wrapper


class SafeThread(threading.Thread):
    """安全的线程类，处理键盘中断"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True  # 设置为守护线程
        self._stop_event = threading.Event()
    
    def stop(self):
        """停止线程"""
        self._stop_event.set()
    
    def stopped(self):
        """检查是否应该停止"""
        return self._stop_event.is_set()
    
    def run(self):
        """重写 run 方法，添加异常处理"""
        try:
            super().run()
        except KeyboardInterrupt:
            print(f"线程 {self.name} 收到键盘中断")
        except Exception as e:
            print(f"线程 {self.name} 出错: {e}")


# 使用示例和修复模板
EXAMPLE_FIX = '''
# 原始代码（可能出现 KeyboardInterrupt）:
# root = tk.Tk()
# root.mainloop()

# 修复后的代码:
import tkinter as tk
from keyboard_interrupt_fix import safe_mainloop, KeyboardInterruptHandler

root = tk.Tk()
root.title("安全的应用程序")

# 方法1: 使用安全的主循环
safe_mainloop(root)

# 方法2: 手动设置处理器
handler = KeyboardInterruptHandler()
handler.setup(root)
try:
    root.mainloop()
except KeyboardInterrupt:
    handler.graceful_shutdown()
'''


def create_safe_app_template():
    """创建安全应用程序模板"""
    template = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加当前目录到路径（如果需要导入本地模块）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keyboard_interrupt_fix import safe_mainloop, KeyboardInterruptHandler

def create_gui():
    """创建 GUI 界面"""
    root = tk.Tk()
    root.title("安全的应用程序")
    root.geometry("600x400")
    
    # 创建界面组件
    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    ttk.Label(frame, text="这是一个安全的 tkinter 应用程序").grid(row=0, column=0, pady=10)
    ttk.Button(frame, text="退出", command=root.quit).grid(row=1, column=0, pady=10)
    
    # 配置网格权重
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    return root

def main():
    """主函数"""
    try:
        root = create_gui()
        
        # 使用安全的主循环
        safe_mainloop(root)
        
    except Exception as e:
        print(f"应用程序错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    return template


def fix_existing_app(file_path):
    """修复现有应用程序的建议"""
    suggestions = f"""
修复 {file_path} 的建议：

1. 在文件开头添加导入：
   from keyboard_interrupt_fix import safe_mainloop, KeyboardInterruptHandler

2. 替换 root.mainloop() 为：
   safe_mainloop(root)

3. 或者手动添加异常处理：
   try:
       root.mainloop()
   except KeyboardInterrupt:
       print("程序被用户中断")
       root.quit()
       root.destroy()
       sys.exit(0)

4. 如果有后台线程，使用 SafeThread 替代 threading.Thread

5. 为长时间运行的函数添加 @keyboard_interrupt_safe 装饰器

6. 在窗口创建后立即设置：
   handler = KeyboardInterruptHandler()
   handler.setup(root)
"""
    return suggestions


if __name__ == "__main__":
    print("键盘中断修复工具")
    print("=" * 50)
    
    # 显示使用示例
    print("使用示例:")
    print(EXAMPLE_FIX)
    
    # 显示修复建议
    print("\n修复建议:")
    print(fix_existing_app("ab_frame_merger.py"))
    
    # 创建示例应用程序
    print("\n创建安全应用程序模板...")
    template = create_safe_app_template()
    
    try:
        with open("safe_app_template.py", "w", encoding="utf-8") as f:
            f.write(template)
        print("已创建 safe_app_template.py")
    except Exception as e:
        print(f"创建模板文件失败: {e}")
