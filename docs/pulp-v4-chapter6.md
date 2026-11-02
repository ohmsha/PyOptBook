# PuLP 4.0 移行メモ（第6章）

## 変更内容

`6.api/problem.py` の変数生成を `prob.add_variable_dicts(...)` に変更し、`pulp.COIN_CMD()` で求解する。`stats.has_solution` が偽の場合はステータスを含む `ValueError` を返し、不正な割当を出力しない。時間制限でも実行可能解があれば利用する。

既存 PR #1 の第6章コード・専用 requirements・回帰テストをそのまま引き継ぐ。学生・車の集合、変数名、制約、通常の DataFrame / CSV / JSON の列名・型と既存の説明コメントは維持する。例外の HTTP 応答は既存フレームワークの処理に委ねる。車 ID は従来どおり行順に対応する0始まりの連番を前提とする。

第6章だけを実行する場合は、Python 3.12 以上で次のように導入する。

```sh
python -m pip install -r 6.api/requirements.txt
cd 6.api
python problem.py
```

## 検証と出力

19テストで24人・6台の144変数・72制約、全学生の割当、定員・免許・学年・男女の条件を確認する。4人・1台の一意解は移行前の DataFrame / CSV / JSON と完全一致で比較する。標準データの複数解では ID の一致を要求せず、元の解・現在の解・車を入れ替えた別解が同じ条件を満たすことを確認する。

実行不能な入力、解あり・解なしの時間制限、繰り返し求解、Flask API・FastAPI・HTML 表示・CSV ダウンロードを検証する。Streamlit は前処理と CSV 変換が対象で、ブラウザーの画面操作はこの CI に含めない。

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q tests/test_api.py
```

## 書籍への修正候補

- `CarGroupProblem._formulate` の変数定義を、問題に所属する変数を生成する形式に更新する。
- `CarGroupProblem.solve` に `LpSolveStats` の取得と `has_solution` の確認を掲載する。
- 目的関数のない実行可能性問題では、条件を満たす割当が複数あることを出力例に補足する。
- 第6章の導入手順に Python 3.12 以上、PuLP 4.0、CBC の導入方法を記載する。

共通の環境と API の注意点は [移行メモ](pulp-v4-migration.md)を参照。
