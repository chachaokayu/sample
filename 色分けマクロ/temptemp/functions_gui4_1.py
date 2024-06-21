import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches as pat
import matplotlib.image as mpimg
import matplotlib.cm as cm
import matplotlib.colors as mc
import matplotlib.patheffects as patheffects
import datetime as dt
import sql
plt.rcParams['font.family'] = "MS Gothic"

# 前処理や図作成用の関数----------------------------------------------------------
# DFを指定時間で切り出す
def timecut(df, lange):
    df = df.query('DateTime >= @lange[0] & DateTime <= @lange[1]')
    return df

# ヒートマップで一定以下を0として無色にする
def zero_clear(cmap, under):
    cmap_data = cmap(np.arange(cmap.N))
    cmap_data[0:under, 3] = 0
    return mc.ListedColormap(cmap_data)

# targetの同じ値が続いた区間をまとめて数を取得する
def switch(df, target):
    df['num'] = np.arange(df.shape[0])
    result = []
    for i in df[target].unique():
        dfi = df[df[target]==i]
        ip = dfi['num'].diff()
        ip.iloc[0] = 3
        sp = ip[ip>=2].index
        if target == 'AREA':
            result.append(df.loc[sp,['DateTime', target]])
        else:
            result.append(df.loc[sp,['DateTime','AREA', target]])
    result = pd.concat(result, axis=0)
    result = result.sort_values('DateTime').reset_index(drop=True)
    result['Tlength'] = dt.timedelta(0)
    time = result['DateTime'].diff().iloc[1:].values
    result.loc[result.index[0:-1],'Tlength'] = time
    result.loc[result.index[-1],'Tlength'] = df.loc[df.index[-1], 'DateTime']-result.loc[result.index[-1],'DateTime']
    return result

# 山積み表用に単位時間当たりで集計する
def summary_work(df, target, unit):
    sample = df[[target]].copy()
    sample['DTG'] = df['DateTime'].dt.floor(unit)
    sample['time'] = abs(df['DateTime'].diff(-1).dt.total_seconds()) / 60
    stat = sample.groupby(['DTG', target]).sum().unstack()['time']
    return stat

# 山積み表用に単位時間当たりで集計する
def summary_inout(df, unit):
    df['floortime'] = df['DateTime'].dt.floor(unit)
    df['Num'] = 1
    dfS = df.groupby(['floortime', '作業'])['Num'].sum().unstack()
    return dfS

# 山積み表を作成する
def E_chart(L, I, xlabel='時間帯',figsize=(15,7)):
    def make_chart(df, ax, color, xlabel, ylabel):
        chart = df.plot.bar(stacked=True, ax=ax, color=color)
        chart.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=8)
        ax.set_xlabel(xlabel, size=9)
        ax.set_ylabel(ylabel, size=9)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                if df.iloc[i,j] > 1:
                    point = df.iloc[i,:j].sum()+df.iloc[i,j]/2
                    plt.text(x=i, y=point, s=f'{round(df.iloc[i,j])}', ha='center',va='bottom',c='k', fontsize=8,
                             path_effects=[patheffects.withStroke(linewidth=2, foreground='white', capstyle="round")])
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
    
    Lcolor = {'移動': "b", '投入': "orange", '仕分け':'darkturquoise', '異常':'r', 'エリア外':'m', '休憩':'pink', '引取':'g'}
    Icolor = {'投入': "orange", '引取':'g'}
    fig = plt.figure(figsize=figsize)
    ax1 = fig.add_subplot(1, 2, 1)
    make_chart(L, ax1, Lcolor, xlabel, '時間(分)')
    ax1.set_title('作業時間', fontsize=12)
    plt.grid()
    ax2 = fig.add_subplot(1, 2, 2)
    make_chart(I, ax2, Icolor, xlabel, '投入/引取 かんばん数')
    ax2.set_title('投入/引取 かんばん数', fontsize=12)
    plt.tight_layout()
    plt.grid()
    return fig

