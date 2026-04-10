## 为什么

当前全局上游基址与密钥常与环境变量或管理面板持久化配置混用。运维上希望**中转站地址仅在管理面板配置**（不写环境变量），而**访问上游的真实密钥与 Cursor 发出的请求一致**（与 `forward-cursor.py` 一样透传 `Authorization` 等头），避免在服务端重复保存一份上游密钥并降低轮换成本。

## 变更内容

- 明确**上游中转站基础地址**仅以管理面板持久化 `settings` 为准；**不**再通过环境变量（如 `PROXY_TARGET_URL`）配置或回退。
- **发往上游的 API 密钥**只从 Cursor 发往本服务的请求头（`Authorization: Bearer`）读取，不在服务端任何位置存储全局密钥。模型映射中的「自定义密钥」仍可覆盖特定模型的上游凭证。
- **不**引入「未配置 `ACCESS_API_KEY` 时才从请求头读密钥」的分支：本变更面向**肯定不配置** `ACCESS_API_KEY` 的部署，`Authorization` 始终用于上游凭证解析。

## 功能 (Capabilities)

### 新增功能

- `upstream-relay-configuration`: 定义全局上游基址**仅**由管理配置（持久化）驱动、不用环境变量；上游密钥**只**从请求头读取（模型映射 `api_key` 可覆盖）、**移除**管理面板全局密钥与环境变量回退；**部署约定不配置 `ACCESS_API_KEY`**。

### 修改功能

- （无独立既有规范目录；行为变更落在上述新能力规范中，并与现有 `settings` / `routes` 实现对齐。）

## 影响

- `settings.py`、`routes/common.py` 及解析 `RouteContext` 的调用链（如 `chat.py`、`responses.py`、`messages.py`）需能传入「当前请求的鉴权头信息」。
- 管理面板 `admin.html` / `admin.js` 与 `routes/admin.py`：移除全局「中转站 API Key」字段（或标注废弃）。
- `README.md` 与 `.env.example`：说明 Cursor 侧 API Key 与上游 URL 均在管理面板侧约定；同步删减或标注废弃 `PROXY_TARGET_URL` 与 `PROXY_API_KEY` 相关说明。
