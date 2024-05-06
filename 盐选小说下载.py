import os
import time
import requests
from bs4 import BeautifulSoup
import re
import base64
from fontTools.ttLib import TTFont
import ddddocr
from PIL import ImageFont, Image, ImageDraw

class FontDecoder:
    def __init__(self, url, headers, cookies_raw):
        self.url = url
        self.headers = headers
        self.cookies_dict = self._parse_cookies(cookies_raw)
        self.ocr_engine = ddddocr.DdddOcr()

    @staticmethod
    def _parse_cookies(cookies_raw):
        return {cookie.split('=')[0]: '='.join(cookie.split('=')[1:]) for cookie in cookies_raw.split('; ')}

    def fetch_content(self):
        response = requests.get(self.url, headers=self.headers, cookies=self.cookies_dict)
        time.sleep(2)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup, response.text

    @staticmethod
    def save_content(soup, title, file_type='txt'):
        filename = f"{title}.{file_type}"
        if file_type == 'html':
            content = str(soup)
        else:
            content = '\n'.join(tag.get_text() for tag in soup.find_all('p'))
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已保存到：{filename}")

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

    def replace_string_matches(self, input_str, mapping_dict):
        pattern = re.compile("|".join(re.escape(key) for key in mapping_dict.keys()))

        def replace_callback(match):
            key = match.group(0)
            return mapping_dict[key]

        output_str = pattern.sub(replace_callback, input_str)
        return output_str

    def my_replace_text(self, input_file, output_file, replace_dict):
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            content = self.replace_string_matches(content, replace_dict)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("文本替换完成，结果已保存至：", output_file)

def get_firstsession(url, i):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'User-Agent: com.zhihu.android/9.30.0 (Android 10; Mobile;)',
    }
    cookies_raw = '填写你的 cookies'

    decoder = FontDecoder(url, headers, cookies_raw)
    soup, text_response = decoder.fetch_content()
    title_tag = soup.find('h1')
    title = title_tag.text if title_tag else "未找到标题"

    decoder.save_content(soup, title, file_type='txt')
    # decoder.save_content(soup, title, file_type='html')
    
    pattern = r"@font-face\s*\{[^\}]*?src:\s*url\(data:font/ttf;charset=utf-8;base64,([A-Za-z0-9+/=]+)\)"
    matches = re.findall(pattern, text_response)

    if matches:
        base64_font_data = matches[2]  # 注意这里是2而不是0，匹配的是具体的字体
        decoded_font_data = base64.b64decode(base64_font_data)
        font_file_path = "font_file.ttf"
        with open(font_file_path, "wb") as font_file:
            font_file.write(decoded_font_data)
        print(f"字体文件已成功保存到：{font_file_path}")

        mapping_dict = decoder.recognize_font(font_file_path)
        input_file = f'{title}.txt'
        output_file = f'第{i}节{title}.txt'
        decoder.my_replace_text(input_file, output_file, mapping_dict)
    os.remove(font_file_path)
    os.remove(input_file)
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
    firstsession_url = 'https://www.zhihu.com/market/paid_column/1730607810226688000/section/1731692951070281728'

    i = 1
    next_url = get_firstsession(firstsession_url, i)
    while next_url:
        i += 1
        time.sleep(2)
        next_url = get_firstsession(next_url, i)
