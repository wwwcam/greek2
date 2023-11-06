import streamlit as st
import StudyGreekAlphabet
import StudyGreekDanajang

PAGES = {
    "헬라어어 알파벳 학습": StudyGreekAlphabet,
    "헬라어어 단어 학습": StudyGreekDanajang
}

def run():
    st.sidebar.title('학습 메뉴')
    selection = st.sidebar.radio("페이지 선택:", list(PAGES.keys()))
    page = PAGES[selection]
    page.run()

if __name__ == "__main__":
    run()
