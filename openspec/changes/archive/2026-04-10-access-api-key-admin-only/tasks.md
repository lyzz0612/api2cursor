## 1. 配置与启动

- [x] 1.1 在 `config.py` 或应用入口（如 `create_app`）中实现：`ACCESS_API_KEY` 去除首尾空白后必须非空，否则记录错误并终止启动。
- [x] 1.2 更新 `README.md` 中 `ACCESS_API_KEY` 说明：改为必填，并删除「留空不启用」类表述；补充与 Cursor/代理请求无需携带该密钥的说明。

## 2. 全局中间件与路由

- [x] 2.1 从 `app.py` 移除（或改写为无操作）基于 `ACCESS_API_KEY` 的全局 `before_request` 鉴权，确保 `/v1/models`、转发路由及 `/health` 不因该变量返回 401。
- [x] 2.2 在 `routes/admin.py` 中更新 `_check_auth`：删除「未配置 `ACCESS_API_KEY` 则放行」分支，始终按请求头与配置比对。
- [x] 2.3 在 `routes/admin.py` 中更新 `admin_login`：删除「未配置则 `ok: True`」分支；未配置情况不应再出现（由启动校验保证）。

## 3. 部署与测试

- [x] 3.1 更新 `docker-compose.yml`（及任何示例 env）中 `ACCESS_API_KEY` 注释与示例，标明必填。
- [x] 3.2 调整 `tests/test_upstream_key.py`（及新增用例）：在测试环境中设置非空 `ACCESS_API_KEY`；必要时增加断言：非管理路径不因访问密钥缺失返回 401、管理 API 在错误密钥时返回 401。
