import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import time
from datetime import datetime
#streamlit run SangHoon_StudyGreek.py --server.enableCORS false

import requests
from io import BytesIO

def fetch_font(url):
    response = requests.get(url)
    font_bytes = BytesIO(response.content)
    return font_bytes

#streamlit run SangHoon_StudyGreek.py --server.enableCORS false

# 헬라어 알파벳과 그 이름
GREEK_WORDS = {
    "φίλος": ['필로스', '친구'],
    "γράμμα": ['그람마', '글자'],
    "δάσος": ['다소스', '숲'],
    "πόλη": ['포리', '도시'],
    "νερό": ['네로', '물'],
    "βιβλίο": ['비블리오', '책'],
    "σχολείο": ['스콜레이오', '학교'],
    "θάλασσα": ['탈라사', '바다'],
    "οικογένεια": ['이코게네이아', '가족'],
    "άνθρωπος": ['안트로포스', '사람']
}
# 폰트 설정
korean_font_path = "https://raw.githubusercontent.com/wwwcam/greek/main/malgun.ttf"
greek_font_path = "https://raw.githubusercontent.com/wwwcam/greek/main/NotoSans-Regular.ttf"
default_font_path = "https://raw.githubusercontent.com/wwwcam/greek/main/NotoSansCJKkr-Regular.ttf"

korean_font = ImageFont.truetype(fetch_font(korean_font_path), 20)
greek_font = ImageFont.truetype(fetch_font(greek_font_path), 20)
default_font = ImageFont.truetype(fetch_font(default_font_path), 20)



