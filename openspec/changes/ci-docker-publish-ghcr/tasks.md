## 1. GitHub Actions 工作流

- [x] 1.1 在 `.github/workflows/` 新增工作流 YAML（例如 `docker-publish.yml`），使用 `docker/build-push-action` 或等效步骤构建根目录 `Dockerfile`
- [x] 1.2 配置 `permissions: contents: read` 与 `packages: write`，并使用 `docker/login-action` 登录 `ghcr.io`（`registry: ghcr.io`，用户名/密码使用 `GITHUB_ACTOR` + `GITHUB_TOKEN`）
- [x] 1.3 定义触发器：至少包含推送 `v*` 标签；可选包含默认分支推送以发布 `latest`（按 `design.md` 决策实现）
- [x] 1.4 设置镜像标签：`type=semver` 或 `type=ref,event=tag` 对应标签，以及需要的 `latest` 策略；镜像名使用小写 `ghcr.io/${{ github.repository }}`

## 2. Docker Compose 与文档

- [x] 2.1 更新 `docker-compose.yml`：为 `api2cursor` 服务增加 `image: ghcr.io/<owner>/<repo>:<tag>`（可用占位或注释说明替换方式），保留 `build: .` 作为本地开发路径，或采用 `profiles`/注释区分 prod/dev
- [x] 2.2 更新 `README.md`「Docker 部署」小节：说明从 GHCR 拉取镜像的用法、与本地 `docker compose build` 的区别，以及可选的环境变量/端口

## 3. 验证

- [x] 3.1 在测试分支或 fork 上验证 workflow 语法（若无法直接推送，至少本地 `actionlint` 或对照 GitHub Actions 文档检查）
- [ ] 3.2 合并后通过推送轻量标签验证 GHCR 出现预期标签的镜像
