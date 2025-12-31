Only main_marisa.py, main_marisa2.py and main.py matters.

data_gen is data generater

other files are rubbish.

I have no idea why the efficiency gap is so so large.

*main_marisa.py* is the most efficient.

It seems that python do not have efficient trie library.

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
