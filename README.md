# 🏢 企业知识库问答系统 | Enterprise RAG Knowledge Base Q&A System

> [中文](#中文) | [English](#english)

---

<a id="中文"></a>
## 🇨🇳 中文

> 基于 RAG（检索增强生成）的企业知识库问答系统，支持上传 PDF/Word/TXT 等多种格式文档，通过语义检索 + AI 生成，让员工用自然语言即可获取准确答案。

![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green?logo=chainlink)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-blue)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

![System Screenshot](screenshots/main.png)

### 📖 什么是 RAG？

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是一种将信息检索与大语言模型（LLM）结合的技术。它先从知识库中检索相关文档片段，再把这些片段作为上下文喂给 LLM 生成答案，从而避免"幻觉"，确保回答基于真实文档。

| | 传统 LLM | RAG 系统 |
|---|---|---|
| 知识来源 | 仅限于训练数据 | 从你的文档实时检索 |
| 准确性 | 可能产生幻觉 | 基于真实文档，有据可查 |
| 数据隐私 | 数据发送给模型提供商 | 本地向量存储，敏感数据不外泄 |
| 更新成本 | 昂贵的微调 | 上传新文档即可 |

### 🎯 应用场景

**企业场景：**
- **内部知识库** — 新员工直接问公司制度、入职指引、技术文档，不用翻一堆文件
- **技术文档助手** — 开发者查询 API 文档、架构说明、故障排查手册，秒出答案
- **合规与 HR 问答** — 员工快速获取数据安全政策、面试标准、公司流程等信息
- **OKR 目标追踪** — 快速查询季度目标和团队 OKR，不用翻多个文档

**个人场景：**
- **学习笔记问答** — 上传课堂笔记和教材，通过提问来复习和检验理解
- **论文分析** — 上传学术论文，让 AI 解释概念、比较方法论、总结发现
- **个人知识管理** — 把书签、剪报、笔记建成可搜索的知识库

### ✨ 功能特性

- 📄 **多格式文档支持** — PDF、Word（.docx）、TXT、Markdown、HTML
- 🔍 **语义检索** — 用 sentence embedding 做概念匹配（不是简单关键词匹配）
- 🤖 **AI 生成回答** — DeepSeek 基于检索结果生成带来源引用的回答
- 📊 **知识库管理** — 查看已加载文档、重建向量库、管理知识库
- 💬 **对话式交互** — 聊天式问答，支持多轮对话历史

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  上传文档     │  │  提问        │  │  管理知识库      │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼─────────────┘
          │                 │                   │
┌─────────▼─────────────────▼───────────────────▼─────────────┐
│                      RAG 引擎                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 加载 & 分割  │  │ 向量存储     │  │  RAG Chain       │  │
│  │ 文档         │  │ (ChromaDB)   │  │  (LangChain)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                                       │
          ▼                                       ▼
┌──────────────────┐                  ┌──────────────────────┐
│ 文档文件          │                  │ DeepSeek API          │
│ (PDF/DOCX/TXT/MD)│                  │ (大模型生成)          │
└──────────────────┘                  └──────────────────────┘
```

### 📊 数据流程

```
文档处理流程：
  PDF/DOCX/TXT → 文本提取 → 分块（Chunk Splitting）→ Embedding → ChromaDB

问答流程：
  用户提问 → Embedding → 相似度检索（Top-K 块）
  → [问题 + 检索到的上下文] → DeepSeek LLM → 带来源的回答
```

### 📁 项目结构

```
rag-knowledge-base/
├── app.py                  # Streamlit Web 界面
├── rag_engine.py           # RAG 引擎：文档处理、向量存储、Chain
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── docs/                   # 示例知识库文档
│   ├── Q2-OKR目标.md
│   ├── RAG技术指南.txt
│   ├── 产品技术方案.md
│   ├── 员工手册.md
│   ├── 数据安全管理制度.md
│   ├── 新员工入职指引.md
│   └── 面试评估标准.md
├── vectorstore/            # ChromaDB 持久化存储（自动生成）
└── screenshots/            # UI 截图
```

### 🚀 快速开始

**环境要求：**
- Python 3.9+
- DeepSeek API Key（[免费获取](https://platform.deepseek.com)）

**安装步骤：**

```bash
# 1. 克隆仓库
git clone https://github.com/SsllF8/enterprise-rag-qa.git
cd enterprise-rag-qa

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 5. 启动应用
streamlit run app.py
```

Windows 用户也可以直接双击 `启动应用.bat`。

> ⚠️ 首次启动会下载 Embedding 模型（约 90MB），可能需要几分钟。

### ⚙️ 环境变量配置

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | ❌ | API 地址（默认 `https://api.deepseek.com`） |

