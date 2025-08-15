#!/data/data/com.termux/files/usr/bin/env python3
import json
import requests
import hashlib
import asyncio
import aiohttp
import os
import time
from functools import lru_cache

class ApiClient:
    def __init__(self, api_key, model, url, timeout=60, cache_dir=None):
        self.api_key = api_key
        self.model = model
        self.url = url
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.in_price = 0.00001
        self.out_price = 0.00002
        
        # 初始化连接池
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 缓存配置
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 异步客户端会话
        self.async_session = None

    def _generate_cache_key(self, messages, prompt):
        """生成缓存键"""
        cache_input = json.dumps({
            "messages": messages,
            "prompt": prompt,
            "model": self.model
        }, sort_keys=True)
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cached_response(self, cache_key):
        """获取缓存的响应"""
        cache_path = os.path.join(self.cache_dir, cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 读取缓存出错: {e}")
        return None

    def _save_response_to_cache(self, cache_key, response, usage):
        """保存响应到缓存"""
        cache_path = os.path.join(self.cache_dir, cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "response": response,
                    "usage": usage,
                    "timestamp": time.time()
                }, f, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存缓存出错: {e}")

    def chat_stream(self, messages, prompt, use_cache=True):
        """流式聊天接口（带缓存）"""
        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(messages, prompt)
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                print("📤 从缓存获取响应...")
                print(cached_data["response"])
                return cached_data["response"], cached_data["usage"]

        payload = {
            "model": self.model,
            "messages": messages + [{"role": "user", "content": prompt}],
            "stream": True
        }
        usage = None
        reply = ""
        try:
            # 使用连接池发送请求
            resp = self.session.post(self.url, json=payload, stream=True, timeout=self.timeout)
            for ln in resp.iter_lines(decode_unicode=True):
                if ln.startswith("data: "):
                    data = ln[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            print(delta["content"], end="", flush=True)
                            reply += delta["content"]
                        if "usage" in chunk:
                            usage = chunk["usage"]
                    except Exception as e:
                        print(f"⚠️ 解析响应出错: {e}")
        except Exception as e:
            print(f"⚠️ API请求出错: {e}")
        
        # 保存到缓存
        if use_cache and reply:
            self._save_response_to_cache(cache_key, reply, usage)

        return reply, usage

    async def async_chat_stream(self, messages, prompt, use_cache=True):
        """异步流式聊天接口"""
        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(messages, prompt)
            cached_data = self._get_cached_response(cache_key)
            if cached_data:
                print("📤 从缓存获取响应...")
                print(cached_data["response"])
                return cached_data["response"], cached_data["usage"]

        # 初始化异步会话
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession(headers=self.headers)

        payload = {
            "model": self.model,
            "messages": messages + [{"role": "user", "content": prompt}],
            "stream": True
        }
        usage = None
        reply = ""
        try:
            async with self.async_session.post(self.url, json=payload, timeout=self.timeout) as resp:
                async for ln in resp.content:
                    line = ln.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                print(delta["content"], end="", flush=True)
                                reply += delta["content"]
                            if "usage" in chunk:
                                usage = chunk["usage"]
                        except Exception as e:
                            print(f"⚠️ 解析响应出错: {e}")
        except Exception as e:
            print(f"⚠️ API请求出错: {e}")
        
        # 保存到缓存
        if use_cache and reply:
            self._save_response_to_cache(cache_key, reply, usage)

        return reply, usage

    def calculate_cost(self, usage):
        """计算API调用成本"""
        if not usage:
            return 0, 0, 0
        in_t = usage.get("prompt_tokens", 0)
        out_t = usage.get("completion_tokens", 0)
        cost = in_t * self.in_price + out_t * self.out_price
        return in_t, out_t, cost

    def close(self):
        """关闭会话资源"""
        if self.session:
            self.session.close()
        if self.async_session and not self.async_session.closed:
            asyncio.run(self.async_session.close())