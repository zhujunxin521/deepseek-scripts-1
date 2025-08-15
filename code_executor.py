#!/data/data/com.termux/files/usr/bin/env python3
import os
import re
import subprocess
import sys

class CodeExecutor:
    def __init__(self):
        self.tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def extract_code_blocks(self, text):
        """提取文本中的代码块"""
        pattern = r'```python-(run|ask)\s*\n(.*?)```'
        return re.findall(pattern, text, re.DOTALL)

    def run_code(self, code):
        """执行Python代码"""
        tmp_file = os.path.join(self.tmp_dir, "_tmp.py")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            result = subprocess.run([sys.executable, tmp_file], capture_output=True, text=True, timeout=15)
            out = result.stdout + result.stderr
            print("\n📟 执行结果：\n" + out)
            return out
        except subprocess.TimeoutExpired:
            print("\n⏰ 代码运行超时（>15s）")
            return ""
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    def process_code_blocks(self, text):
        """处理文本中的代码块"""
        code_blocks = self.extract_code_blocks(text)
        results = []
        for mode, code in code_blocks:
            code = code.strip()
            if mode == "run":
                results.append(self.run_code(code))
            elif mode == "ask":
                if input("\n🤔 是否立即运行这段代码？(y/n) ").lower() == "y":
                    results.append(self.run_code(code))
                else:
                    print("⏸️ 已跳过执行")
                    results.append("代码已跳过执行")
        return results