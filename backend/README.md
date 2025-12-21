# 电影数据仓库后端 API

基于Flask的电影数据仓库后端服务，支持OpenGauss、Hive和Neo4j三种数据库的统一查询接口和性能对比。

## 功能特性

- ✅ **多数据库支持**: 同时支持关系型(华为OpenGauss)、分布式(Hive)和图数据库(Neo4j)
- ✅ **性能监控**: 自动对比三种数据库的查询性能
- ✅ **数据可视化**: 提供图表数据格式化的API
- ✅ **数据治理**: 内置数据质量检查和血缘追踪
- ✅ **RESTful API**: 标准的REST API设计
- ✅ **并发查询**: 支持并发执行多数据库查询

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose (推荐)
- 数据库服务 (OpenGauss, Hive, Neo4j)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制环境变量模板并配置：

```bash
cp env.example .env
# 编辑 .env 文件，设置数据库连接信息
```

**重要：远程数据库连接配置**

如果连接远程服务器上的数据库（IP: 139.196.151.22），请确保 `.env` 文件包含以下配置：

```bash
# OpenGauss数据库配置 (华为云服务器)
OPENGAUSS_HOST=139.196.151.22
OPENGAUSS_PORT=5432
OPENGAUSS_USER=gaussdb
OPENGAUSS_PASSWORD=GaussDB@2025
OPENGAUSS_DATABASE=movie_dw

# Hive配置 (华为云服务器)
HIVE_HOST=139.196.151.22
HIVE_PORT=10000
HIVE_USER=hive
HIVE_DATABASE=default

# Neo4j配置 (华为云服务器)
NEO4J_URI=bolt://139.196.151.22:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password
```

**网络连接注意事项：**
- 确保服务器防火墙开放相应端口（5432, 10000, 7687）
- 如果在Docker容器中运行，需要确保容器能访问外部网络
- 可能需要配置VPN或安全组规则允许连接

### 运行应用

#### 连接诊断
在启动应用前，建议先运行连接诊断：

```bash
python diagnostics.py
```

这将检查与远程数据库的网络连通性。

#### 开发模式
```bash
python run.py
```

#### Docker 方式
```bash
docker-compose up --build
```

#### 生产部署
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# 使用Docker
docker build -t movie-warehouse-backend .
docker run -p 8000:5000 movie-warehouse-backend
```

## API 接口文档

### 基础接口

#### 健康检查
```
GET /api/health
```

响应示例：
```json
{
  "status": "healthy",
  "service": "Movie Data Warehouse API",
  "version": "1.0.0"
}
```

### 查询接口

#### 按年份查询电影
```
GET /api/query/movies-by-year?year=2020
```

#### 按导演查询电影
```
GET /api/query/movies-by-director?director=Christopher Nolan
```

#### 按演员查询电影
```
GET /api/query/movies-by-actor?actor=Leonardo DiCaprio&role_type=starring
```

#### 按类型查询统计
```
GET /api/query/movies-by-genre?genre=Action
```

#### 高评分电影查询
```
GET /api/query/high-rated-movies?min_score=4.0&min_reviews=10
```

#### 演员合作关系
```
GET /api/query/actor-collaborations?min_collaborations=2&limit=20
```

#### 导演演员合作关系
```
GET /api/query/director-actor-collaborations?director=Steven Spielberg&min_collaborations=1&limit=10
```

#### 热门演员组合（仅Neo4j）
```
GET /api/query/popular-actor-combinations?genre=Action
```

### 数据治理接口

#### 数据质量报告
```
GET /api/query/data-quality
```

#### 数据血缘信息
```
GET /api/query/data-lineage
```

#### 性能报告
```
GET /api/query/performance-report
```

## 响应格式

所有API响应都遵循统一的格式：

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "charts": {...},
  "execution_time": 0.123,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 数据库配置

### 远程服务器配置 (推荐)
如果连接远程服务器 (139.196.151.22) 上的数据库：

```bash
# OpenGauss数据库配置 (华为云服务器)
OPENGAUSS_HOST=139.196.151.22
OPENGAUSS_PORT=5432
OPENGAUSS_USER=gaussdb
OPENGAUSS_PASSWORD=GaussDB@2025
OPENGAUSS_DATABASE=movie_dw

# Hive配置 (华为云服务器)
HIVE_HOST=139.196.151.22
HIVE_PORT=10000
HIVE_USER=hive
HIVE_DATABASE=default

# Neo4j配置 (华为云服务器)
NEO4J_URI=bolt://139.196.151.22:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password
```

### 本地开发配置
如果使用本地Docker环境：

### OpenGauss (关系型数据库)
```python
OPENGAUSS_HOST=localhost
OPENGAUSS_PORT=5432
OPENGAUSS_USER=gaussdb
OPENGAUSS_PASSWORD=GaussDB@2025
OPENGAUSS_DATABASE=movie_dw
```

### Hive (分布式存储)
```python
HIVE_HOST=localhost
HIVE_PORT=10000
HIVE_USER=hive
HIVE_DATABASE=default
```

### Neo4j (图数据库)
```python
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password
```

**网络连接注意事项：**
- 确保服务器防火墙开放相应端口（5432, 10000, 7687）
- 如果在Docker容器中运行，需要确保容器能访问外部网络
- 可能需要配置VPN或安全组规则允许连接

## 开发指南

### 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask应用工厂
│   ├── models/              # 数据模型层
│   │   ├── opengauss/       # OpenGauss模型
│   │   ├── hive/           # Hive模型
│   │   └── neo4j/          # Neo4j模型
│   ├── controllers/         # 控制器层
│   │   └── api/            # API控制器
│   ├── services/           # 服务层
│   │   ├── query_service.py        # 查询服务
│   │   ├── performance_service.py  # 性能监控
│   │   └── visualization_service.py # 可视化服务
│   ├── utils/              # 工具类
│   └── config/             # 配置管理
├── config/                 # 全局配置
├── tests/                  # 测试
├── requirements.txt        # 依赖
├── run.py                 # 启动脚本
└── Dockerfile            # Docker构建
```

### 添加新查询

1. 在相应数据库模型中添加查询方法
2. 在 `query_service.py` 中添加统一接口
3. 在 `query_controller.py` 中添加API端点
4. 更新文档

### 测试

运行测试：
```bash
pytest
```

运行特定测试：
```bash
pytest tests/unit/test_models.py
```

## 部署

### 开发环境
```bash
docker-compose up --build
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# 使用Docker
docker build -t movie-warehouse-backend .
docker run -p 8000:5000 movie-warehouse-backend
```

## 监控和日志

- 应用日志输出到控制台
- 查询性能自动记录
- 支持健康检查端点
- 数据库连接池监控

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接参数
   - 检查网络配置

2. **查询超时**
   - 调整 `QUERY_TIMEOUT` 配置
   - 优化查询语句
   - 检查数据库性能

3. **内存不足**
   - 增加Docker内存限制
   - 优化数据处理逻辑
   - 使用分页查询

## 许可证

本项目采用 MIT 许可证。