# 山積み表を作成する（INOUTなし）
def E_chart_noio(L, xlabel='時間帯',figsize=(8,7)):
    def make_chart(df, ax, color, xlabel, ylabel):
        chart = df.plot.bar(stacked=True, ax=ax, color=color)
        chart.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=8)
        ax.set_xlabel(xlabel, size=9)
        ax.set_ylabel(ylabel, size=9)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                if df.iloc[i,j] > 1:
                    point = df.iloc[i,:j].sum()+df.iloc[i,j]/2
                    plt.text(x=i, y=point, s=f'{round(df.iloc[i,j])}', ha='center',va='bottom',c='k', fontsize=8,
                             path_effects=[patheffects.withStroke(linewidth=2, foreground='white', capstyle="round")])
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
    
    Lcolor = {'移動': "b", '投入': "orange", '仕分け':'darkturquoise', '異常':'r', 'エリア外':'m', '休憩':'pink', '引取':'g'}
    fig = plt.figure(figsize=figsize)
    ax1 = fig.add_subplot(1, 1, 1)
    make_chart(L, ax1, Lcolor, xlabel, '時間(分)')
    ax1.set_title('作業時間', fontsize=12)
    plt.grid()
    plt.tight_layout()
    return fig

# 複数人比較用の山積み表を作成する
def MP_chart(Set, figsize=(15,7)):
    ID = list(Set.keys())
    work = pd.concat([summary_work(Set[key].dfL,'job2','4D') for key in Set], axis=0)
    work.index = ID
    if Set[list(Set)[0]].ioflag == True:
        inout = pd.concat([summary_inout(Set[key].dfI, '4D') for key in Set], axis=0)
        inout.index = ID
        fig = E_chart(work, inout, xlabel='作業者', figsize=figsize)
    else:
        fig = E_chart_noio(work, xlabel='作業者', figsize=figsize)
    return fig

# 全体の山積み表を作成する
def total_chart(Set, unit, figsize=(15,7)):
    work = pd.concat([summary_work(Set[key].dfL,'job2', unit) for key in Set], axis=0)
    work = work.sum(level=0, axis=0)
    if Set[list(Set)[0]].ioflag == True:
        inout = pd.concat([summary_inout(Set[key].dfI, unit) for key in Set], axis=0)
        inout = inout.sum(level=0, axis=0)
        fig = E_chart(work, inout, figsize=figsize)
    else:
        fig = E_chart_noio(work, figsize=figsize)
    return fig

# INOUTのCSVを読み込む
def inout_read(path):
    df = pd.read_csv(path)
    if df.shape[1] > 8:
        df = change_style(df)
    df = df.mask(df == '« NULL »', np.nan)
    df['投入時間'] = pd.to_datetime(df['投入時間'])
    df['引取時間'] = pd.to_datetime(df['引取時間'])
    df['品番'] = df['品番'].str.replace(' ', '')
    return df

# トレサビから取得したCSVを従来形式に変換する
def change_style(df):
    df = df[['品番', 'かんばん枝番','部品/工程間ストア投入日時', '部品/工程間ストア投入者', '部品/工程間ストア引取り日時', '部内/工程間ストア引取り者', '部品/工程間ストア棚番']]
    df.columns = ['品番', '枝番', '投入時間', '投入作業者ID', '引取時間', '引取り作業者ID',	'ストアNo.']
    df = df.mask(df == '9999-12-31 00:00:00', np.nan)
    return df

