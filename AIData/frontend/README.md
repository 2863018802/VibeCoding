# AIData Frontend

智能数据分析系统前端，基于 React 18 + TypeScript + Vite + TailwindCSS。

## 快速启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5174

## 环境要求

- Node.js 18+

## 目录结构

```
frontend/
├── src/
│   ├── api/              # API 客户端
│   ├── components/       # React 组件
│   │   ├── layout/       # 布局组件
│   │   ├── session/      # 会话管理组件
│   │   ├── chat/         # 聊天组件
│   │   └── chart/         # 图表组件
│   ├── stores/           # Zustand 状态管理
│   ├── lib/              # 工具函数
│   ├── App.tsx           # 根组件
│   └── main.tsx          # 入口文件
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```
