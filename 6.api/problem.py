import pandas as pd
import pulp


class CarGroupProblem():
    """学生の乗車グループ分け問題を解くクラス"""
    def __init__(self, students_df, cars_df, name='ClubCarProblem'):
        # 初期化メソッド
        self.students_df = students_df
        self.cars_df = cars_df
        self.name = name
        self.prob = self._formulate()

    def _formulate(self):
        # 学生の乗車グループ分け問題（0-1整数計画問題）のインスタンス作成
        prob = pulp.LpProblem(self.name, pulp.LpMinimize)

        # リスト
        # 学生のリスト
        S = self.students_df['student_id'].to_list()
        # 車のリスト
        C = self.cars_df['car_id'].to_list()
        # 学年のリスト
        G = [1, 2, 3, 4]
        # 学生と車のペアのリスト
        SC = [(s, c) for s in S for c in C]
        # 免許を持っている学生のリスト
        S_license = self.students_df[self.students_df['license'] == 1]['student_id']
        # 学年が  g  の学生のリスト
        S_g = {g: self.students_df[self.students_df['grade'] == g]['student_id'] for g in G}
        # 男性と女性のリスト
        S_male = self.students_df[self.students_df['gender'] == 0]['student_id']
        S_female = self.students_df[self.students_df['gender'] == 1]['student_id']

        # 定数
        # 車の乗車定員
        U = self.cars_df['capacity'].to_list()

        # 変数
        # 学生をどの車に割り当てるかを変数として定義
        x = pulp.LpVariable.dicts('x', SC, cat='Binary')

        # 制約
        # (1) 各学生を１つの車に割り当てる
        for s in S:
            prob += pulp.lpSum([x[s, c] for c in C]) == 1

        # (2) 法規制に関する制約：各車には乗車定員より多く乗ることができない
        for c in C:
            prob += pulp.lpSum([x[s, c] for s in S]) <= U[c]

        # (3) 法規制に関する制約：各車にドライバーを1人以上割り当てる
        for c in C:
            prob += pulp.lpSum([x[s, c] for s in S_license]) >= 1

        # (4) 懇親を目的とした制約: 各車に各学年の学生を１人以上割り当てる
        for c in C:
            for g in G:
                prob += pulp.lpSum([x[s, c] for s in S_g[g]]) >= 1

        # (5) 各車に男性を1人以上割り当てる
        for c in C:
            prob += pulp.lpSum([x[s, c] for s in S_male]) >= 1

        # (6) 各車に女性を1人以上割り当てる
        for c in C:
            prob += pulp.lpSum([x[s, c] for s in S_female]) >= 1

        # 最適化後に利用するデータを返却
        return {'prob': prob, 'variable': {'x': x}, 'list': {'S': S, 'C': C}}

    def solve(self):
        # 最適化問題を解くメソッド
        # 問題を解く
        status = self.prob['prob'].solve()

        # 最適化結果を格納
        x = self.prob['variable']['x']
        S = self.prob['list']['S']
        C = self.prob['list']['C']
        car2students = {c: [s for s in S if x[s, c].value() == 1] for c in C}
        student2car = {s: c for c, ss in car2students.items() for s in ss}
        solution_df = pd.DataFrame(list(student2car.items()), columns=['student_id', 'car_id'])

        return solution_df


if __name__ == '__main__':
    # データの読み込み
    students_df = pd.read_csv('resource/students.csv')
    cars_df = pd.read_csv('resource/cars.csv')

    # 数理モデル インスタンスの作成
    prob = CarGroupProblem(students_df, cars_df)

    # 問題を解く
    solution_df = prob.solve()

    # 結果の表示
    print('Solution: \n', solution_df)
