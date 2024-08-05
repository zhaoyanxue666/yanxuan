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
        self.cookies_dict = self._parse_cookies(cookies_raw)
        self.ocr_engine = ddddocr.DdddOcr()
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update(self.cookies_dict)

    @staticmethod
    def _parse_cookies(cookies_raw):
        return {cookie.split('=')[0]: '='.join(cookie.split('=')[1:]) for cookie in cookies_raw.split('; ')}

    def fetch_content(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        time.sleep(2)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup, response.text

    def save_content(self, soup, title, folder_path, file_type='txt'):
        filename = f"{title}.{file_type}"
        full_path = os.path.join(folder_path, filename)
        if file_type == 'html':
            content = str(soup)
        else:
            content = '\n'.join(tag.get_text() for tag in soup.find_all('p'))
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已保存到：{full_path}")

    def recognize_font(self, font_path):
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
                recognized_text = self.ocr_engine.classification(img)
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
    def convert_dialogue(self, text):
        # 匹配以"广"开头，以"上"结尾的文本，中间可以是任何内容
        pattern = r'广(.*?)上'
        
        # 替换函数
        def replace(match):
            # 获取匹配的内容（不包括"广"和"上"）
            content = match.group(1)
            # 返回用「」包围的内容
            return f'「{content}」'
        
        # 使用re.sub进行替换
        converted_text = re.sub(pattern, replace, text)
        
        # 替换 "o" 为 "。"
        converted_text = converted_text.replace('o', '。')
        
        # 替换 "I" 为 "！"
        converted_text = converted_text.replace('I', '！')
        
        return converted_text
    def replace_string_matches(self, input_str, mapping_dict):
        pattern = re.compile("|".join(re.escape(key) for key in mapping_dict.keys()))

        def replace_callback(match):
            key = match.group(0)
            return mapping_dict[key]

        output_str = pattern.sub(replace_callback, input_str)
        return output_str

    def my_replace_text(self, input_file, output_file, replace_dict, folder_path):
        input_path = os.path.join(folder_path, input_file)
        output_path = os.path.join(folder_path, output_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 然后执行原有的替换逻辑
            content = self.replace_string_matches(content, replace_dict)
            # 首先执行新的替换逻辑
            content = self.convert_dialogue(content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


        print("文本替换完成，结果已保存至：", output_path)
        os.remove(input_path)
        print(f"已删除文件：{input_path}")

def get_firstsession(url, i, folder_path, decoder):
    try:
        soup, text_response = decoder.fetch_content(url)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None

    title_tag = soup.find('h1')
    title = title_tag.text if title_tag else "未找到标题"

    decoder.save_content(soup, title, folder_path, file_type='txt')

    pattern = r"@font-face\s*\{[^\}]*?src:\s*url\(data:font/ttf;charset=utf-8;base64,([A-Za-z0-9+/=]+)\)"
    matches = re.findall(pattern, text_response)
    if matches and len(matches) > 2:
        base64_font_data = matches[2]
        decoded_font_data = base64.b64decode(base64_font_data)
        font_file_path = "/tmp/font_file.ttf"
        with open(font_file_path, "wb") as font_file:
            font_file.write(decoded_font_data)
        print(f"字体文件已成功保存到：{font_file_path}")

        mapping_dict = decoder.recognize_font(font_file_path)
        input_file = f'{title}.txt'
        output_file = f'第{i}节{title}.txt'
        decoder.my_replace_text(input_file, output_file, mapping_dict, folder_path)
        os.remove(font_file_path)
        
    url_pattern = re.compile(r'"next_section":{[^}]*"url":"(https?://[^"]+)"')
    match = url_pattern.search(text_response)
    if match:
        url = match.group(1)
        print("下一节连接:"+url)
        return url
    else:
        print("未找到下一节URL。")
        return None

if __name__ == '__main__':

    folder_path = '/Users/yanxue/Download/'
   



    firstsession_url = 'https://www.zhihu.com/market/paid_column/1799112318019334144/section/1801706263165427714'

    cookies = '填写自己ck'
   

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
       
    }

    decoder = FontDecoder(headers, cookies)

    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"成功创建或确认文件夹存在：{folder_path}")
    except Exception as e:
        print(f"创建文件夹 {folder_path} 时发生错误：{e}")

    i = 1
    next_url = get_firstsession(firstsession_url, i, folder_path, decoder)
    while next_url:
        i += 1
        time.sleep(5)
        next_url = get_firstsession(next_url, i, folder_path, decoder)
