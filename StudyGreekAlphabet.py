import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import time
from datetime import datetime
import requests

#streamlit run SangHoon_StudyGreek.py --server.enableCORS false





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
        st.session_state.remaining_alphabets = list(GREEK_ALPHABET.keys())
        st.session_state.correct_count = 0
        st.session_state.correct_answers = set()

def generate_alphabet_table_image():
    cell_width, cell_height = 90, 80
    columns = 12
    remaining_alphabets = {key: value for key, value in GREEK_ALPHABET.items() if key not in st.session_state.correct_answers}
    rows = len(remaining_alphabets) // columns + (1 if len(remaining_alphabets) % columns else 0)
    
    table_width = cell_width * columns
    table_height = cell_height * max(1, rows)  # 최소 1행을 가진 표를 생성합니다.
    
    img = Image.new('RGB', (table_width, table_height), color='white')
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("./malgun.ttf", 20)
    
    if rows == 0:
        # 모든 문제를 완료한 경우의 메시지를 추가합니다.
        d.text((10, 10), "모든 문제를 완료하셨습니다. 수고하셨습니다.", font=font, fill='black')
    else:
        x, y = 0, 0
        for letter, name in remaining_alphabets.items():
            d.text((x + 10, y + 10), letter, font=font, fill='black')
            d.text((x + 10, y + 50), name[0], font=font, fill='gray')

            x += cell_width
            if x >= table_width:
                x = 0
                y += cell_height
                
    return img


def render_quiz():
    st.header("그리스 알파벳 퀴즈")
    img = generate_alphabet_table_image()
    if img and isinstance(img, Image.Image):
        st.image(img, width=800)
    else:
        st.error("이미지 생성 오류!")

    remaining_alphabets = {key: value for key, value in GREEK_ALPHABET.items() if key not in st.session_state.correct_answers}

    if not remaining_alphabets:  # 모든 알파벳을 처리했다면
        end_time = datetime.now()
        time_spent = end_time - st.session_state.start_time
        minutes, seconds = divmod(time_spent.seconds, 60)
        st.success(f"모든 알파벳을 맞추셨습니다! 축하합니다! 소요 시간: {minutes}분 {seconds}초")
    else:
        if 'alphabet' not in st.session_state or st.session_state.alphabet not in remaining_alphabets:
            st.session_state.alphabet, st.session_state.pronunciation = random.choice(list(remaining_alphabets.items()))

        st.header(f"다음 그리스 알파벳의 발음은 무엇인가요?")
        st.markdown(f"<h1 style='font-size: 80px;'>{st.session_state.alphabet}</h1>", unsafe_allow_html=True)

        random.seed(st.session_state.alphabet)
        options = [st.session_state.pronunciation[0]]
        other_pronunciations = [pronunciation[0] for alphabet, pronunciation in GREEK_ALPHABET.items() if alphabet != st.session_state.alphabet and pronunciation[0] not in options]
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
                    

def run():
    global GREEK_ALPHABET
    # 헬라어 알파벳과 그 이름
    # 헬라어 알파벳과 그 이름
    GREEK_ALPHABET = {
        "Α":['알파', '알'],
        "Β":['베타', '베'],
        "Γ":['감마', '감'],
        "Δ":['델타', '델'],
        "Ε":['엡실론', '엡'],
        "Ζ":['제타', '제'],
        "Η":['에타', '에'],
        "Θ":['쎄타', '쎄'],
        "Ι":['이오타', '이'],
        "Κ":['카파', '카'],
        "Λ":['람다', '람'],
        "Μ":['뮤', '뮤'],
        "Ν":['뉴', '뉴'],
        "Ξ":['크시', '크'],
        "Ο":['오미크론', '오'],
        "Π":['파이', '파'],
        "Ρ":['로', '로'],
        "Σ":['시그마', '시'],
        "Τ":['타우', '타'],
        "Υ":['웁실론', '웁'],
        "Φ":['피', '피'],
        "Χ":['카이', '카'],
        "Ψ":['프시', '프'],
        "Ω":['오메가', '오'],
        "α":['알파', '알'],
        "β":['베타', '베'],
        "γ":['감마', '감'],
        "δ":['델타', '델'],
        "ε":['엡실론', '엡'],
        "ζ":['제타', '제'],
        "η":['에타', '에'],
        "θ":['쎄타', '쎄'],
        "ι":['이오타', '이'],
        "κ":['카파', '카'],
        "λ":['람다', '람'],
        "μ":['뮤', '뮤'],
        "ν":['뉴', '뉴'],
        "ξ":['크시', '크'],
        "ο":['오미크론', '오'],
        "π":['파이', '파'],
        "ρ":['로', '로'],
        "σ":['시그마', '시'],
        "ς":['시그마', '시'],
        "τ":['타우', '타'],
        "υ":['엡실론', '엡'],
        "φ":['파이', '파'],
        "χ":['카이', '카'],
        "ψ":['프시', '프'],
        "ω":['오메가', '오'],
    }

    st.markdown("<h1 style='text-align: center; color: white;'>그리스 알파벳 학습</h1>", unsafe_allow_html=True)
    initialize_app_state()
    render_quiz()