### 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Web 框架 | Streamlit | 交互式 Web UI |
| LLM 框架 | LangChain | RAG Chain 编排 |
| 大模型 | DeepSeek | 回答生成 |
| 向量数据库 | ChromaDB | Embedding 存储与相似度检索 |
| Embedding 模型 | sentence-transformers (`all-MiniLM-L6-v2`) | 文本向量化 |
| 文档解析 | pypdf, python-docx, BeautifulSoup | 多格式文本提取 |
| 文本分割 | LangChain TextSplitters | 基于分块的文档处理 |

### 💡 面试要点 / Interview Talking Points

**1. 为什么选择 RAG 而不是直接用 ChatGPT？**
- 企业数据敏感，不能直接发给第三方模型
- LLM 训练数据有截止日期，无法获取最新信息
- RAG 可以基于企业自有文档给出"有据可查"的回答，避免幻觉

**2. 为什么选 ChromaDB？**
- 轻量级，无需额外安装数据库服务，Python 原生
- 适合中小规模知识库（千到十万级文档块）
- API 简洁，上手快，适合原型验证和 demo

**3. Embedding 模型为什么选 all-MiniLM-L6-v2？**
- 体积小（约 80MB），推理速度快
- 支持中英双语（虽然中文效果不如专用中文模型，但够用）
- 384 维向量，兼顾精度和存储效率

**4. chunk_size 和 overlap 怎么定的？**
- chunk_size=500：太大导致检索不精准（噪声多），太小导致上下文不完整
- overlap=50：保证相邻 chunk 之间的语义连续性，避免关键信息被截断

**5. LangChain 在这个项目里起了什么作用？**
- 提供了文档加载器（DocumentLoaders）、文本分割器（TextSplitters）
- 封装了 RAG Chain（retrieve + generate），不用手动拼接 prompt
- 统一了 Embedding 和 LLM 的调用接口

### ⚠️ 搭建中可能遇到的问题 / Troubleshooting

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 首次运行卡很久 | 下载 Embedding 模型约 90MB | 耐心等待，或提前设置 `HF_HUB_OFFLINE=1` 使用缓存 |
| 中文检索效果不好 | all-MiniLM-L6-v2 以英文为主 | 可换用 `paraphrase-multilingual-MiniLM-L12-v2` |
| 回答不准确 | chunk_size 不合适 | 调整 `chunk_size`（300-1000）和 `overlap`（50-200）|
| ChromaDB 报 Rust bindings 错误 | Streamlit rerun 时重复创建 PersistentClient | 用 EphemeralClient（内存模式）替代 |
| pypdf 提取中文乱码 | 某些 PDF 编码特殊 | 尝试换用 `pdfplumber` 或 `PyMuPDF` |
| API 超时 | 网络问题或 DeepSeek 服务波动 | 增大 timeout，或加入重试逻辑 |

### 🚀 扩展方向 / Future Enhancements

- **接入更强大的 Embedding 模型** — 换用 BGE-large-zh 或 text2vec-large-chinese 提升中文语义检索精度
- **支持实时文档更新** — 监听目录变化，自动增删向量库中的文档
- **多轮对话优化** — 基于对话历史做 query 改写，让多轮问答更自然
- **权限管理** — 不同部门只能检索自己有权限的文档
- **混合检索** — 向量检索 + BM25 关键词检索，取交集提升召回率
- **对话评估** — 增加 RAGAS 框架评估回答质量（忠实度、相关性、上下文利用）
- **前端重构** — 用 React/Vue 重写前端，支持更丰富的交互（拖拽上传、实时搜索建议）

---

<a id="english"></a>
## 🇬🇧 English

> A production-ready RAG (Retrieval-Augmented Generation) knowledge base system that enables employees to get accurate answers from enterprise documents using semantic search and AI-powered response generation.

![System Screenshot](screenshots/main.png)

### What is RAG?

**RAG (Retrieval-Augmented Generation)** combines information retrieval with large language models (LLMs). Instead of relying solely on the LLM's training data, RAG first searches a knowledge base for relevant documents, then feeds those documents as context to the LLM to generate accurate, grounded answers.

| | Traditional LLM | RAG System |
|---|---|---|
| Knowledge | Limited to training data | Continuously updated from your documents |
| Accuracy | May hallucinate | Grounded in real documents |
| Privacy | Data sent to model provider | Local vector store, sensitive data stays in-house |
| Cost | Expensive fine-tuning | Just upload new documents |

### Use Cases

**Enterprise:**
- **Internal Knowledge Base** — Employees ask questions about policies, onboarding, and tech docs
- **Technical Documentation Assistant** — Developers query API docs, architecture guides, and troubleshooting manuals
- **Compliance & HR Q&A** — Instant answers about security policies, interview standards, and procedures
- **OKR & Goal Tracking** — Query quarterly objectives without searching multiple documents