def play_sound(is_correct):
    if is_correct:
        audio_path = 'https://raw.githubusercontent.com/wwwcam/greek/main/jung.mp3'
    else:
        audio_path = 'https://raw.githubusercontent.com/wwwcam/greek/main/oh.mp3'
    
    audio_script = f"""
    <audio controls autoplay>
        <source src="{audio_path}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_script, unsafe_allow_html=True)
    
    # 음악 파일의 길이를 가져옵니다.
    response = requests.head(audio_path)
    file_size = int(response.headers['Content-Length'])
    
    # 예상 길이를 기반으로 일시 중지 (이 방법은 정확하지 않을 수 있음. 대략적인 추정임)
    sleep_time = file_size / (16 * 1024)  # 16KB/s bitrate로 예상
    time.sleep(sleep_time)

    
    # JavaScript의 'audioEnded' 변수를 Python에서 확인하려면 이와 같이 Streamlit 컴포넌트나 추가적인 방법을 사용해야 합니다.
    # 현재 Streamlit의 내장 기능만으로는 JavaScript 변수의 상태를 직접적으로 확인하는 것이 어렵습니다.

    
def resize_image(img, max_width=800):
    if img.size[0] > max_width:
        base_width = max_width
        w_percent = base_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.ANTIALIAS)
    return img

        
def initialize_app_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.start_time = datetime.now()
        st.session_state.remaining_words = list(GREEK_WORDS.keys())
        st.session_state.correct_count = 0
        st.session_state.correct_answers = set()


def determine_font(character):
    """주어진 문자에 대한 적절한 폰트를 결정합니다."""
    if '\u1100' <= character <= '\u11FF' or '\u3130' <= character <= '\u318F' or '\uAC00' <= character <= '\uD7AF':
        # 한글 범위
        return korean_font
    elif '\u0370' <= character <= '\u03FF':
        # 그리스어 범위
        return greek_font
    else:
        # 기타 폰트 (예: 영어나 숫자 등)
        return default_font

def draw_centered_text(draw, text, position, fill="black"):
    """텍스트를 이미지의 주어진 위치에 중앙정렬로 그립니다."""
    x, y = position
    total_width = sum([determine_font(char).textbbox(char)[0] for char in text])
    current_x = x - total_width / 2
    for char in text:
        font = determine_font(char)
        draw.text((current_x, y), char, fill=fill, font=font)
        current_x += font.getsize(char)[0]
        
def get_max_text_width(words):
    """주어진 단어 리스트에서 가장 긴 단어의 길이를 반환합니다."""
    return max([get_text_width(word) for word in words])

def determine_font_for_text(text):
    """주어진 텍스트 내의 각 문자에 대한 폰트 리스트를 반환합니다."""
    return [determine_font(char) for char in text]

def get_text_width(text):
    img_temp = Image.new('RGB', (1, 1))
    draw_temp = ImageDraw.Draw(img_temp)
    
    fonts = determine_font_for_text(text)
    total_width = sum([font.getsize(char)[0] for char, font in zip(text, fonts)])
    return total_width

def generate_word_table_image():
    columns = 5
    remaining_words = {key: value for key, value in GREEK_WORDS.items() if key not in st.session_state.correct_answers}
    rows = len(remaining_words) // columns + (1 if len(remaining_words) % columns else 0)
    
    max_text_widths = [get_max_text_width(list(remaining_words.values())[i:i+columns]) for i in range(0, len(remaining_words), columns)]
    max_cell_width = max(max_text_widths) + 20  # 20은 여유 공간

    table_width = max_cell_width * columns
    cell_height = 100
    table_height = cell_height * max(1, rows)
    
    img = Image.new('RGB', (table_width, table_height), color='white')
    d = ImageDraw.Draw(img)
    
    if rows == 0:
        draw_centered_text(d, "모든 문제를 완료하셨습니다. 수고하셨습니다.", (table_width/2, 10))
    else:
        x, y = max_cell_width / 2, cell_height / 2
        for letter, name in remaining_words.items():
            draw_centered_text(d, letter, (x, y - 20))  # 알파벳
            draw_centered_text(d, name[0], (x, y + 20), fill='gray')  # 발음. name[0]을 사용하여 첫 번째 발음만 사용합니다.

            x += max_cell_width
            if x >= table_width:
                x = max_cell_width / 2
                y += cell_height
                
    return img



def render_quiz():
    st.header("그리스어 단어 퀴즈")
    img = generate_word_table_image()
    if img and isinstance(img, Image.Image):
        st.image(img, width=1000)
    else:
        st.error("이미지 생성 오류!")

    remaining_words = {key: value for key, value in GREEK_WORDS.items() if key not in st.session_state.correct_answers}

    if not remaining_words:  # 모든 알파벳을 처리했다면
        end_time = datetime.now()
        time_spent = end_time - st.session_state.start_time
        minutes, seconds = divmod(time_spent.seconds, 60)
        st.success(f"모든 알파벳을 맞추셨습니다! 축하합니다! 소요 시간: {minutes}분 {seconds}초")
    else:
        if 'alphabet' not in st.session_state or st.session_state.alphabet not in remaining_words:
            st.session_state.alphabet, st.session_state.pronunciation = random.choice(list(remaining_words.items()))

        st.header(f"다음 그리스 알파벳의 발음은 무엇인가요?")
        st.markdown(f"<h1 style='font-size: 80px;'>{st.session_state.alphabet}</h1>", unsafe_allow_html=True)

        random.seed(st.session_state.alphabet)
        options = [st.session_state.pronunciation[0]]
        other_pronunciations = [pronunciation[0] for alphabet, pronunciation in GREEK_WORDS.items() if alphabet != st.session_state.alphabet and pronunciation[0] not in options]
        options.extend(random.sample(other_pronunciations, 3))
        random.shuffle(options)

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        columns = [col1, col2, col3, col4]
        for idx, option in enumerate(options):
            with columns[idx]:
                unique_key = f"option_{idx}_{option}"
                if st.button(option, key=unique_key):
                    if option == st.session_state.pronunciation[0]:
                        play_sound(True)
                        st.write(f'정답 : {option == st.session_state.pronunciation[0]}')
                        st.session_state.correct_answers.add(st.session_state.alphabet)
                    else:
                        play_sound(False)
                        st.write(f'틀렸습니다 : {option == st.session_state.pronunciation[0]}')
  
                    if 'alphabet' in st.session_state:
                        del st.session_state.alphabet
                    st.experimental_rerun()
                    

if __name__ == '__main__' :
    st.markdown("<h1 style='text-align: center; color: white;'>그리스어 단어 학습</h1>", unsafe_allow_html=True)
    initialize_app_state()
    render_quiz()
