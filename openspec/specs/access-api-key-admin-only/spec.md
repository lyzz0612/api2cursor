# ACCESS_API_KEY 管理端鉴权

### 需求:ACCESS_API_KEY 为必填配置

系统必须在进程启动时读取环境变量 `ACCESS_API_KEY`；若该值为空或仅包含空白字符，**必须**拒绝启动并输出明确错误信息（包含变量名）。**禁止**以「未配置则跳过鉴权」的方式运行服务。

#### 场景:未设置访问密钥时启动失败

- **当** 启动应用且环境变量 `ACCESS_API_KEY` 未设置或为空字符串
- **那么** 进程必须退出或抛出致命错误，且不得监听业务端口

#### 场景:已设置非空访问密钥时启动成功

- **当** 启动应用且 `ACCESS_API_KEY` 为非空字符串
- **那么** 应用必须正常完成初始化（除其它无关错误外）

### 需求:非管理接口禁止依据 ACCESS_API_KEY 鉴权

系统**禁止**在 Flask `before_request` 或等价全局钩子中，对路径不属于管理相关前缀的请求校验 `ACCESS_API_KEY`。非管理接口包括但不限于：健康检查、OpenAI/Anthropic/Gemini 等代理路由、`GET /v1/models` 以及任何非 `/admin`、`/static/`、`/api/admin` 管理 API 的路径。

#### 场景:代理请求无需携带访问密钥

- **当** 客户端请求某条转发 API 且未提供与 `ACCESS_API_KEY` 匹配的 `Authorization` 或 `x-api-key`（或仅携带用于上游的 `Authorization`）
- **那么** 系统不得仅因「访问密钥不匹配」对该请求返回 401；上游凭证与转发逻辑按既有规则处理

#### 场景:模型列表接口无需访问密钥

- **当** 客户端对 `GET /v1/models` 发起请求且未提供与 `ACCESS_API_KEY` 匹配的凭据
- **那么** 系统不得仅因 `ACCESS_API_KEY` 对该请求返回 401

### 需求:管理相关接口必须使用 ACCESS_API_KEY

对于管理面板页面与静态资源路径（`/admin`、`/admin/`、`/static/` 前缀），以及管理 REST API（`/api/admin` 前缀），系统必须继续使用 `ACCESS_API_KEY` 作为访问控制依据：对需要鉴权的管理 API，请求头中的 `Bearer` token 或 `x-api-key` 必须与配置值一致；登录接口 `POST /api/admin/login` 的请求体密钥字段必须与配置值一致。**禁止**在「未配置 `ACCESS_API_KEY`」时放行管理写操作或敏感读操作。

#### 场景:管理 API 缺少或错误密钥时拒绝

- **当** 客户端请求某条需鉴权的管理 API（例如 `GET /api/admin/settings`），且 `Bearer`/`x-api-key` 与 `ACCESS_API_KEY` 不一致或缺失
- **那么** 系统必须返回 401 或等价未授权响应

#### 场景:登录密钥错误时拒绝

- **当** 客户端调用 `POST /api/admin/login` 且 body 中的密钥与 `ACCESS_API_KEY` 不一致
- **那么** 系统必须返回表示登录失败的结果且 HTTP 状态为 401
