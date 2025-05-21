import pycorrector 
from pycorrector import Corrector

m = Corrector()
text = input("请输入待纠错文本：")

corrected_text = m.correct(text) 

print("\n原始文本：", text)
print("\n")
print("纠正后文本：", corrected_text)

