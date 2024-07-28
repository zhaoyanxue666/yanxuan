
此次分析仅供学习，禁作他用
# 知乎盐选小说批量下载 百分百还原
使用的库TTFont、PIL
PIL的包要 10 以下，建议 9.5.0
## 主要步骤：识别盐选反爬为字体反爬，通过使用 ddddocr 得到字体映射字典，将爬取的文本进行替换，得到初始文本
整体功能解释
初始化和配置：

导入必要的模块，如 requests、BeautifulSoup、re、base64、dddocr、PIL 等。
FontDecoder 类负责处理字体解码、OCR 识别、内容抓取和保存等功能。
使用 tkinter 模块打开文件夹选择对话框，允许用户选择下载路径。
字体解码和OCR：

FontDecoder 类包含多个方法：
_parse_cookies：将原始 Cookie 字符串解析为字典。
fetch_content：发送请求并获取网页内容。
save_content：保存网页内容到文件。
recognize_font：识别字体映射关系，通过 OCR 识别字符。
replace_string_matches：使用映射字典替换字符串中的匹配项。
my_replace_text：替换文本内容并保存到新文件。
抓取和处理网页内容：

get_firstsession 函数负责抓取和处理每一节的网页内容：
发送请求获取内容并解析。
提取标题并保存内容到文件。
查找并处理 Base64 编码的字体文件。
使用 OCR 识别字体映射关系，并替换文本中的特殊字符。
查找下一节的 URL。
主程序：

使用 tkinter 选择下载路径。
从 ck.txt 文件读取 cookies。
设置请求头信息。
初始化 FontDecoder 实例。
循环抓取每一节内容，直到没有下一节为止。

![image](https://github.com/user-attachments/assets/e1e453e9-6a29-4fa4-8ef1-afabd0fa6ef8)

# 使用方法
填写 cookies:
cookies_raw = '这里输入你的 cookies' 
firstsession_url = '这里要输入严选小说的第一节链接'

# 关键代码函数recognize_font、、replace_string_matches
recognize_font主要功能：解码 base64 字体文件，通过 ddddocr 生成映射字典

replace_string_matches 对已经保存的乱码文字通过字典进行还原



# 感谢anchovy126大佬修改
# Q 群210909794  学习交流
有 chatgptplus 合租

遵守开源协议，请下载测试后删除脚本，禁用违法用途，如有任何纠纷，由使用者承担
