"""
RAG 知识库问答系统 - 核心模块

功能：
1. 加载文档（PDF、Word、TXT）
2. 文档分块（Chunking）
3. 向量化存储（Embedding + Vector Store）
4. 检索 + 问答（Retrieval + Generation）
"""

import os
import glob
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ============================================================
# 配置
# ============================================================

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# DeepSeek 兼容 OpenAI 格式，所以用 OpenAI 的客户端类
# 模型名：deepseek-chat 是 DeepSeek 的对话模型
LLM_MODEL = "deepseek-chat"

# Embedding 模型：用 DeepSeek 官方的 embedding 模型
# 但为了离线可用，我们也支持本地方案
EMBEDDING_MODEL = "deepseek-chat"  # DeepSeek 暂无专用 embedding API，使用本地方案

# 向量数据库存储路径
VECTORSTORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorstore")

# 文档目录
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


# ============================================================
# 第一部分：文档加载（Document Loading）
# ============================================================

def load_document(file_path: str):
    """
    根据文件类型加载文档
    
    支持：.pdf, .docx, .txt
    返回：LangChain Document 对象列表
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext in (".txt", ".md"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 .pdf, .docx, .txt, .md")
    
    docs = loader.load()
    
    # 给每个文档片段加上源文件信息（方便后面做引用溯源）
    for doc in docs:
        doc.metadata["source_filename"] = os.path.basename(file_path)
    
    return docs


def load_all_documents(docs_dir: str = DOCS_DIR):
    """
    加载 docs 目录下的所有文档
    """
    all_docs = []
    
    # 支持的文件格式
    patterns = ["*.pdf", "*.docx", "*.txt", "*.md"]
    
    for pattern in patterns:
        files = glob.glob(os.path.join(docs_dir, pattern))
        for file_path in files:
            print(f"📄 正在加载: {os.path.basename(file_path)}")
            docs = load_document(file_path)
            all_docs.extend(docs)
            print(f"   ✓ 加载了 {len(docs)} 个文本片段")
    
    return all_docs


# ============================================================
# 第二部分：文档分块（Text Splitting / Chunking）
# ============================================================

def split_documents(documents, chunk_size: int = 500, chunk_overlap: int = 100):
    """
    将长文档切分成小块
    
    参数：
    - chunk_size: 每块的最大字符数（500 是个不错的起点）
    - chunk_overlap: 块之间的重叠字符数（保证上下文不丢失）
    
    为什么需要分块？
    - LLM 有上下文长度限制，不能一次处理整篇文档
    - 分块后可以精准检索到相关段落，而不是整篇文档
    - 500 字符大约是 200-300 个中文字，适合语义检索
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],  # 优先按段落、句子分割
        length_function=len,
    )
    
    chunks = splitter.split_documents(documents)
    print(f"✂️  文档分块完成: {len(documents)} 个片段 → {len(chunks)} 个小块")
    
    return chunks


# ============================================================
# 第三部分：向量化与存储（Embedding + Vector Store）
# ============================================================

def get_embeddings():
    """
    获取 Embedding 模型（将文本转成向量的工具）
    
    Embedding 是什么？
    - 把一段文字变成一串数字（向量）
    - 语义相近的文字，向量也相近
    - 这样就能用数学方法找"意思最接近"的段落
    
    这里使用 sentence-transformers 的本地模型，免费且不需要 API
    """
    # 使用 HuggingFace 开源的中文 embedding 模型
    # all-MiniLM-L6-v2 轻量且效果好，支持中英文
    from langchain_huggingface import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},  # 用 CPU 跑，有 GPU 可改为 "cuda"
    )
    
    return embeddings


def build_vector_store(chunks, persist_directory: str = VECTORSTORE_DIR):
    """
    构建向量数据库
    
    做了什么？
    1. 把每个文本块用 Embedding 模型转成向量
    2. 把向量和原文一起存到 ChromaDB（一个轻量向量数据库）
    3. 存到本地磁盘，下次不用重新计算
    """
    embeddings = get_embeddings()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )
    
    print(f"💾 向量数据库构建完成，存储在: {persist_directory}")
    print(f"   共 {len(chunks)} 个向量")
    
    return vectorstore


def load_vector_store(persist_directory: str = VECTORSTORE_DIR):
    """
    加载已有的向量数据库（不用重新计算 embedding）
    """
    embeddings = get_embeddings()
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    
    print(f"📂 从磁盘加载向量数据库: {persist_directory}")
    
    return vectorstore


# ============================================================
# 第四部分：检索 + 问答（Retrieval + Generation）
# ============================================================

def get_llm():
    """
    获取 DeepSeek 大语言模型
    
    这就是 RAG 中负责"生成回答"的部分
    """
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.1,  # 低温度 = 更稳定的回答，适合知识库问答
    )
    return llm


