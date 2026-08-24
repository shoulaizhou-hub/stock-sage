# StockSage 📈

> **A股智能分析助手** — 基于 Flask 与东方财富数据，提供行情、技术面、基本面、新闻舆情、股票筛选及 AI 智能问答，辅助投资决策。

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-orange)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-Learning%20Only-lightgrey)](#注意事项)

## ✨ 功能特性

- 📊 **行情概览**：实时获取股票行情与公司基本信息
- 📈 **技术面分析**：计算 MA、MACD、RSI、KDJ 等常用技术指标
- 💰 **基本面分析**：盈利能力、杜邦分析、现金流等财务数据
- 📰 **新闻舆情**：抓取个股相关新闻，辅助情绪判断
- 🔍 **股票筛选**：按自定义条件批量筛选股票
- 🤖 **AI 智能问答**：基于 LangChain + OpenAI，结合用户偏好回答个股问题
- 📝 **分析报告**：自动生成个股综合分析报告

## 🏗️ 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Python · Flask |
| 数据源 | 东方财富公开接口 |
| AI | LangChain · OpenAI（GPT） |
| 前端 | HTML / CSS / JavaScript（Jinja2 模板） |
| 配置 | python-dotenv |

## 📂 项目结构

```
stock-sage/
├── app.py                     # Flask 应用入口与路由
├── templates/
│   └── index.html             # 前端页面
├── services/                  # 业务逻辑
│   ├── data_fetcher.py        # 数据抓取（东方财富）
│   ├── technical_analysis.py  # 技术指标计算
│   ├── fundamental_analysis.py# 基本面分析
│   ├── news_analysis.py       # 新闻舆情
│   ├── stock_screener.py      # 股票筛选
│   └── ai_qa.py               # AI 问答与报告
├── .env                       # 环境变量（不入库）
└── .gitignore
```

## 🚀 快速开始

1. **克隆仓库**

   ```bash
   git clone https://github.com/shoulaizhou-hub/stock-sage.git
   cd stock-sage
   ```

2. **安装依赖**

   ```bash
   pip install flask requests pandas python-dotenv langchain langchain-openai openai
   ```

3. **配置环境变量**

   在项目根目录创建 `.env` 文件：

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **启动服务**

   ```bash
   python app.py
   ```

   浏览器访问 <http://127.0.0.1:8080>

## 📡 API 接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/stock_list` | GET | 获取股票列表 |
| `/api/history_data` | POST | 获取历史行情数据 |
| `/api/technical_indicators` | POST | 计算技术指标 |
| `/api/fundamental_data` | POST | 获取基本面数据 |
| `/api/news` | POST | 获取个股新闻 |
| `/api/screen_stocks` | POST | 按条件筛选股票 |
| `/api/ai_question` | POST | AI 智能问答 |
| `/api/analysis_report` | POST | 生成分析报告 |

## 📌 数据来源

所有行情与财务数据均来自 [东方财富](https://www.eastmoney.com/) 的公开接口，仅供学习研究使用。

## ⚠️ 注意事项

- `.env` 含敏感密钥，已被 `.gitignore` 忽略，请勿提交
- AI 问答功能依赖 OpenAI API，未配置 Key 时相关接口不可用
- 本项目仅作学习交流，不构成任何投资建议

## License

本项目仅供学习交流使用。
