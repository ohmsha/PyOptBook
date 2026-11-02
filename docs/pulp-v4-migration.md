# PuLP 4.0 移行メモ

本家の `v4.0` ブランチへ、第2・3・4・5・6章を章別の PR で移行する。共通の依存関係とテスト基盤を先に取り込み、その後は各章を独立してレビューする。第5章は初版と第2版を同じ PR にまとめる。第7章は PuLP を使っていないためコードの変更対象に含めない。

元の移行コードは `ikki407/PyOptBook` の PR #1・#2 にあり、章別の PR ではその最終状態を引き継ぐ。uv への移行は別作業とする。

## 共通する変更と書籍への補足候補

| 箇所 | PuLP 4.0 での記載 |
| --- | --- |
| 実行環境・インストール | Python 3.12 以上を使用する。`pulp[cbc]==4.0.0` で CBC も導入する。main の PuLP 3.2.2 向け環境とは区別する。 |
| 変数の生成 | 問題を作成してから `prob.add_variable(...)` / `prob.add_variable_dicts(...)` を呼ぶ。変数を異なる問題へ使い回さない。 |
| 求解と結果の表示 | `solve()` は `LpSolveStats` を返す。表示には `stats.status_str`、実行可能解の有無には `stats.has_solution` を使う。 |
| 最適性の判定 | `stats.status == pulp.LpSolveStatus.Optimal` と比較する。`GapLimit` や `TimeLimit` で得た解と区別する。 |
| CBC の指定 | 廃止された `PULP_CBC_CMD` を `COIN_CMD` に変更する。厳密な最適解を求める例では `gapRel=0, gapAbs=0` を明示する。 |
| 制約の参照 | `prob.constraints()` はリストを返す。名前で取得する場合は `prob.get_constraint_by_name(name)` を使う。本書の移行対象コードに直接の変更箇所はない。 |
| 出力例 | 複数最適解の割当・経路、許容ギャップで終了する例の目的値、計算時間は環境により変わる。 |

章固有の変更と書籍の修正候補は、各章の PR に追加する `docs/pulp-v4-chapter2.md` から `docs/pulp-v4-chapter6.md` にまとめる。コード中の既存コメントは維持し、API 名など必要な箇所だけを置換する。

関連: [Issue #28](https://github.com/ohmsha/PyOptBook/issues/28)、[PuLP 公式移行ガイド](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html)。

## 回帰テスト

```sh
python -m pip install -r requirements-test.txt
python -m pytest -q
```

CI は Ubuntu・macOS・Windows の Python 3.12 / 3.13 で、取り込み済みの章のテストを実行する。共通基盤だけの段階では CBC の導入・整数計画の求解と、未変更の第7章 Notebook の形式・構文を確認し、章別 PR が各章のテストを追加する。第7章の全セル実行や CVXPY / QDLDL の検証は、この CI の対象に含めない。

既存 PR で取得した移行前の69回の求解結果を `tests/fixtures/notebook_results.csv` に維持する。変数数・制約数・解の上下限・整数性・全制約を検査し、目的値の比較には絶対誤差 `1e-5` / 相対誤差 `1e-8` を用いる。制約の許容誤差は係数の大きさに応じた `1e-7` とする。これは移行前の計算結果との比較であり、全章の書籍紙面や出力全体の完全一致を意味しない。

第5章の大規模配送は許容ギャップ内の実行可能性を検証し、暫定目的値の一致を条件にしない。各求解の上限は120秒、大規模配送のみ600秒とする。Notebook の実行済み出力と実行番号も維持し、元の PR で全セルを実行した出力をそのまま引き継ぐ。

macOS の CI は Homebrew の CBC を使う。別の CBC を使ってテストする場合は `PYOPTBOOK_CBC_PATH=/path/to/cbc python -m pytest -q` を実行する。アプリケーションで明示する場合は `pulp.COIN_CMD(path='/path/to/cbc')` を使う。

ローカルの macOS arm64 では `cbcbox 2.935` の CBC 実行が終了コード -9 で失敗したため、既存 PR の出力作成時は CBC 2.10.3 を指定した。CBC の版が異なる場合は、具体的な割当・経路・探索時間も変わり得る。
