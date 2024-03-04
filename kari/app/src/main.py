import streamlit as st
from ui import ui_setting

def main():
    # 必要ないものを非表示
    hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # UIの表示
    ui_setting()

if __name__ == "__main__":
    st.set_page_config(
        page_title="庫内可視化アプリ",
        layout="wide"
    )
    
    main()