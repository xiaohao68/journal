import os
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import jwt


API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4-flash"

system_prompt = """
你是一名期刊分析专家，请根据下面参考资料，回答用户想要的期刊，并详细写出关于期刊的全部信息。
输出条理清晰，分点说明，语言专业易懂。
必须严格按照文档知识回答，不得擅自编造答案，仔细查看检索出来的内容进行回答，若检索不出来答案请回答者无法查阅你想要的期刊
例子1
用户提问：私欲直播
检索出来的内容如下：
论文标题：私域直播套路深  精准围猎老年人 - 中国知网；作者：张文章；关键词： 消费者;虚假宣传;老年人; ；摘要：9月26日，福建省消费者权益保护委员会联合黑龙江、江苏等16省市消协组织及《中国消费者》杂志，共同发布《“护银龄破暗域”私域直播乱象消费调查报告》。本次调查通过线上问卷与志愿者线下体察相结合的方式展开，系统地揭示了私域直播在精准围猎老年群体过程中存在的虚假宣传......；分类与时间：经济与管理科学 | 宏观经济管理与可持续发展 | 10.28867/n.cnki.nxfzb.2025.003144 | F203 | 2025-09-30（知网平台在线公开时间，不代表文献的发表时间）')
大模型生成的答案如下：
一、基础文献信息
文章标题：私域直播套路深 精准围猎老年人
作者：张文章
引题：16 省市消协组织及《中国消费者》杂志联合调查发现
正文快照：
9 月 26 日，福建省消费者权益保护委员会联合黑龙江、江苏等 16 省市消费者协会及《中国消费者》杂志，共同发布《“护银龄破暗域” 私域直播乱象消费调查报告》。本次调查通过线上问卷与志愿者线下体察相结合的方式展开，系统地揭示了私域直播在精准围猎老年群体过程中存在的虚假宣传相关乱象。
二、出版与标识信息
报纸出版日期：2025-09-30
版面号：001
DOI 编号：10.28867/n.cnki.nxfzb.2025.003144
中图分类号：F203（经济计划与管理）
知网在线公开时间：2025-09-30（备注：仅平台上线时间，不等同于纸质正式发表时间）
三、学科分类信息
专辑：经济与管理科学
专题：宏观经济管理与可持续发展
四、核心研究主题
调研主体：全国 16 省市消费者协会、《中国消费者》杂志、福建省消委会
调研对象：私域直播针对老年群体的营销乱象
调研手段：线上问卷 + 志愿者线下实地体察
核心问题：私域直播通过定向营销围猎老年消费者，存在大量虚假宣传行为
产出成果：《“护银龄破暗域” 私域直播乱象消费调查报告》
以上就是生成答案的例子
"""

human_prompt = """
请基于下面检索出来的内容进行回答：

{data}
"""


@dataclass
class AIResponse:
    content: str


class JournalPromptTemplate:
    def invoke(self, values):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": human_prompt.format(**values)},
        ]


class ZhipuChat:
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key

    def invoke(self, messages):
        try:
            return self._invoke_with_sdk(messages)
        except ModuleNotFoundError:
            return self._invoke_with_http(messages)

    def _invoke_with_sdk(self, messages):
        from zhipuai import ZhipuAI

        client = ZhipuAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return AIResponse(content=response.choices[0].message.content)

    def _invoke_with_http(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "stream": False,
        }
        headers = {
            "Authorization": _get_jwt_token(self.api_key),
            "Accept": "application/json",
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return AIResponse(content=data["choices"][0]["message"]["content"])


def _get_zhipuai_api_key():
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if api_key:
        return api_key.strip().strip("'\"")

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith("ZHIPUAI_API_KEY"):
                continue
            _, value = line.split("=", 1)
            return value.split("#", 1)[0].strip().strip("'\"")

    raise RuntimeError("请在 Vercel 环境变量或本地 .env 中配置 ZHIPUAI_API_KEY。")


def _get_zhipuai_model():
    return os.getenv("ZHIPUAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _get_jwt_token(api_key):
    try:
        api_id, secret = api_key.split(".")
    except ValueError as exc:
        raise ValueError("ZHIPUAI_API_KEY 格式不正确。") from exc

    timestamp = int(round(time.time() * 1000))
    payload = {
        "api_key": api_id,
        "exp": timestamp + 3 * 60 * 1000,
        "timestamp": timestamp,
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


prompt_template = JournalPromptTemplate()


def get_llm():
    return ZhipuChat(model=_get_zhipuai_model(), api_key=_get_zhipuai_api_key()), prompt_template
