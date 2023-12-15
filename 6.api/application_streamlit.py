"""
Streamlitによる最適化WEBアプリケーション

```
$ pip install streamlit
```

```
$ streamlit run application_streamlit.py
```
"""
import pandas as pd
import streamlit as st  # streamlitのimport

from problem import CarGroupProblem


def preprocess(students, cars):
    """UploadedFile(csv) -> pd.DataFrame"""
    students_df = pd.read_csv(students)
    cars_df = pd.read_csv(cars)
    return students_df, cars_df


def convert_to_csv(df):
    """pd.DataFrame -> csv"""
    return df.to_csv().encode('utf-8')


# 画面を二分割する（画面の左側をファイルアップロード、右側を最適化結果の表示とする）
# col1: 左側、col2: 右側
col1, col2 = st.columns(2)

# 画面の左側の実装
with col1:
    # ファイルアップロードのフィールド
    students = st.file_uploader('学生データ', type='csv')
    cars = st.file_uploader('車データ', type='csv')
    # 全てのデータがアップロードされたら以降のUIを表示（studentsとcarsはファイルアップロードがされていない場合はNoneとなり、以下UIの表示はしない）
    if students is not None and cars is not None:
        # 最適化ボタンの表示
        if st.button('最適化を実行'):
            # 最適化ボタンが押されたら最適化を実行
            # 前処理（データ読み込み）
            students_df, cars_df = preprocess(students, cars)
            # 最適化実行
            solution_df = CarGroupProblem(students_df, cars_df).solve()
            # 画面の右側にダウンロードボタンと最適化結果を表示する
            with col2:
                st.write('#### 最適化結果')
                # ダウンロードボタンの表示
                csv = convert_to_csv(solution_df)
                st.download_button(
                    'Press to Download',
                    csv,
                    'solution.csv',
                    'text/csv',
                    key='download-csv')
                # 最適化結果の表示
                st.write(solution_df)
