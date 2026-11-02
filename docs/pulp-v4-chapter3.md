# PuLP 4.0 移行メモ（第3章）

## 変更内容

`school.ipynb` の3つのモデルを移行する。変数生成を `prob.add_variable_dicts(...)`、求解を `pulp.COIN_CMD(gapRel=0, gapAbs=0)` に変更する。表示は `stats.status_str`、従来の数値ステータスを表示する箇所は `stats.status.value` を使う。

`school_python-mip.ipynb` はコメントに残る PuLP の比較コードだけを更新する。python-mip 自体のコード、318人の同梱データ、制約・目的関数の係数と既存の説明コメントは維持する。既存 PR #2 のファイルをそのまま引き継ぐ。

## 検証と出力

元データで3つのモデルを解き、各モデルの2,544変数・406制約、変数の上下限・整数性、全制約を検証する。実行可能性問題の目的値0と、初期編成を維持するモデルの目的値298を移行前の基準値と比較する。2冊の Notebook の形式・Python 構文と旧 PuLP API の残存も確認する。

`school.ipynb` は既存 PR で全セルを実行した出力・グラフ・実行番号を維持する。複数の正しい編成があり、生徒 ID の割当やグラフの完全一致は要求しない。python-mip 版は既存の出力を維持し、全セル再実行はこの回帰テストに含めない。

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q tests/test_chapter3.py
```

## 書籍への修正候補

- 段階的なモデル作成、まとめたモデル、初期編成を維持するモデルの変数定義と求解結果の取得を更新する。
- 数値ステータスと表示文字列の取り出し方を説明する。
- 書籍の生徒 ID と異なる編成でも、各制約と目的値を満たす別解があることを出力例に補足する。

共通の環境と API の注意点は [移行メモ](pulp-v4-migration.md)を参照。
