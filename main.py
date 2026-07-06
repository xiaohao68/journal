
import sys
import os

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
def resource_path(relative_path):
    """获取资源文件绝对路径，兼容开发 & PyInstaller打包"""
    try:
        # 打包exe临时解压目录
        base_path = sys._MEIPASS
    except Exception:
        # 本地开发：当前main.py文件所在文件夹
        base_path = os.path.dirname(os.path.abspath(__file__))
        print("本地基础路径：", base_path)
    return os.path.join(base_path, relative_path)

app=FastAPI(title="期刊获取")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static",StaticFiles(directory=resource_path("template"),html=True))





from model import QueryRequest,Journal_Response
from retriever import get_retriever
retriever=get_retriever()
from llm import get_llm
llm = None
prompt_template = None


def get_chat_chain():
    global llm, prompt_template
    if llm is None or prompt_template is None:
        llm, prompt_template = get_llm()
    return llm, prompt_template


@app.get("/")
def index():
    return FileResponse(resource_path("template/index.html"))

#这里如果不加body，会默认为查询参数
@app.post("/journal_information")
def get_journal(request:QueryRequest=Body(...)):
    try:
        journal = request.journal.strip()
        if not journal:
            return Journal_Response(journal_information="请输入要查询的期刊关键词。")

        retriever_data = retriever.invoke(journal)
        if not retriever_data:
            return Journal_Response(journal_information="无法查阅你想要的期刊。")

        context_text = "\n\n".join(doc.page_content for doc in retriever_data)
        llm, prompt_template = get_chat_chain()
        prompt_value = prompt_template.invoke({"data": context_text})
        response = llm.invoke(prompt_value)
        print("response结果为:",response.content)
        return Journal_Response(journal_information=response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务异常：{str(e)}") from e


if __name__=="__main__":
    import  uvicorn
    uvicorn.run("main:app",port=8000,host="127.0.0.1",reload=True)
