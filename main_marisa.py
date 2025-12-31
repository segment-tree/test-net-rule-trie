import ipaddress
import marisa_trie
import numpy as np


def getprefix (ip : ipaddress) -> int:
    return int(ip.network_address) >> (ip.max_prefixlen - ip.prefixlen)


def ip_to_bitstring(net: ipaddress._BaseNetwork) -> str:
    """Return the binary string (length = prefixlen) representing the network
    address's most-significant bits (the network prefix) as a string of '0'
    and '1'.
    """
    addr_int = int(net.network_address)
    prefixlen = net.prefixlen
    maxlen = net.max_prefixlen
    prefix_int = addr_int >> (maxlen - prefixlen)
    if prefixlen == 0:
        return ""
    bitstr = format(prefix_int, 'b').zfill(prefixlen)
    return bitstr


def find_min_index_marisa(trie: marisa_trie.Trie, query_string: str, key_to_index: dict):
    # marisa_trie.Trie.prefixes returns list of matching prefixes (strings)
    prefixes = trie.prefixes(query_string)
    if not prefixes:
        return None
    # choose the prefix whose stored index is minimal
    try:
        min_prefix = min(prefixes, key=lambda k: key_to_index[k])
        return key_to_index[min_prefix]
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

    keys = []  # bitstring keys (in insertion order for labels)
    vals = []  # labels (0/1)

    # We'll build a marisa_trie from the set of keys and keep a mapping
    # key -> index_position (position in vals list). We store the position
    # so labels can be looked up reliably even if some input lines are skipped.
    key_to_index = {}

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
        # append to lists; store mapping key->position (last write wins)
        pos = len(vals)
        keys.append(key)
        vals.append(bit)
        if key not in key_to_index:
            key_to_index[key] = pos

    # Build marisa trie from unique keys (keys of key_to_index)
    trie_keys = list(key_to_index.keys())
    # marisa_trie.Trie expects an iterable of unicode strings
    trie = marisa_trie.Trie(trie_keys)

    # store into numpy arrays
    networks_arr = np.array(keys, dtype=object)
    labels_arr = np.array(vals, dtype=np.int8)

    # Print a small summary
    print(f"Inserted {len(networks_arr)} prefixes into trie")

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

        index = find_min_index_marisa(trie, query_bitstr, key_to_index)
        if index is not None:
            # defensive: ensure index within labels_arr
            if 0 <= index < labels_arr.shape[0]:
                label = labels_arr[index]
                print(f'match rule {index}, {"permit" if label == 1 else "reject"}')
            else:
                print('match none')
        else:
            print('match none')  # default action if no match found


if __name__ == '__main__':
    main()
