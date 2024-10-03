import streamlit as st
import sqlite3
import pandas as pd
import datetime
import pytz

conn = sqlite3.connect('Safety.db')
c = conn.cursor()
c.execute("""CREATE TABLE if not exists "member" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT,
    "shokui" TEXT,
	"birthday"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
)""")
c.execute("""CREATE TABLE if not exists "data" (
	"id"	INTEGER NOT NULL,
    "name"	TEXT,         
    "event_name" TEXT,
    "answer" TEXT,
    "other" TEXT,
	"timestamp"	INTEGER,
	PRIMARY KEY("id")
)""")
c.execute("""CREATE TABLE if not exists "event" (
	"id"	INTEGER NOT NULL,
    "event_name" TEXT,
	"timestamp"	INTEGER,
	PRIMARY KEY("id")
)""")

def rcd():
    conn = sqlite3.connect('Safety.db')
    c = conn.cursor()

    c.execute("INSERT INTO data (name,event_name,answer,other,timestamp) VALUES(?,?,?,?,?)",(select_person,select_event,answer,other,now,))
    conn.commit()

    c.execute("select * from data where name=? order by timestamp DESC LIMIT 5",(select_person,))
    
    data = c.fetchall()
    # カラム名を取得
    columns = [desc[0] for desc in c.description]

    # DataFrameに変換
    df = pd.DataFrame(data, columns=columns)

    # StreamlitでDataFrameを表示
    st.dataframe(df)

    conn.close()


tab1,tab2,tab3,tab4 = st.tabs(["入力","登録状況照会","事案設定","社員設定"])

# 入力
with tab1:

    conn = sqlite3.connect('Safety.db')

    event = pd.read_sql_query("select event_name from event order by timestamp DESC",conn)
    member =  pd.read_sql_query("select name from member order by shokui ASC , birthday ASC",conn)

    select_event =st.selectbox('事案名',event)
    select_person = st.selectbox('氏名',member)

    answer = st.radio("状況",("無事","困難あり"), horizontal=True)

    other = st.text_area('連絡事項等：')

    # 東京のタイムゾーン
    JST = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')
    
    if st.button('登録'):
        rcd()

    conn.close()

# 照会
with tab2:

    conn = sqlite3.connect('Safety.db')

    event = pd.read_sql_query("select event_name from event order by timestamp DESC",conn)
    event_name = st.selectbox('事案名：',event)
    
    jyokyo = pd.read_sql_query("select name,answer,other,timestamp from data where event_name=?",conn,params=[event_name])
    
    member =  pd.read_sql_query("select name from member order by shokui ASC ,birthday ASC",conn)

    # DataFrameに変換
    df = pd.merge(member,jyokyo, on='name',how='left')

        # StreamlitでDataFrameを表示
    st.dataframe(df)

    conn.close()

# 事案登録
with tab3:
    
    event_name = st.text_input('事案名')
    # 東京のタイムゾーン
    JST = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('Safety.db')
    df_before = pd.read_sql_query('SELECT * FROM event order by timestamp DESC',conn)
    
    st.dataframe(df_before)

    if st.button('事案登録'):
        conn = sqlite3.connect('Safety.db')
        c = conn.cursor()

        c.execute("INSERT INTO event (event_name,timestamp) VALUES(?,?)",(event_name,now,))
        conn.commit()

        st.success('事案登録完了')

        c.execute('SELECT * FROM event order by timestamp DESC')
        rows = c.fetchall()
        st.dataframe(rows)

        conn.close()

#　社員情報
with tab4:  

    conn = sqlite3.connect('Safety.db')
    c = conn.cursor()

    # CSVファイルをアップロード
    uploaded_file = st.file_uploader("社員名簿CSVファイルを選択してください", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="Shift-JIS")

        # DataFrameをSQLite3に挿入（または更新）
        df.to_sql('member', conn, if_exists='replace', index=False)
        st.success('社員名簿が更新されました！')

    # SQLite3からデータを取得し、表示
    c.execute('SELECT * FROM member')
    rows = c.fetchall()
    st.dataframe(rows)

    conn.close()