# タグ一つでの分析クラス
class tag_analysis:
    # データを読み込んで準備する
    def __init__(self, tag, lange):
        self.dfL = sql.load_pos(tag, lange[0], lange[1])
        self.areas = sql.load_areas()
        self.ioflag = False
        self.img = mpimg.imread('data/INOUT_layout/Handa_map.png')
        self.colors = pd.Series(['b', 'orange', 'darkturquoise','r', 'm', 'pink', 'g'], index = ['移動', '投入', '仕分け', '異常', 'エリア外', '休憩', '引取'])
        self.dfL = self.dfL.sort_values('DateTime').reset_index(drop=True)
        self.rng = [self.dfL['DateTime'].iloc[0], self.dfL['DateTime'].iloc[-1]]
        

    # INOUTを読み混んで準備する
    def inout(self, data, ID):
        self.ID = ID
        if isinstance(data, str):
            data = inout_read(data)
        data['投入作業者ID'] = data['投入作業者ID'].fillna(0).astype(int)
        data['引取り作業者ID'] = data['引取り作業者ID'].fillna(0).astype(int)
        tounyu = data.query('投入作業者ID == @ID')[['品番', '枝番', '投入時間']].rename(columns={'投入時間':'DateTime'})
        tounyu['作業'] = '投入'
        hikitori = data.query('引取り作業者ID == @ID')[['品番', '枝番', '引取時間']].rename(columns={'引取時間':'DateTime'})
        hikitori['作業'] = '引取'
        self.dfI = pd.concat([tounyu, hikitori], axis = 0)
        self.dfI = self.dfI.sort_values('DateTime').reset_index(drop=True)
        self.dfI = timecut(self.dfI, self.rng)
        df_c = self.dfI.copy()
        df_c['n'] = np.arange(df_c.shape[0])
        flag = ((df_c['品番'] == df_c['品番'].shift(1)))
        subdf = df_c.loc[flag==False, ['品番', 'DateTime', '作業', 'n']]
        subdf['num'] = abs(subdf['n'].diff(-1))
        subdf['num'].iloc[-1] = subdf['n'].iloc[-1] - subdf['n'].iloc[-1]+1
        self.subdf = subdf
        self.ioflag = True

    # フィルター処理をして誤差を減らす
    def filter(self, tsi, asi, win):
        def accuracy(df):
            Xaccuracy = df['X'].rolling(window = win, center=True).mean() - df['X']
            Yaccuracy = df['Y'].rolling(window = win, center=True).mean() - df['Y']
            Accuracy = np.sqrt(Xaccuracy**2 + Yaccuracy**2)
            AW = np.exp(-(Accuracy / np.sqrt(2)*asi)**2)
            return AW
        def prepare_matrix(df):
            def shift_matrix(sr):
                columns = np.arange(win) - int(np.floor(win/2))
                df = pd.concat([sr.shift(x) for x in columns], axis=1)
                df.columns = columns
                return df
            X = shift_matrix(df['X'])
            Y = shift_matrix(df['Y'])
            T = shift_matrix(df['DateTime'])
            ST = T.sub(T[0], axis=0)
            ST = pd.concat([ST[i].dt.total_seconds() for i in T.columns], axis=1)
            TW = np.exp(-((ST / np.sqrt(2)*tsi)**2))
            AW = accuracy(df)
            AW = shift_matrix(AW)
            W = TW*AW
            return X, Y, W

        X, Y, W = prepare_matrix(self.dfL)
        self.dfL['X'] = ((X*W).sum(axis=1) / W.sum(axis=1)).values
        self.dfL['Y'] = ((Y*W).sum(axis=1) / W.sum(axis=1)).values
        self.dfL['TMPX'] = self.dfL['X'] * 45.8 + 35
        self.dfL['TMPY'] = self.dfL['Y'] * (-45.8) + 6925

    # 中央差分的に速度を計算する
    def Vcal(self):
        self.dfL['Timedelta'] = (self.dfL['DateTime'].shift(-1) - self.dfL['DateTime'].shift(1)).dt.total_seconds()
        self.dfL['Vx'] = (self.dfL['X'].shift(-1) - self.dfL['X'].shift(1)).div(self.dfL['Timedelta'])
        self.dfL['Vy'] = (self.dfL['Y'].shift(-1) - self.dfL['Y'].shift(1)).div(self.dfL['Timedelta'])
        self.dfL['Velocity'] = np.sqrt((self.dfL['Vx'])**2 + (self.dfL['Vy'])**2)

    # 滞在エリアを判定する
    def area_judge(self):
        self.dfL['AREA'] = 'エリア外'
        for i in self.areas.index:
            rx = [self.areas.loc[i,'rect_x1'], self.areas.loc[i,'rect_x2']]
            ry = [self.areas.loc[i,'rect_y1'], self.areas.loc[i,'rect_y2']]
            self.dfL.loc[(self.dfL['TMPX']>=rx[0]) & (self.dfL['TMPX']<=rx[1]) &
                         (self.dfL['TMPY']>=ry[0]) & (self.dfL['TMPY']<=ry[1]),'AREA'] = self.areas.loc[i, 'name']
        self.arealist = pd.Series(self.dfL['AREA'].unique())

    # 速度から作業中か移動中かを判定する
    def V_filter(self, thr):
        M_index = self.dfL[self.dfL['Velocity']>=thr[0]].index
        E_index = self.dfL[self.dfL['Velocity']>=thr[1]].index
        self.dfL['STATUS'] = '静止'
        self.dfL.loc[M_index, 'STATUS'] = '移動'
        self.dfL.loc[E_index, 'STATUS'] = '異常'
        self.dfL['job'] = self.dfL['AREA']
        self.dfL.loc[M_index, 'job'] = '移動'
        self.dfL.loc[E_index, 'job'] = '異常'
        self.joblist = pd.Series(self.dfL['job'].unique())
        self.dfL['job2'] = self.dfL['job']
        # エリアに従い作業を分類する（物流課仕様になっているため他職場では使えない）
        self.dfL.loc[(self.dfL['job'] != '移動') & (self.dfL['job'] != '異常') & (self.dfL['job'] != 'エリア外'), 'job2'] = '投入'
        self.dfL.loc[(self.dfL['job'] == '受入職場-部品運搬-なし-01') | (self.dfL['job'] == 'ライン-00-材料運搬-定位置-02'), 'job2'] = '移動'
        self.dfL.loc[(self.dfL['job'] == '受入職場-部品運搬-定位置') | (self.dfL['job'] == '受入職場-部品運搬-なし') | \
                     (self.dfL['job'] == 'ライン-0000-材料運搬-樹脂引取※-01') | (self.dfL['job'] == 'ライン-0000-部品運搬-部品引取/空箱投入※-03'), 'job2'] = '仕分け'
        self.dfL.loc[abs(self.dfL['DateTime'].diff(-1)) >= dt.timedelta(minutes=10), 'job2'] = '休憩'

    # 指定時間内のサイクルを切り出す（物流課仕様でスタート地点を決めている）
    def cycle_cut(self, lange, startarea='受入職場-部品運搬-定位置', border=30, figsize=(5,5)):
        df = timecut(self.dfL, lange)
        dfs = switch(df, 'AREA').query('AREA==@startarea')
        dfs['diff'] = dfs['DateTime'].diff().dt.total_seconds()
        dfs.iloc[0,-1] = 2000
        dfs = dfs.query('diff >= @border')
        dfs['endtime'] = dfs['DateTime'].shift(-1)
        cycle = dfs[['DateTime', 'endtime']].iloc[:-1,:]
        cycle['cycletime'] = cycle['endtime'] - cycle['DateTime']
        cycle = cycle.reset_index(drop=True)
        cycle['No'] = cycle.index.values
        self.cycle = cycle
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1,1,1)
        ax.axis('off')
        ax.table(cellText=cycle[['No', 'DateTime','endtime','cycletime']].values,
            colLabels=['No', '開始時刻','終了時刻','サイクルタイム'], loc='center', bbox=[0,0,1,1])
        return fig

    # 指定した時間内の作業を集計する
    def work_table(self, lange):
        self.lange = lange
        self.cutdfL = timecut(self.dfL, lange)
        self.cutdfA = switch(self.cutdfL, 'AREA')
        self.cutdfj = switch(self.cutdfL, 'job2')
        self.cutarealist = pd.Series(self.cutdfL['AREA'].unique())
        if self.ioflag == True:
            self.io = timecut(self.subdf, lange)
            self.io['記号'] = ('[' + pd.Series(np.arange(self.io.shape[0]) +1).astype(str) + ']').values

    # 時間内のエリアと作業の推移を可視化する
    def plot_timescale_INOUT(self, figsize=(35,3)):
        sample = self.cutdfA
        TlengthM = sample.Tlength.dt.total_seconds()/60
        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(2, 1, 1)
        bottom = 0
        for i in sample.index:
            if sample.loc[i, 'AREA'] == 'エリア外':
                c = 'm'
            elif len(self.cutarealist) <= 10:
                c = cm.tab10(self.cutarealist.index[self.cutarealist == sample.loc[i, 'AREA']])
            else:
                c = cm.tab20(self.cutarealist.index[self.cutarealist == sample.loc[i, 'AREA']])
        
            ax1.barh(1, TlengthM[i], left=bottom, color = c, height=0.5, alpha=0.7)
            bottom += TlengthM[i]
        ax1.set_xticks(np.arange(0,bottom,0.5))
        plt.xticks(fontsize=6)
        ax1.set_yticks([])
        ax1.set_ylabel('エリア', size=9, rotation=90)

        sample = self.cutdfj
        TlengthM = sample.Tlength.dt.total_seconds()/60
        # fig = plt.figure(figsize=figsize)
        ax2 = fig.add_subplot(2, 1, 2)
        bottom = 0
        for i in sample.index:
            c = self.colors[sample.loc[i, 'job2']]
            ax2.barh(1, TlengthM[i], left=bottom, color = c, height=0.5, alpha=0.7)
            bottom += TlengthM[i]
        ax2.set_xticks(np.arange(0,bottom,0.5))
        ax2.set_yticks([])
        if (self.ioflag == True) and (self.io.shape[0] > 0):
            io = self.io.copy()
            io['DateTime'] = (io['DateTime'] - self.lange[0]).dt.total_seconds()/60
            ax2.vlines(x=io['DateTime'], ymin=0.7, ymax=1.3, color='orangered', linewidth=6)
            for i, d in io.iterrows():
                ax2.annotate(d['記号'], xy =(d['DateTime']+0.02, 1), size=15)
        plt.tight_layout()
        plt.xticks(fontsize=6)
        ax2.set_xlabel('時間（分）', size=9)
        ax2.set_ylabel('作業', size=9, rotation=90)
        return fig

    # 半田工場のマップ上に作業エリアを表示する
    def area_map(self, arealist, ax):
        areas = self.areas[self.areas['name'].isin(arealist)]
        ax.imshow(self.img)
        for i in areas.index:
            if len(arealist) <= 10:
                c = cm.tab10(arealist.index[arealist == areas.loc[i,'name']])[0]
            else:
                c = cm.tab20(arealist.index[arealist == areas.loc[i,'name']])[0]
            area = areas.loc[i,:]
            patch = pat.Rectangle(xy=(area['rect_x1'], area['rect_y1']), width=area['rect_x2']-area['rect_x1'],\
                                    height=area['rect_y2']-area['rect_y1'], color=c, alpha=0.4, label = areas.loc[i,'name'])
            ax.add_patch(patch)

    # 動線図を作成する
    def trace_plot_INOUT(self, figsize=(10,15)):
        # 位置をプロット
        sample = self.cutdfL
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1,1,1)
        self.area_map(self.cutarealist, ax)
        ax.plot(sample['TMPX'], sample['TMPY'], alpha=0.5, linewidth=0.8, c='b')

        for j in self.colors.index:
            ss = sample.query('job2 == @j')
            ax.scatter(ss.loc[:,'TMPX'], ss.loc[:,'TMPY'], s=10, c = self.colors[j], alpha=1, label=j, zorder=3)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
        ax.scatter(sample['TMPX'].iloc[0], sample['TMPY'].iloc[0], s=30, label='start', c = 'y', zorder=5, linewidth=1, ec='b')   
        ax.scatter(sample['TMPX'].iloc[-1], sample['TMPY'].iloc[-1], s=30, label='end', c = 'g', zorder=5, linewidth=1, ec='b')
        ax.legend(fontsize=6, prop={'size':8}, 
                    loc='center left', bbox_to_anchor=(1,0.5))

        # INOUTをプロット
        if self.ioflag == True:
            def search_xy(d):
                i = (sample['DateTime'] - d).abs().idxmin()
                return pd.Series([sample.loc[i, 'TMPX'], sample.loc[i, 'TMPY']])
            if self.io.shape[0] > 0:
                self.io[['X', 'Y']] = self.io['DateTime'].apply(search_xy)
                ax.scatter(self.io['X'], self.io['Y'], s=60, alpha=1, zorder=5, c='orangered', marker='s', linewidth=1.5, ec='b')
                for i, d in self.io.iterrows():
                    ax.annotate(d['記号'], xy =(d['X']+25, d['Y']), size=15)

        ax.axis('equal')
        ax.set_xlim([sample['TMPX'].min()-300, sample['TMPX'].max()+300])
        ax.set_ylim([sample['TMPY'].min()-300, sample['TMPY'].max()+300])
        ax.invert_yaxis()
        plt.grid(False)
        plt.tight_layout()
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        return fig

    # INOUTの実績を表で出力する
    def output_table(self, figsize=(5,5)):
        self.io['num'] = self.io['num'].astype('int')
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1,1,1)
        ax.axis('off')
        ax.table(cellText=self.io[['品番','作業','num','記号']].values,
            colLabels=['品番','作業','数','番号'], loc='center', bbox=[0,0,1,1])
        return fig

    # 指定時間内のヒートマップを作成する
    def heatmap(self, lange=None, figsize=(10,10)):
        if lange == None:
            sample = self.dfL
            arealist = self.arealist
        elif isinstance(lange[0], dt.datetime):
            sample = timecut(self.dfL, lange)
            arealist = pd.Series(sample['AREA'].unique())
        bins = max(int(np.floor(200*len(sample)/40000)), 70)
        xl = sample['TMPX'].max() - sample['TMPX'].min()
        yl = sample['TMPY'].max() - sample['TMPY'].min()
        if xl >= yl:
            bins = [bins, int(np.floor(bins*yl/xl))]
        else:
            bins = [int(np.floor(bins*xl/yl)), bins]
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1,1,1)
        self.area_map(arealist, ax)
        ax.hist2d(sample.loc[:,'TMPX'], sample.loc[:,'TMPY'], cmap=cm.jet, bins=bins, norm=mc.LogNorm(), zorder=2, alpha=0.8)
        span = round(max(sample['TMPX'].max()-sample['TMPX'].min(), sample['TMPY'].max()-sample['TMPY'].min())/7, -1)
        ax.set_xticks(np.arange(round(sample['TMPX'].min(), -1), round(sample['TMPX'].max(), -1), span))
        ax.set_yticks(np.arange(round(sample['TMPY'].min(), -1), round(sample['TMPY'].max(), -1), span))
        ax.axis('equal')
        ax.set_xlim([sample['TMPX'].min()-300, sample['TMPX'].max()+300])
        ax.set_ylim([sample['TMPY'].min()-300, sample['TMPY'].max()+300])
        ax.invert_yaxis()
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        return fig

    # 山積み表を作成する
    def element_chart(self, unit, target='job2', figsize=(15,7)):
        work = summary_work(self.dfL, target, unit)
        if self.ioflag == True:
            inout = summary_inout(self.dfI, unit)
            fig = E_chart(work, inout, figsize=figsize)
        else:
            fig = E_chart(work, target, unit)
        return fig

