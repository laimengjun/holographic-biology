"""holography_stats v2 — 全息度量：高斯法 + 分箱法（后者能看见交互）
2026-10-24　配套 research/10.5-operationalizing-9-and-12.md
运行：python holography_stats_v2.py
"""
import numpy as np


def _erf(x):
    s = np.sign(x); x = np.abs(x); t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
              - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x)
    return s * y


def _erfinv(y):
    y = np.clip(y, -0.999999, 0.999999); a = 0.147
    ln1 = np.log(1 - y * y); t = 2 / (np.pi * a) + ln1 / 2
    x = np.sign(y) * np.sqrt(np.sqrt(t * t - ln1 / a) - t)
    for _ in range(2):
        x = x - (_erf(x) - y) / (2 / np.sqrt(np.pi) * np.exp(-x * x))
    return x


def _norm(x):
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    n = x.shape[0]; out = np.empty_like(x)
    for j in range(x.shape[1]):
        o = np.argsort(x[:, j], kind="mergesort"); r = np.empty(n); r[o] = np.arange(1, n + 1)
        out[:, j] = np.sqrt(2.0) * _erfinv(2 * ((r - .5) / n) - 1)
    return out


def _Hcov(z):
    d = z.shape[1]; c = np.cov(z, rowvar=False)
    c = np.array([[float(c)]]) if d == 1 else c
    s, ld = np.linalg.slogdet(c)
    return np.nan if s <= 0 else .5 * (d * np.log(2 * np.pi * np.e) + ld)


def gauss_mi(x, y):
    zx, zy = _norm(x), _norm(y)
    return max(0., _Hcov(zx) + _Hcov(zy) - _Hcov(np.hstack([zx, zy])))


def _bins(x, nb):
    x = np.asarray(x, dtype=float)
    q = np.quantile(x, np.linspace(0, 1, nb + 1)[1:-1])
    return np.searchsorted(q, x, side="right")


def _Hc(counts, n):
    p = counts[counts > 0] / n
    return float(-(p * np.log(p)).sum())


def binned_mi(x, y, nb=6):
    bx, by = _bins(x, nb), _bins(y, nb); n = len(bx)
    h = np.zeros((nb, nb))
    for i in range(n):
        h[bx[i], by[i]] += 1
    return max(0., _Hc(h.sum(1), n) + _Hc(h.sum(0), n) - _Hc(h, n))


def binned_synergy(a, b, c, nb=5):
    ba, bb, bc = _bins(a, nb), _bins(b, nb), _bins(c, nb); n = len(ba)
    h = np.zeros((nb, nb, nb))
    for i in range(n):
        h[ba[i], bb[i], bc[i]] += 1
    Hab, Hc = _Hc(h.sum(2), n), _Hc(h.sum((0, 1)), n)
    Habc, Ha = _Hc(h, n), _Hc(h.sum((1, 2)), n)
    Hac, Hb = _Hc(h.sum(1), n), _Hc(h.sum((0, 2)), n)
    Hbc = _Hc(h.sum(0), n)
    return float((Hab + Hc - Habc) - (Ha + Hc - Hac) - (Hb + Hc - Hbc))


def binned_partial_mi(x, y, z, nb=4):
    bx, by, bz = _bins(x, nb), _bins(y, nb), _bins(z, nb); n = len(bx)
    h = np.zeros((nb, nb, nb))
    for i in range(n):
        h[bx[i], by[i], bz[i]] += 1
    return max(0., _Hc(h.sum(1), n) + _Hc(h.sum(0), n) - _Hc(h.sum((0, 1)), n) - _Hc(h, n))


def null_z(fn, *arr, n_perm=200, seed=0):
    rng = np.random.default_rng(seed); obs = fn(*arr)
    tgt = np.asarray(arr[-1], dtype=float).copy(); head = list(arr[:-1])
    d = np.empty(n_perm)
    for i in range(n_perm):
        rng.shuffle(tgt); d[i] = fn(*head, tgt)
    mu, sd = d.mean(), d.std(ddof=1)
    return {"obs": obs, "mu": mu, "z": (obs - mu) / sd if sd > 1e-12 else np.nan,
            "p": (np.sum(d >= obs) + 1) / (n_perm + 1)}


def verdict(z, zc=1.645):
    if not np.isfinite(z): return "不可判定"
    return "冗余（看一块就够）" if z <= -zc else ("协同（必须拼起来）" if z >= zc else "加性（各管一摊）")


if __name__ == "__main__":
    rng = np.random.default_rng(7); n = 3000
    print(f"{'场景':<12}{'观测':>9}{'零均值':>9}{'z(分箱)':>10}  {'判定':<12}{'z(高斯)':>9}")
    print("-" * 70)
    A = rng.normal(size=n); B = rng.normal(size=n); C = rng.normal(size=n)
    C2 = rng.normal(size=n)
    A3 = rng.normal(size=n); B3 = rng.normal(size=n)
    cases = [("独立", A, B, C),
             ("冗余", C2 + .3 * rng.normal(size=n), C2 + .3 * rng.normal(size=n), C2),
             ("协同XOR", A3, B3, np.sign(A3) * np.sign(B3) + .2 * rng.normal(size=n))]
    for nm, a, b, c in cases:
        r = null_z(binned_synergy, a, b, c)
        zg = null_z(lambda p, q, s: gauss_mi(np.hstack([_norm(p), _norm(q)]), s) - gauss_mi(p, s) - gauss_mi(q, s),
                    a, b, c)["z"]
        print(f"{nm:<12}{r['obs']:>9.4f}{r['mu']:>9.4f}{r['z']:>10.2f}  {verdict(r['z']):<12}{zg:>9.2f}")
    Cc = rng.normal(size=n); Ax = Cc + .2 * rng.normal(size=n); Bx = Cc + .2 * rng.normal(size=n)
    print(f"\nI(A;B)={binned_mi(Ax,Bx):.4f}  I(A;B|C)={binned_partial_mi(Ax,Bx,Cc):.4f} nat")
