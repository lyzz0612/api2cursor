## 上下文

api2cursor 作为 Cursor 的 OpenAI Base URL 替代入口，将请求桥接到真实上游（中转站）。变更后：**上游基址与密钥均不再使用环境变量**（`PROXY_TARGET_URL` / `PROXY_API_KEY` 全部移除）。基址仅来自管理面板持久化配置；密钥**只**从请求头读取（模型映射 `api_key` 可覆盖特定模型），**不**保留管理面板全局 `proxy_api_key` 回退。`settings.resolve_model()` 将解析后的 `api_key` 交给 `utils/http.py` 构建上游请求头。

参考脚本 `forward-cursor.py` 将客户端请求中的 `authorization` 等头原样转发给上游，使「Cursor 里填的密钥」即上游凭证。用户希望：**中转站 URL 在管理端配置**，**上游密钥从 Cursor 发往本服务的 HTTP 头读取**，避免在服务端重复维护一份上游密钥。

部署约定：**不配置 `ACCESS_API_KEY`**。因此 `Authorization`（及按需支持的其它客户端鉴权头）仅用于解析并转发给上游的密钥材料，不与「访问本代理服务」的鉴权争用同一头。

## 目标 / 非目标

**目标：**

- 全局「中转站基础 URL」**仅**来自管理面板持久化配置，部署**不**配置 `PROXY_TARGET_URL`（代码与文档均不以环境变量作为基址来源或回退）。
- 上游调用使用的密钥材料**优先**从当前 HTTP 请求中解析（与 `forward-cursor.py` 一致，核心使用 `Authorization` Bearer token；可按后端类型映射为现有 `build_*_headers` 所需形式）。
- 当请求头未提供可用密钥时，唯一回退：模型映射中该模型的 `api_key`；若映射也无密钥则上游请求无凭证（**不**存在全局密钥回退）。

**非目标：**

- 不改变各协议适配器（CC / Responses / Messages / Gemini）的 URL 路径拼装规则，除非为传递密钥所必需的最小改动。
- 不在此变更中实现完整的通用「头白名单透传」；若需与参考脚本对齐，可仅对鉴权相关头做最小扩展并记入任务。

## 决策

1. **上游密钥来源优先级**  
   - 第一优先：从当前请求头解析出的 Bearer token。  
   - 第二优先：该 Cursor 模型在映射表中的 `api_key`（用于特定模型需要不同密钥的场景）。  
   - **无全局回退**：不再有管理面板全局 `proxy_api_key` 或环境变量 `PROXY_API_KEY`。

2. **从请求头解析密钥**  
   - 从 `Authorization: Bearer <token>` 提取 `<token>` 作为密钥材料（与 OpenAI 客户端行为一致）。  
   - 若未来需兼容无 `Bearer ` 前缀的裸 token，可在实现层与 `build_*_headers` 约定统一入口。  
   - 部署**肯定不配置 `ACCESS_API_KEY`**，上述 Bearer token **始终**作为上游密钥材料（README 中应说明 Cursor 填写的 API Key 即中转站凭证，与 `forward-cursor.py` 一致）。

3. **管理面板**  
   - 「中转站地址」为必关注字段语义，且为全局上游基址的**唯一**来源。  
   - **移除**全局「中转站 API Key」字段（或标注废弃），密钥只从请求头读取。  
   - `PROXY_TARGET_URL`、`PROXY_API_KEY` 环境变量及管理面板 `proxy_api_key` **均移除**。

4. **替代方案（已否决）**  
   - 仅依赖管理面板密钥、不从请求读取：不满足用户需求。  
   - 保留管理面板全局密钥作为回退：增加多源冲突风险，且违背「密钥只在客户端维护」的设计意图。

## 风险 / 权衡

- **[风险] 密钥出现在访问日志或调试日志中** → 缓解：保持现有日志脱敏策略；verbose 日志中对 `Authorization` / 上游头做截断或省略。  
- **[权衡] 无全局密钥回退** → 请求头不带密钥且模型映射无覆盖时上游调用会失败；属预期行为，在文档与错误信息中明示。

## 迁移计划

1. 部署新版本前：在 README 中说明密钥与 URL 来源变更；原先依赖 `PROXY_TARGET_URL` / `PROXY_API_KEY` / 管理面板全局密钥的部署须改为在管理面板配置地址、在 Cursor 侧填写真实密钥。  
2. 回滚：恢复上一版本镜像/代码；`settings.json` 向后兼容，无需强制迁移数据。

## 开放问题

- `x-api-key`（Anthropic 客户端常用）是否需与 `Authorization` 二选一解析为上游密钥，以实现与多客户端兼容（可在实现阶段用最小规则确定）。
