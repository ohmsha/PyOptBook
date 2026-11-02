# PuLP 4.0 移行メモ（第2章）

## 変更内容

`tutorial.ipynb` と `tutorial_scipy_optimize_milp.ipynb` の実行コードを移行する。`tutorial_python-mip.ipynb` はコメントに残る PuLP の比較コードだけを更新し、python-mip 自体のコードと保存済み出力を維持する。既存 PR #2 のファイルをそのまま引き継ぐ。

変数は `problem.add_variable(...)` / `problem.add_variable_dicts(...)` で生成する。求解は `pulp.COIN_CMD(gapRel=0, gapAbs=0)` を使い、結果の表示は `stats.status_str` に変更する。制約・目的関数の係数と既存の説明コメントは維持する。

## 検証と出力

連立方程式・LP・整数計画の7回と SciPy 比較の2回、計9回の PuLP 求解を移行前の基準値と比較する。モデルの規模、変数の上下限・整数性、全制約と目的値を検証する。SciPy の比較コードも実行する。3冊の Notebook の形式・Python 構文と旧 PuLP API の残存も確認する。

PuLP を実行する2冊は、既存 PR で全セルを実行した出力・表・実行番号を維持する。python-mip 版の全セル再実行は、この回帰テストに含めない。

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q tests/test_chapter2.py
```

## 書籍への修正候補

- 連立方程式・LP・整数計画の変数定義を、問題から変数を作る形式へ置換する。逐次定義や辞書内包表記の比較コードも合わせて更新する。
- 求解結果の表示を `LpSolveStats.status_str` に変更し、CBC の別途導入と明示指定を説明する。
- 一意の解と目的値を確認する例は維持する。ソルバーのログや計算時間は環境により変わることを補足する。

共通の環境と API の注意点は [移行メモ](pulp-v4-migration.md)を参照。
