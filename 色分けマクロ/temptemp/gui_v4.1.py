import customtkinter as ctk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import functions_gui4_1 as fc
import datetime as dt
import glob
import matplotlib as mpl
import seaborn as sns
import warnings
sns.set(style="white")
mpl.rcParams['axes.xmargin'] = 0.01
plt.rcParams['font.family'] = "MS Gothic"
warnings.simplefilter('ignore')

FONT_TYPE = "meiryo"

'''
親クラス-------------------------------------------------------------------------------------------------------
'''
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.fonts = (FONT_TYPE, 15)
        self.csv_filepath = None

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        # フォームサイズ設定
        self.geometry("700x300")
        self.title("人流見える化")

        self.grid_columnconfigure(0, weight=1)

        self.fullframe = Full_Frame(master=self, header_name="設定")
        self.fullframe.grid(row=0, column=0, sticky="nsew")


'''
統括フレーム-----------------------------------------------------------------------------------------------------------------
'''
class Full_Frame(ctk.CTkScrollableFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs, width=300, height=800)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.setting_frame = SettingFrame(master=self, header_name="設定")
        self.setting_frame.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

        self.comp_frame = CompFrame(master=self, header_name="設定")
        self.comp_frame.grid(row=1, column=0, padx=10, pady=20, sticky="ew")     

        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=2, column=0, pady=10, sticky="ew")

        self.choise = ChoiseFrame(master=self, header_name="設定")
        self.choise.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.chart = ChartFrame(master=self, header_name="設定")
        self.chart.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.heatmap = HeatmapFrame(master=self, header_name="設定")
        self.heatmap.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        self.cycle = CycleFrame(master=self, header_name="設定")
        self.cycle.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

        self.makeline = LineFrame(master=self, header_name="設定")
        self.makeline.grid(row=7, column=0, padx=10, pady=10, sticky="ew")


'''
アウトプット用サブフレーム------------------------------------------------------------------------------------------------------
'''
class Result_Display(ctk.CTkFrame):
    def __init__(self, *args, text, color, **kwargs):
        super().__init__(*args, **kwargs)
        self.fonts = (FONT_TYPE, 15)

        # フォームのセットアップをする
        self.result = ctk.CTkLabel(self, text= text, font=(FONT_TYPE, 17), text_color=color)
        self.result.grid(row=0, column=0,padx=20, sticky="w")

class Figure_Frame(ctk.CTkFrame):
    def __init__(self, *args, fig, **kwargs):
        super().__init__(*args, **kwargs)
        self.fonts = (FONT_TYPE, 15)

        # フォームのセットアップをする
        self.canvas = FigureCanvasTkAgg(fig,  master=self)
        self.canvas.get_tk_widget().grid(row=0,column=0, padx=20, pady=10, sticky="nsew")


'''
条件設定フレーム--------------------------------------------------------------------------------------------------------------
'''
class SettingFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.readfileframe = ReadFileFrame(self)
        self.readfileframe.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self, text, color):
        self.result = Result_Display(self, text=text, color=color)
        self.result.grid(row=1, column=0, padx=10, sticky="ew")

class add_worker:
    def __init__(self, master, row):

        self.IDlabel = ctk.CTkLabel(master, text='氏名コード', font=(FONT_TYPE, 15))
        self.IDlabel.grid(row=row, column=0, padx=20, sticky="w")

        IDs = tuple(pd.read_csv('data/INOUT_layout/ID.csv', dtype='object').iloc[:,0].sort_values())
        self.IDbox = ctk.CTkComboBox(master, values=IDs)
        self.IDbox.grid(row=row, column=1, padx=10, pady=(0,10), sticky="w")

        self.Taglabel = ctk.CTkLabel(master, text='タグ番号', font=(FONT_TYPE, 15))
        self.Taglabel.grid(row=row, column=2, padx=20, sticky="e")

        TagsF = tuple(pd.read_csv('data/INOUT_layout/Tag.csv').iloc[:,0])
        self.TagFbox = ctk.CTkComboBox(master, values=TagsF)
        self.TagFbox.grid(row=row, column=3, padx=10, pady=(0,10), sticky="w")

        TagsB = ('なし',) + TagsF
        self.TagBbox = ctk.CTkComboBox(master, values=TagsB)
        self.TagBbox.grid(row=row, column=4, padx=(0,10), pady=(0,10), sticky="w")

class ReadFileFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()


    def setup_form(self):


        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=1)
        # 列方向のマスのレイアウトを設定する
        # self.grid_columnconfigure(1, weight=1)

        # フレームのラベルを表示
        self.label = ctk.CTkLabel(self, text='設定', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.workers = {}
        self.workers[1] = add_worker(self, 1)
        self.p = 2

        self.button_add = ctk.CTkButton(master=self, command=self.button_add_callback, text="追加", font=self.fonts)
        self.button_add.grid(row=1, column=5, padx=10, pady=(0,10))        

        self.Timelabel = ctk.CTkLabel(self, text='勤務時間', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=2, column=0, padx=20, pady=(20,10), sticky="w")        

        
        self.date_entry = DateEntry(self)
        self.date_entry.grid(row=2, column=1, padx=10, pady=(20,10), sticky="w")
        # self.date_entry.set_date(dt.datetime(2023,10,24))
        
        self.cbox = ctk.CTkComboBox(self, values=('昼','夜'))
        self.cbox.grid(row=2, column=2, padx=10, pady=(20,10), sticky="w")

        # 開始ボタン
        self.button_open = ctk.CTkButton(master=self, command=self.button_open_callback, text="分析開始", font=self.fonts)
        self.button_open.grid(row=2, column=3, padx=10, pady=(20,10))

    def button_add_callback(self):
        self.workers[self.p] = add_worker(self, self.p)
        self.button_add.grid(row=self.p, column=5, padx=10, pady=(0,10))
        self.Timelabel.grid(row=self.p+1, column=0, padx=20, pady=(20,10), sticky="w")
        self.date_entry.grid(row=self.p+1, column=1, padx=10, pady=(20,10), sticky="w")
        self.cbox.grid(row=self.p+1, column=2, padx=10, pady=(20,10), sticky="w")
        self.button_open.grid(row=self.p+1, column=3, padx=10, pady=(20,10))
        self.p += 1


    def button_open_callback(self):
        """
        開始ボタンが押されたときのコールバック。条件を読み込んでデータを準備する。
        """
        def prepare_data(worker, inout):
            ID = int(worker.IDbox.get())
            date = dt.datetime.combine(self.date_entry.get_date(), dt.time())
            time = self.cbox.get()
            if time == '昼':
                starttime = date + dt.timedelta(hours=8, minutes=30)
                endtime = date + dt.timedelta(hours=21, minutes=00)
            elif time == '夜':
                starttime = date + dt.timedelta(hours=21, minutes=00)
                endtime = date + dt.timedelta(days=1, hours=8, minutes=30)
            timerange = [starttime, endtime]
            print(timerange)
            
            tagF = worker.TagFbox.get()
            tagB = worker.TagBbox.get()
            if tagB == 'なし':
                L = fc.tag_analysis(tagF, timerange)
                L.filter(2, 1, 9)
            else:
                L = fc.twin_tag_analysis(tagF, tagB, timerange)
                L.dual_filter('1S', 2, 1, 9)
            
            if len(inout) > 0:
                L.inout(inout, ID)
            L.Vcal()
            L.area_judge()
            L.V_filter([0.7, 2.3])
            return L

        Ipath = glob.glob('data/INOUT/*.csv')
        Ipath = [f for f in Ipath if self.date_entry.get_date().strftime('%m') in f]
        if len(Ipath) > 0:
            Ipath = Ipath[0]
            inout = fc.inout_read(Ipath)
        else:
            inout = []
        try:
            self.master.master.datas = {}
            for n in self.workers:
                if self.workers[n].IDbox.get() != '':
                    self.master.master.datas[self.workers[n].IDbox.get()] = prepare_data(self.workers[n], inout)
            self.master.master.choise.cbox.configure(values=self.master.master.datas.keys())
            result_text = '>> 準備完了'
            color = 'cyan'
        except:
            result_text = '>> データ読み込み失敗 日付、タグ番号を確認してください'
            color = 'salmon'
        self.master.update(result_text, color)

'''
全体比較フレーム
'''
class CompFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.settingframe = CompSetting(self)
        self.settingframe.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self):
        self.result = Figure_Frame(self, fig=self.fig)
        self.result.grid(row=1, column=0, padx=10, sticky="ew")

