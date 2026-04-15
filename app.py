"""
RAG 知识库问答系统 - Web 前端界面

运行方式：streamlit run app.py
"""

import os
import sys
import time
import tempfile
import shutil

import streamlit as st

# 确保能导入同目录下的 rag_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_engine import (
    get_or_build_knowledge_base,
    create_rag_chain,
    ask_question,
    load_document,
    split_documents,
    build_vector_store,
    DOCS_DIR,
    VECTORSTORE_DIR,
)

# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="星辰科技 - 企业知识库问答系统",
    page_icon="🏢",
    layout="wide",
)

# ============================================================
# 自定义样式
# ============================================================

st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        text-align: center;
        padding: 20px 0;
    }
    
    /* 对话气泡样式 */
    .chat-answer {
        background-color: #f0f4ff;
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #4f8ef7;
        margin: 8px 0;
    }
    
    .chat-question {
        background-color: #f8f9fa;
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #6c757d;
        margin: 8px 0;
    }
    
    /* 来源信息样式 */
    .source-tag {
        display: inline-block;
        background-color: #e9ecef;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 初始化 Session State
# ============================================================

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kb_built" not in st.session_state:
    st.session_state.kb_built = False

# ============================================================
# 侧边栏 - 知识库管理
# ============================================================

with st.sidebar:
    st.header("⚙️ 知识库管理")
    
    # 显示当前文档
    st.subheader("📁 当前文档")
    
    if os.path.exists(DOCS_DIR):
        doc_files = [f for f in os.listdir(DOCS_DIR) 
                     if f.lower().endswith(('.pdf', '.docx', '.txt', '.md'))]
        if doc_files:
            for f in doc_files:
                st.text(f"📄 {f}")
        else:
            st.info("暂无文档，请上传")
    else:
        st.info("暂无文档，请上传")
    
    st.divider()
    
    # 上传新文档
    st.subheader("📤 上传文档")
    uploaded_files = st.file_uploader(
        "支持 PDF、DOCX、TXT、Markdown 格式",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        key="file_uploader",
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # 保存到 docs 目录
            save_path = os.path.join(DOCS_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ 已上传: {uploaded_file.name}")
    
    st.divider()
    
    # 构建知识库按钮
    st.subheader("🔨 操作")
    
    build_clicked = st.button(
        "构建 / 重建知识库",
        type="primary",
        use_container_width=True,
        help="将 docs 目录中的文档向量化，构建可检索的知识库",
    )
    
    if build_clicked:
        with st.spinner("正在构建知识库，首次运行需下载模型，请稍候..."):
            # 先清除旧的 RAG chain（释放 ChromaDB 的文件锁）
            st.session_state.pop("rag_chain", None)
            
            # 清除旧的向量数据库（使用 gc + onerror 处理 Windows 文件锁）
            if os.path.exists(VECTORSTORE_DIR):
                import gc
                gc.collect()
                # Windows 下文件可能被占用，逐个删除
                for attempt in range(5):
                    try:
                        shutil.rmtree(VECTORSTORE_DIR)
                        break
                    except PermissionError:
                        time.sleep(0.5)
                        gc.collect()
                else:
                    st.warning("⚠️ 旧知识库文件被占用，尝试覆盖构建...")
            
            vectorstore = get_or_build_knowledge_base()
            if vectorstore:
                st.session_state.rag_chain = create_rag_chain(vectorstore)
                st.session_state.kb_built = True
                st.session_state.messages = []  # 清空对话历史
                st.success("✅ 知识库构建完成！可以开始提问了")
                st.rerun()  # 刷新页面，确保状态同步
    
    # 清空对话
    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # 参数调整
    st.subheader("📊 检索参数")
    top_k = st.slider("检索结果数量", 1, 10, 3, 
                       help="每次检索返回的文档块数量，越多越全面但可能引入噪声")
    
    # 重新创建 chain（如果参数变化）
    if st.session_state.rag_chain and top_k != 3:
        # 简单处理：top_k 变化时需要重建
        pass  # 实际应用中可以动态调整

# ============================================================
# 主页面
# ============================================================

# 标题
st.markdown("""
<div class="main-title">
    <h1>🏢 星辰科技 · 企业知识库问答系统</h1>
    <p style="color: #6c757d; font-size: 16px;">
        上传文档 → 构建知识库 → 开始提问 | 基于 LangChain + DeepSeek + ChromaDB
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# 如果知识库未构建，显示引导
if not st.session_state.kb_built:
    # 检查是否有自动加载的可能
    if os.path.exists(VECTORSTORE_DIR) and os.listdir(VECTORSTORE_DIR):
        with st.spinner("正在加载已有知识库..."):
            vectorstore = get_or_build_knowledge_base()
            st.session_state.rag_chain = create_rag_chain(vectorstore)
            st.session_state.kb_built = True
            st.success("✅ 已加载已有知识库！")

if not st.session_state.kb_built:
    st.info("👋 欢迎使用企业知识库问答系统！\n\n"
            "**使用步骤：**\n"
            "1. 在左侧上传 PDF/DOCX/TXT/Markdown 文档\n"
            "2. 点击「构建知识库」按钮\n"
            "3. 在下方输入问题，开始提问")
    
    # 快速开始区域
    st.markdown("---")
    st.subheader("🚀 快速开始")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **什么是 RAG？**
        
        RAG（检索增强生成）是一种让 AI 基于你的文档来回答问题的技术。
        
        - 📥 导入你的文档
        - 🔍 AI 先在文档中查找相关信息
        - 💬 基于查找到的内容生成回答
        - 📎 引用来源，可追溯
        """)
    
    with col2:
        st.markdown("""
        **支持的功能：**
        
        - ✅ 多种文件格式（PDF、Word、TXT）
        - ✅ 语义检索（理解问题含义）
        - ✅ 来源追溯（答案引用原始文档）
        - ✅ 中文支持
        
        **技术栈：**
        
        - LangChain（AI 应用框架）
        - DeepSeek（大语言模型）
        - ChromaDB（向量数据库）
        - Streamlit（Web 界面）
        """)

else:
    # 显示对话历史
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📎 查看来源"):
                        for source in msg["sources"]:
                            st.markdown(f"**{source['filename']}**")
                            st.code(source["content"])
    
    # 输入框
    if question := st.chat_input("在这里输入你的问题..."):
        # 显示用户问题
        with st.chat_message("user"):
            st.write(question)
        
        st.session_state.messages.append({"role": "user", "content": question})
        
        # 生成回答
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                try:
                    answer, sources = ask_question(st.session_state.rag_chain, question)
                    
                    st.markdown(answer)
                    
                    # 显示来源
                    if sources:
                        with st.expander("📎 来源文档"):
                            for source in sources:
                                st.markdown(f"**📄 {source['filename']}**")
                                st.code(source["content"])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })
                    
                except Exception as e:
                    st.error(f"出错了: {str(e)}")
                    st.info("提示：请检查 .env 文件中的 API Key 是否正确")
