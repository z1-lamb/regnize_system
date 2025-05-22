from openai import OpenAI
import json
import re

# ✅ 使用 DeepSeek 的 API Key 和 base_url
client = OpenAI(
    api_key="########################",  # ← 替换为你的真实 Key
    base_url="https://api.deepseek.com"
)

def detect_typo_with_deepseek(text):
    prompt = f"""
你是一个金融文本纠错专家，请帮我识别并纠正下列文本中的错别字。
请输出标准 JSON 格式，包含以下字段：
- corrected_text：纠正后的文本
- corrections：一个列表，每条包含 original（原错字）、corrected（正确字）、position（错字在文本中的位置）

文本如下：
{text}
""".strip()

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个中文金融文本纠错助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw_content = response.choices[0].message.content
        print("\n📨 LLM 原始返回：\n", raw_content)

        # 清理 ```json 包裹
        clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_content.strip())
        result = json.loads(clean_json)

        return result

    except Exception as e:
        print("❌ 调用 DeepSeek API 出错：", str(e))
        return None

if __name__ == "__main__":
    while True:
        user_input = input("\n请输入要纠正的金融文本（输入 q 退出）：\n> ")
        if user_input.lower() == 'q':
            print("程序退出。")
            break

        result = detect_typo_with_deepseek(user_input)

        if result:
            print("\n✅ 纠正结果：")
            print("原文：", user_input)
            print("纠正后：", result["corrected_text"])
            print("修改详情：")
            for item in result["corrections"]:
                print(f"- 错字: {item['original']} → 正确: {item['corrected']}（位置: {item['position']}）")
        else:
            print("⚠️ 无法获取纠正结果，请检查输入或 API Key。")
