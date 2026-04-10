## 上下文

仓库根目录已有基于 `python:3.13-alpine` 的多阶段 `Dockerfile`，`docker-compose.yml` 当前仅使用 `build: .` 本地构建。目标是在 GitHub 上自动化构建并发布镜像，使部署方可直接 `docker pull`，同时保留本地开发用 Compose 构建路径。

约束：优先使用 GitHub 原生集成（Actions + GHCR），避免引入额外付费服务；工作流须仅在有权限的仓库内使用默认 `GITHUB_TOKEN` 推送到 GHCR（需正确权限与 `permissions`）。

## 目标 / 非目标

**目标：**

- 在推送 Git 标签（如 `v*`）或主分支时构建并推送镜像到 `ghcr.io/<owner>/<repo>`（或项目约定的镜像名）。
- 为镜像打上语义化标签（如 `v1.2.3`）及可预测的浮动标签（如 `latest` 仅用于主分支/默认分支策略，需在决策中固定）。
- 更新 `docker-compose.yml`：提供使用已发布镜像的示例（`image:`），与现有 `build:` 开发路径并存或注释说明二选一。

**非目标：**

- 不修改应用 Python 代码或运行时行为。
- 不强制要求多架构镜像（若未特别需要，可先 `linux/amd64`；若需 arm 可在后续变更扩展 `buildx`）。
- 不实现私有仓库除 GHCR 以外的发布目标（可后续扩展）。

## 决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 注册表 | GitHub Container Registry (GHCR) | 与 GitHub 同源，权限与 `GITHUB_TOKEN` 集成简单，无需额外密钥（若用 `docker/login-action` 与 `permissions: packages: write`）。 |
| 触发条件 | 推送 `v*` 标签必发；`main`/`master` 推送可选发 `latest` | 版本标签用于可复现发版；主分支浮动标签便于尝鲜（可按团队偏好关闭）。 |
| 镜像名 | `ghcr.io/<lowercase_owner>/<lowercase_repo>` | GHCR 惯例；仓库名需小写。 |
| Compose 同步 | 增加 `image:` 与注释或 `profiles` 区分 `dev`（build）与 `prod`（pull） | 避免破坏仅本地构建的用户；文档化“生产拉镜像”路径。 |

**备选方案：**

- Docker Hub：需额外账号与 `DOCKERHUB_TOKEN`，未选。
- 仅手动构建：不满足自动化需求。

## 风险 / 权衡

| 风险 | 缓解 |
|------|------|
| `latest` 语义漂移 | 文档说明生产环境应固定标签；CI 中仅对默认分支打 `latest`（若启用）。 |
| GHCR 权限失败 | Workflow 中显式 `permissions: contents: read, packages: write`；文档说明 fork 与 PR 不默认推镜像（仅 `push` 到主仓或 tag）。 |
| 镜像体积与缓存 | 使用 BuildKit 缓存（可选 `cache-from`/`cache-to`）；首版可简化，后续优化。 |

## 迁移计划

| 步骤 | 说明 |
|------|------|
| 合并 | 合并包含 workflow 与 Compose/README 的 PR。 |
| 验证 | 推送测试标签 `v0.0.0-test`，确认 GHCR 出现镜像。 |
| 回滚 | 删除或禁用 workflow 文件；已推送镜像保留或由维护者手动删除包版本。 |

## 开放问题

- 默认分支名是 `main` 还是 `master`：实现时以仓库实际默认分支为准。
- 是否在首版启用 `buildx` 多平台：若用户无 arm 需求，可先单平台以降低复杂度。
