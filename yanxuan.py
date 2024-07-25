import os
import time
import requests
from bs4 import BeautifulSoup
import re
import base64
from fontTools.ttLib import TTFont
import ddddocr
from PIL import ImageFont, Image, ImageDraw
from aligo import Aligo
from flask import Flask, request

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

    def replace_string_matches(self, input_str, mapping_dict):
        pattern = re.compile("|".join(re.escape(key) for key in mapping_dict.keys()))

        def replace_callback(match):
            key = match.group(0)
            return mapping_dict[key]

        output_str = pattern.sub(replace_callback, input_str)
        return output_str

    def my_replace_text(self, input_file, output_file, replace_dict, folder_path):
        input_path = os.path.join(folder_path, input_file)  # 输入文件的完整路径
        output_path = os.path.join(folder_path, output_file)  # 输出文件的完整路径
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = self.replace_string_matches(content, replace_dict)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("文本替换完成，结果已保存至：", output_path)
##下载当前链接
def get_firstsession(url, i, folder_path):
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
    cookies_raw ='KLBRSID=d6f775bb0765885473b0cba3a5fa9c12|1718508469|1718505176;q_c1=127e964d73a14583814f3fcb76e954b2|1712405164000|1712405164000;tst=r;z_c0=2|1:0|10:1718508468|4:z_c0|92:Mi4xQWExd0FnQUFBQUFBMEZ6cjRheHNHQ1lBQUFCZ0FsVk5zcWxiWndCSG1ZVzZXakJvWGdtWUJieHFSYWlqZDFNRm1n|d788b17f0266949564480ae6e5c1452be4adba230f9151c55f2d9f44c259e3d9;gdxidpyhxdE=c3NfNI0ysjlBnQGCWNczj31U17qNo1tJ%2FZpQE4R9%2B3sYwciH09GEkvqPeYpq8HjDrlgeZxeO7LR%2B90%2FlX9q5%5C%5CYtMDf6GgaD%5CIPJXg0%5CALwlZRBQpN%2Be4Py0CiLVLqotadx3Drcc%2Fsj7XtI85c34qe87PnHzqXcSpU3R6xWj8%5C5gLn3%5C%3A1718509335958;_xsrf=xkxrVwKVuXBrIoVQNPDRBrUSJeUZrFEQ;BEC=04f80badde0b95441251f0ed57775ff7;captcha_session_v2=2|1:0|10:1718508434|18:captcha_session_v2|88:Vlk4UVN1RzY0aDJVMWVRYk5WQTFCWkcxK2JvczZNR3A1TVFPS2dLVHBjYm43QW0zbmVwZU5HdjZLZTZNVDQ0Rg==|98decfe14c572003774c13372871d62f7048f3cda9f89c477d03a6737776cbcb;__snaker__id=lqp42dmVsrC1Xnks;__zse_ck=001_2fkzm6Sc=MlXUCm+PcxWo1BxPbRsLyP+XyeEwBGRAuTobH7cbqxjTwzxHMB1To2es6=UjhqX8PGh2zgkvYWP3OT==yoYwYoGdw2GuE709EDAfvMdFZuQQPQILOryW8CW;_zap=0122a310-4a12-4976-8b50-7dd0c18171e9;d_c0=ANBc6-GsbBiPTop4fth74Y6AOXlohf2e4HE=|1712389937;Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1711420900,1712191771,1712389939,1712895889;q_c1=127e964d73a14583814f3fcb76e954b2|1718505684000|1712405164000;SESSIONID=wv1r7u52o9LJNX4J9sCJ3z0YUNwpCGJHfUgVOQJgaM6;unlock_ticket=AJDWelhPlRUmAAAAYAJVTZhibmbAkM4HzvcRxqpxkwBjGCkj_4BIBQ=='
    decoder = FontDecoder(url, headers, cookies_raw)
    soup, text_response = decoder.fetch_content()
    title_tag = soup.find('h1')
    title = title_tag.text if title_tag else "未找到标题"

    decoder.save_content(soup, title, folder_path, file_type='txt')
    
    pattern = r"@font-face\s*\{[^\}]*?src:\s*url\(data:font/ttf;charset=utf-8;base64,([A-Za-z0-9+/=]+)\)"
    matches = re.findall(pattern, text_response)
    if matches and len(matches) > 2:
        base64_font_data = matches[2]  # 注意这里是2而不是0，匹配的是具体的字体
        decoded_font_data = base64.b64decode(base64_font_data)
        font_file_path = "font_file.ttf"
        with open(font_file_path, "wb") as font_file:
            font_file.write(decoded_font_data)
        print(f"字体文件已成功保存到：{font_file_path}")

        mapping_dict = decoder.recognize_font(font_file_path)
        input_file = f'{title}.txt'
        output_file = f'第{i}节{title}.txt'
        
        decoder.my_replace_text(input_file, output_file, mapping_dict, folder_path)
        os.remove(font_file_path)
        
        input_file  = os.path.join(folder_path, input_file)
        # os.remove(input_file)
    url_pattern = re.compile(r'"next_section":{[^}]*"url":"(https?://[^"]+)"')
    match = url_pattern.search(text_response)
    ##寻找下一节链接
    if match:
        url = match.group(1)
        print("下一节连接:"+url)
        return url
    else:
        print("未找到下一节URL。")
        return None

if __name__ == '__main__':
    

    folder_path = f"/Users/yanxue/Downloads/小说下载/梆子声声"
    firstsession_url = 'https://www.zhihu.com/market/paid_column/1727644753636626432/section/1751628630944571392'
    i = 1
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"成功创建或确认文件夹存在：{folder_path}")
    except Exception as e:
        print(f"创建文件夹 {folder_path} 时发生错误：{e}")

    get_firstsession(firstsession_url, i, folder_path)
    
    next_url = get_firstsession(firstsession_url, i, folder_path)
    while next_url:
        i += 1
        time.sleep(5)
        next_url = get_firstsession(next_url, i, folder_path)
