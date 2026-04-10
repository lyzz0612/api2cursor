"""启动入口

用法: python start.py
"""

import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)

from config import Config
from app import create_app


def main():
    """加载应用并以 Waitress 方式启动代理服务。"""
    app = create_app()
    import settings
    print(f'代理服务启动于 0.0.0.0:{Config.PROXY_PORT}')
    target = settings.get_url()
    print(f'上游地址: {target or "(未配置，请在管理面板设置)"}')
    print(f'管理面板: http://localhost:{Config.PROXY_PORT}/admin')

    from waitress import serve
    serve(
        app,
        host='0.0.0.0',
        port=Config.PROXY_PORT,
        channel_timeout=Config.API_TIMEOUT,
        send_bytes=1,
    )


if __name__ == '__main__':
    main()