# タグを二つ使った場合のクラス
class twin_tag_analysis(tag_analysis):
    def __init__(self, front_tag, back_tag, lange):
        super().__init__(front_tag, lange)
        self.F = self.dfL
        self.B = sql.load_pos(back_tag, lange[0], lange[1])

    def dual_filter(self, span, tsi, asi, win):
        def accuracy(df):
            Xaccuracy = df['X'].rolling(window = win, center=True).mean() - df['X']
            Yaccuracy = df['Y'].rolling(window = win, center=True).mean() - df['Y']
            Accuracy = np.sqrt(Xaccuracy**2 + Yaccuracy**2)
            AW = np.exp(-(Accuracy / np.sqrt(2)*asi)**2)
            return AW

        def prepare_matrix(df):
            def shift_matrix(sr, ind):
                columns = np.arange(win) - int(np.floor(win/2))
                df = pd.concat([sr.shift(x) for x in columns], axis=1)
                df.index = ind; df.columns = columns
                df = df[~df.index.duplicated(keep='first')]
                return df
            ind = df['DateTime'].dt.round(span)
            X = shift_matrix(df['X'], ind)
            Y = shift_matrix(df['Y'], ind)
            T = shift_matrix(df['DateTime'], ind)
            ST = T.sub(T.index, axis=0)
            ST = pd.concat([ST[i].dt.total_seconds() for i in T.columns], axis=1)
            TW = np.exp(-((ST / np.sqrt(2)*tsi)**2))
            AW = accuracy(df)
            AW = shift_matrix(AW, ind)
            W = TW*AW
            return {'X':X, 'Y':Y, 'W':W}

        F = prepare_matrix(self.F)
        B = prepare_matrix(self.B)
        ind = np.sort(list(set(F['X'].index) & set(B['X'].index)))
        F['X'] = F['X'].loc[ind,:]; F['Y'] = F['Y'].loc[ind,:]; F['W'] = F['W'].loc[ind,:]
        B['X'] = B['X'].loc[ind,:]; B['Y'] = B['Y'].loc[ind,:]; B['W'] = B['W'].loc[ind,:]
        N = F['W'].sum(axis=1) + B['W'].sum(axis=1)
        dfL = pd.DataFrame(np.zeros((len(ind),2)), columns=('X', 'Y'))
        dfL['X'] = (((F['X']*F['W']).sum(axis=1) + (B['X']*B['W']).sum(axis=1)) / N).values
        dfL['Y'] = (((F['Y']*F['W']).sum(axis=1) + (B['Y']*B['W']).sum(axis=1)) / N).values
        dfL['DateTime'] = ind
        dfL['TMPX'] = dfL['X'] * 45.8 + 35
        dfL['TMPY'] = dfL['Y'] * (-45.8) + 6925
        dfL = dfL.dropna()
        self.dfL = dfL
