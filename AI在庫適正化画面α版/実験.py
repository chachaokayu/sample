#メモリのリセット

#ライブラリのimport
import os
import pandas as pd
import numpy as np
%matplotlib inline
import matplotlib.pyplot as plt
import re 
from dateutil.relativedelta import relativedelta
#元データのパス
folder_path_zaikoMB = 'データ置き場/在庫MB'
folder_path_LTMB = 'データ置き場/所在管理MB'
folder_path_tehaisu = 'データ置き場/手配必要数'
folder_path_tehaiunyo = 'データ置き場/手配運用情報'
file_path_pitch = 'データ置き場/不等ピッチ係数/不等ピッチ係数.csv'
folder_path_kumitate = 'データ置き場/組立実績MB'
#中間成果物のパス
folder_path_interproduct = '中間成果物'
file_path_zaikodata = '中間成果物/在庫MBデータ_統合済.csv'
file_path_LTdata = '中間成果物/所在管理MBデータ_統合済.csv'
file_path_LTdata_extract = '中間成果物/所在管理MBデータ_統合済&特定日時抽出済.csv'
file_path_tehaisu_with_tehaiunyo = '中間成果物/手配数データ_手配運用情報統合済'
file_path_LTdata_extract_with_tehaisu = '中間成果物/所在管理MBデータ_統合済&特定日時抽出済&手配数と手配運用情報統合済.csv'
file_path_weekly_data = '中間成果物/週単位のデータ.csv'
file_path_kumitate = '中間成果物/組立実績MB_統合済.csv'
# フォルダー内の全てのCSVファイルを見つける
csv_files_zaikoMB = [f for f in os.listdir(folder_path_zaikoMB) if f.endswith('.csv')]
#
print(f"{len(csv_files_zaikoMB)}つのファイルが見つかりました！")

# 統合結果を保存するための空のDataFrameを作成
merged_df_zaiko = pd.DataFrame()
# CSVファイルをDataFrameに読み込んでリストに保存
for file in csv_files_zaikoMB:
    file_path = os.path.join(folder_path_zaikoMB, file)
    df_zaiko = pd.read_csv(file_path, encoding='Shift_JIS')
    merged_df_zaiko = pd.concat([merged_df_zaiko, df_zaiko], ignore_index=True)

