"""
streamlitによるWEBアプリ

$ streamlit run application_st.py
"""
import pandas as pd
import streamlit as st

from problem import CarGroupProblem


def preprocess(students, cars):
    """リクエストデータを受け取り、データフレームに変換する関数"""
    # pandas で読み込む
    students_df = pd.read_csv(students)
    cars_df = pd.read_csv(cars)
    return students_df, cars_df


def convert_df(df):
    return df.to_csv().encode('utf-8')


col1, col2 = st.columns(2)

with col1:
    students = st.file_uploader('学生データ', type='csv')
    cars = st.file_uploader('車データ', type='csv')
    if students and cars:
        if st.button('最適化を実行'):
            with col2:
                # 前処理（データ読み込み）
                students_df, cars_df = preprocess(students, cars)
                # 最適化実行
                solution_df = CarGroupProblem(students_df, cars_df).solve()
                st.write('# 最適化結果')
                # ダウンロードボタン
                csv = convert_df(solution_df)
                st.download_button(
                    'Press to Download',
                    csv,
                    'solution.csv',
                    'text/csv',
                    key='download-csv')
                # 結果表示
                st.write(solution_df)
