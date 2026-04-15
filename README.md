# 🏢 企业知识库问答系统

> 基于 **RAG（Retrieval-Augmented Generation，检索增强生成）** 技术的企业级智能知识库问答系统。上传企业文档，即可通过自然语言提问，AI 会基于真实文档内容给出准确回答并标注来源，有效解决大模型「幻觉」问题。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 功能演示

### 知识库构建
> 上传文档 → 一键构建知识库 → 支持多种格式

### 智能问答
> 自然语言提问 → AI 基于文档内容回答 → 标注来源可追溯

*(截图占位：运行项目后截图替换此处)*

---

## ✨ 功能特性

| 特性 | 描述 |
|------|------|
| 📄 **多格式支持** | PDF、Word（.docx）、TXT、Markdown（.md） |
| 🔍 **语义检索** | 基于 Embedding 向量的语义匹配，而非简单关键词搜索 |
| 💬 **智能问答** | 基于检索到的真实文档内容生成回答，拒绝幻觉 |
| 📎 **来源追溯** | 每个回答都标注来自哪篇文档的哪段内容，可验证可信度 |
| 🎨 **Web 界面** | 基于 Streamlit 构建的简洁美观交互界面 |
| 💾 **持久化存储** | 向量数据库持久化到磁盘，重启无需重建知识库 |
| ⚡ **本地 Embedding** | 使用开源模型本地向量化，零 API 成本 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                   用户界面 (Streamlit)                    │
│            文档上传 │ 知识库管理 │ 对话问答                  │
├─────────────────────────────────────────────────────────┤
│                 RAG 核心引擎 (LangChain)                  │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌───────────────────┐   │
│  │ 文档加载  │──→│ 文本分块  │──→│ Embedding 向量化   │   │
│  │ PDF/TXT/  │   │ 500字/块  │   │ all-MiniLM-L6-v2  │   │
│  │ DOCX/MD   │   │ overlap  │   │ （本地模型）       │   │
│  └──────────┘   └──────────┘   └────────┬──────────┘   │
│                                          │              │
│                                          ▼              │
│                                  ┌───────────────┐      │
│                                  │   ChromaDB    │      │
│                                  │  向量数据库     │      │
│                                  └───────┬───────┘      │
│                                          │              │
│  ┌──────────┐   ┌──────────┐            │              │
│  │ 用户提问  │──→│ 语义检索  │←───────────┘              │
│  │          │   │ Top-K=3  │                           │
│  └──────────┘   └────┬─────┘                           │
│                      │                                  │
│                      ▼                                  │
│              ┌───────────────┐                           │
│              │ DeepSeek LLM  │                           │
│              │  生成最终回答   │                           │
│              └───────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

### RAG 工作原理（三步走）

```
第1步：数据准备                    第2步：语义检索                    第3步：增强生成
┌──────────┐                  ┌──────────────┐               ┌──────────────┐
│ 企业文档  │  → 分块 → 向量化  │ 用户提问："年假"│  → 向量匹配  │ 文档片段+问题  │
│ PDF/Word │                  │ 找到员工手册    │              │ → DeepSeek   │
│ TXT/MD   │                  │ 第3.2节相关内容  │              │ → "年假5天"  │
└──────────┘                  └──────────────┘               └──────────────┘
```

---

## 🛠️ 技术栈

| 组件 | 技术选型 | 选型理由 |
|------|---------|----------|
| AI 框架 | LangChain 0.3 | 主流 RAG 开发框架，生态完善 |
| 大语言模型 | DeepSeek (deepseek-chat) | 中文能力强，性价比高，API 兼容 OpenAI |
| Embedding | sentence-transformers (all-MiniLM-L6-v2) | 开源本地模型，免费，支持中英双语 |
| 向量数据库 | ChromaDB | 轻量级嵌入式数据库，零配置启动 |
| 文档解析 | PyPDF2 / python-docx | 覆盖 PDF 和 Word 格式 |
| 前端界面 | Streamlit | Python 生态，快速构建数据应用 UI |
| 环境管理 | python-dotenv | 安全管理 API Key |

