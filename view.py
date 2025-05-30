import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from pycorrector import Corrector
from openai import OpenAI
import json
import re

# 解决 matplotlib 中文显示问题（适合 Windows，Linux请安装字体替换字体名）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文黑体字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示为方块的问题

# 初始化 LLM (DeepSeek API)
client = OpenAI(
    api_key="sk-83444752ca6f437997542ad3d02746f0",  # ← 替换为你的 Key
    base_url="https://api.deepseek.com"
)

# 传统方法（pycorrector 1.1.2 版本）
def detect_pycorrector(text):
    corrector = Corrector()
    result = corrector.correct(text)

    corrected_text = None
    corrections = []

    if isinstance(result, dict):
        corrected_text = result.get('correct_text', text)
        errors = result.get('errors', [])

        if errors and isinstance(errors[0], tuple):
            for err in errors:
                corrections.append({
                    "original": err[0],     # 错误词
                    "corrected": err[1],    # 正确词
                    "position": err[2]      # 位置
                })
        else:
            corrections = []
    else:
        corrected_text = text

    return {
        "corrected_text": corrected_text,
        "corrections": corrections
    }


# LLM 方法
def detect_llm(text):
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
        raw = response.choices[0].message.content
        clean = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
        result = json.loads(clean)
        return result
    except Exception as e:
        print("❌ DeepSeek API 调用失败：", e)
        return {"corrected_text": text, "corrections": []}

# 示例测试文本
text = "近年来，中国经济持徐发展，科技创兴不断涌现。然而，在城是化过程中，一些环保问题逐渐突显，需哟政府和公众共同参与解决。同时，教育体系也面临着诸多挑站，特别是在偏远地趣，教育资源配置不均。我们应当加大对基础教育的投制，推动公平而优制的教育环境建设。"

# 获取结果
py_result = detect_pycorrector(text)
llm_result = detect_llm(text)

print("传统方法纠正后文本：", py_result["corrected_text"])
print("传统方法纠正详情：", py_result["corrections"])
print("LLM方法纠正后文本：", llm_result["corrected_text"])
print("LLM方法纠正详情：", llm_result["corrections"])

# 条形图：错字数量对比
py_count = len(py_result["corrections"])
llm_count = len(llm_result["corrections"])

plt.figure(figsize=(6, 4))
plt.bar(["传统方法", "LLM方法"], [py_count, llm_count], color=["skyblue", "lightgreen"])
plt.title("每条文本错字数量对比", fontdict={'family':'SimHei', 'size':14})
plt.ylabel("错字数量", fontdict={'family':'SimHei', 'size':12})
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("bar_comparison.png")
plt.show()

# Venn图：错字位置重合情况（用起始位置 position）
py_positions = set([item['position'] for item in py_result["corrections"] if item['position'] is not None])
llm_positions = set([item['position'] for item in llm_result["corrections"] if item['position'] is not None])

plt.figure(figsize=(5, 5))
venn2([py_positions, llm_positions], set_labels=("传统方法", "LLM方法"))
plt.title("错字位置重合 Venn 图", fontdict={'family':'SimHei', 'size':14})
plt.savefig("venn_comparison.png")
plt.show()
