#!/data/data/com.termux/files/usr/bin/env python3
import json
import os

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '.deepseek_config.json')
        self.default_config = {
            'api_key': '',
            'model': 'deepseek-chat',
            'url': 'https://api.deepseek.com/v1/chat/completions',
            'timeout': 60,
            'max_history': 100
        }
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                return {**self.default_config, **config}
            except Exception as e:
                print(f"⚠️ 加载配置文件出错: {e}")
                print("使用默认配置")
        return self.default_config.copy()

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 保存配置文件出错: {e}")
            return False

    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save_config()

    def get_api_key(self, cli_api_key=None):
        """获取API Key (优先级: 命令行参数 > 配置文件 > 输入)"""
        api_key = cli_api_key or self.get('api_key')
        if not api_key:
            api_key = input("请输入 DeepSeek API Key：").strip()
            if not api_key:
                print("❌ API Key 不能为空！")
                exit(1)
            self.set('api_key', api_key)
        return api_key

    def get_model(self, cli_model=None):
        """获取模型名称 (优先级: 命令行参数 > 配置文件 > 默认值)"""
        model = cli_model or self.get('model')
        if model != self.get('model'):
            self.set('model', model)
        return model