**Personal:**
- **Study Notes Q&A** — Upload lecture notes and quiz yourself by asking questions
- **Research Paper Analysis** — Upload academic papers and ask AI to explain concepts or compare methodologies
- **Personal Knowledge Management** — Build a searchable knowledge base from bookmarks and notes

### Features

- 📄 **Multi-format Support** — PDF, Word (.docx), TXT, Markdown, HTML
- 🔍 **Semantic Search** — Conceptual matching via sentence embeddings (not just keyword matching)
- 🤖 **AI-Powered Answers** — DeepSeek generates context-aware responses with source citations
- 📊 **Knowledge Base Management** — View documents, rebuild vector store, manage your KB
- 💬 **Conversational Interface** — Chat-style Q&A with conversation history

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Upload Docs │  │  Ask Question │  │  Manage KB       │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼─────────────┘
          │                 │                   │
┌─────────▼─────────────────▼───────────────────▼─────────────┐
│                      RAG Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Load & Split │  │ Vector Store │  │  RAG Chain       │  │
│  │ Documents    │  │ (ChromaDB)   │  │  (LangChain)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                                       │
          ▼                                       ▼
┌──────────────────┐                  ┌──────────────────────┐
│ Document Files   │                  │ DeepSeek API         │
│ (PDF/DOCX/TXT/MD)│                  │ (LLM for generation) │
└──────────────────┘                  └──────────────────────┘
```

### Project Structure

```
rag-knowledge-base/
├── app.py                  # Streamlit web interface
├── rag_engine.py           # RAG engine: document processing, vector store, chain
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── docs/                   # Sample knowledge base documents
├── vectorstore/            # ChromaDB persistent storage (auto-generated)
└── screenshots/            # UI screenshots
```

### Quick Start

```bash
git clone https://github.com/SsllF8/enterprise-rag-qa.git
cd enterprise-rag-qa
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env  # Fill in your DEEPSEEK_API_KEY
streamlit run app.py
```

> ⚠️ First run downloads the embedding model (~90MB). This may take a few minutes.

### Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | ✅ | Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | ❌ | API base URL (defaults to `https://api.deepseek.com`) |

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Streamlit | Interactive web UI |
| LLM Framework | LangChain | RAG chain orchestration |
| LLM | DeepSeek | Response generation |
| Vector Database | ChromaDB | Embedding storage & similarity search |
| Embedding Model | sentence-transformers (`all-MiniLM-L6-v2`) | Text vectorization |
| Document Parsing | pypdf, python-docx, BeautifulSoup | Multi-format text extraction |

### Interview Talking Points

**1. Why RAG instead of just using ChatGPT?**
- Enterprise data sensitivity — can't send proprietary docs to third-party models
- LLMs have training data cutoffs — can't access latest information
- RAG provides verifiable answers grounded in real documents, reducing hallucinations

**2. Why ChromaDB?**
- Lightweight, no separate database service needed, Python-native
- Suitable for small-to-medium scale knowledge bases (thousands to ~100K chunks)
- Simple API, fast to prototype

**3. Why all-MiniLM-L6-v2 for embeddings?**
- Small footprint (~80MB), fast inference
- Supports Chinese + English
- 384-dimensional vectors — good balance of accuracy and storage

**4. How did you choose chunk_size and overlap?**
- chunk_size=500: too large introduces noise, too small loses context
- overlap=50: maintains semantic continuity between adjacent chunks

**5. What role does LangChain play?**
- Document loaders, text splitters
- Encapsulates RAG Chain (retrieve + generate) — no manual prompt engineering
- Unified interface for embeddings and LLM calls

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| First run hangs | Downloading embedding model (~90MB) | Wait, or set `HF_HUB_OFFLINE=1` to use cache |
| Poor Chinese retrieval | all-MiniLM-L6-v2 is English-focused | Try `paraphrase-multilingual-MiniLM-L12-v2` |
| Inaccurate answers | chunk_size not optimal | Tune `chunk_size` (300-1000) and `overlap` (50-200) |
| ChromaDB Rust bindings error | Repeated PersistentClient creation on Streamlit rerun | Use EphemeralClient instead |
| Chinese PDF garbled text | Special PDF encoding | Try `pdfplumber` or `PyMuPDF` |
| API timeout | Network or DeepSeek service issues | Increase timeout, add retry logic |

### Future Enhancements

- **Better Chinese Embeddings** — Switch to BGE-large-zh or text2vec-large-chinese for improved Chinese semantic search
- **Real-time Document Sync** — Watch directory for changes, auto-update vector store
- **Multi-turn Conversation** — Query rewriting based on chat history for more natural follow-up questions
- **Access Control** — Restrict document access by department/role
- **Hybrid Retrieval** — Combine vector search + BM25 keyword search for better recall
- **RAG Evaluation** — Integrate RAGAS framework to evaluate answer quality (faithfulness, relevance)
- **Frontend Rewrite** — Rebuild with React/Vue for richer interactions (drag-and-drop, live search suggestions)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
