## 1. 请求头解析与优先级

- [x] 1.1 实现从 Flask `request` 解析上游密钥材料的函数：以 `Authorization: Bearer` 为主（部署约定不配置 `ACCESS_API_KEY`），并处理空值与格式错误；可选支持 `x-api-key` 等与 `build_*_headers` 对齐的补充规则。
- [x] 1.2 实现「请求头密钥 → 模型映射 `api_key`」合并逻辑，**不**回退到管理面板全局 `proxy_api_key` 或环境变量；仅在请求头**无法**提供材料时使用映射中的密钥。
- [x] 1.3 调整全局上游基址解析：`get_url()`（或等价逻辑）**仅**使用持久化 `proxy_target_url`，移除对 `Config.PROXY_TARGET_URL` 的回退；在基址缺失且映射未覆盖时返回可诊断错误。
- [x] 1.4 移除 `get_key()` 全局密钥回退（或使其不再被数据面路由调用）；管理面板全局 `proxy_api_key` 字段废弃或删除。

## 2. 路由与上下文

- [x] 2.1 扩展 `build_route_context`（或等价入口）使其接收 `request`，将合并后的上游密钥写入 `RouteContext.api_key`。
- [x] 2.2 更新 `routes/chat.py`、`routes/responses.py` 中所有 `build_route_context` 调用处传入 `request`。
- [x] 2.3 更新 `routes/messages.py` 中直接使用 `resolve_model` 的路径，改为与上述一致的上游密钥解析与回退行为。

## 3. 管理与文档

- [x] 3.1 管理面板与 `routes/admin.py`：移除全局「中转站 API Key」字段（或标注废弃不参与路由）；保留「中转站地址」为唯一全局配置。
- [x] 3.2 更新 `README.md`、`.env.example`：移除或废弃 `PROXY_TARGET_URL` 与 `PROXY_API_KEY` 文档与示例；说明中转站 URL 仅在管理面板配置；说明 Cursor 填写的 API Key 经 `Authorization` 作为上游凭证。

## 4. 验证

- [x] 4.1 为密钥解析添加单元测试（覆盖：仅有请求头、仅有映射 `api_key`、二者皆无等）。
- [x] 4.2 手动或脚本冒烟：请求携带 `Authorization: Bearer` 时上游收到正确凭证；无头且无映射时上游无凭证（不回退全局）。
- [x] 4.3 持久化中转站地址为空且映射未覆盖 `target_url` 时，返回明确错误且不读取 `PROXY_TARGET_URL`。
- [x] 4.4 确认管理面板全局 `proxy_api_key` 与环境变量 `PROXY_API_KEY` 均不再参与密钥解析。