def create_rag_chain(vectorstore, top_k: int = 3):
    """
    创建 RAG 问答链（使用 LangChain LCEL 方式）
    
    工作流程：
    1. 用户提问
    2. 从向量数据库检索最相关的 top_k 个文档块
    3. 把问题和检索到的文档块一起发给 LLM
    4. LLM 基于文档内容生成回答
    """
    # 检索器：从向量库中找最相关的文档
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # 相似度检索
        search_kwargs={"k": top_k},  # 返回最相关的 k 个结果
    )
    
    llm = get_llm()
    
    # 提示词模板：告诉 AI 怎么回答
    system_prompt = """你是一个专业的知识库问答助手。请根据以下检索到的参考资料回答用户的问题。

要求：
1. 只根据提供的参考资料来回答，不要编造信息
2. 如果参考资料中没有相关信息，请如实告知用户"知识库中未找到相关信息"
3. 回答要简洁、准确、有条理
4. 如果答案来自参考资料，在回答末尾标注来源文件名

参考资料：
{context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # 格式化检索到的文档为文本
    def format_docs(docs):
        return "\n\n".join(
            doc.page_content for doc in docs
        )
    
    # 使用 LCEL 构建 RAG 链
    # RunnablePassthrough: 直接传递用户输入
    # retriever | format_docs: 检索并格式化文档
    # prompt: 填充模板
    # llm: 调用大模型
    # StrOutputParser: 提取纯文本回答
    chain = (
        {
            "context": retriever | format_docs,
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 用包装类同时保存 retriever 和 chain
    return {"chain": chain, "retriever": retriever}


def ask_question(rag_chain, question: str):
    """
    向 RAG 系统提问
    
    返回：answer（回答文本）+ sources（来源文档信息）
    """
    # 先检索文档（用于来源展示）
    docs = rag_chain["retriever"].invoke(question)
    
    # 再生成回答
    answer = rag_chain["chain"].invoke(question)
    
    # 提取来源信息
    sources = []
    for doc in docs:
        source_info = {
            "filename": doc.metadata.get("source_filename", "未知文件"),
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
        }
        # 去重
        if source_info not in sources:
            sources.append(source_info)
    
    return answer, sources


# ============================================================
# 第五部分：一键构建（从文档到可用系统的完整流程）
# ============================================================

def build_knowledge_base(docs_dir: str = DOCS_DIR, vectorstore_dir: str = VECTORSTORE_DIR):
    """
    一键构建知识库
    
    完整流程：加载文档 → 分块 → 向量化 → 存储
    """
    print("=" * 50)
    print("🚀 开始构建 RAG 知识库")
    print("=" * 50)
    
    # Step 1: 加载文档
    print("\n📥 第一步：加载文档...")
    documents = load_all_documents(docs_dir)
    
    if not documents:
        print("⚠️  docs 目录下没有找到任何文档！")
        print(f"   请将 PDF/DOCX/TXT 文件放入: {docs_dir}")
        return None
    
    # Step 2: 文档分块
    print("\n✂️  第二步：文档分块...")
    chunks = split_documents(documents)
    
    # Step 3: 向量化存储
    print("\n🔢 第三步：向量化存储（首次运行需要下载模型，请耐心等待）...")
    vectorstore = build_vector_store(chunks, vectorstore_dir)
    
    print("\n" + "=" * 50)
    print("✅ 知识库构建完成！现在可以开始提问了")
    print("=" * 50)
    
    return vectorstore


def get_or_build_knowledge_base(docs_dir: str = DOCS_DIR, vectorstore_dir: str = VECTORSTORE_DIR):
    """
    智能加载或构建知识库
    
    如果向量数据库已存在，直接加载（秒开）
    如果不存在，从文档重新构建
    """
    if os.path.exists(vectorstore_dir) and os.listdir(vectorstore_dir):
        print("📂 检测到已有向量数据库，直接加载...")
        return load_vector_store(vectorstore_dir)
    else:
        return build_knowledge_base(docs_dir, vectorstore_dir)


# ============================================================
# 测试入口
# ============================================================

if __name__ == "__main__":
    # 构建知识库
    vectorstore = get_or_build_knowledge_base()
    
    if vectorstore:
        # 创建问答链
        rag_chain = create_rag_chain(vectorstore)
        
        # 交互式问答
        print("\n💬 知识库问答系统已就绪！输入问题开始提问，输入 'quit' 退出")
        print("-" * 50)
        
        while True:
            question = input("\n🙋 你的问题: ").strip()
            
            if question.lower() in ["quit", "exit", "q", "退出"]:
                print("👋 再见！")
                break
            
            if not question:
                continue
            
            answer, sources = ask_question(rag_chain, question)
            
            print(f"\n🤖 回答:\n{answer}")
            
            if sources:
                print(f"\n📎 来源: {', '.join(s['filename'] for s in sources)}")
