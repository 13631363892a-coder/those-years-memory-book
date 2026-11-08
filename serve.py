# -*- coding: utf-8 -*-
"""本地静态服务器：启动相册并自动打开浏览器。无需安装任何依赖。"""
import os, sys, threading, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PORT = int(os.environ.get("ALBUM_PORT", "8000"))


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 保持控制台干净

    def end_headers(self):
        # 本地相册无需缓存，方便改文案后刷新即生效
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}/"
    print("=" * 58)
    print("  那些年，我们一起走过 · 初二—初三 青春纪念册")
    print("=" * 58)
    print(f"  本地地址：{url}")
    print("  按 Ctrl+C 关闭服务器")
    print("=" * 58)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已关闭。")
    except OSError as e:
        print(f"\n端口 {PORT} 可能被占用：{e}")
        print("可设置环境变量 ALBUM_PORT=8001 后重试。")
        sys.exit(1)
