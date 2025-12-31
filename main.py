import ipaddress
import datrie
import numpy as np


def getprefix (ip : ipaddress) -> int:
    return int(ip.network_address) >> (ip.max_prefixlen - ip.prefixlen)


def ip_to_bitstring(net: ipaddress._BaseNetwork) -> str:
    """Return the binary string (length = prefixlen) representing the network address's
    most-significant bits (the network prefix) as a string of '0' and '1'.
    """
    addr_int = int(net.network_address)
    prefixlen = net.prefixlen
    if prefixlen == 0:
        return ""
    maxlen = net.max_prefixlen
    prefix_int = addr_int >> (maxlen - prefixlen)
    bitstr = format(prefix_int, 'b').zfill(prefixlen)
    return bitstr


def test_main():
    # Example usage of ipaddress module
    ip : ipaddress = ipaddress.ip_network('10.0.0.0/8')
    print(ip.max_prefixlen)
    print(f"Network: {ip}, prefix length: {ip.prefixlen}, ip: {int(ip.network_address)}")
    print(f"Prefix: {getprefix(ip)}")

    
def find_min_index_iter(trie: datrie.Trie, query_string:str) :
    it = trie.iter_prefix_items(query_string)
    try:
        _, index = min(it, key=lambda x: x[1])
        return index
    except ValueError:
        return None

def main():
    import sys

    # Read number of entries
    nStr = sys.stdin.readline()
    if not nStr:
        print("No input provided", file=sys.stderr)
        return
    try:
        n:int = int(nStr.strip())
    except Exception:
        print("Invalid number input", file=sys.stderr)
        return

    keys = []  # bitstring keys
    vals = []  # labels (0/1)

    # build a datrie that accepts only '0' and '1'
    trie = datrie.Trie('01')

    for i in range(n):
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.strip().split()
        if len(parts) != 2:
            print(f"Skipping malformed line: {line.strip()}", file=sys.stderr)
            continue
        net_str, bit_str = parts
        try:
            net = ipaddress.ip_network(net_str, strict=False)
            bit = int(bit_str)
            if bit not in (0, 1):
                raise ValueError("label(permit/reject) must be 0 or 1")
        except Exception as e:
            print(f"Skipping invalid entry '{line.strip()}': {e}", file=sys.stderr)
            continue

        key = ip_to_bitstring(net)
        # store into datrie (if duplicate keys appear, last one wins)
        if not key in trie:
            trie[key] = i
        keys.append(key)
        vals.append(bit)

    # store into numpy arrays
    networks_arr = np.array(keys, dtype=object)
    labels_arr = np.array(vals, dtype=np.int8)

    # Print a small summary
    print(f"Inserted {len(networks_arr)} prefixes into trie")
    # Optionally return structures if this module is used programmatically
    
    mStr = sys.stdin.readline()
    if not mStr:
        print("No input provided", file=sys.stderr)
        return
    try:
        m:int = int(mStr.strip())
    except Exception:
        print("Invalid number input", file=sys.stderr)
        return

    for j in range(m):
        line = sys.stdin.readline()
        if not line:
            break
        query_ip_str = line.strip()
        try:
            query_ip = ipaddress.ip_address(query_ip_str)
        except Exception as e:
            print(f"Skipping invalid query '{line.strip()}': {e}", file=sys.stderr)
            continue

        query_ip_int = int(query_ip)
        maxlen = query_ip.max_prefixlen
        query_bitstr = format(query_ip_int, 'b').zfill(maxlen)
    
        index = find_min_index_iter(trie, query_bitstr)
        if index is not None:
            label = labels_arr[index]
            print(f'match rule {index}, {"permit" if label == 1 else "reject"}')
        else:
            print('match none')  # default action if no match found



if __name__ == '__main__':
    main()