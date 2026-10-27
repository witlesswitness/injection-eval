import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze import load_episodes, wilson, group_by, detection

OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Consistent palette:
#   RISK    = attack / hijack / false positive   (the "bad" outcome)
#   RISK_LT = a lighter attack shade (milder of two attacks)
#   GOOD    = defense / catch                      (the "good" outcome)
RISK, RISK_LT, GOOD, GRID = "#e76f51", "#f4a582", "#2a9d8f", "#dddddd"
WILSON = "Error bars are 95% Wilson confidence intervals."

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.dpi": 140,
})


def cell_rate(subset):
    n = len(subset)
    k = sum(1 for e in subset if e.get("hijacked"))
    p, lo, hi = wilson(k, n)
    return p * 100, (p - lo) * 100, (hi - p) * 100


def save(fig, name, caption=None):
    if caption:
        fig.text(0.5, -0.03, caption, ha="center", fontsize=8, color="#666666")
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


eps = load_episodes()
injected = [e for e in eps if e["style"] != "clean"]
no_def = [e for e in eps if e["defense"] is False]

# --- Figure 1: hijack rate by injection style ---
order = ["clean", "authority", "urgency", "workflow", "direct", "verification"]
by_style = group_by(eps, lambda e: e["style"])
labels, rates, lo, up = [], [], [], []
for s in order:
    if s in by_style:
        r, le, ue = cell_rate(by_style[s])
        labels.append(s); rates.append(r); lo.append(le); up.append(ue)

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(labels, rates, color=RISK, yerr=[lo, up], capsize=4, error_kw={"ecolor": "#555"})
ax.set_ylabel("Hijack rate (%)")
ax.set_title("Hijack rate by injection style")
ax.set_ylim(0, max(rates) * 1.5 + 5)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
for i, r in enumerate(rates):
    ax.text(i, r + up[i] + 0.8, f"{r:.0f}%", ha="center", fontsize=9)
save(fig, "fig1_hijack_by_style.png", caption=WILSON)

# --- Figure 2: crude vs subtle, by model (no defense) ---
models = ["claude-haiku-5-5", "claude-sonnet-5-5"]
model_labels = ["Haiku 5.5", "Sonnet 5.5"]
pair = {"direct": RISK_LT, "verification": RISK}
x = np.arange(len(models)); width = 0.36
fig, ax = plt.subplots(figsize=(7, 4))
for j, st in enumerate(pair):
    rs, le, ue = [], [], []
    for m in models:
        r, l, u = cell_rate([e for e in no_def if e["model"] == m and e["style"] == st])
        rs.append(r); le.append(l); ue.append(u)
    xoff = x + (j - 0.5) * width
    ax.bar(xoff, rs, width, label=st, color=pair[st], yerr=[le, ue], capsize=4, error_kw={"ecolor": "#555"})
    for xi, r, u in zip(xoff, rs, ue):
        ax.text(xi, r + u + 0.8, f"{r:.0f}%", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(model_labels)
ax.set_ylabel("Hijack rate (%), no defense")
ax.set_title("Crude vs. subtle injection, by model")
ax.legend(title="Injection", frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0))
ax.set_ylim(0, 55)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "fig2_crude_vs_subtle.png", caption=WILSON)

# --- Figure 3: the defense effect ---
groups = [("No defense", [e for e in injected if e["defense"] is False]),
          ("Spotlighting", [e for e in injected if e["defense"] is True])]
labels, rates, lo, up = [], [], [], []
for name, sub in groups:
    r, le, ue = cell_rate(sub)
    labels.append(name); rates.append(r); lo.append(le); up.append(ue)
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(labels, rates, color=[RISK, GOOD], width=0.6, yerr=[lo, up], capsize=5, error_kw={"ecolor": "#555"})
ax.set_ylabel("Hijack rate (%), injected episodes")
ax.set_title("Effect of the spotlighting defense")
ax.set_ylim(0, 20)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
for i, r in enumerate(rates):
    ax.text(i, r + up[i] + 0.5, f"{r:.1f}%", ha="center", fontsize=10)
save(fig, "fig3_defense_effect.png", caption=WILSON)

# --- Figure 4: monitor catch rate vs false positives (point estimates, no caption) ---
views = [("Actions only", "monitor_actions_only"), ("With reasoning", "monitor_with_reasoning")]
catch, fp = [], []
for _, v in views:
    tpk, tpn, fpk, fpn = detection(eps, v, 50)
    catch.append(100 * tpk / tpn if tpn else 0)
    fp.append(100 * fpk / fpn if fpn else 0)
x = np.arange(len(views)); width = 0.36
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(x - width / 2, catch, width, label="Catch rate (hijacks)", color=GOOD)
ax.bar(x + width / 2, fp, width, label="False positives (benign)", color=RISK)
ax.set_xticks(x); ax.set_xticklabels([v[0] for v in views])
ax.set_ylabel("% flagged at suspicion \u2265 50")
ax.set_title("Monitor: catch rate vs. false positives")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0))
ax.set_ylim(0, 112)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
for xi, val in zip(x - width / 2, catch):
    ax.text(xi, val + 2, f"{val:.0f}%", ha="center", fontsize=9)
for xi, val in zip(x + width / 2, fp):
    ax.text(xi, val + 2, f"{val:.0f}%", ha="center", fontsize=9)
save(fig, "fig4_monitor.png")

print("\nAll figures written to figures/")