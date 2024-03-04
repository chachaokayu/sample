import pandas as pd
from plot.packing_qubic import PlotPacking

def get_naiji_plot(data_path, track_mst_path):
    # データフレームとして読み込み
    df = pd.read_csv(data_path)
    # dfのキュービック縦横高さ重複識別モデルを変更する(受入が違うものを混載させてはいけないのでラベルを分けています)
    df["キュービック縦横高さ重複識別ラベル"] = \
        df["キュービック_たて"].astype(str) +"_"+ df["キュービック_よこ"].astype(str) +"_"+ df["キュービック_高さ"].astype(str) + "_" + df["受入"].astype(str)
    # 受入とキュービックのたて、よこ、高さが同じなら混載しても良いとして、まとめてしまいます
    df_amari = df.drop_duplicates("キュービック縦横高さ重複識別ラベル")
    # indexをリセット
    df_amari = df_amari.reset_index(drop=True)
    df_amari["混載しても出る箱だけ入れた時の体積(面取りあり)"] = df_amari["キュービック_たて"] * df_amari["キュービック_よこ"] * df_amari["箱_高さ"] * df_amari["必要段数"]
    # 余り箱_識別ラベルを作成。後でキュービック縦横高さ重複識別ラベルに置き換える
    df_amari["余り箱_識別ラベル"] = \
        df_amari["キュービック_たて"].astype(str) +"_"+ df_amari["キュービック_よこ"].astype(str) +"_"+ round(df_amari["混載条件のパレット含めた高さ"], 3).astype(str) + "_" + df_amari["受入"].astype(str)
    # 混載した上で綺麗になるキュービック数を計算する
    df_edit_duplicate = df_amari.copy()
    
    df_groupby = df.groupby("キュービック縦横高さ重複識別ラベル")
    qubic_num = (df_groupby["綺麗なキュービック数"].sum() + df_groupby["混載するきれいなキュービック"].max()).astype(int)
    # 綺麗なキュービックと混載して綺麗になったキュービックの数を足し合わせて　df_edit_duplicate　に更新する
    df_edit_duplicate = pd.merge(df_edit_duplicate, qubic_num.rename("綺麗_混載で綺麗_キュービック数"), left_on=["キュービック縦横高さ重複識別ラベル"], right_index=True)
    df_edit_duplicate.sort_values(["キュービック_たて","キュービック_高さ"], inplace=True, ascending=False)
    df_edit_duplicate.reset_index(inplace=True, drop=True)
    # もし必要段数と「箱/段数332　5段　332.5　4段」が同じなら余り箱_識別ラベルの高さをキュービック縦横高さ重複識別ラベルの高さに揃える
    df_edit_duplicate.loc[df_edit_duplicate["箱/段数332　5段　332.5　4段"] == df_edit_duplicate["必要段数"], "余り箱_識別ラベル"] = df_edit_duplicate["キュービック縦横高さ重複識別ラベル"]
    
    # 面取りしたキュービックのデータを追加するため、新しいデータフレームを作成
    df_amaribako = df_edit_duplicate.copy()
    # 「箱/段数」と「必要段数」が同じ場合、「キュービック高さ」は「混載条件のパレット含めた高さ」と同じにする
    df_amaribako.loc[df_amaribako["箱/段数332　5段　332.5　4段"] != df_amaribako["必要段数"], "キュービック_高さ"] = df_amaribako["混載条件のパレット含めた高さ"]
    # 「キュービック縦横高さ重複識別ラベル」を「余り箱_識別ラベル」と同じにする
    df_amaribako["キュービック縦横高さ重複識別ラベル"] = df_amaribako["余り箱_識別ラベル"]
    # 混載しても余った箱は、面取りしたキュービックに積まれるため、「綺麗_混載で綺麗_キュービック数」に1を加える
    df_amaribako["綺麗_混載で綺麗_キュービック数"] = 1
    # データを結合する
    df_edit_duplicate = pd.concat([df_edit_duplicate, df_amaribako])
    # 荷物は「1.キュービックたて, 2.キュービック_高さ」の優先度で並び替える
    df_edit_duplicate = df_edit_duplicate.sort_values(by=["キュービック_たて", "キュービック_高さ"], ascending=[False, False])
    # 綺麗_混載で綺麗_キュービック数=0の行を削除する
    df_edit_duplicate = df_edit_duplicate[df_edit_duplicate["綺麗_混載で綺麗_キュービック数"] != 0]
    # indexを振り直す
    df_edit_duplicate.reset_index(inplace=True, drop=True)
    # 重複ラベルから受入を消す
    # キュービック縦横高さ重複識別モデルを変更する
    df_edit_duplicate["キュービック縦横高さ重複識別ラベル"] = \
        df_edit_duplicate["キュービック_たて"].astype(str) +"_"+ df_edit_duplicate["キュービック_よこ"].astype(str) +"_"+ round(df_edit_duplicate["キュービック_高さ"], 3).astype(str)
    # キュービック高さが変更されている行があるため、キュービック体積を再計算する
    df_edit_duplicate["キュービック_体積"] = df_edit_duplicate["キュービック_たて"] * df_edit_duplicate["キュービック_よこ"] * df_edit_duplicate["キュービック_高さ"]
    # 面取り有の時のトラック1台分の体積を計算する
    # cube_volume_total = sum(df_edit_duplicate["キュービック_体積"] * df_edit_duplicate["綺麗_混載で綺麗_キュービック数"])
    
    # キュービックを詰込み、2D, 3D可視化figureを取得する
    plotter = PlotPacking(track_mst_path=track_mst_path, df=df_edit_duplicate)
    fig_2d = plotter.plot_2d(visualize_type="内示")
    fig_3d = plotter.plot_3d()
    
    return fig_2d, fig_3d