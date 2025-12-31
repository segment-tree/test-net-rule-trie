import ipaddress
import datrie
import numpy as np
import sys

def ip_to_bitstring(net: ipaddress._BaseNetwork) -> str:
    """
    将网段转换为01字符串。
    例如 10.0.0.0/8 (IPv4) -> '00001010'
    """
    addr_int = int(net.network_address)
    prefixlen = net.prefixlen
    maxlen = net.max_prefixlen
    # 将地址右移，只保留前缀部分
    prefix_int = addr_int >> (maxlen - prefixlen)
    # 格式化为二进制字符串，并补齐长度
    bitstr = format(prefix_int, 'b').zfill(prefixlen)
    return bitstr

def find_min_index_iter(trie: datrie.Trie, query_string: str):
    """
    查找所有匹配的前缀，并返回其中索引(value)最小的一个。
    这对应于 ACL/防火墙 的 "First Match" 原则。
    """
    # prefix_items 返回路径上所有匹配的节点 [(key, value), ...]
    items = trie.prefix_items(query_string)
    
    if not items:
        return None
    
    # 找到 value (即 rule index) 最小的那个
    # item[1] 是 value
    min_index = min(items, key=lambda x: x[1])[1]
    return min_index

def main():
    # 读取规则数量
    line = sys.stdin.readline()
    if not line:
        return
    try:
        n = int(line.strip())
    except ValueError:
        print("Invalid number input", file=sys.stderr)
        return

    # 使用字典暂存规则：Key=BitString, Value=Original_Index
    # 目的1: 去重。如果出现相同的网段，只保留第一次出现的（Index最小的），因为ACL是顺序匹配。
    # 目的2: 为排序做准备。
    rules_map = {}
    
    # 存储动作标签 (0/1)，下标对应 Original_Index
    # 预分配空间，因为我们知道 n 的大小
    labels_list = [0] * n 

    for i in range(n):
        line = sys.stdin.readline()
        if not line:
            break
        
        parts = line.strip().split()
        if len(parts) != 2:
            continue
            
        net_str, bit_str = parts
        try:
            # strict=False 允许输入如 10.0.0.1/8 这样的非规范写法，自动转为 10.0.0.0/8
            net = ipaddress.ip_network(net_str, strict=False)
            bit = int(bit_str)
            if bit not in (0, 1):
                raise ValueError
        except Exception:
            print(f"Skipping invalid entry: {line.strip()}", file=sys.stderr)
            continue

        # 记录动作
        labels_list[i] = bit

        # 生成 Trie 的 Key
        key = ip_to_bitstring(net)

        # 【逻辑关键】：如果 Key 已存在，说明之前有更靠前的规则定义了该网段。
        # 由于我们只关心 First Match，后面的规则被以此 Key 为准的匹配屏蔽，因此不需要更新字典。
        if key not in rules_map:
            rules_map[key] = i

    # 转为 numpy 数组以便后续快速查询动作
    labels_arr = np.array(labels_list, dtype=np.int8)

    # -------------------------------------------------------
    # 【性能优化关键】：静态插入 (Static Insertion)
    # datrie 在插入按字典序排序的 Keys 时性能最高 (线性时间构建)
    # -------------------------------------------------------
    
    # 1. 提取所有唯一的 Key 并排序
    sorted_keys = sorted(rules_map.keys())

    # 2. 初始化 Trie，显式指定字符集范围 '0'~'1' (ASCII 48~49) 以节省内存
    trie = datrie.Trie(ranges=[(ord('0'), ord('1'))])

    # 3. 按顺序插入
    for key in sorted_keys:
        trie[key] = rules_map[key]

    print(f"Inserted {len(sorted_keys)} unique prefixes into trie")

    # 读取查询数量
    line = sys.stdin.readline()
    if not line:
        return
    try:
        m = int(line.strip())
    except ValueError:
        return

    # 处理查询
    for _ in range(m):
        line = sys.stdin.readline()
        if not line:
            break
        
        query_ip_str = line.strip()
        try:
            query_ip = ipaddress.ip_address(query_ip_str)
        except ValueError:
            print(f"Skipping invalid query: {query_ip_str}", file=sys.stderr)
            continue

        # 将查询 IP 转为完整的二进制字符串
        query_ip_int = int(query_ip)
        maxlen = query_ip.max_prefixlen
        query_bitstr = format(query_ip_int, 'b').zfill(maxlen)

        # 在 Trie 中查找匹配的最早规则索引
        index = find_min_index_iter(trie, query_bitstr)

        if index is not None:
            # 通过索引去数组查动作
            action = labels_arr[index]
            print(f'match rule {index}, {"permit" if action == 1 else "reject"}')
        else:
            print('match none')

if __name__ == '__main__':
    main()