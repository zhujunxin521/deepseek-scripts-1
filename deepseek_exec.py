#!/data/data/com.termux/files/usr/bin/env python3
import sys
import argparse
import readline
import asyncio

# 导入自定义模块
from config import ConfigManager
from history import HistoryManager
from code_executor import CodeExecutor
from api_client import ApiClient

# 解析命令行参数
parser = argparse.ArgumentParser(
    description='DeepSeek 对话工具 - 多轮流式对话+代码执行',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='''
使用示例:
  python deepseek_exec.py                       # 正常启动，使用配置文件或提示输入API Key
  python deepseek_exec.py --api-key your_api_key  # 指定API Key启动
  python deepseek_exec.py --model deepseek-chat  # 指定模型
  python deepseek_exec.py --config custom_config.json  # 使用自定义配置文件
  python deepseek_exec.py --no-cache             # 禁用缓存
  python deepseek_exec.py --async                # 使用异步模式

交互命令:
  /new    - 清空对话历史
  /help   - 显示帮助信息
  exit/quit - 退出程序

代码执行:
  使用 ```python-run 代码块``` 自动执行代码
  使用 ```python-ask 代码块``` 询问是否执行代码
    '''
)
parser.add_argument('--api-key', help='DeepSeek API Key，优先级高于配置文件')
parser.add_argument('--model', default='deepseek-chat', help='模型名称 (默认: deepseek-chat)')
parser.add_argument('--config', default=None, help='配置文件路径 (默认: .deepseek_config.json)')
parser.add_argument('--no-cache', action='store_true', help='禁用响应缓存')
parser.add_argument('--async', action='store_true', dest='use_async', help='使用异步模式')
args = parser.parse_args()

# 初始化配置管理器
config_manager = ConfigManager(args.config)

# 获取 API Key 和模型
api_key = config_manager.get_api_key(args.api_key)
model = config_manager.get_model(args.model)
url = config_manager.get('url')
timeout = config_manager.get('timeout')

# 初始化历史管理器
max_history = config_manager.get('max_history')
history_manager = HistoryManager(max_history=max_history)

# 初始化API客户端
api_client = ApiClient(api_key, model, url, timeout)

# 初始化代码执行器
code_executor = CodeExecutor()

def show_help():
    print("\n📖 DeepSeek 对话工具帮助信息\n")
    print("可用命令:\n")
    print("  /new                - 清空对话历史")
    print("  /help               - 显示此帮助信息")
    print("  exit/quit           - 退出程序\n")
    print("代码执行:\n")
    print("  ```python-run 代码块```  - 自动执行代码")
    print("  ```python-ask 代码块```  - 询问是否执行代码\n")
    print("命令行参数:\n")
    print("  --api-key  your_api_key  - 指定DeepSeek API Key")
    print("  --model    model_name    - 指定模型名称 (默认: deepseek-chat)")
    print("  --config   config_path   - 指定配置文件路径")
    print("  --no-cache             - 禁用响应缓存")
    print("  --async                - 使用异步模式\n")
    print("配置文件:\n")
    print("  默认路径: .deepseek_config.json")
    print("  格式参考: .deepseek_config.example.json\n")

print("\n✅ 已开启多轮流式对话+代码执行\n提示：代码块用 ```python-run 或 ```python-ask 包裹\n输入 /new 清空历史，/help 查看帮助，exit 退出\n")

# 定义异步主循环
async def async_main_loop():
    while True:
        try:
            user = await asyncio.to_thread(input, "\n你：")
            user = user.strip()
            if user.lower() in {"exit", "quit"}:
                print("\n👋 再见！")
                break
            if user == "/new":
                history_manager.clear_history()
                continue
            if user == "/help":
                show_help()
                continue
            print("DeepSeek：", end="")
            messages = history_manager.get_messages()
            reply, usage = await api_client.async_chat_stream(messages, user, use_cache=not args.no_cache)
            history_manager.save_message("user", user)
            history_manager.save_message("assistant", reply)

            # 处理代码块（同步执行）
            code_executor.process_code_blocks(reply)

            if usage:
                in_t, out_t, cost = api_client.calculate_cost(usage)
                print(f"\n📊 本回合：输入 {in_t} tokens，输出 {out_t} tokens，约 ${cost:.6f}")
            else:
                print("\n⚠️ 未能获取 token 用量")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break

# 定义同步主循环
def sync_main_loop():
    while True:
        try:
            user = input("\n你：").strip()
            if user.lower() in {"exit", "quit"}:
                print("\n👋 再见！")
                break
            if user == "/new":
                history_manager.clear_history()
                continue
            if user == "/help":
                show_help()
                continue
            print("DeepSeek：", end="")
            messages = history_manager.get_messages()
            reply, usage = api_client.chat_stream(messages, user, use_cache=not args.no_cache)
            history_manager.save_message("user", user)
            history_manager.save_message("assistant", reply)

            code_executor.process_code_blocks(reply)

            if usage:
                in_t, out_t, cost = api_client.calculate_cost(usage)
                print(f"\n📊 本回合：输入 {in_t} tokens，输出 {out_t} tokens，约 ${cost:.6f}")
            else:
                print("\n⚠️ 未能获取 token 用量")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break

# 启动主循环
try:
    if args.use_async:
        print("🚀 使用异步模式运行...")
        asyncio.run(async_main_loop())
    else:
        sync_main_loop()
finally:
    # 确保关闭API客户端资源
    api_client.close()
    print("🔌 已释放资源")