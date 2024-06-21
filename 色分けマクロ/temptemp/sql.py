import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import datetime as dt

#####################################################################################################
def load_pos(tag, start, end):
    blueiot = "mysql+mysqlconnector://root:blueiot@160.203.161.76/blueiot"
    B_engine = create_engine(blueiot, echo=True)

    # タグ番号照会
    tag_state = "select * from localsense_tag"
    tags = pd.read_sql_query(tag_state, B_engine)
    tagid = tags[tags['TAGNAME'].str.contains(tag)]['TAGID'].iloc[0]

    # テーブル検索
    tb_state = "select * from localsense_tag_map"
    tables = pd.read_sql_query(tb_state, B_engine)

    to_datetime = lambda x : dt.datetime.fromtimestamp(x/1000)
    tables['BTime'] = tables['HISBEGINTM'].apply(to_datetime)
    tables['ETime'] = tables['HISENDTM'].apply(to_datetime)

    stable = tables.query('BTime <= @start').iloc[-1,:]
    etable = tables.query('ETime >= @end').iloc[0,:]

    sstamp = start.timestamp()*1000
    estamp = end.timestamp()*1000

    # 位置情報読み取り
    if stable['HISID'] == etable['HISID']:
        table_name = stable['HISTABLE']
        ps_state = f"select TAGID, X, Y, TIMESTAMP from {table_name} \
                    where TAGID={tagid} and TIMESTAMP >= {sstamp} and TIMESTAMP <= {estamp}"
        df = pd.read_sql_query(ps_state, B_engine)    
    else:
        IDs = np.arange(stable['HISID'], etable['HISID']+1)
        df = []
        for i in IDs:
            table_name = tables.query('HISID == @i')['HISTABLE'].iloc[0]
            ps_state = f"select TAGID, X, Y, TIMESTAMP from {table_name} \
                        where TAGID={tagid} and TIMESTAMP >= {sstamp} and TIMESTAMP <= {estamp}"
            df.append(pd.read_sql_query(ps_state, B_engine))
        df = pd.concat(df, axis=0)

    df['DateTime'] = df['TIMESTAMP'].apply(to_datetime)
    return df

def load_areas():
    footprint = "mysql+mysqlconnector://admi:admin@160.203.161.56:1234/footprint"
    F_engine = create_engine(footprint, echo=True)
    ar_state = "select * from areas"
    areas = pd.read_sql_query(ar_state, F_engine)
    return areas
