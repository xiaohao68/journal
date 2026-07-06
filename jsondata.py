from pathlib import Path

from langchain_community.document_loaders import JSONLoader


DATA_PATH = Path(__file__).resolve().parent / "journal_information.json"

def get_json_data():
    data = JSONLoader(
        str(DATA_PATH),
        jq_schema=r'''.[] | "期刊标题：\(.journal_title)；作者：\(.journal_author | join("、"))；关键词：\(.journal_keyword)；摘要：\(.journal_abstract)；分类与时间：\(if has("专题信息与公开时间") then .["专题信息与公开时间"] | join(" | ") else .journal_metadata | join(" | ") end)"''',
    )
    json_data = data.load()
    return json_data
