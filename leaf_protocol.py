"""leaf_protocol.py — 在真实叶片数据上跑第 9 条（映射表）与第 12 条（协同）
2026-10-24　配套 research/10.6-real-leaf-test.md

数据：Swedish Leaf Dataset（15 种 / 1125 张剪影）
  https://www.cvl.isy.liu.se/en/research/datasets/swedish-leaf/   （leaf1.zip … leaf15.zip）

用法：
  1) python leaf_protocol.py features <图像目录> <输出 csv>   # 提特征
  2) python leaf_protocol.py matrix  <features csv>          # 偏互信息表 + 行内占比
  3) python leaf_protocol.py synergy <features csv>          # 协同量 + 置换 z
  4) python leaf_protocol.py synth                           # 造已知加性的对照数据
"""
import sys, csv, math, glob, os
import numpy as np

COLS = ["AR", "C", "Sol", "tipA", "baseA",
        "base_half", "base_rough", "base_pf",
        "mid_half", "mid_rough", "mid_pf",
        "tip_half", "tip_rough", "tip_pf"]
TH = ["AR", "C", "Sol", "tipA", "baseA"]


# ---------------------------------------------------------------- 特征
def features_from_contour(pts):
    import cv2
    pts = np.asarray(pts, float) - np.mean(pts, 0)
    ev, evec = np.linalg.eigh(np.cov(pts.T))
    v = evec[:, np.argmax(ev)]
    th = math.atan2(v[1], v[0])
    R = np.array([[math.cos(-th), -math.sin(-th)], [math.sin(-th), math.cos(-th)]])
    Y = pts @ R.T
    x, y = Y[:, 0], Y[:, 1]
    A = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    P = np.sum(np.linalg.norm(np.diff(np.vstack([Y, Y[:1]]), axis=0), axis=1))
    Hs = abs(cv2.contourArea(cv2.convexHull(Y.astype(np.float32))))
    Yn = Y / math.sqrt(max(A, 1e-9))
    AR = (Yn[:, 0].max() - Yn[:, 0].min()) / max(1e-9, Yn[:, 1].max() - Yn[:, 1].min())
    C = P * P / (4 * math.pi * A)
    Sol = A / max(Hs, 1e-9)
    if abs(Yn[Yn[:, 0].argmin(), 1]) > abs(Yn[Yn[:, 0].argmax(), 1]):
        Yn[:, 0] = -Yn[:, 0]
    Ys = Yn[np.argsort(np.arctan2(Yn[:, 1], Yn[:, 0]))]

    def apex(sign):
        i = np.argmax(sign * Ys[:, 0])
        p0, p1, p2 = Ys[i], Ys[(i + 12) % len(Ys)], Ys[(i - 12) % len(Ys)]
        a1, a2 = p1 - p0, p2 - p0
        cv = np.dot(a1, a2) / (np.linalg.norm(a1) * np.linalg.norm(a2) + 1e-12)
        return math.degrees(math.acos(max(-1, min(1, cv))))

    out = [AR, C, Sol, apex(1), apex(-1)]
    x0, x1 = Yn[:, 0].min(), Yn[:, 0].max()
    for a, b in [(x0, x0 + (x1 - x0) / 3),
                 (x0 + (x1 - x0) / 3, x0 + 2 * (x1 - x0) / 3),
                 (x0 + 2 * (x1 - x0) / 3, x1)]:
        sel = (Yn[:, 0] >= a) & (Yn[:, 0] <= b)
        sub = Yn[sel]
        if len(sub) < 10:
            return None
        out += [np.abs(sub[:, 1]).mean() / max(1e-9, x1 - x0), np.std(np.abs(sub[:, 1])), sel.mean()]
    return out


def features_from_image(path):
    import cv2
    img = cv2.imread(path, 0)
    if img is None:
        return None
    s = 800.0 / max(img.shape)
    if s < 1:
        img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    m = (img < 160).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    m = (lab == k).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    return features_from_contour(c[:, 0, :]) if len(c) >= 50 else None


# ---------------------------------------------------------------- 估计器
def _erf(x):
    s = np.sign(x); x = np.abs(x); t = 1 / (1 + 0.3275911 * x)
    return s * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                      - 0.284496736) * t + 0.254829592) * t * np.exp(-x * x))


def _erfinv(y):
    y = np.clip(y, -0.999999, 0.999999); a = 0.147
    ln1 = np.log(1 - y * y); t = 2 / (np.pi * a) + ln1 / 2
    x = np.sign(y) * np.sqrt(np.sqrt(t * t - ln1 / a) - t)
    for _ in range(2):
        x = x - (_erf(x) - y) / (2 / np.sqrt(np.pi) * np.exp(-x * x))
    return x


def _norm(x):
    x = np.asarray(x, float)
    if x.ndim == 1:
        x = x[:, None]
    out = np.empty_like(x); n = x.shape[0]
    for j in range(x.shape[1]):
        o = np.argsort(x[:, j], kind="mergesort"); r = np.empty(n); r[o] = np.arange(1, n + 1)
        out[:, j] = np.sqrt(2) * _erfinv(2 * ((r - .5) / n) - 1)
    return out


def _H(z):
    d = z.shape[1]; c = np.cov(z, rowvar=False)
    c = np.array([[float(c)]]) if d == 1 else c
    s, ld = np.linalg.slogdet(c)
    return .5 * (d * np.log(2 * np.pi * np.e) + ld)


def gauss_mi(x, y):
    zx, zy = _norm(x), _norm(y)
    return max(0., _H(zx) + _H(zy) - _H(np.hstack([zx, zy])))


