# 电影数据仓库前端应用

基于React + TypeScript + Ant Design的数据仓库可视化界面，支持多数据库查询、性能对比和数据治理。

## 🚀 功能特性

- ✅ **多数据库查询**: 同时查询OpenGauss、Hive、Neo4j三个数据库
- ✅ **性能对比可视化**: 实时显示查询性能对比和统计
- ✅ **数据可视化**: 图表展示查询结果的各种维度分析
- ✅ **数据治理**: 数据质量监控和血缘追踪
- ✅ **响应式设计**: 支持桌面端和移动端
- ✅ **TypeScript**: 完整的类型安全

## 📦 技术栈

- **React 19** - 用户界面框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI组件库
- **Chart.js** - 图表可视化
- **Axios** - HTTP客户端
- **React Router** - 路由管理
- **Vite** - 构建工具

## 🛠️ 快速开始

### 环境要求

- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
cd frontend/data-warehouse
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
npm run preview
```

## 📁 项目结构

```
src/
├── components/           # React组件
│   ├── Layout.tsx       # 主布局
│   ├── QueryForm.tsx    # 查询表单
│   ├── PerformanceChart.tsx    # 性能图表
│   ├── DataVisualization.tsx   # 数据可视化
│   └── DataQualityDashboard.tsx # 数据质量仪表板
├── services/            # API服务
│   └── api.ts          # API调用封装
├── types/              # TypeScript类型定义
│   └── index.ts        # 全局类型
├── utils/              # 工具函数
│   └── formatters.ts   # 数据格式化
├── hooks/              # 自定义Hooks
├── App.tsx            # 主应用组件
├── main.tsx           # 应用入口
└── index.css          # 全局样式
```

## 🔧 配置说明

### API配置

在 `vite.config.ts` 中配置后端API地址：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 后端API地址
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
VITE_API_BASE_URL=http://localhost:5000
```

## 📊 功能说明

### 1. 数据查询

支持以下查询类型：
- **按年份查询电影**: 查看特定年份的电影统计
- **按导演查询电影**: 查找特定导演的作品
- **按演员查询电影**: 支持主演和参演查询
- **按类型查询统计**: 查看电影类型分布
- **高评分电影**: 筛选高质量电影
- **演员合作关系**: 分析演员合作网络
- **导演演员合作**: 查看导演与演员的合作历史

### 2. 性能监控

- 实时显示三个数据库的查询执行时间
- 性能倍数对比
- 成功率统计
- 详细的性能指标

### 3. 数据可视化

- **时间序列图**: 电影上映年份分布
- **评分分布**: 用户评分统计
- **类型饼图**: 电影类型占比
- **评论统计**: 评论数量分布
- **导演统计**: 导演作品数量排名

### 4. 数据治理

- **数据质量评估**: 完整性、唯一性、有效性检查
- **异常检测**: 识别数据问题
- **血缘追踪**: 数据来源和处理流程
- **改进建议**: 基于质量分析的优化建议

## 🎨 自定义主题

在 `App.tsx` 中可以自定义Ant Design主题：

```typescript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
    },
  }}
>
  {/* 应用内容 */}
</ConfigProvider>
```

## 📱 响应式设计

应用支持多种屏幕尺寸：
- **桌面端**: 完整功能展示
- **平板端**: 适配布局调整
- **移动端**: 简化界面和触摸优化

## 🔍 开发指南

### 添加新查询类型

1. 在 `types/index.ts` 中定义新的查询类型
2. 在 `services/api.ts` 中添加API方法
3. 在 `components/QueryForm.tsx` 中添加表单字段
4. 在 `App.tsx` 中处理新的查询逻辑

### 添加新图表

1. 在 `components/DataVisualization.tsx` 中添加图表组件
2. 使用Chart.js或自定义图表库
3. 确保响应式设计

### 自定义样式

使用styled-components或修改 `index.css`：

```typescript
import styled from 'styled-components';

const StyledComponent = styled.div`
  background: ${props => props.theme.primaryColor};
  border-radius: 8px;
`;
```

## 🚀 部署

### 使用Docker

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 静态部署

将 `dist` 目录部署到任何静态文件服务器。

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   - 检查后端服务是否启动
   - 验证API地址配置
   - 查看浏览器网络面板

2. **图表不显示**
   - 确认Chart.js依赖已安装
   - 检查数据格式是否正确
   - 查看控制台错误信息

3. **样式异常**
   - 清除浏览器缓存
   - 检查CSS变量定义
   - 验证Ant Design版本

## 📄 许可证

本项目采用 MIT 许可证。