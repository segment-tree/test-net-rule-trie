#!/usr/bin/env python3
# totally gen by ai
"""
Generate a single data file suitable for piping to `main.py`.
Format produced:
  <n>\n
  <network1> <0/1>\n
  ... n rules ...\n
  <m>\n
  <query_ip1>\n
  ... m queries ...\n
By default n=m=1_000_000. The generator uses numpy in chunks for performance.
"""
import argparse
import ipaddress
import numpy as np
import sys


def gen_rules_chunk(rng, chunk_size, min_prefix=8, max_prefix=32):
    # prefix lengths
    prefixlens = rng.integers(min_prefix, max_prefix + 1, size=chunk_size, dtype=np.int32)
    # random 32-bit addresses
    addrs = rng.integers(0, 2**32, size=chunk_size, dtype=np.uint64)
    # labels 0/1
    labels = rng.integers(0, 2, size=chunk_size, dtype=np.int8)

    # mask addresses according to prefixlen: keep top prefixlen bits
    # compute host bits = 32 - prefixlen
    host_bits = 32 - prefixlens
    # build masks using numpy left shift on uint64 to avoid Python integer overflow
    # mask = (0xFFFFFFFF << host_bits) & 0xFFFFFFFF
    masks = (np.left_shift(np.uint64(0xFFFFFFFF), host_bits.astype(np.uint64)) & np.uint64(0xFFFFFFFF)).astype(np.uint64)
    net_addrs = addrs & masks

    for a, p, lab in zip(net_addrs, prefixlens, labels):
        yield f"{ipaddress.IPv4Address(int(a))}/{int(p)} {int(lab)}\n"


def gen_queries_chunk(rng, chunk_size):
    addrs = rng.integers(0, 2**32, size=chunk_size, dtype=np.uint64)
    for a in addrs:
        yield f"{ipaddress.IPv4Address(int(a))}\n"


def write_data(out_path, n, m, seed=None, chunk_size=100_000):
    rng = np.random.default_rng(seed)
    with open(out_path, 'w') as f:
        # write n
        f.write(f"{n}\n")

        # rules in chunks
        written = 0
        while written < n:
            this = min(chunk_size, n - written)
            for line in gen_rules_chunk(rng, this):
                f.write(line)
            written += this
            print(f"Wrote {written}/{n} rules", file=sys.stderr)

        # write m (same as n)
        f.write(f"{m}\n")

        # queries in chunks
        written_q = 0
        while written_q < m:
            this = min(chunk_size, m - written_q)
            for line in gen_queries_chunk(rng, this):
                f.write(line)
            written_q += this
            print(f"Wrote {written_q}/{m} queries", file=sys.stderr)


def parse_args():
    p = argparse.ArgumentParser(description="Generate rules+queries data file for main.py")
    p.add_argument('--n', type=int, default=1_000_000, help='Number of rules and queries (default 1e6)')
    p.add_argument('--out', type=str, default='data_1e6.txt', help='Output file path (default data.txt)')
    p.add_argument('--seed', type=int, default=None, help='Random seed')
    p.add_argument('--chunk', type=int, default=100_000, help='Chunk size for generation (default 100k)')
    return p.parse_args()


def main():
    args = parse_args()
    print(f"Generating n={args.n} rules and queries into {args.out} (chunk={args.chunk})", file=sys.stderr)
    write_data(args.out, 1_000_000, args.n, seed=args.seed, chunk_size=args.chunk)
    print("Done", file=sys.stderr)


if __name__ == '__main__':
    main()
