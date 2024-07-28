import os
import time
import requests
from bs4 import BeautifulSoup
import re
import base64
from fontTools.ttLib import TTFont
import ddddocr
from PIL import ImageFont, Image, ImageDraw
from tkinter import Tk
from tkinter.filedialog import askdirectory

class FontDecoder:
    def __init__(self, headers, cookies_raw):
        self.headers = headers
        self.cookies_dict = self._parse_cookies(cookies_raw)  # 将原始 Cookie 字符串解析为字典
        self.ocr_engine = ddddocr.DdddOcr()  # 初始化 OCR 引擎
        self.session = requests.Session()  # 创建一个会话对象
        self.session.headers.update(headers)  # 更新会话的 headers
        self.session.cookies.update(self.cookies_dict)  # 更新会话的 cookies

    @staticmethod
    def _parse_cookies(cookies_raw):
        # 将原始 Cookie 字符串解析为字典
        return {cookie.split('=')[0]: '='.join(cookie.split('=')[1:]) for cookie in cookies_raw.split('; ')}

    def fetch_content(self, url):
        # 发送请求获取内容
        response = self.session.get(url)
        response.raise_for_status()  # 确保请求成功
        time.sleep(2)  # 等待 2 秒
        soup = BeautifulSoup(response.text, 'html.parser')  # 解析页面内容
        return soup, response.text

    def save_content(self, soup, title, folder_path, file_type='txt'):
        # 保存内容到文件
        filename = f"{title}.{file_type}"
        full_path = os.path.join(folder_path, filename)
        if file_type == 'html':
            content = str(soup)
        else:
            content = '\n'.join(tag.get_text() for tag in soup.find_all('p'))  # 提取所有段落的文本
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已保存到：{full_path}")

    def recognize_font(self, font_path):
        # 识别字体映射关系
        with open(font_path, 'rb') as f:
            font = TTFont(f)
            cmap = font.getBestCmap()
            unicode_list = list(cmap.keys())

        recognition_dict = {}
        failed_recognitions = []

        for unicode_code in unicode_list:
            char = chr(unicode_code)
            img_size = 128
            img = Image.new('RGB', (img_size, img_size), 'white')
            draw = ImageDraw.Draw(img)
            font_size = int(img_size * 0.7)
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = draw.textsize(char, font=font)
            draw.text(((img_size - text_width) / 2, (img_size - text_height) / 2), char, fill='black', font=font)

            try:
                recognized_text = self.ocr_engine.classification(img)  # 使用 OCR 识别字符
                if recognized_text:
                    recognition_dict[char] = recognized_text[0]
                else:
                    failed_recognitions.append(char)
            except Exception as e:
                print(f"在识别字符 {char} 时发生错误: {e}")
                failed_recognitions.append(char)

        if failed_recognitions:
            print(f"以下字符未能成功识别: {failed_recognitions}")
        else:
            print("所有字符识别成功并构建了映射字典。")

        print("字体映射字典:", recognition_dict)

        return recognition_dict

    def replace_string_matches(self, input_str, mapping_dict):
        # 使用映射字典替换字符串中的匹配项
        pattern = re.compile("|".join(re.escape(key) for key in mapping_dict.keys()))

        def replace_callback(match):
            key = match.group(0)
            return mapping_dict[key]

        output_str = pattern.sub(replace_callback, input_str)
        return output_str

    def my_replace_text(self, input_file, output_file, replace_dict, folder_path):
        # 替换文本内容并保存到新文件
        input_path = os.path.join(folder_path, input_file)
        output_path = os.path.join(folder_path, output_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = self.replace_string_matches(content, replace_dict)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("文本替换完成，结果已保存至：", output_path)
        os.remove(input_path)
        print(f"已删除文件：{input_path}")

def get_firstsession(url, i, folder_path, decoder):
    try:
        soup, text_response = decoder.fetch_content(url)  # 获取并解析内容
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None

    title_tag = soup.find('h1')
    title = title_tag.text if title_tag else "未找到标题"  # 获取标题

    decoder.save_content(soup, title, folder_path, file_type='txt')  # 保存内容到文件

    pattern = r"@font-face\s*\{[^\}]*?src:\s*url\(data:font/ttf;charset=utf-8;base64,([A-Za-z0-9+/=]+)\)"
    matches = re.findall(pattern, text_response)  # 查找 Base64 编码的字体文件
    if matches and len(matches) > 2:
        base64_font_data = matches[2]  # 注意这里是2而不是0，匹配的是具体的字体
        decoded_font_data = base64.b64decode(base64_font_data)
        font_file_path = "/tmp/font_file.ttf"  # 将临时字体文件保存在 /tmp 目录中
        with open(font_file_path, "wb") as font_file:
            font_file.write(decoded_font_data)
        print(f"字体文件已成功保存到：{font_file_path}")

        mapping_dict = decoder.recognize_font(font_file_path)  # 识别字体映射关系
        input_file = f'{title}.txt'
        output_file = f'第{i}节{title}.txt'
        decoder.my_replace_text(input_file, output_file, mapping_dict, folder_path)
        os.remove(font_file_path)

    url_pattern = re.compile(r'"next_section":{[^}]*"url":"(https?://[^"]+)"')  # 寻找下一节链接
    match = url_pattern.search(text_response)
    if match:
        url = match.group(1)
        print("下一节连接:" + url)
        return url
    else:
        print("未找到下一节URL。")
        return None

if __name__ == '__main__':
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = askdirectory(title="选择下载路径")  # 打开文件夹选择对话框
    root.destroy()  # 关闭主窗口

    if not folder_path:
        print("未选择下载路径，程序退出。")
        exit()

    firstsession_url = input("请输入下载的第一节URL (例如：https://www.zhihu.com/market/paid_column/1634930379587784704/section/1634931949033426944): ")

    try:
        with open("ck.txt", "r", encoding="utf-8") as file:
            cookies = file.read().strip()  # 从文件读取 cookies
    except FileNotFoundError:
        print("ck.txt 文件未找到，请确保该文件存在并包含 cookies 信息。")
        exit()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8'
    }

    decoder = FontDecoder(headers, cookies)

    try:
        os.makedirs(folder_path, exist_ok=True)  # 创建目录
        print(f"成功创建或确认文件夹存在：{folder_path}")
    except Exception as e:
        print(f"创建文件夹 {folder_path} 时发生错误：{e}")

    i = 1
    next_url = get_firstsession(firstsession_url, i, folder_path, decoder)  # 下载第一节内容
    while next_url:  # 循环下载每一节内容，直到没有下一节为止
        i += 1
        time.sleep(5)  # 每次下载之间等待 5 秒
        next_url = get_firstsession(next_url, i, folder_path, decoder)
