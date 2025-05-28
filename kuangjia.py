from openai import OpenAI
import json
import re
from pycorrector import Corrector

# DeepSeek API 初始化
client = OpenAI(
    api_key="sk-83444752ca6f437997542ad3d02746f0",
    base_url="https://api.deepseek.com"
)

def detect_typo_with_deepseek(text):
    prompt = f"""
你是一个金融文本纠错专家，请帮我识别并纠正下列文本中的错别字。
请输出标准 JSON 格式，包含以下字段：
- corrected_text：纠正后的文本
- corrections：一个列表，每条包含 original（原错字）、corrected（正确字）、position（错字在文本中的位置）
- message：如果文本无错别字，请 message 字段填“文本无错误”，并且 corrections 为空列表。

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
        clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_content.strip())
        result = json.loads(clean_json)
        return result
    except Exception as e:
        print("调用 DeepSeek API 出错：", e)
        return None

def local_correct(text):
    m = Corrector()
    corrected_text= m.correct(text)
    return corrected_text

if __name__ == "__main__":
    print("请选择纠错方式：")
    print("1 - 本地传统方法 (pycorrector)")
    print("2 - LLM 云端方法 (DeepSeek API)")
    choice = input("请输入选项数字(1或2)：")

    while True:
        text = input("\n请输入要纠正的文本（输入 q 退出）：\n> ")
        if text.lower() == 'q':
            print("程序退出。")
            break

        if choice == '1':
            corrected_text= local_correct(text)
            print("\n【本地传统方法纠正结果】")
            print("纠正后文本：", corrected_text)
        

        elif choice == '2':
            result = detect_typo_with_deepseek(text)
            if result.get("corrections") == []:
                print(" 文本无错误√")
            elif result.get("corrections") != []:
                print("\n【LLM 云端方法纠正结果】")
                print("纠正后文本：", result["corrected_text"])
                print("修改详情：")
                for item in result["corrections"]:
                    print(f"- 错字: {item['original']} → 正确: {item['corrected']}（位置: {item['position']}）")
            else:
                print(" DeepSeek API 无法获取纠正结果。")

        else:
            print("无效选项，请重新运行程序并输入 1 或 2。")
            break
