import json
from dataclasses import dataclass
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "journal_information.json"


@dataclass
class Document:
    page_content: str


def _format_document(item):
    authors = item.get("journal_author") or ["无作者"]
    if isinstance(authors, str):
        authors_text = authors
    else:
        authors_text = "、".join(authors) or "无作者"

    metadata = item.get("专题信息与公开时间") or item.get("journal_metadata") or []
    if isinstance(metadata, str):
        metadata_text = metadata
    else:
        metadata_text = " | ".join(str(value) for value in metadata)

    return (
        f"期刊标题：{item.get('journal_title', '无标题')}；"
        f"作者：{authors_text}；"
        f"关键词：{item.get('journal_keyword', '无关键词')}；"
        f"摘要：{item.get('journal_abstract', '无摘要')}；"
        f"分类与时间：{metadata_text}"
    )


def get_json_data():
    with DATA_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Document(page_content=_format_document(item)) for item in data]
