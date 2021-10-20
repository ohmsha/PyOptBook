# 正誤表

正誤表をまとめています。ご連絡いただいた読者の皆様、大変ありがとうございます。


## **コード**(2021.10.20以前)

<!--
| ページ | 誤 | 正 |
| ---- | ---- | ---- |
| XXXX | YYYY | ZZZZ |
-->

<table>
    <thead>
        <tr>
            <th scope="col">ページ</th>
            <th scope="col">誤</th>
            <th scope="col">正</th>
        </tr>
    </thead>
<tbody>
<!-- 1行開始 -->
<tr>
<td>
P32/P34/P37
</td>
<td>

「生産量は在庫の範囲」という制約を定義する際に`stock[m]`直前で不要な改行がある

```python
for m in M:
    problem += pulp.lpSum([require[p,m] * x[p] for p in P]) <= 
stock[m]
```

</td>
<td>

```python
for m in M:
    problem += pulp.lpSum([require[p,m] * x[p] for p in P]) <= stock[m]
```
</td>
</tr>
<!-- 1行開始 -->
<tr>
<td>
P67/P83
</td>
<td>

直前で定義したリストのペア`SS`を使っていない。  
P67のコードでも正常動作するが、P61のコードをそのまま記述するのが正しい。

```py
for row in s_pair_df.itertuples():
    s1 = row.student_id1
    s2 = row.student_id2
    for c in C:
        prob += x[s1,c] + x[s2,c] <= 1
```

</td>
<td>

```py
for s1, s2 in SS:
    for c in C:
        prob += x[s1,c] + x[s2,c] <= 1
```
</td>
</tr>
<!-- 1行開始 -->
<tr>
<td>
P223
</td>
<td>

2つ目のコードブロックで改行記号（↩︎）が2箇所抜けている

```html
<form name=download action="/download" method=post 
enctype=multipart/form-data>
    <input type=hidden name=solution_html value="{{ 
solution_html }}">
```

</td>
<td>

```html
<form name=download action="/download" method=post      ↩︎
enctype=multipart/form-data>
    <input type=hidden name=solution_html value="{{     ↩︎
solution_html }}">
```
</td>
</tr>
<!-- 1行開始 -->
<tr>
<td>
P264
</td>
<td>

cvxoptのimportの仕方を修正する。

```py
from cvxopt import solvers
```

</td>
<td>

```py
import cvxopt
```
</td>
</tr>
<!-- 1行開始 -->
<tr>
<td>
P269
</td>
<td>

cvxoptをimportしないようにする。  
なお、元のコードではimportのタイポ(inport)がある。

```py
inport cvxopt
```

</td>
<td>

```
```
</td>
</tr>
</tbody>
</table>




## **本文**


| ページ | 誤 | 正 |
| ---- | ---- | ---- |
| P49 | 173,3 | 173.3 |
| P54 | 8クラスをA〜Hのアルファベットで表しています。 | 8クラスをA〜Hのアルファベットで表すことにします。 |
| P60 | ![x_{s1, c} + s_{s2, c} \leq 1](https://latex.codecogs.com/gif.latex?x_%7Bs1%2C%20c%7D%20&plus;%20s_%7Bs2%2C%20c%7D%20%5Cleq%201) | ![x_{s1, c} + x_{s2, c} \leq 1](https://latex.codecogs.com/gif.latex?x_%7Bs1%2C%20c%7D%20&plus;%20x_%7Bs2%2C%20c%7D%20%5Cleq%201) |



## **本文**(2021.10.20以降)
| ページ(箇所) | 誤 | 正 |
| ---- | ---- | ---- |
| P2 1行目 | 扱う扱う | 扱う |
| P17 図内(2箇所)| 利益 | 利得 |
| P20 最下行| 利益 | 利得 |
| P18 3-4行目| 線形計画問題と連立一次方程式と異なる箇所として | 線形計画問題が連立一次方程式と異なる箇所として |
| P27 下から3行目| それぞれ require_df, gain_df, stock_df から取得します。 | それぞれ stock_df, require_df, gain_df から取得します。 |
| P38 2.4節2行目| 二次方程式と線形計画問題の実装はよく似ており、制約式や目的関数の設定に違いがあること | 連立一次方程式と線形計画問題の実装はよく似ているが、制約式や目的関数の設定には違いがあること |
| P296 7行目| 今日から使える! 組み合わせ最適化 離散問題ガイドブック | 今日から使える! 組合せ最適化 離散問題ガイドブック |



