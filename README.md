# 方针管理导入评估系统 (Hoshin Kanri Assessment)

基于 30 题四维评估模型的一体化 Web 应用，支持三种使用场景：

- **A 交互评估工具** — 咨询师填表出完整报告（含雷达图、四象限、维度分析、双路线图）
- **B 咨询师工作台** — 评估后策略分解与追踪
- **C 客户自评问卷** — 客户填表自动出概览

## 技术栈

FastAPI + Jinja2 + SQLite + Chart.js + Bootstrap 5
字体：Inter（英文） + Noto Sans SC（中文）
配色：McKinsey 风格（深蓝 #002B5E + 品牌蓝 #0052FF）

## 快速启动

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# http://localhost:8000
```

## 评估流程

1. 填写企业基本信息（名称、行业、规模、愿景使命）
2. 30 题四维评分（每题四档：1分-初始级 / 3分-规划级 / 6分-规范级 / 9分-优化级）
3. 生成完整报告（雷达图+四象限定位+维度分析+优劣势+双路线图）

## 核心公式

```
渴望度 Desire = avg(Q1-Q4, Q9-Q12)
能力值 Capability = avg(Q5-Q8, Q13-Q30)
```

四象限：A有愿无能 → B无愿无能 → C有能有愿 → D有能无愿

## 部署

推荐 Zeabur 或 Railway，连接 GitHub 仓库一键部署。

详细文档见 `docs/方针管理导入评估系统-技术文档.md`
