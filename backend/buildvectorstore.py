from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

vectorstore_path="vectorstore"

def load_docs(folder_path):
    docs = []
    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        if file.endswith(".pdf"):
            docs.extend(PyMuPDFLoader(path).load())
        elif file.endswith(".docx"):
            docs.extend(Docx2txtLoader(path).load())
    return docs


def build_vectorstore(doc_path, vectorstore_path="vectorstore"):
    # 加载 PDF 和 Word 文档
    docs = load_docs(doc_path)  # doc 文件夹
    # 将文档切分为较小的段落块，便于向量化与匹配
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(docs)
    # 使用 HuggingFace 模型对文本生成向量嵌入
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    # 构建 FAISS 向量数据库，用于之后的“相似度检索”
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local(vectorstore_path)
    print(f"共向量化了 {len(vectorstore.docstore._dict)} 个文档片段")