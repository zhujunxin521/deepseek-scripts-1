#!/data/data/com.termux/files/usr/bin/env python3
import json
import os
from collections import deque

class HistoryManager:
    def __init__(self, history_file=None, max_history=100):
        self.history_file = history_file or os.path.join(os.path.dirname(__file__), "history.jsonl")
        self.max_history = max_history
        self.messages = deque(self.load_history(), maxlen=self.max_history)

    def load_history(self):
        """加载对话历史"""
        messages = []
        if os.path.isfile(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    for ln in f:
                        if ln.strip():
                            messages.append(json.loads(ln))
            except Exception as e:
                print(f"⚠️ 加载历史文件出错: {e}")
                print("使用空历史")
        return messages

    def save_message(self, role, content):
        """保存单条消息"""
        message = {"role": role, "content": content}
        self.messages.append(message)
        try:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(message, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"⚠️ 保存历史消息出错: {e}")
            return False

    def clear_history(self):
        """清空对话历史"""
        self.messages.clear()
        try:
            open(self.history_file, "w").close()
            print("✅ 已清空历史")
            return True
        except Exception as e:
            print(f"⚠️ 清空历史文件出错: {e}")
            return False

    def get_messages(self):
        """获取历史消息列表"""
        return list(self.messages)