# 統合したデータを新しいCSVファイルに保存
with open(file_path_zaikodata, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    merged_df_zaiko.to_csv(f)

#作成したDataFrameの内容を確認
display(merged_df_zaiko)
# フォルダー内の全てのCSVファイルを見つける
csv_files_LTMB = [f for f in os.listdir(folder_path_LTMB) if f.endswith('.csv')]
#
print(f"{len(csv_files_LTMB)}つのファイルが見つかりました！")

# 統合結果を保存するための空のDataFrameを作成
merged_df_LT = pd.DataFrame()
# CSVファイルをDataFrameに読み込んでリストに保存
for file in csv_files_LTMB:
    file_path = os.path.join(folder_path_LTMB, file)
    df_LT = pd.read_csv(file_path, encoding='Shift_JIS',dtype=str)
    merged_df_LT = pd.concat([merged_df_LT, df_LT], ignore_index=True)

# 不要な特定の列を削除
merged_df_LT = merged_df_LT.drop("伝票番号", axis=1)
merged_df_LT = merged_df_LT.drop("拠点所番地", axis=1)
merged_df_LT = merged_df_LT.drop("組立投入日時", axis=1)
merged_df_LT = merged_df_LT.drop("発注取消日時", axis=1)
merged_df_LT = merged_df_LT.drop("発注〜組立LT", axis=1)
merged_df_LT = merged_df_LT.drop("長期滞留フラグ", axis=1)

# 特定の文字列を含む行を削除する
target_string = "< NULL >"
merged_df_LT = merged_df_LT[~merged_df_LT.apply(lambda x: x.str.contains(target_string)).any(axis=1)]

# 統合したデータを新しいCSVファイルに保存
with open(file_path_LTdata, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    merged_df_LT.to_csv(f)

#作成したDataFrameの内容を確認
display(merged_df_LT)
# ユーザーからの入力を受け付けて特定の日付範囲のDataFrameを取り出す
start_date_input = input("開始日を入力してください（YYYY-MM-DD）: ")
end_date_input = input("終了日を入力してください（YYYY-MM-DD）: ")

##########所在管理MBデータ

# datetime型に変換する
merged_df_LT['回収日時'] = pd.to_datetime(merged_df_LT['回収日時'], errors='coerce')
merged_df_LT['納入日'] = pd.to_datetime(merged_df_LT['納入日'], errors='coerce') 

# 入力された日付をdatetime型に変換
start_date = pd.to_datetime(start_date_input).date()
end_date = pd.to_datetime(end_date_input).date()

# 特定の日付範囲のDataFrameを取り出す
merged_df_LT2 = merged_df_LT[(merged_df_LT["回収日時"].dt.date >= start_date) & (merged_df_LT["回収日時"].dt.date <= end_date)]

#インデックスを振り直す
merged_df_LT2.reset_index(drop=True, inplace=True)

# 統合したデータを新しいCSVファイルに保存
with open(file_path_LTdata_extract, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    merged_df_LT2.to_csv(f)

display(merged_df_LT2)
# フォルダー内の全てのCSVファイルを見つける
csv_files_tehaisu = [f for f in os.listdir(folder_path_tehaisu) if f.endswith('.csv')]
year_tehaisu = [file[2:4] for file in os.listdir(folder_path_tehaisu) if file.endswith(".csv")]
month_tehaisu = [file[4:6].replace("0", "") for file in os.listdir(folder_path_tehaisu) if file.endswith(".csv")]
#
print(f"{len(csv_files_tehaisu)}つのファイルが見つかりました！")

for i in range(len(year_tehaisu)):
    print(f"{year_tehaisu[i]}年の{month_tehaisu[i]}月のデータが見つかりました！") 

csv_files_tehaiunyo = [f for f in os.listdir(folder_path_tehaiunyo) if f.endswith('.csv')]
#
print(f"{len(csv_files_tehaiunyo)}つのファイルが見つかりました！")

pattern = r"手配運用情報(\d+)"
results = []
for file in csv_files_tehaiunyo:
    match = re.search(pattern, file)
    if match:
        results.append(match.group(1))
year_tehaiunyo = [file[0:2] for file in results]
month_tehaiunyo = [file[2:4].replace("0", "") for file in results]

for i in range(len(year_tehaiunyo)):
    print(f"{year_tehaiunyo[i]}年の{month_tehaiunyo[i]}月のデータが見つかりました！") 

year_diff = end_date.year - start_date.year
month_diff = end_date.month - start_date.month
total_months =  year_diff * 12 + month_diff + 1
print(total_months)

input_years = []
input_months = []

start_date_temp = start_date
for i in range(total_months):
    input_year = str(start_date_temp.year)[2:]
    input_month = start_date_temp.month
    start_date_temp = start_date_temp + relativedelta(months=i+1)
    print(input_year,input_month)
    
    input_years.append(input_year)
    input_months.append(input_month)
    
    flag = 0
    for j in range(len(csv_files_tehaisu)):
        if (int(input_year) == int(year_tehaisu[j])) and (int(input_month) == int(month_tehaisu[j])):
            flag = 1
    if flag == 1:
        print("手配数あります")
    elif flag == 0:
        print("手配数ありません")
        
    flag = 0
    for j in range(len(csv_files_tehaiunyo)):
        if (int(input_year) == int(year_tehaiunyo[j])) and (int(input_month) == int(month_tehaiunyo[j])):
            flag = 1
    if flag == 1:
        print("手配運用情報あります")
    elif flag == 0:
        print("手配運用情報ありません")
year_match = []
month_match = []

index_tehaisu = 0
for file in csv_files_tehaisu:
    file_path = os.path.join(folder_path_tehaisu, file)
    tehaisudata = pd.read_csv(file_path, encoding='Shift_JIS',dtype=str)#手配数データを読み込んでDataframeを作成
    index_tehaiunyo = 0
    for file in csv_files_tehaiunyo:
        print(month_tehaisu[index_tehaisu],month_tehaiunyo[index_tehaiunyo])
        file_path = os.path.join(folder_path_tehaiunyo, file)
        tehaiunyodata = pd.read_csv(file_path, skiprows = 9, encoding='cp932',dtype=str)#手配数データを読み込んでDataframeを作成
        tehaiunyodata.columns = [col.replace("=","").replace('"','') for col in tehaiunyodata.columns]
        tehaiunyodata_cleaned = tehaiunyodata.applymap(lambda x: x.replace('=','').replace('"','') if isinstance(x, str) else x)
        if (year_tehaisu[index_tehaisu] == year_tehaiunyo[index_tehaiunyo]) and (month_tehaisu[index_tehaisu] == month_tehaiunyo[index_tehaiunyo]):
            long_tehaisu = tehaisudata.iloc[:,1]#手配数データの行長さを取得
            long_tehaiunyo = tehaiunyodata_cleaned.iloc[:,1]#手配運用データの行長さを取得
            for i in range(len(long_tehaisu)):
                hinban_tehaisu = merged_df_LT2.loc[i,'品番'].replace("-", "").replace(" ", "")#品番名から" "を削除 
                for j in range(len(long_tehaiunyo)):
                    hinban_tehaiunyo = tehaiunyodata_cleaned.loc[j,'品番'].replace('-', '').replace(' ', '')#品番名から" "を削除
                    if hinban_tehaisu == hinban_tehaiunyo:
                        tehaisudata.loc[i,"納入回数（間隔）"] = tehaiunyodata_cleaned.loc[j,"納入ｻｲｸﾙ.間隔"]
                        tehaisudata.loc[i,"納入回数（回数）"] = tehaiunyodata_cleaned.loc[j,"納入ｻｲｸﾙ.回数"]
                        tehaisudata.loc[i,"納入回数（遅れ）"] = tehaiunyodata_cleaned.loc[j,"納入ｻｲｸﾙ.情報"]
                        tehaisudata.loc[i,"箱種類"] = tehaiunyodata_cleaned.loc[j,"登録箱種"]
                        tehaisudata.loc[i,"箱重量"] = tehaiunyodata_cleaned.loc[j,"総重量(Kg)"]
        index_tehaiunyo = index_tehaiunyo + 1
    
    # 統合したデータを新しいCSVファイルに保存
    file_new = file_path_tehaisu_with_tehaiunyo + year_tehaisu[index_tehaisu] + month_tehaisu[index_tehaisu] + ".csv"
    with open(file_new, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
        tehaisudata.to_csv(f)
    
    year_match.append(year_tehaisu[index_tehaisu])
    month_match.append(month_tehaisu[index_tehaisu])
        
    index_tehaisu = index_tehaisu + 1
    
    display(tehaisudata)
#中間成果物をダウンロード
merged_df_LT2 = pd.read_csv(file_path_LTdata_extract,encoding='shift_jis')

merged_df_LT2['回収日時'] = pd.to_datetime(merged_df_LT2['回収日時'], errors='coerce')
merged_df_LT2['回収月'] = merged_df_LT2['回収日時'].dt.month
merged_df_LT2['回収年'] = merged_df_LT2['回収日時'].dt.year
    
#index_file = 0
long = merged_df_LT2.iloc[:,1]
for m in range(total_months):
    input_year = input_years[m]
    input_month = input_months[m]
    file_path = file_path_tehaisu_with_tehaiunyo + str(input_year) + str(input_month) + ".csv"
    tehaisudata = pd.read_csv(file_path, encoding='Shift_JIS',dtype=str)#手配数データを読み込んでDataframeを作成
    for i in range(len(long)):
        if (int(str(merged_df_LT2.loc[i,'回収年'])[2:]) == int(input_years[m])) and (int(merged_df_LT2.loc[i,'回収月']) == int(input_months[m])):
            hinban = merged_df_LT2.loc[i,'品番']#品番名を取りだす 
            hinban2 = hinban.replace("-", "")#品番名から"-"を削除
            hinban3 = hinban2.replace(" ", "")#品番名から" "を削除 
            long_tehaisudata = tehaisudata.iloc[:,1]#手配数データの行長さを取得
            for j in range(len(long_tehaisudata)):
                tehaisuhinban = tehaisudata.loc[j,'品番'].replace('-', '')#品番名から"-"を削除
                tehaisuhinban2 = tehaisuhinban.replace(' ', '')#品番名から" "を削除
                if hinban3 == tehaisuhinban2:
                    merged_df_LT2.loc[i,"納入回数（間隔）"] = tehaisudata.loc[j,"納入回数（間隔）"]
                    merged_df_LT2.loc[i,"納入回数（回数）"] = tehaisudata.loc[j,"納入回数（回数）"]
                    merged_df_LT2.loc[i,"納入回数（遅れ）"] = tehaisudata.loc[j,"納入回数（遅れ）"]
                    merged_df_LT2.loc[i,"箱種類"] = tehaisudata.loc[j,"箱種類"]
                    merged_df_LT2.loc[i,"箱重量"] = tehaisudata.loc[j,"箱重量"]
                    merged_df_LT2.loc[i,"基準在庫日数"] = tehaisudata.loc[j,"基準在庫日数"]
                    merged_df_LT2.loc[i,"基準在庫枚数"] = tehaisudata.loc[j,"基準在庫枚数"]
                    day = merged_df_LT2.loc[i,'回収日時'].day
                    index = tehaisudata.columns.get_loc("翌々々月稼働日数") + day
                    merged_df_LT2.loc[i,'日量数'] = int(str(tehaisudata.iloc[j,index]).replace(',', ''))
                    merged_df_LT2.loc[i,'日量数（箱数）'] = int(merged_df_LT2.loc[i,'日量数']) /int(merged_df_LT2.loc[i, '収容数'])
                    merged_df_LT2.loc[i, '便Ave'] = merged_df_LT2.loc[i,'日量数（箱数）']/int(merged_df_LT2.loc[i, '納入回数（回数）'])
                    if int(str(tehaisudata.loc[j,'当月必要数']).replace(',', '')) != 0:
                        avenichiryo = int(str(tehaisudata.loc[j,'当月必要数']).replace(',', ''))/int(tehaisudata.loc[j,'当月稼働日数'])
                        merged_df_LT2.loc[i,'月平均日量数'] = avenichiryo
                        merged_df_LT2.loc[i,'月平均日量数（箱数）'] = avenichiryo//int(merged_df_LT2.loc[i, '収容数'])
                        merged_df_LT2.loc[i,'基準在庫枚数（日数）'] = (int(tehaisudata.loc[j,'基準在庫枚数'])*int(merged_df_LT2.loc[i, '収容数']))/avenichiryo
                        merged_df_LT2.loc[i,'基準在庫日数（基準在庫枚数込み）']= float(merged_df_LT2.loc[i,"基準在庫日数"]) + float(merged_df_LT2.loc[i,'基準在庫枚数（日数）'])
                    else:
                        merged_df_LT2.loc[i,'月平均日量数'] = 0
                        merged_df_LT2.loc[i,'月平均日量数（箱数）'] = 0
                        merged_df_LT2.loc[i,'基準在庫枚数（日数）'] = 0
                        merged_df_LT2.loc[i,'基準在庫日数（基準在庫枚数込み）']= 0
                        
    #index_file = index_file + 1

# 統合したデータを新しいCSVファイルに保存
with open(file_path_LTdata_extract_with_tehaisu, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    merged_df_LT2.to_csv(f)
    
display(merged_df_LT2)
#週単位で加工

#中間成果物をダウンロード
zaikodata = pd.read_csv(file_path_zaikodata,encoding='shift_jis')
LTdata = pd.read_csv(file_path_LTdata_extract_with_tehaisu,encoding='shift_jis')

# '計測日時'をdatatime型に変換
zaikodata['計測日時'] = pd.to_datetime(zaikodata['計測日時'], errors='coerce')
# '回収日'をdatatime型に変換
LTdata['回収日時'] = pd.to_datetime(LTdata['回収日時'], errors='coerce')

#在庫推移データを週単位に加工
zaikodata.dropna(subset=['計測日時'], inplace=True)#土日は入庫出庫の履歴がないことがあるので欠損値は削除
zaikodata['年'] = zaikodata['計測日時'].dt.year
zaikodata['週番号'] = zaikodata['計測日時'].dt.isocalendar().week
#週ごとにグループ化し、'在庫数（箱）', '入庫数（箱）', '出庫数（箱）'を計算
weekly_zaikodata = zaikodata.groupby(['品番', '年', '週番号']).agg({
   '在庫数（箱）': 'median',
   '入庫数（箱）': 'sum',
   '出庫数（箱）': 'sum'
}).reset_index()

#LTデータを週単位に加工
LTdata['年'] = LTdata['回収日時'].dt.year
LTdata['週番号'] = LTdata['回収日時'].dt.isocalendar().week
#週ごとにグループ化し、各グループのLT中央値を計算➀
weekly_LTdata_1 = LTdata.groupby(['品番', '仕入先名','年','週番号','基準在庫日数', '基準在庫日数（基準在庫枚数込み）','基準在庫枚数','箱種類','納入回数（間隔）','納入回数（回数）','納入回数（遅れ）']).agg({'日量数（箱数）':'median','発注〜印刷LT': 'median','発注〜検収LT': 'median','発注〜順立装置入庫LT': 'median', '発注〜順立装置出庫LT': 'median', '発注〜回収LT': 'median'})
#週ごとにグループ化し、各グループの行数（かんばん数）をカウント➁
weekly_LTdata_2 = LTdata.groupby(['品番','仕入先名','年', '週番号','基準在庫日数', '基準在庫日数（基準在庫枚数込み）','基準在庫枚数','箱種類','納入回数（間隔）','納入回数（回数）','納入回数（遅れ）']).size().reset_index(name='回収かんばん数')
#➀と➁データを統合
merged_weekly_LTdata = pd.merge(weekly_LTdata_1, weekly_LTdata_2, on=['品番', '仕入先名','年','週番号'], how='outer')

#週単位の在庫推移データとLTデータを統合
weekly_data = pd.merge(weekly_zaikodata, merged_weekly_LTdata, on=['品番', '年', '週番号'], how='inner')

#検収と入庫の時間変なやつある

#各LTの計算
long = weekly_data.iloc[:,1]
count = 0
for i in range(len(long)):
    weekly_data.loc[i, '印刷検収LT'] = float(weekly_data.loc[i, '発注〜検収LT']) - float(weekly_data.loc[i, '発注〜印刷LT'])
    weekly_data.loc[i, '検収入庫LT'] = float(weekly_data.loc[i, '発注〜順立装置入庫LT'])-float(weekly_data.loc[i, '発注〜検収LT'])
    weekly_data.loc[i, '入庫出庫LT'] = float(weekly_data.loc[i, '発注〜順立装置出庫LT'])-float(weekly_data.loc[i, '発注〜順立装置入庫LT'])
    weekly_data.loc[i, '出庫回収LT'] = float(weekly_data.loc[i, '発注〜回収LT'])-float(weekly_data.loc[i, '発注〜順立装置出庫LT'])
    weekly_data.loc[i, '社内LT（検収〜回収LT）'] = float(weekly_data.loc[i, '発注〜回収LT'])-float(weekly_data.loc[i, '発注〜検収LT'])
    count = count + 1
print(count)

# Load the new CSV file into a DataFrame with 'Shift_JIS' encoding
pitch = pd.read_csv(file_path_pitch, encoding='Shift_JIS')

longi = len(weekly_data.loc[:,"品番"])
longj = len(pitch.loc[:,"仕入先名"])

for i in range(longi):
    for j in range(longj):
        if (weekly_data.loc[i, '仕入先名'] == pitch.loc[j,'仕入先名']):
            weekly_data.loc[i,"不等ピッチ係数"] = pitch.loc[j,"不等ピッチ係数【日】"]

# '基準在庫日数' から '社内LT（検収～回収LT）' を引いた新しい列 'LT_差分' を追加
weekly_data['社内LT/設計値LT'] = weekly_data['社内LT（検収〜回収LT）']/weekly_data['基準在庫日数']
weekly_data['社内LT/設計値LT（基準在庫枚数込み）'] = weekly_data['社内LT（検収〜回収LT）']/weekly_data['基準在庫日数（基準在庫枚数込み）']
weekly_data['順立装置在庫量/設計値MIN'] = weekly_data['在庫数（箱）']/(0.1*(weekly_data['日量数（箱数）']*weekly_data['納入回数（間隔）']*(1+weekly_data['納入回数（遅れ）'])/weekly_data['納入回数（回数）']))
weekly_data['順立装置在庫量/設計値MAX'] = weekly_data['在庫数（箱）']/(weekly_data['順立装置在庫量/設計値MIN'] + weekly_data['日量数（箱数）']/weekly_data['納入回数（回数）'] + weekly_data['日量数（箱数）']*weekly_data.loc[i,"不等ピッチ係数"])

display(weekly_data)

# 統合したデータを新しいCSVファイルに保存
with open(file_path_weekly_data, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    weekly_data.to_csv(f)
# フォルダー内の全てのCSVファイルを見つける
csv_files_kumitateMB = [f for f in os.listdir(folder_path_kumitate) if f.endswith('.csv')]
#
print(f"{len(csv_files_kumitateMB)}つのファイルが見つかりました！")

# 統合結果を保存するための空のDataFrameを作成
merged_df_kumitate = pd.DataFrame()
# CSVファイルをDataFrameに読み込んでリストに保存
for file in csv_files_kumitateMB:
    file_path = os.path.join(folder_path_kumitate, file)
    df_kumitate = pd.read_csv(file_path, encoding='cp932')
    merged_df_kumitate = pd.concat([merged_df_kumitate, df_kumitate], ignore_index=True)

# 統合したデータを新しいCSVファイルに保存
with open(file_path_kumitate, mode='w',newline='', encoding='shift_jis',errors='ignore') as f:
    merged_df_kumitate.to_csv(f)

#作成したDataFrameの内容を確認
display(merged_df_kumitate)

# データフレームのインデックスを日付型に変換
merged_df_kumitate['LINE_DATE'] = pd.to_datetime(merged_df_kumitate['LINE_DATE'])
#AVAILABLE_RATE.set_index('LINE_DATE', inplace=True)
# 'WEEK_NUMBER'列を追加し、'LINE_DATE'の週番号を計算
merged_df_kumitate['Week_Number'] = merged_df_kumitate['LINE_DATE'].dt.isocalendar().week
merged_df_kumitate['WEEKDAY'] = merged_df_kumitate['LINE_DATE'].dt.weekday

# 土日を除外
merged_df_kumitate2 = merged_df_kumitate[(merged_df_kumitate['WEEKDAY'] != 5) & (merged_df_kumitate['WEEKDAY'] != 6)]

#1Y
merged_df_kumitate3 = merged_df_kumitate2[(merged_df_kumitate2['KUMI_CD'] == "NM11") | (merged_df_kumitate2['KUMI_CD'] == "NM12")]

#作成したDataFrameの内容を確認
display(merged_df_kumitate3)

# 'AVAILABLE_RATE'列を週単位でリサンプリングし、平均を計算
weekly_average_available_rate = merged_df_kumitate3.groupby('Week_Number').agg({'OPERATION_RATE': 'median', 'KAKO_CNT': 'median'})

weekly_average_available_rate = weekly_average_available_rate.rename(columns={'OPERATION_RATE': '時間稼働率'})
weekly_average_available_rate = weekly_average_available_rate.rename(columns={'KAKO_CNT': '加工数'})

#AVAILABLE_RATE.head(300)
display(weekly_average_available_rate)
#merged_weekly_LTdata.head(5)
#weekly_zaikodata.head(5)
#weekly_data.head(5)
#merged_df_LT2.loc[:,"回収月"].head(5)
merged_df_LT2.head(15)
#t = int(merged_df_LT2.loc[2,"回収月"])
conda update matplotlib
conda update ipython
merged_df.isnull().sum()
#merged_df.isnull().info()
merged_df.dtypes
merged_df.head(5)

