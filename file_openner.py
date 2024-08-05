"""
文件打开者，专门为打开文件
"""

import os
import subprocess


def open_file(full_path_file: str):
    """
    打开文件
    """
    if os.path.exists(full_path_file):
        # if full_path_file.endswith(".py"):
        #     # 用pycharm打开python文件
        #     pycharm_path = r"D:\Program Files\JetBrains\PyCharm Community Edition 2023.3.3\bin"
        #     subprocess.run([pycharm_path, full_path_file])
        #     return
        print("当前系统：", os.name)
        if os.name == "win32" or os.name == "nt":
            os.startfile(full_path_file)
        elif os.name == "posix":
            # macOS 系统
            os.system(f"open {full_path_file}")
        else:
            # linux 系统
            os.system(f"xdg-open {full_path_file}")
    else:
        print("文件不存在！")
