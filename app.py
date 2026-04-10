"""Flask 应用工厂

创建并配置 Flask 应用：
  - 注册所有路由蓝图
  - 设置 JSON 错误处理器（避免返回 HTML）
  - 校验必填环境变量 `ACCESS_API_KEY`（仅用于管理端，见 routes.admin）
"""

import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS

import settings
from config import Config
from routes import register_routes

logger = logging.getLogger(__name__)


def create_app():
    """创建并配置 Flask 应用实例。

    这里统一完成跨路由共享的初始化逻辑，包括配置加载、跨域、错误处理、
    管理端所需密钥校验、健康检查以及蓝图注册。
    """
    access_key = (os.getenv('ACCESS_API_KEY') or '').strip()
    if not access_key:
        logger.critical(
            '环境变量 ACCESS_API_KEY 必须设置为非空字符串（用于 /admin 与 /api/admin 访问控制）'
        )
        raise SystemExit(1)
    Config.ACCESS_API_KEY = access_key

    app = Flask(__name__)
    CORS(app)
    settings.load()

    # ─── JSON 错误处理器 ──────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        """将未匹配到的路径统一转换为 JSON 404 响应。"""
        return jsonify({'error': {'message': '未找到', 'type': 'not_found'}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """将不支持的请求方法统一转换为 JSON 405 响应。"""
        return jsonify({'error': {'message': '方法不允许', 'type': 'method_not_allowed'}}), 405

    @app.errorhandler(500)
    def internal_error(e):
        """将未捕获的服务端异常统一包装为 JSON 500 响应。"""
        return jsonify({'error': {'message': '服务器内部错误', 'type': 'server_error'}}), 500

    # ─── 健康检查 ────────────────────────────────

    @app.route('/health', methods=['GET'])
    def health():
        """返回服务健康状态和当前生效的上游地址。"""
        return jsonify({'status': 'ok', 'target': settings.get_url()})

    # ─── 注册路由蓝图 ────────────────────────────

    register_routes(app)

    return app
