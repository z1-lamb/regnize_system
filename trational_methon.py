import pycorrector 

# 待纠正文本（包含错别字）
text = "少先队员因该为老人让坐"

# 调用 pycorrector 进行纠错
corrected_text, detail = pycorrector.correct(text)

# 输出结果
print("原句：", text)
print("纠正后：", corrected_text)
print("错误详情：", detail)  # [(错字, 正确字, 位置)]
