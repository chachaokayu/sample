import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv

class PlotPacking():
    def __init__(self, track_mst_path, df) -> None:
        self.track_list = [] # トラック台数分を格納するリスト
        self.change_label = [] # 2D表示の際にキュービックの配置を格納したリスト
        # 3D表示時にて3次元ブロックを作成するためのリスト
        self.track_3d_list = [] # 3D可視化に必要な情報をトラック毎に格納したリスト
        
        self.df_trackmst = self.get_trackmst(track_mst_path)
        # クリアランスを考慮したトラック内寸の更新
        self.X = round(self.df_trackmst.at["length","15tQ"] - 0.15,3)
        self.Y = round(self.df_trackmst.at["width","15tQ"] - 0.15,3)
        self.Z = round(self.df_trackmst.at["height","15tQ"] - 0.15,3)
        
        # キュービック詰込みを実行
        self.packing(df)
        # 2D可視化用のデータ取得
        self.get_data_for_2D()
        # 3D可視化用のデータ取得
        self.get_data_for_3D()
    
    # トラックマスタ情報の取得
    def get_trackmst(self, track_mst_path):
        # トラックのマスタ情報
        df_trackmst = pd.read_csv(track_mst_path, index_col = 0)
        # トラックの体積計算 クリアランス考慮
        df_trackmst.loc["volume"] = round(df_trackmst.at["length","15tQ"]-0.15,3) * round(df_trackmst.at["width","15tQ"]-0.15,3) * round(df_trackmst.at["height","15tQ"]-0.15,3)
        return df_trackmst
    
    # 詰め込み処理の実行
    def packing(self, df):
        # 後の処理とセル分けしないと初期化が効かず、正しい値が出ません(後の処理と統合しないでください)
        work_list = [] # 高さ方向に積むためのためのリスト(縦＋高さ)
        work_list_2 = [] # トラック１台分に積み込むためのリスト
        ll = [] # 縦方向に並べるためのリスト
        
        x_work = self.X
        y_work = self.Y
        z_work = self.Z
        for label in df["キュービック縦横高さ重複識別ラベル"].tolist():
            
            x = df[df["キュービック縦横高さ重複識別ラベル"] == label]["キュービック_よこ"].values[0]
            y = df[df["キュービック縦横高さ重複識別ラベル"] == label]["キュービック_たて"].values[0]
            z = df[df["キュービック縦横高さ重複識別ラベル"] == label]["キュービック_高さ"].values[0]
            for i in range(df[df["キュービック縦横高さ重複識別ラベル"] == label]["綺麗_混載で綺麗_キュービック数"].values[0]):
                # 縦方向に空があり、縦方向に２列未満の場合
                if(y_work >= y and len(ll) < 2):
                    # print("*************縦方向のスペース確認*************")
                    ll.append(label) # キュービックを格納
                    y_work = y_work - y # 縦方向の残りの長さを更新
                    continue
                # 縦方向に次のキュービックが入るスペースがなくなった場合　または　縦方向に２列に積まれている場合
                # 上の段に積まれるようにする
                else:
                    # print("*************高さ方向の長さ更新*************")
                    y_work = self.Y # 縦方向の残り長さを初期化
                    before_z = [item.split("_")[-1] for item in ll]  ####2023/11/14 出口さん困りごとのため追加
                    before_z = float(max(before_z))  ####2023/11/14 出口さん困りごとのため追加
                    z_work = z_work - before_z # 高さ方向の残り長さを更新
                # 高さ方向に次のキュービックが入る場合
                if(z_work >= z):
                    # print("*************高さ方向のスペース確認************")
                    work_list.append(ll) # 縦方向に並べたキュービックを格納  ####2023/11/14 出口さん困りごとのため追加
                    ll = [] # １次ワークリストを初期化  ####2023/11/14 出口さん困りごとのため追加
                    ll.append(label)
                    y_work = y_work - y # 縦方向の残りの長さを更新
                    continue
                # 高さ方向に次のキュービックが入らない場合
                else:
                    # print("**********x方向へ列移動して直前の列を格納する**********")
                    work_list.append(ll) # 縦方向に並べたキュービックを格納  ####2023/11/14 出口さん困りごとのため追加
                    ll = [] # １次ワークリストを初期化  ####2023/11/14 出口さん困りごとのため追加
                    work_list_2.append(work_list) # 縦方向に並べたキュービック・高さ方向に積んだキュービックをトラック内の１列として格納
                    work_list = [] # ワークの初期化
                    x_work = x_work - x # 列移動に伴ってよこ方向の長さを更新
                    y_work = self.Y # 列移動に伴って高さ方向の残り長さを初期化
                    z_work = self.Z # 列移動に伴って縦方向の残り長さを初期化
                    y_work = y_work - y # 縦方向の残りの長さを更新
                    ll.append(label) # キュービックを格納
                # よこ方向に次のキュービックが入らない場合
                if(x_work < x):
                    # print("*********X方向に次のキュービックが入らない場合***********")
                    self.track_list.append(work_list_2) # トラック１台分に格納してきたキュービックをトラックリストに格納
                    ll = []
                    work_list = []
                    work_list_2 = [] # トラック１台分の格納リストを初期化
                    x_work = self.X # トラック入れ替えに伴ってよこ方向の残り長さを初期化
                    y_work = self.Y # トラック入れ替えに伴って高さ方向の残り長さを初期化
                    z_work = self.Z # トラック入れ替えに伴って縦方向の残り長さを初期化
                    ll.append(label) # キュービックを格納 
                    y_work = y_work - y # 縦方向の残りの長さを更新
        if(x_work >= x):
            work_list.append(ll)
            work_list_2.append(work_list)
            self.track_list.append(work_list_2)
    
    # 2Dプロットの作成
    def plot_2d(self, visualize_type):
        # 2D表示
        # 箱ごとに色分けされるように表示を変更した。
        # 箱はカラフルに、空の領域を灰色に表示する。
        color = ["royalblue", "yellow", "limegreen", "red", "orange", "cyan", "pink"]
        
        fig_list = []
        for i, track in enumerate(self.track_h):
            fig, ax = plt.subplots(1,1, figsize=(27,9))
            ax.set_xlabel("トラック荷積み列", fontname="MS Gothic")
            ax.set_ylabel("トラック庫内スペース高さ", fontname="MS Gothic")
            for j, luggage_col in enumerate(track):
                bar_max_width = 0.6
                y_num = len(luggage_col)
                bar_size = bar_max_width / y_num # 棒グラフを縦方向のキュービック数分に分割する
                for k, luggage in enumerate(luggage_col):
                    z_max = self.Z
                    before_z = 0
                    for l, qubic in enumerate(luggage):
                        # z_max: 空の領域の棒グラフの縦幅
                        z_max -= qubic
                        width = bar_max_width - ((k+1) * bar_size)
                        # キュービックの棒グラフ追加
                        # j-width:棒グラフのx軸の始点, qubic:棒グラフの縦幅, bar_size:棒グラフの横幅, before_z:棒グラフのy軸の始点, color[l]:キュービックごとに色分け
                        ax.bar(j-width, qubic, bar_size, before_z, color=color[l], edgecolor="black")
                        # キュービックの高さを記載
                        ax.text(x=j-width-0.01, y=before_z+0.05, s=str(round(qubic, 3)))
                        # 積まれているキュービックの高さを更新
                        before_z += qubic
                    # 空の領域をグレーの棒グラフで表示
                    ax.bar(j-width, z_max, bar_size, before_z, color="gray", edgecolor="black")
                    ax.text(x=j-width-0.01, y=before_z+0.05, s=str(round(z_max, 3)))
            ax.set_title(f"トラック庫内イメージ(等ピッチ)_{visualize_type}_トラック{i+1}", fontname="MS Gothic")
            # 作成したFigureの格納
            fig_list.append(fig)
        return fig_list
    
    # 3Dプロットの作成
    def plot_3d(self):
        p_list = []
        # トラック毎に処理を実行
        for track in self.track_3d_list:
            # PyVistaのプロットの定義
            p = pv.Plotter()
            # トラックモデルの作成
            # center: モデルの中心座標, x_length: モデルのX座標, y_length: モデルのY座標, z_length: モデルのZ座標
            track_cube = pv.Cube(center=(self.X/2, self.Y/2, self.Z/2), x_length=self.X, y_length=self.Y, z_length=self.Z)
            # トラックモデルの表示をプロットに追加
            # style="wireframe"とすることでモデルをフレーム表示のみにする
            p.add_mesh(track_cube, style="wireframe")
            
            # キュービックの数だけ繰り返し処理
            for qubic_size, qubic_point, qubic_name in zip(track[0], track[1], track[2]):
                # キュービックモデルの作成
                cube = pv.Cube(center=qubic_point, x_length=qubic_size[0], y_length=qubic_size[1], z_length=qubic_size[2])
                # キュービックモデルの表示をプロットに追加
                p.add_mesh(cube, show_edges=True, opacity=0.5)
                # キュービックモデルの中心に赤点を表示
                p.add_point_labels([np.array(qubic_point)], [qubic_name], font_size=10, point_size=10, point_color="red", fill_shape=True)
            p.view_isometric()
            # プロットをリストに追加
            p_list.append(p)
        return p_list
    
    # 2D可視化に必要なデータの作成
    def get_data_for_2D(self):
        # 2D表示しやすいように配列の形状を変形
        # 転置可能な形式にするために、列の足りないリストにダミー変数を格納し配列の列数を合わせる
        for i, track in enumerate(self.track_list):
            for j, luggage_col in enumerate(track):
                max_y = max([len(v) for v in luggage_col])
                for k, luggage in enumerate(luggage_col):
                    if len(luggage) < max_y:
                        self.track_list[i][j][k].append("dummy")
        
        # 配列を転置して縦方向と高さ方向の値を入れ替える
        # 転置後、ダミー変数を削除する
        for i, track in enumerate(self.track_list):
            x_list = []
            for j, luggage_col in enumerate(track):
                luggage_col_t = np.array(luggage_col).T.tolist()
                y_list = []
                for k, luggage in enumerate(luggage_col_t):
                    z_list = [x for x in luggage if not x == "dummy"]
                    y_list.append(z_list)
                x_list.append(y_list)
            self.change_label.append(x_list)
        
        # キュービック高さのみを格納したリストを作成
        self.track_h = copy.deepcopy(self.change_label)
        for i, track in enumerate(self.track_h):
            for j, luggage_col in enumerate(track):
                for k, luggage in enumerate(luggage_col):
                    self.track_h[i][j][k] = [round(float(x.split("_")[2]),3) for x in luggage]
    
    # 3D可視化に必要なデータの作成
    def get_data_for_3D(self):
        qubic_size_list = [] # 各キュービックの寸法を格納したリスト
        qubic_center_list = [] # 各キュービックの配置を格納したリスト
        qubic_name_list = [] # 各キュービックの名称を格納したリスト
        center_point = np.zeros(3) # キュービックの中心座標
        
        for track in self.change_label:
            x_point = 0 # 作成するキュービックモデルの中心X座標
            for i, luggage_col in enumerate(track):
                y_point = 0 # 作成するキュービックモデルの中心Y座標
                max_x = 0
                for j, luggage in enumerate(luggage_col):
                    z_point = 0 # 作成するキュービックモデルの中心Z座標
                    max_y = 0
                    for k, qubic in enumerate(luggage):
                        x = round(float(qubic.split("_")[1]), 3) # キュービックモデルのよこ方向のサイズ
                        y = round(float(qubic.split("_")[0]), 3) # キュービックモデルのたて方向のサイズ
                        z = round(float(qubic.split("_")[2]), 3) # キュービックモデルの高さ方向のサイズ
                        qubic_size = np.array([x, y, z]) # キュービックモデルのサイズをまとめる
                        center_point = np.array([x_point, y_point, z_point]) + qubic_size/2 # キュービックモデルの中心座標
                        
                        # 各情報をリストに格納
                        qubic_size_list.append(tuple(qubic_size))
                        qubic_center_list.append(tuple(center_point))
                        qubic_name_list.append(qubic)
                        
                        # 次に置かれるキュービックは前に置かれた縦・横のサイズが大きいキュービックに合わせる
                        # これをしないとキュービックモデルが重なって表示されてしまう場合がある
                        if max_x < x:
                            max_x = x
                        if max_y < y:
                            max_y = y
                        
                        z_point += z # 次のキュービックを置くZ座標の更新
                    y_point += max_y # 次のキュービックを置くY座標の更新
                x_point += max_x     # 次のキュービックを置くX座標の更新
            # トラックに積むキュービックモデルの情報を格納
            self.track_3d_list.append(
                [
                    qubic_size_list,
                    qubic_center_list,
                    qubic_name_list,
                ]
            )