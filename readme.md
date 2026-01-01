Only main_marisa.py, main_marisa2.py and main.py matters.

data_gen is data generater

other files are rubbish.

I have no idea why the efficiency gap is so so large.

*main_marisa.py* is the most efficient.

It seems that python do not have (very) efficient trie library.

---

输入先是一个数 n 表示一个结点的规则数

然后是 n 行规则。

然后一个 m 表示查询数

然后 n 个 ip 查询。

输出：

rule 的 match 情况。

---

`time python main_marisa.py < data_1e6.txt > /dev/null`

1e6 规则 1e6 询问大概 8.5s

`time python main_marisa.py < data_1e5.txt > /dev/null`

1e5 规则 1e5 询问大概 0.77s

---

以下为 1e6 次询问，规则数为不同量级的数据测试：

10:

2.05s

100:

2.08s

1000:

2.38s

1e4

3.19s

5e4

3.75s

1e5

4.1s

5e5

5.5s

1e6

8.5s