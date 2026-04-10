## 为什么

项目已提供 `Dockerfile` 与 `docker-compose.yml`，但缺少自动化构建与发布流程；维护者每次发版需本地构建并手动推送镜像，易出错且不可追溯。通过 GitHub Actions 在推送标签或主分支时构建并推送镜像到容器注册表，并与 Compose 配置对齐，可降低部署摩擦、保证镜像与源码版本一致。

## 变更内容

- 新增 GitHub Actions workflow：在约定触发条件下构建多阶段 `Dockerfile` 镜像，并推送到 GitHub Container Registry（GHCR），镜像标签与 Git 引用对齐（如 `latest`、语义化版本标签）。
- 同步更新 `docker-compose.yml`：增加基于已发布镜像的部署方式说明或可选服务定义（保留本地 `build: .` 路径以便开发），使文档化部署与 CI 产出一致。
- **非破坏性**：不改变应用运行时行为；仅增加 CI 与 Compose 侧配置。

## 功能 (Capabilities)

### 新增功能

- `docker-image-release`: 定义通过 CI 将本仓库构建为可拉取的容器镜像并发布到 GHCR 的需求，以及与 Docker Compose 文档/片段的一致性。

### 修改功能

<!-- 无既有 OpenSpec 规范；本变更为首次引入该能力。 -->

## 影响

- 仓库 `.github/workflows/` 新增 workflow 文件。
- `docker-compose.yml`（及必要时 `README.md` 中 Docker 小节）更新。
- 需启用 GitHub Actions 与 `GITHUB_TOKEN`/`GHCR` 写权限策略；使用者需知悉镜像坐标（`ghcr.io/<owner>/<repo>` 形式）。
