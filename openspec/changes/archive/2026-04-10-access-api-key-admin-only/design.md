## 上下文

当前 `app.py` 中 `before_request` 在配置了 `ACCESS_API_KEY` 时，对除 `/health`、`/admin`、`/static/`、`/api/admin` 前缀外的路径统一校验 `Bearer` 或 `x-api-key` 是否等于该值。代理与 `/v1/models` 等路由因此被纳入「访问本服务」的鉴权，与上游转发使用同一请求头（`Authorization`）产生耦合。`routes/admin.py` 中 `_check_auth` 在「未配置密钥」时放行管理 API，与「生产环境必须保护管理」的常见需求不一致。

## 目标 / 非目标

**目标：**

- `ACCESS_API_KEY` **必须**在启动时配置（非空）；未配置则进程拒绝启动并给出明确错误信息。
- **仅**管理相关路径依赖该密钥进行访问控制：`/admin`、`/static/`、`/api/admin/*`（与现有管理蓝图一致）。
- **禁止**在应用级中间件中，对非上述路径（含转发 API、`/v1/models`、`/health` 等）依据 `ACCESS_API_KEY` 做校验。

**非目标：**

- 不改变上游密钥从 `Authorization` / 模型映射解析并转发的既有规则（与 `openspec` 归档中上游中继行为一致的部分）。
- 不引入除 `ACCESS_API_KEY` 以外的第二套管理登录机制（仍沿用 Bearer / `x-api-key` 与登录 POST body 的约定）。

## 决策

1. **移除全局 `before_request` 中的 `ACCESS_API_KEY` 校验**  
   理由：鉴权与「管理 API 内的 `_check_auth`」重复，且误伤非管理路由。删除后，非管理路径不再因该环境变量返回 401。

2. **启动时校验**  
   在 `create_app()` 或 `settings.load()` 之后、`register_routes` 之前，若 `ACCESS_API_KEY` 为空或仅空白，则 `raise` 或 `sys.exit(1)` 并记录日志。  
   替代方案：允许空密钥但文档警告 —— 与用户「必须要配」冲突，故不采用。

3. **管理端逻辑**  
   - `_check_auth()`：因密钥恒存在，**必须**始终比对请求头与 `CONFIG.ACCESS_API_KEY`；移除「未配置则返回 None（放行）」分支。  
   - `admin_login`：移除「未配置则 `ok: True`」分支；登录成功条件仍为 body `key` 与配置一致。  
   理由：与「必填」一致，避免「无密钥开放管理」窗口。

4. **健康检查**  
   `/health` 保持无 `ACCESS_API_KEY` 校验（便于编排探活）。

## 风险 / 权衡

- **[风险]** 本地开发必须设置 `ACCESS_API_KEY`，增加一步配置。  
  **缓解**：在 `README` 与 `.env.example`（若存在）中给出示例值；错误信息指明变量名。

- **[风险]** 与历史文档「留空 = 不启用」表述冲突。  
  **缓解**：同步更新 `README`、`docker-compose` 注释与变更说明，**BREAKING** 已写入提案。

- **[权衡]** 管理面板静态页 `/admin` 可无需 Bearer 打开 HTML，敏感操作仍依赖 API 的 `_check_auth` —— 与当前模型一致，不扩大本变更范围。

## 迁移计划

1. 现有部署在设置 `ACCESS_API_KEY` 时，若仅用于保护管理端，去掉全局中间件后，Cursor 侧**无需**再为代理请求额外带访问密钥，行为更宽松。  
2. 现有部署**未**设置 `ACCESS_API_KEY` 的，升级后**必须**设置该变量，否则无法启动 —— 需在发布说明中突出。  
3. 回滚：恢复旧版 `app.py`/`admin.py` 与配置说明（不推荐长期保留）。

## 开放问题

- 无。
