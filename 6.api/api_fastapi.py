"""
最適化問題を解き、最適化結果を返すAPI

```
# Install uvicorn
$ pip install "uvicorn[standard]"
```

```
# Run FastAPI server
$ uvicorn api_fastapi:app --workers 4
```

```
$ curl -X POST \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d @resource/request_fastapi.json \
    http://127.0.0.1:8000/api
```
"""
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import uvicorn


from problem import CarGroupProblem


app = FastAPI()


def preprocess(students, cars):
    """リクエストデータを受け取り、データフレームに変換する関数"""
    # pandas で読み込む
    students_df = pd.DataFrame(students)
    cars_df = pd.DataFrame(cars)
    return students_df, cars_df


def postprocess(solution_df):
    """データフレームを csv に変換する関数"""
    solution_csv = solution_df.to_dict(orient='records')
    return solution_csv


class Student(BaseModel):
    student_id: int
    license: int
    gender: int
    grade: int


class Car(BaseModel):
    car_id: int
    capacity: int


class Solution(BaseModel):
    student_id: int
    car_id: int


@app.post('/api')
def solve(students: list[Student], cars: list[Car]) -> list[Solution]:
    """最適化問題を解く API 用の関数"""
    # 1. リクエスト受信
    students = [s.dict() for s in students]
    cars = [c.dict() for c in cars]
    students_df, cars_df = preprocess(students, cars)
    # 2. 最適化実行
    solution_df = CarGroupProblem(students_df, cars_df).solve()
    # 3. レスポンス返送
    response = postprocess(solution_df)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