class CompSetting(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.grid_rowconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text='山積み表（全体）', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.Timelabel = ctk.CTkLabel(self, text='比較基準', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=1, column=0, padx=20, sticky="w")        

        self.cbox = ctk.CTkComboBox(self, values=('作業者比較','時間比較'))
        self.cbox.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")
      
        self.TimeEbox = ctk.CTkEntry(master=self, width=120, font=self.fonts)
        self.TimeEbox.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")
        self.TimeEbox.insert(0, '1H')

        # 図の作成
        self.button_open = ctk.CTkButton(master=self, command=self.make_plot, text="作成", font=self.fonts)
        self.button_open.grid(row=1, column=3, padx=10, pady=(0,10))

    def make_plot(self):
        typ = self.cbox.get()
        unit = self.TimeEbox.get()
        if typ == '作業者比較':
            self.master.fig = fc.MP_chart(self.master.master.datas, figsize=(9, 5))
        elif typ == '時間比較':
            self.master.fig = fc.total_chart(self.master.master.datas, unit, figsize=(9, 5))
        self.master.update()


'''
対象選択フレーム
'''
class ChoiseFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        self.label = ctk.CTkLabel(self, text='個別分析', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.label2 = ctk.CTkLabel(self, text='対象選択', font=(FONT_TYPE, 15))
        self.label2.grid(row=1, column=0, padx=20, sticky="w")

        self.cbox = ctk.CTkComboBox(self, values=(' '))
        self.cbox.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")
        
        self.button_open = ctk.CTkButton(master=self, command=self.choise_callback, text="選択", font=self.fonts)
        self.button_open.grid(row=1, column=2, padx=10, pady=(0,10))
        
    def choise_callback(self):
        ID = self.cbox.get()
        self.master.L = self.master.datas[ID]
        self.master.heatmap.Heatmap.TimeSbox.delete(0, 100)
        self.master.heatmap.Heatmap.TimeEbox.delete(0, 100)
        self.master.cycle.Cycle.TimeSbox.delete(0, 100)
        self.master.cycle.Cycle.TimeEbox.delete(0, 100)
        self.master.makeline.MakeLine.TimeSbox.delete(0, 100)
        self.master.makeline.MakeLine.TimeEbox.delete(0, 100)

        self.master.heatmap.Heatmap.TimeSbox.insert(0,self.master.L.rng[0].strftime('%Y/%m/%d %H:%M'))
        self.master.heatmap.Heatmap.TimeEbox.insert(0,self.master.L.rng[1].strftime('%Y/%m/%d %H:%M'))
        self.master.cycle.Cycle.TimeSbox.insert(0,self.master.L.rng[0].strftime('%Y/%m/%d %H:%M'))
        self.master.cycle.Cycle.TimeEbox.insert(0,(self.master.L.rng[0]+dt.timedelta(minutes=20)).strftime('%Y/%m/%d %H:%M'))
        self.master.makeline.MakeLine.TimeSbox.insert(0,self.master.L.rng[0].strftime('%Y/%m/%d %H:%M'))
        self.master.makeline.MakeLine.TimeEbox.insert(0,(self.master.L.rng[0]+dt.timedelta(minutes=5)).strftime('%Y/%m/%d %H:%M'))

'''
山積み表フレーム------------------------------------------------------------------------------------------------------
'''
class ChartFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.settingframe = ChartSetting(self)
        self.settingframe.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self):
        self.result = Figure_Frame(self, fig=self.fig)
        self.result.grid(row=1, column=0, padx=10, sticky="ew")

class ChartSetting(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text='山積み表作成', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.Timelabel = ctk.CTkLabel(self, text='時間間隔', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=1, column=0, padx=20, sticky="w")        

        self.TimeEbox = ctk.CTkEntry(master=self, width=120, font=self.fonts)
        self.TimeEbox.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")
        self.TimeEbox.insert(0, '1H')

        # 図の作成
        self.button_open = ctk.CTkButton(master=self, command=self.make_plot, text="作成", font=self.fonts)
        self.button_open.grid(row=1, column=3, padx=10, pady=(0,10))

    def make_plot(self):
        unit = self.TimeEbox.get()
        self.master.fig = self.master.master.L.element_chart(unit, figsize=(9, 5))
        '''
        a = fc.summary_work(self.master.master.L.dfL, 'job2', '1H')
        self.master.fig = px.bar(a, barmode='relative')
        '''
        self.master.update()

'''
ヒートマップフレーム------------------------------------------------------------------------------------------------------
'''
class HeatmapFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.p = 0
        self.Heatmap = Heatmap(self)
        self.Heatmap.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self):
        if self.p == 1:
            self.result.grid_remove()
        self.result = Figure_Frame(self, fig=self.fig)
        self.result.grid(row=1, column=0, padx=10, sticky="ew")
        self.p = 1

    def update2(self):
        if self.p == 1:
            self.result.grid_remove()
        self.result = Result_Display(self, text='位置情報なし 表示時間を変更してください', color='salmon')
        self.result.grid(row=1, column=0, padx=10, sticky="ew")
        self.p = 1


class Heatmap(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=1)

        # フレームのラベルを表示
        self.label = ctk.CTkLabel(self, text='ヒートマップ', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.Timelabel = ctk.CTkLabel(self, text='表示時間', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=1, column=0, padx=20, sticky="w")        

        self.TimeSbox = ctk.CTkEntry(master=self, width=200, placeholder_text="開始", font=self.fonts)
        self.TimeSbox.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")

        self.TimeEbox = ctk.CTkEntry(master=self, width=200, placeholder_text="終了", font=self.fonts)
        self.TimeEbox.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")

        self.button_open = ctk.CTkButton(master=self, command=self.button_open_callback, text="作成", font=self.fonts)
        self.button_open.grid(row=1, column=3, padx=10, pady=(0,10))


    def button_open_callback(self):
        start = pd.to_datetime(self.TimeSbox.get())
        end = pd.to_datetime(self.TimeEbox.get())
        try:
            self.master.fig = self.master.master.L.heatmap([start, end], figsize=(7,4))
            self.master.update()
        except:
            self.master.update2()


'''
サイクル切り出しフレーム------------------------------------------------------------------------------------------------------
'''
class CycleFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.p = 0
        self.Cycle = Cycle(self)
        self.Cycle.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self):
        if self.p == 1:
            self.result.grid_remove()
        self.result = Figure_Frame(self, fig=self.fig)
        self.result.grid(row=1, column=0, padx=10, sticky="ew")
        self.p = 1

    def update2(self):
        if self.p == 1:
            self.result.grid_remove()
        self.result = Result_Display(self, text='エラー 表示時間を変更してください', color='salmon')
        self.result.grid(row=1, column=0, padx=10, sticky="ew")
        self.p = 1


class Cycle(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=1)

        # フレームのラベルを表示
        self.label = ctk.CTkLabel(self, text='サイクル分割', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.Timelabel = ctk.CTkLabel(self, text='検索時間', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=1, column=0, padx=20, sticky="w")

        self.TimeSbox = ctk.CTkEntry(master=self, width=200, placeholder_text="開始", font=self.fonts)
        self.TimeSbox.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")

        self.TimeEbox = ctk.CTkEntry(master=self, width=200, placeholder_text="終了", font=self.fonts)
        self.TimeEbox.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")

        self.button_open = ctk.CTkButton(master=self, command=self.button_open_callback, text="実行", font=self.fonts)
        self.button_open.grid(row=1, column=3, padx=10, pady=(0,10))


        self.choiselabel = ctk.CTkLabel(self, text='サイクル選択', font=(FONT_TYPE, 15))
        self.choiselabel.grid(row=2, column=0, padx=20, sticky="w")

        self.cbox = ctk.CTkComboBox(self, values=(' '))
        self.cbox.grid(row=2, column=2, padx=10, pady=(0,10), sticky="w")

        self.button_choise = ctk.CTkButton(master=self, command=self.button_choise_callback, text="選択", font=self.fonts)
        self.button_choise.grid(row=2, column=3, padx=10, pady=(0,10))

    def button_open_callback(self):
        start = pd.to_datetime(self.TimeSbox.get())
        end = pd.to_datetime(self.TimeEbox.get())
        # try:
        self.master.fig = self.master.master.L.cycle_cut([start, end], figsize=(7,4))
        self.cbox.configure(values=self.master.master.L.cycle.index.astype('str').values.tolist())
        self.master.update()
        # except:
            # self.master.update2()

    def button_choise_callback(self):
        ID = int(self.cbox.get())
        start = self.master.master.L.cycle.iloc[ID, 0]
        end = self.master.master.L.cycle.iloc[ID, 1]
        self.master.master.makeline.MakeLine.TimeSbox.delete(0, 100)
        self.master.master.makeline.MakeLine.TimeEbox.delete(0, 100)
        self.master.master.makeline.MakeLine.TimeSbox.insert(0,start.strftime('%Y/%m/%d %H:%M:%S'))
        self.master.master.makeline.MakeLine.TimeEbox.insert(0,end.strftime('%Y/%m/%d %H:%M:%S'))


'''
動線作成フレーム------------------------------------------------------------------------------------------------------
'''
class LineFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        self.p=0
        self.MakeLine = MakeLine(self)
        self.MakeLine.grid(row=0, column=0, padx=10, sticky="ew")
    
    def update(self):
        if self.p == 1:
            self.result1.grid_remove()
            self.result2.grid_remove()
            self.result3.grid_remove()

        self.result1 = Figure_Frame(self, fig=self.fig1)
        self.result1.grid(row=1, column=0, padx=10, pady=(0,3), sticky="ew")
        self.result2 = Figure_Frame(self, fig=self.fig2)
        self.result2.grid(row=2, column=0, padx=10, pady=(0,3), sticky="ew")
        if self.master.L.io.shape[0] > 0:
            self.result3 = Figure_Frame(self, fig=self.fig3)
            self.result3.grid(row=3, column=0, padx=10, pady=(0,3), sticky="ew")
        else:
            self.result3 = Result_Display(self, text='INOUTなし', color='salmon')
            self.result3.grid(row=3, column=0, padx=10, pady=(0,3), sticky="ew")
        self.p = 1
        

    def update2(self):
        if self.p == 1:
            self.result1.grid_remove()
            self.result2.grid_remove()
            self.result3.grid_remove()

        self.result1 = Result_Display(self, text='位置情報なし 表示時間を変更してください', color='salmon')
        self.result1.grid(row=1, column=0, padx=10, pady=(0,3), sticky="ew")
        self.result2 = Result_Display(self, text='', color='salmon')
        self.result2.grid(row=2, column=0, padx=10, pady=(0,3), sticky="ew")
        self.result3 = Result_Display(self, text='', color='salmon')
        self.result3.grid(row=3, column=0, padx=10, pady=(0,3), sticky="ew")
        self.p = 1

class MakeLine(ctk.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=1)
        # 列方向のマスのレイアウトを設定する
        # self.grid_columnconfigure(1, weight=1)

        # フレームのラベルを表示
        self.label = ctk.CTkLabel(self, text='動線作成', font=(FONT_TYPE, 20))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.Timelabel = ctk.CTkLabel(self, text='表示時間', font=(FONT_TYPE, 15))
        self.Timelabel.grid(row=1, column=0, padx=20, sticky="w")        

        self.TimeSbox = ctk.CTkEntry(master=self, width=200, placeholder_text="開始", font=self.fonts)
        self.TimeSbox.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")
        # self.TimeSbox.insert(0,str(self.master.master.rng[0]))

        self.TimeEbox = ctk.CTkEntry(master=self, width=200, placeholder_text="終了", font=self.fonts)
        self.TimeEbox.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")
        # self.TimeEbox.insert(0,str(self.master.master.rng[1]))

        # 開始ボタン
        self.button_open = ctk.CTkButton(master=self, command=self.button_open_callback, text="作成", font=self.fonts)
        self.button_open.grid(row=1, column=3, padx=10, pady=(0,10))


    def button_open_callback(self):
        start = pd.to_datetime(self.TimeSbox.get())
        end = pd.to_datetime(self.TimeEbox.get())
        try:
            self.master.master.L.work_table([start, end])
            self.master.fig1 = self.master.master.L.plot_timescale_INOUT(figsize=(9,2))
            self.master.fig2 = self.master.master.L.trace_plot_INOUT(figsize=(9,4))
            if self.master.master.L.io.shape[0] > 0:
                self.master.fig3 = self.master.master.L.output_table(figsize=(5,2))
            self.master.update()
        except:
            self.master.update2()


if __name__ == "__main__":
    app = App()
    app.mainloop()