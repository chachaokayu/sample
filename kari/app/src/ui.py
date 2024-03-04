import numpy as np
import streamlit as st

from io import BytesIO
from PIL import Image
from stpyvista import stpyvista

from plot.visualize_naiji import get_naiji_plot
from plot.visualize_track import get_track_plot

# streamlit上にmatplotpibによるfigureを表示させる関数
def show_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)
    st.image(np.asarray(img))
    buf.close()

# 表示するUI
def ui_setting():
    title = '<p style="font-family:Courier; color:White; font-size: 40px;">庫内可視化</p>'
    st.markdown(title, unsafe_allow_html=True)
    
    data_path = st.text_input('可視化に必要なデータのファイルパスを入力して下さい。')
    track_mst_path = st.text_input('トラックマスタ情報のファイルパスを入力してください。')
    
    data_type_radio = st.radio(
        "可視化対象を選択してください。",
        ["内示", "確定"],
    )
    
    if st.button("可視化を実行する"):
        # パスが両方記載されたときに実行
        if data_path != "" and track_mst_path != "":
            # 2D・3Dのプロットを作成し取得する
            if data_type_radio == "内示":
                fig_2d, fig_3d = get_naiji_plot(data_path=data_path, track_mst_path=track_mst_path)
            elif data_type_radio == "確定":
                fig_2d, fig_3d = get_track_plot(data_path=data_path, track_mst_path=track_mst_path)
            
            # 作成したプロットの表示
            for idx, (f2d, f3d) in enumerate(zip(fig_2d, fig_3d)):
                show_image(f2d)
                stpyvista(f3d, key=f"pv_track_{idx}")