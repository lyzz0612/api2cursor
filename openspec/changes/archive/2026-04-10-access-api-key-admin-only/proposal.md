## 为什么

当前在配置 `ACCESS_API_KEY` 后，全局 `before_request` 会对除健康检查与管理面板路径外的**所有**请求做鉴权，与「上游密钥仅经 `Authorization` 转发」的部署约定冲突，也使 `/v1/models` 等面向 Cursor 的接口被迫携带访问密钥。需要将访问密钥**仅**用于保护管理端能力，并明确 **`ACCESS_API_KEY` 为必填**，避免误部署为「无密钥开放管理」或「双重要求密钥」的模糊状态。

## 变更内容

- **移除** 应用级全局鉴权中间件中对代理/API 路由（含 `/v1/models`、转发相关路径等）的 `ACCESS_API_KEY` 校验；这些接口**不再**检查该环境变量。
- **保留并收紧** 管理相关能力对 `ACCESS_API_KEY` 的依赖：`/admin` 页面、管理静态资源、`/api/admin/*` 等仍通过既有逻辑（含 `_check_auth`、登录接口）使用该密钥；在「密钥必填」前提下，**删除**「未配置密钥则管理 API 放行」的分支行为。
- **BREAKING**：`ACCESS_API_KEY` 由可选变为**必填**。未设置时进程应拒绝启动（或等价失败 fast），并在文档与部署示例中写明；不再支持「留空 = 不启用全局鉴权且管理端无密钥保护」的旧模式。

## 功能 (Capabilities)

### 新增功能

- `access-api-key-admin-only`: 定义 `ACCESS_API_KEY` 为必填，且仅用于管理端（管理面板 UI、管理 API）的访问控制；健康检查与代理/模型列表等面向业务的接口不依据该变量做鉴权。

### 修改功能

- （无独立既有规范目录于项目根 `openspec/specs/`；本变更以新增能力规范为主。）

## 影响

- `app.py`：移除或改写全局 `check_access`，使非管理路径不校验 `ACCESS_API_KEY`；可增加启动时对 `ACCESS_API_KEY` 非空的校验。
- `routes/admin.py`：`_check_auth`、`admin_login` 等与「未配置密钥」相关的分支需与「必填」语义一致。
- `config.py`、`README.md`、`docker-compose.yml` 注释：更新环境变量说明与示例。
- 依赖 `ACCESS_API_KEY` 可选性的测试需调整。
