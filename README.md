# DeepSeek 对话工具

这是一个基于 DeepSeek API 的对话工具，支持多轮流式对话和代码执行功能。

## 功能特点
- 多轮流式对话
- 代码执行功能（支持自动执行和询问执行两种模式）
- 对话历史记录
- 响应缓存
- 异步支持

## 使用说明
1. 安装依赖: `pip install -r requirements.txt`
2. 配置 API Key: 复制 `.deepseek_config.example.json` 为 `.deepseek_config.json` 并填写 API Key
3. 运行程序: `python deepseek_exec.py`

## 代码执行
使用 ```python-run 代码块``` 自动执行代码
使用 ```python-ask 代码块``` 询问是否执行代码

## 命令行参数
- `--api-key`: 指定 DeepSeek API Key
- `--model`: 指定模型名称 (默认: deepseek-chat)
- `--config`: 指定配置文件路径
- `--no-cache`: 禁用响应缓存
- `--async`: 使用异步模式