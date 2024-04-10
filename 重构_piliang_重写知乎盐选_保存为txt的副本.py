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
    cookies_raw = '_zap=1222246a-aa4c-4c46-b2e3-8861a8ceadc6; d_c0=AWBRHlN3WRePTiRp3JPEUjIhL-5dxLplxsc=|1693920960; YD00517437729195%3AWM_NI=3trIZkborAx%2BSpoImolhTkdY1kJLc1iVCu5cTPy%2Fl2VvblO7eU6w2s2lcVe9QkgXpnXEjJ6FFkV4%2BMIhUuz1Jb6mY8FkO7YathR0MBp0IkendKgGipMlKwZuFise5Z5VUHc%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eea9ee70f4eec0d6fc3ab49e8fb7c84a878e9bb0d56688a8fe88d339a69882aef92af0fea7c3b92af1acbeaad961a2b1bea2fb2191b0a1aaf065b0b89c8ce753f3b586ade23bab8a8d96b8699890b7d0ef3a96aaae8dce3da78bfa98b179f2b4adb7e83393b5a9b9f3669c9ba6abb54e86b59ad5aa478bb89b96f93b8abefa8edc3486b581d8dc6bb8b89ed1d04ab4f0878ce866a895a9a8ec7c8fb48598d97f86b7bd86b852f78a9ba9e237e2a3; YD00517437729195%3AWM_TID=HDPyYblb7TVBVEEFFUbAyDgmhfnbCNYn; q_c1=a38952338eb947fcbbcaa37004b83cd1|1696159265000|1696159265000; _xsrf=wtpCfFgc62J2Nyu1lbpVpg66spt8I4wx; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1710926382,1711101461,1711420900,1712191771; q_c1=a38952338eb947fcbbcaa37004b83cd1|1712305948000|1696159265000; captcha_session_v2=2|1:0|10:1712312523|18:captcha_session_v2|88:cm5SbmIyTmlRdXdzMjE1N2tVQ2ptTUVzZWJTRDZETUh2Nlh6ZnJROE9jbnd1Tm5xaXQ4cVlvTHJZOU5FZHpKeA==|ace480bd845c92daf7bd1fa5e09d5c6bdbfe408f71b8dc3c27020dcedb6999b1; SESSIONID=m63ujBQdiuhnEYiXEmThfgns4om29Ib6OMecjEtkqG4; JOID=UFoTBkxELZqyYywuJEJIDYc1XHI3KR-qxQxue0MoWPbfJHBHeIz6lNNmKCkl6Ke5qWzVvGywYD-P8ov8cLxQtf8=; osd=UF4VB0lEKZyzZiwqIkNNDYMzXXc3LRmrwAxqfUItWPLZJXVHfIr7kdNiLigg6KO_qGnVuGqxZT-L9Ir5cLhWtPo=; __snaker__id=6yosHL4Oxi3POX2x; gdxidpyhxdE=g7gy%2FdS%2FWDBW14xA%5C%2FhWw%2BVdvbhCsh9P2SaEAAda3oPzS8IErWCdSkwRLE%5Cb6ui9qiLKQqiDV4SKLYV31o0w%2B2LnSvVPOB%5C92Sb9mvxBg%2FkvNU80x9NAma0nPfrOB%2F53nOcOklnKOBYuPYChDZ5ea5Jq%5CEmOnjLripDGDUzt18f1mtVt%3A1712313424891; o_act=login; ref_source=other_https://www.zhihu.com/signin?next=https://www.zhihu.com/market/paid_column/1720820710732206080/section/1720813077795295233; expire_in=15552000; tst=r; z_c0=2|1:0|10:1712312611|4:z_c0|92:Mi4xRS1fc0d3QUFBQUFCWUZFZVUzZFpGeGNBQUFCZ0FsVk5HaF85WmdBY2kwYnB3bVpkN05CMTZ3NlNSRFJsT0wxNEVB|ba60a23c92f03b0c22f964cd5f6d4ca457531776ceedc3741917ce8adab4befd; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1712312699; KLBRSID=ed2ad9934af8a1f80db52dcb08d13344|1712312700|1712302568'
   

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