def _Hc(c, n):
    p = c[c > 0] / n
    return float(-(p * np.log(p)).sum())


def _bn(a, nb):
    return np.searchsorted(np.quantile(a, np.linspace(0, 1, nb + 1)[1:-1]), a, side="right")


def binned_synergy(a, b, c, nb=4):
    ba, bb, bc = _bn(a, nb), _bn(b, nb), _bn(c, nb)
    n = len(ba); h = np.zeros((nb, nb, nb)); np.add.at(h, (ba, bb, bc), 1)
    Hab, Hcc = _Hc(h.sum(2), n), _Hc(h.sum((0, 1)), n)
    Habc, Ha = _Hc(h, n), _Hc(h.sum((1, 2)), n)
    Hac, Hb = _Hc(h.sum(1), n), _Hc(h.sum((0, 2)), n)
    Hbc = _Hc(h.sum(0), n)
    return float((Hab + Hcc - Habc) - (Ha + Hcc - Hac) - (Hb + Hcc - Hbc))


def partial_mi_table(M):
    th = M[:, :5]
    regs = {"base": M[:, 5:8], "mid": M[:, 8:11], "tip": M[:, 11:14]}
    T = np.zeros((3, 5))
    for i, (_, u) in enumerate(regs.items()):
        for j in range(5):
            Z = np.delete(th, j, axis=1)
            T[i, j] = max(0., gauss_mi(u, np.hstack([_norm(th[:, [j]]), _norm(Z)])) - gauss_mi(u, Z))
    return T, list(regs)


# ---------------------------------------------------------------- 三件事
def cmd_features(src_dir, out_csv):
    files = sorted(sum([glob.glob(os.path.join(src_dir, "**", e), recursive=True)
                        for e in ("*.tif", "*.png", "*.jpg", "*.bmp")], []))
    rows = []
    for i, f in enumerate(files):
        r = features_from_image(f)
        if r:
            rows.append([os.path.basename(os.path.dirname(f)), os.path.basename(f)] + [round(v, 6) for v in r])
        if i % 200 == 0:
            print(i, len(rows), flush=True)
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["species", "file"] + COLS); w.writerows(rows)
    print("saved", out_csv, len(rows))


def load(path):
    with open(path) as fh:
        first = next(csv.reader(fh))
    if first[:2] == ["species", "file"]:
        return np.array([[float(r[c]) for c in COLS] for r in csv.DictReader(open(path))])
    rows = [r for r in csv.reader(open(path)) if r]
    return np.array([[float(v) for v in r[-len(COLS):]] for r in rows if len(r) >= len(COLS)])


def cmd_matrix(path):
    T, names = partial_mi_table(load(path))
    print("单元".ljust(6) + "".join(f"{t:>8}" for t in TH) + "   行内占比")
    for i, rn in enumerate(names):
        share = "".join(f"{T[i, j] / max(T[i].max(), 1e-9):>7.0%}" for j in range(5))
        print(f"{rn:<6}" + "".join(f"{T[i, j]:>8.3f}" for j in range(5)) + "  " + share)
    share = T / np.maximum(T.max(axis=1, keepdims=True), 1e-9)
    print("行内占比达一半的格数：", (share >= .5).sum(axis=1))


def cmd_synergy(path, seed=5):
    M = load(path); th = M[:, :5]
    regs = {"base": M[:, 5:8], "mid": M[:, 8:11], "tip": M[:, 11:14]}
    rng = np.random.default_rng(seed); zs = []
    for k, tn in enumerate(TH):
        for a, b in [("tip", "base"), ("tip", "mid"), ("mid", "base")]:
            y = th[:, k].copy(); obs = binned_synergy(regs[a][:, 0], regs[b][:, 0], y)
            d = np.empty(120)
            for i in range(120):
                rng.shuffle(y); d[i] = binned_synergy(regs[a][:, 0], regs[b][:, 0], y)
            z = (obs - d.mean()) / d.std(ddof=1); zs.append(z)
            print(f"{a}+{b}->{tn:<6} Δ={obs:+.4f} z={z:+.2f}")
    zs = np.array(zs)
    print(f"正显著比例 {100*np.mean(zs>1.645):.0f}%　均值 {zs.mean():+.1f}")


def cmd_synth(n=800, seed=11):
    """超椭圆生成，四个参数独立 → 已知加性，用作校准对照。"""
    rng = np.random.default_rng(seed); rows = []
    for _ in range(n):
        AR = 1 + rng.random() * 3; expo = 1.5 + rng.random() * 1.5
        tipw = rng.random() * 1.2; serr = .02 * rng.random()
        t = np.linspace(0, 2 * np.pi, 900, endpoint=False)
        c, s = np.cos(t), np.sin(t)
        x = np.sign(c) * np.abs(c) ** (2 / expo) * AR
        y = np.sign(s) * np.abs(s) ** (2 / expo)
        y = y / (1 + tipw * np.clip(x / x.max(), 0, None) ** 2) * (1 + serr * np.sin(14 * t))
        r = features_from_contour(np.stack([x, y], 1))
        if r:
            rows.append([round(v, 6) for v in r])
    with open("synth_features.csv", "w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    print("saved synth_features.csv", len(rows))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "features":
        cmd_features(sys.argv[2], sys.argv[3])
    elif cmd == "matrix":
        cmd_matrix(sys.argv[2])
    elif cmd == "synergy":
        cmd_synergy(sys.argv[2])
    elif cmd == "synth":
        cmd_synth()
