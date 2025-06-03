import os
from volcenginesdkarkruntime import Ark
# 从环境变量中读取您的方舟API Key
client = Ark(api_key=os.environ.get("a104e834-a3c5-4760-a819-2e4dd8de484d"))
completion = client.chat.completions.create(
    # 替换 <Model>为 Model ID
    model="doubao-1-5-thinking-pro-250415",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)
print(completion.choices[0].message)