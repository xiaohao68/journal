# journal
journal_information

## Vercel 环境变量

部署到 Vercel 后，需要在项目的 `Settings -> Environment Variables` 中配置：

```text
ZHIPUAI_API_KEY=你的智谱 API Key
ZHIPUAI_MODEL=glm-4-flash
```

`ZHIPUAI_MODEL` 可选，不配置时默认使用 `glm-4-flash`。