---

## 🚀 快速开始

### 前置要求

- **Python 3.10+**
- **DeepSeek API Key**（[免费注册，送 500 万 Token](https://platform.deepseek.com)）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/enterprise-rag-qa.git
cd enterprise-rag-qa

# 2. 创建虚拟环境
python -m venv .venv

# Windows 激活
.venv\Scripts\activate
# macOS/Linux 激活
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key

# 5. 启动应用
streamlit run app.py
```

打开浏览器访问 `http://localhost:8501`，开始使用！

---

## 📖 使用方法

1. **上传文档**：将 PDF / Word / TXT / Markdown 文件放入 `docs/` 目录，或在左侧栏上传
2. **构建知识库**：点击「构建知识库」按钮（首次运行需下载约 90MB 的 Embedding 模型）
3. **开始提问**：在底部输入框中用自然语言提问，AI 会基于文档内容回答并标注来源

### 示例问题

| 问题 | 回答来源 |
|------|----------|
| "公司年假有几天？" | 员工手册 → 考勤制度章节 |
| "出差报销标准是多少？" | 员工手册 → 差旅制度章节 |
| "Q2 营收目标多少？" | Q2 OKR → 销售部门目标 |
| "入职需要带什么材料？" | 新员工入职指引 → 入职准备章节 |
| "数据泄露了怎么办？" | 数据安全管理制度 → 应急流程章节 |

---

## 🎯 项目亮点

### 1. 完整实现 RAG 全流程
文档加载 → 文本分块 → Embedding 向量化 → 向量存储 → 语义检索 → Prompt 组装 → LLM 生成回答，每一步都清晰可控。

### 2. 来源追溯机制
每个回答都附带来源文档信息，用户可展开查看原文，有效解决 LLM「幻觉」问题，增强可信度。

### 3. 本地 Embedding 零成本
使用 `sentence-transformers` 本地模型进行向量化，不依赖付费 Embedding API，适合中小企业和个人开发者。

### 4. 多格式文档支持
统一处理 PDF、Word、TXT、Markdown 四种企业常见格式，自动识别编码和结构。

### 5. 持久化向量存储
知识库构建后持久化到磁盘，应用重启可直接加载，无需重复构建。

---

## 📂 项目结构

```
enterprise-rag-qa/
├── app.py                # Streamlit Web 前端界面
├── rag_engine.py         # RAG 核心引擎（加载、分块、检索、生成）
├── requirements.txt      # Python 依赖清单
├── 启动应用.bat           # Windows 一键启动脚本
├── .env.example          # 环境变量模板
├── .env                  # 环境变量（含 API Key，已 gitignore）
├── .gitignore            # Git 忽略规则
├── docs/                 # 文档目录
│   ├── 员工手册.md        # 示例：公司规章制度
│   ├── 产品技术方案.md     # 示例：产品架构文档
│   ├── Q2-OKR目标.md      # 示例：公司季度目标
│   ├── 面试评估标准.md     # 示例：HR 管理文档
│   ├── 新员工入职指引.md   # 示例：新员工指南
│   ├── 数据安全管理制度.md  # 示例：安全制度文档
│   └── RAG技术指南.txt     # 示例：技术参考文档
└── vectorstore/           # 向量数据库（自动生成，已 gitignore）
```

---

## 🔧 优化方向

- [ ] 混合检索（向量检索 + BM25 关键词检索）
- [ ] Reranking 重排序优化检索精度
- [ ] 多轮对话记忆（上下文关联）
- [ ] 多模态支持（图片 OCR + 表格解析）
- [ ] 用户认证和权限管理
- [ ] Docker 容器化部署
- [ ] RESTful API 接口
- [ ] 对话历史导出

---

## 📜 License

MIT License
