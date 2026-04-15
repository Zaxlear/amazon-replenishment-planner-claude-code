# Amazon 补货与销售规划系统

亚马逊 FBA 多仓发货计划、销售预测与库存规划管理系统。

## 项目简介

本系统为亚马逊 FBA 卖家设计，解决多仓补货流程中的三个核心痛点：

- **多仓发货管理** — 美西/美中/美东三仓按比例分配发货量，自动计算每仓货件数量与到货时间
- **库存预测与断货预警** — 基于销量规划逐日推算库存变化，提前预警断货风险
- **库存周转分析** — 通过 FIFO 消耗模型追踪每批货件的周转效率

### 系统架构

```
Frontend (React + TypeScript + Ant Design)
    │
    │  REST API
    ▼
Backend (FastAPI + SQLAlchemy)
    │
    ├── PostgreSQL 16  (数据持久化)
    └── Redis 7        (计算缓存)
```

### 功能模块

| 模块 | 说明 |
|------|------|
| 发货规划 | 创建发货计划，配置三仓比例与物流时效，管理多批次发货，自动生成货件明细 |
| 销售/库存规划 | 录入每日销量预测，关联发货计划，运行库存计算引擎，支持库存校正 |
| 图表面板 | 库存趋势图（面积图 + 柱状图），到货标记，断货区域高亮，日期范围缩放 |
| 周转分析 | FIFO 消耗追踪，每批货件平均周转天数，售罄日期计算 |

### 技术栈

**后端**: Python 3.10+ · FastAPI · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2

**前端**: React 19 · TypeScript · Ant Design · Recharts · Vite

**基础设施**: PostgreSQL 16 · Redis 7 · Docker Compose

---

## 部署指南

### 环境要求

| 依赖 | 版本要求 |
|------|---------|
| Python | >= 3.10 |
| Node.js | >= 18 |
| Docker & Docker Compose | 最新版 (用于 PostgreSQL 和 Redis) |
| Git | 任意版本 |

### 1. 克隆项目

```bash
git clone https://github.com/your-username/amazon-replenishment-planner.git
cd amazon-replenishment-planner
```

### 2. 启动数据库和缓存服务

使用 Docker Compose 启动 PostgreSQL 和 Redis：

```bash
make dev-services
```

等价于：

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

启动后：
- PostgreSQL 运行在 `localhost:5432`（用户名/密码: `postgres/postgres`，数据库: `replenishment`）
- Redis 运行在 `localhost:6379`

验证服务是否正常：

```bash
docker ps
# 应看到 replenishment-db 和 replenishment-redis 两个容器
```

### 3. 配置后端

```bash
cd backend

# 创建 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cp ../.env.example .env
```

如果数据库地址、端口或密码与默认值不同，请编辑 `backend/.env` 中的 `DATABASE_URL`：

```
DATABASE_URL=postgresql+asyncpg://用户名:密码@主机:端口/数据库名
```

### 4. 初始化数据库

运行 Alembic 迁移创建所有表：

```bash
# 确保在 backend/ 目录且虚拟环境已激活
alembic revision --autogenerate -m "init"
alembic upgrade head
```

或使用 Makefile（从项目根目录）：

```bash
make migrate
```

### 5. 启动后端服务

```bash
# 在 backend/ 目录，虚拟环境已激活
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或从项目根目录：

```bash
make dev-backend
```

启动后访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/health

### 6. 配置并启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

或从项目根目录：

```bash
make dev-frontend
```

前端运行在 http://localhost:5173，API 请求通过 Vite 代理转发到后端 `localhost:8000`。

### 7. 验证

打开浏览器访问 http://localhost:5173，应看到系统界面。尝试以下操作验证功能正常：

1. **发货规划** — 点击「新建发货计划」，填写计划名称、数量，配置三仓比例，添加批次后创建
2. **销售规划** — 点击「新建规划」，关联上一步的发货计划，设置日期范围和期初库存
3. **录入销量** — 在规划详情中使用「批量输入」设置每日销量，点击「计算」查看库存推演结果
4. **图表面板** — 选择规划查看库存趋势图
5. **周转分析** — 选择规划查看各货件的周转天数

---

## 常用命令

```bash
# 启动/停止基础设施
make dev-services          # 启动 PostgreSQL + Redis
make dev-services-down     # 停止并移除容器

# 开发
make dev-backend           # 启动后端 (端口 8000)
make dev-frontend          # 启动前端 (端口 5173)

# 数据库
make migrate               # 运行迁移
make migrate-new msg="描述" # 生成新迁移

# 测试
make test                  # 运行后端测试 (32 tests)
```

## 项目结构

```
amazon-replenishment-planner/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑
│   │   │   ├── shipment_service.py    # 发货计划 CRUD
│   │   │   ├── sales_service.py       # 销售规划 CRUD
│   │   │   ├── inventory_engine.py    # 库存计算引擎 (核心)
│   │   │   └── turnover_service.py    # FIFO 周转分析
│   │   ├── routers/         # API 路由 (22 个端点)
│   │   ├── utils/           # 工具函数
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   └── main.py          # 应用入口
│   ├── alembic/             # 数据库迁移
│   ├── tests/               # 测试 (32 tests)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── shipment/    # 发货相关组件
│       │   ├── sales/       # 销售/库存相关组件
│       │   ├── charts/      # 图表组件
│       │   └── common/      # 通用布局组件
│       ├── pages/           # 页面
│       ├── services/        # API 调用层
│       ├── types/           # TypeScript 类型定义
│       └── utils/           # 工具函数
├── docker/
│   └── docker-compose.dev.yml
├── Makefile
└── .env.example
```
