# PetOS 2.1 — 宠物陪伴智能系统

面向宠物陪伴场景的全栈系统：后端统一管理宠物档案、设备、聊天互动、插件、设置与通知，前端提供陪伴式桌面端界面。所有业务数据均来自数据库，前端不保留本地 mock。

> 本仓库为团队交付版本，`git clone` 后按下方步骤即可在本地跑起来。

## ✨ 功能特性

- **宠物档案**：多宠物切换、状态数值（饱食/饮水/精力/心情/健康）与健康指标实时计算
- **陪伴互动**：聊天对话、快速互动按钮、互动次数持久化
- **设备管理**：已绑定设备与附近设备列表、设备抽屉详情
- **设置中心**：网络 / 设备 / 通知 / 个人 / 摄像头等分组配置，全部入库驱动
- **通知中心**：未读提醒与已读状态
- **插件中心**：8 个内置插件，开关状态持久化
- **监控域（预留）**：传感器数据、告警抓拍、大屏统计，可接 ESP32 / 香橙派

## 🧱 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite 5 + Pinia + Vue Router 4 + Axios |
| 后端 | Python 3.10+ / FastAPI + Uvicorn + SQLite（可切 MySQL） |
| 通信预留 | MQTT（EMQX）、大模型（OpenAI 兼容协议） |
| 文档 | Swagger UI 自动生成接口文档 |

> `backend/src/` 为旧版 SpringBoot 参考源码，仅作对照，**不参与当前运行**；当前后端由 FastAPI 提供全部接口。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 克隆并启动后端

```powershell
git clone <你的仓库地址>
cd backend
pip install -r requirements.txt          # 首次
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

- 接口文档：<http://localhost:8080/docs>
- 健康检查：<http://localhost:8080/api/health>

首次启动会自动创建 `petos.db` 并灌入种子数据（数据库文件不入库，见下文）。

### 2. 启动前端

新开一个终端：

```powershell
cd frontend
npm install                               # 首次
npm run dev
```

浏览器打开终端打印的 `Local:` 地址（默认 `http://localhost:5173`，若端口被占用 Vite 会自动顺延到 5174/5175…）。前端已把 `/api`、`/images` 代理到 `127.0.0.1:8080`。

## 📁 项目结构

```
PetOS2.1/
├─ backend/                FastAPI 后端
│  ├─ app/                 应用源码（routers / services / common / seed / database）
│  ├─ scripts/             db_tool.py（数据库导出/导入/重置）、verify_api.py（接口自检）
│  ├─ sql/                 SQLite / MySQL 数据快照与建库脚本
│  ├─ docs/                API.md / DATABASE.md / INTEGRATION.md
│  ├─ upload-images/       抓拍样图（sample_*.jpg 入库，运行时上传不入库）
│  ├─ src/  pom.xml        （legacy）旧 SpringBoot 参考源码
│  └─ README.md
├─ frontend/               Vue 3 前端
│  └─ src/ views/ components/ stores/ config/ router/
├─ 系统整合与答辩说明.md
├─ 算法与技术栈说明.md
└─ README.md               （本文件）
```

## 📄 文档

- [系统整合与答辩说明.md](系统整合与答辩说明.md) — 总体架构、启动、演示数据同步、答辩要点
- [算法与技术栈说明.md](算法与技术栈说明.md) — 技术选型与算法说明
- [backend/README.md](backend/README.md) — 后端详细说明
- [backend/docs/API.md](backend/docs/API.md) — 接口清单
- [backend/docs/DATABASE.md](backend/docs/DATABASE.md) — 数据库设计
- [backend/docs/INTEGRATION.md](backend/docs/INTEGRATION.md) — 硬件/前端集成说明

## 🔐 环境变量与密钥

- 仓库只提交 `*.example` / `*.development` / `*.production` 模板，**不包含任何真实密钥**。
- `backend/.env` 为本地实际配置（已被 `.gitignore` 排除），复制 `.env.example` 填写即可。
- MQTT / 大模型地址留空时，后端自动进入**演示兜底模式**：聊天走内置话术、硬件指令仅打印日志，不影响本地联调与答辩。

## 📦 演示数据

- `petos.db`（本地 SQLite）不入库，首次运行自动建表 + 灌入种子数据。
- `backend/sql/petos_companion_sqlite.sql` 是可提交的数据快照，答辩前用它让所有队友拿到**完全一致**的状态：

  ```powershell
  # 导出方（backend 目录）
  python scripts/db_tool.py export
  # 导入方（backend 目录）
  python scripts/db_tool.py import --force
  ```

## 🧪 自检

后端启动后，在 `backend/` 目录运行：

```powershell
python scripts/verify_api.py      # 全量接口自检，全部通过输出“结果：全部通过 ✅”
```
