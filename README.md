
此次分析仅供学习，禁作他用
# 知乎盐选小说批量下载 百分百还原
使用的库TTFont、PIL
PIL的包要 10 以下，建议 9.5.0
## 主要步骤：识别盐选反爬为字体反爬，通过使用 ddddocr 得到字体映射字典，将爬取的文本进行替换，得到初始文本

代码大致解析
TTFont：将知乎的自定义字体反爬解析，知乎的自定义字体在html 源码的 stlye 的，采用 base64 编码
这里使用的是第三个 base64 编码，我一个一个试出来的

<img width="466" alt="image" src="https://github.com/zhaoyanxue666/-/assets/39113888/b67beb7b-ca9c-4877-8866-15b276b121cf">

# 使用方法
填写 cookies:
cookies_raw = '这里输入你的 cookies' 
firstsession_url = '这里要输入严选小说的第一节链接'

# 关键代码函数recognize_font、、replace_string_matches
recognize_font主要功能：解码 base64 字体文件，通过 ddddocr 生成映射字典

replace_string_matches 对已经保存的乱码文字通过字典进行还原



# 感谢anchovy126大佬修改
# Q 群210909794
有 chatgptplus 合租

遵守开源协议，请下载测试后删除脚本，禁用违法用途，如有任何纠纷，由使用者承担
