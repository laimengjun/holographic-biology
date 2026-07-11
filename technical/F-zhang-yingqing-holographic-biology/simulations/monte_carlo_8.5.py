"""8.5 Monte Carlo Simulation - CORRECTED VERSION
Simple independent Bernoulli model for each sensor.
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False

OUT = r'D:\obsidian\Holographic-Biology\technical\F-zhang-yingqing-holographic-biology\simulations'
os.makedirs(OUT, exist_ok=True)
PRIOR = 0.05

def generate_observations(n_patients, sensors, prior=PRIOR, rho=0.0):
    """
    CORRECT model:
    - Patients with disease (prior%): each sensor positive with prob = sensitivity
    - Patients without disease: each sensor positive with prob = 1-specificity (false positive)
    - Correlation: shared latent variable for disease+ patients, shared different for disease- patients
    """
    n = len(sensors)
    has_disease = np.random.random(n_patients) < prior
    obs = np.zeros((n_patients, n), dtype=bool)
    
    for i, (sens, spec) in enumerate(sensors):
        # Generate independent noise
        noise = np.random.random(n_patients)
        
        # For correlated noise, blend with shared noise
        shared_noise = np.random.random(n_patients)
        z = rho * shared_noise + (1 - rho) * noise
        z = np.clip(z, 0, 1)  # keep in [0,1]
        
        # Threshold depends on disease state
        thresh = np.where(has_disease, 1 - sens, spec)
        obs[:, i] = z > thresh
    
    return has_disease, obs

def compute_posterior(obs, sensors, prior=PRIOR):
    """Vectorized Bayes posterior."""
    n = len(sensors)
    prior_odds = prior / (1 - prior)
    lr = np.ones(obs.shape[0])
    for i, (sens, spec) in enumerate(sensors):
        pos_lr = sens / (1 - spec)
        neg_lr = (1 - sens) / spec
        lr *= np.where(obs[:, i], pos_lr, neg_lr)
    po = prior_odds * lr
    return po / (1 + po), lr

def compute_confusion(has_disease, posteriors, decision_thresh=0.5):
    pred = posteriors > decision_thresh
    tp = np.sum(pred & has_disease)
    fp = np.sum(pred & ~has_disease)
    tn = np.sum(~pred & ~has_disease)
    fn = np.sum(~pred & has_disease)
    total = len(has_disease)
    return {
        'accuracy': (tp+tn)/total,
        'precision': tp/(tp+fp) if (tp+fp)>0 else 0,
        'recall': tp/(tp+fn) if (tp+fn)>0 else 0,
        'specificity': tn/(tn+fp) if (tn+fp)>0 else 0,
        'f1': 2*tp/(2*tp+fp+fn) if (2*tp+fp+fn)>0 else 0,
    }

# Standard 5-sensor setup
sensors_5 = [(0.75, 0.85), (0.70, 0.80), (0.72, 0.82), (0.68, 0.78), (0.71, 0.83)]
N = 500000  # 500K patients for robust stats

print("="*60)
print("HOLOGRAPHIC DIAGNOSIS MONTE CARLO SIMULATION")
print(f"Patients: {N:,}, Prior: {PRIOR}, Sensors: 5")
print("="*60)

# === Sim 1: Basic accuracy analysis ===
print("\n--- Sim 1: Accuracy by positive sensor count ---")
hd, obs = generate_observations(N, sensors_5, rho=0.0)
post, lr = compute_posterior(obs, sensors_5)

npos = np.sum(obs, axis=1)
pred = post > 0.5

# Overall accuracy
overall_cm = compute_confusion(hd, post)
print(f"  Overall accuracy:  {overall_cm['accuracy']*100:.1f}%")
print(f"  Precision:         {overall_cm['precision']*100:.1f}%")
print(f"  Recall:            {overall_cm['recall']*100:.1f}%")
print(f"  F1 score:          {overall_cm['f1']*100:.1f}%")

# By positive count
for pos in range(6):
    mask = npos == pos
    c = np.sum(mask)
    if c > 0:
        cm = compute_confusion(hd[mask], post[mask])
        avg_p = np.mean(post[mask])
        print(f"  {pos}/5 positive: n={c:6d}  acc={cm['accuracy']*100:5.1f}%  "
              f"avg_post={avg_p*100:5.1f}%  prec={cm['precision']*100:5.1f}%")

# === Sim 2: Correlation effect ===
print("\n--- Sim 2: Sensor correlation effect ---")
rhos = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
corr_results = []
for rho in rhos:
    hd_r, obs_r = generate_observations(N//2, sensors_5, rho=rho)
    post_r, _ = compute_posterior(obs_r, sensors_5)
    cm = compute_confusion(hd_r, post_r)
    corr_results.append(cm)
    print(f"  rho={rho:.1f}: acc={cm['accuracy']*100:.1f}%  prec={cm['precision']*100:.1f}%  rec={cm['recall']*100:.1f}%  f1={cm['f1']*100:.1f}%")

# === Sim 3: Sensor count effect ===
print("\n--- Sim 3: Sensor count (rho=0.0 vs 0.3) ---")
sensor_pool = [(0.75,0.85),(0.70,0.80),(0.72,0.82),(0.68,0.78),(0.71,0.83),
               (0.73,0.84),(0.69,0.79),(0.74,0.86),(0.66,0.77),(0.70,0.81)]
n_pool = len(sensor_pool)
count_uncorr = []
count_corr = []
for n in range(1, n_pool+1):
    ss = sensor_pool[:n]
    hd_u, ob_u = generate_observations(N//3, ss, rho=0.0)
    hd_c, ob_c = generate_observations(N//3, ss, rho=0.3)
    post_u, _ = compute_posterior(ob_u, ss)
    post_c, _ = compute_posterior(ob_c, ss)
    cm_u = compute_confusion(hd_u, post_u)
    cm_c = compute_confusion(hd_c, post_c)
    count_uncorr.append(cm_u)
    count_corr.append(cm_c)
    print(f"  n={n:2d}: uncorr={cm_u['accuracy']*100:.1f}%  corr(0.3)={cm_c['accuracy']*100:.1f}%")

# === Sim 4: Prior sensitivity ===
print("\n--- Sim 4: Prior sensitivity ---")
priors = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30]
prior_results = []
for p in priors:
    hd_p, ob_p = generate_observations(N//2, sensors_5, prior=p)
    post_p, _ = compute_posterior(ob_p, sensors_5, prior=p)
    cm = compute_confusion(hd_p, post_p)
    prior_results.append(cm)
    print(f"  prior={p:.2f}: acc={cm['accuracy']*100:.1f}%  prec={cm['precision']*100:.1f}%  rec={cm['recall']*100:.1f}%  f1={cm['f1']*100:.1f}%")

# === Sim 5: Sensor quality ===
print("\n--- Sim 5: Sensor quality ---")
quality_sets = {
    'Poor (0.6,0.7)': [(0.60, 0.70)]*5,
    'Standard (0.7,0.8)': [(0.70, 0.80)]*5,
    'Good (0.8,0.9)': [(0.80, 0.90)]*5,
    'Excellent (0.9,0.95)': [(0.90, 0.95)]*5,
}
qual_results = {}
for label, ss in quality_sets.items():
    hd_q, ob_q = generate_observations(N//2, ss)
    post_q, _ = compute_posterior(ob_q, ss)
    cm = compute_confusion(hd_q, post_q)
    qual_results[label] = cm
    print(f"  {label}: acc={cm['accuracy']*100:.1f}%  prec={cm['precision']*100:.1f}%  rec={cm['recall']*100:.1f}%  f1={cm['f1']*100:.1f}%")

# === Sim 6: Decision threshold optimization ===
print("\n--- Sim 6: Threshold optimization ---")
thresholds = np.arange(0.05, 0.96, 0.05)
thresh_results = []
for th in thresholds:
    hd_t, ob_t = generate_observations(N//2, sensors_5)
    post_t, _ = compute_posterior(ob_t, sensors_5)
    cm = compute_confusion(hd_t, post_t, decision_thresh=th)
    thresh_results.append((th, cm))
    if abs(th - 0.5) < 0.01 or abs(th - 0.3) < 0.01 or abs(th - 0.7) < 0.01:
        print(f"  thresh={th:.2f}: acc={cm['accuracy']*100:.1f}%  prec={cm['precision']*100:.1f}%  "
              f"rec={cm['recall']*100:.1f}%  f1={cm['f1']*100:.1f}%")

# === PLOTS ===
print("\n--- Generating plots ---")

# Fig 1: Accuracy by positive count (WITH proper positive count data)
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Count positives per decision threshold
pos_counts = {}
for pos in range(6):
    mask = npos == pos
    c = np.sum(mask)
    if c > 0:
        cm = compute_confusion(hd[mask], post[mask])
        pos_counts[pos] = cm

pos_vals = sorted(pos_counts.keys())
acc_vals = [pos_counts[k]['accuracy']*100 for k in pos_vals]
# Also compute P(disease|n_pos) from simulation
pd_given_npos = []
for pos in pos_vals:
    mask = npos == pos
    if np.sum(mask) > 0:
        pd_given_npos.append(np.mean(hd[mask])*100)
    else:
        pd_given_npos.append(0)

ax1.bar(pos_vals, acc_vals, color='steelblue', alpha=0.8, width=0.6)
ax1.set_xlabel('Positive Sensors (out of 5)')
ax1.set_ylabel('Accuracy (%)')
ax1.set_title('Diagnostic Accuracy vs Positive Count')
ax1.set_ylim(0, 105)
ax1.set_xticks(pos_vals)
for p, v in zip(pos_vals, acc_vals):
    ax1.text(p, v+0.5, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')

ax2.bar(pos_vals, pd_given_npos, color='coral', alpha=0.8, width=0.6)
ax2.set_xlabel('Positive Sensors (out of 5)')
ax2.set_ylabel('Actual Disease Prevalence (%)')
ax2.set_title('P(Disease | n Positive Sensors) [Empirical]')
ax2.set_ylim(0, 105)
ax2.set_xticks(pos_vals)
ax2.axhline(y=50, color='red', ls='--', alpha=0.5, label='80% threshold')
for p, v in zip(pos_vals, pd_given_npos):
    ax2.text(p, v+0.5, f'{v:.1f}%', ha='center', fontsize=9)
fig1.tight_layout()
fig1.savefig(os.path.join(OUT, 'fig1_accuracy_vs_positive_count.png'), dpi=150)
plt.close(fig1)
print("  fig1: accuracy_vs_positive_count.png")

# Fig 2: Correlation effect
fig2, ax = plt.subplots(figsize=(8, 5))
ax.plot(rhos, [r['f1']*100 for r in corr_results], 'o-', color='darkred', lw=2, markersize=8, label='F1 Score')
ax.plot(rhos, [r['accuracy']*100 for r in corr_results], 's--', color='steelblue', lw=2, markersize=8, label='Accuracy')
ax.set_xlabel('Average Sensor Correlation (rho)')
ax.set_ylabel('Performance (%)')
ax.set_title('Effect of Sensor Correlation on Diagnostic Performance')
ax.set_xlim(-0.03, 0.93)
ax.set_ylim(0, 105)
ax.grid(True, alpha=0.3)
ax.legend()
fig2.tight_layout()
fig2.savefig(os.path.join(OUT, 'fig2_correlation_effect.png'), dpi=150)
plt.close(fig2)
print("  fig2: correlation_effect.png")

# Fig 3: Sensor count
fig3, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(1, n_pool+1), [c['accuracy']*100 for c in count_uncorr], 'o-', color='steelblue', lw=2, label='Independent (rho=0)')
ax.plot(range(1, n_pool+1), [c['accuracy']*100 for c in count_corr], 's--', color='darkorange', lw=2, label='Correlated (rho=0.3)')
ax.set_xlabel('Number of Sensors')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Diagnostic Accuracy vs Number of Sensors')
ax.set_xticks(range(1, n_pool+1))
ax.set_ylim(50, 100)
ax.grid(True, alpha=0.3)
ax.legend()
ax.axvspan(5.5, 10.5, alpha=0.08, color='green')
ax.text(8, 52, 'Diminishing\nReturns', ha='center', fontsize=9, color='green', style='italic')
fig3.tight_layout()
fig3.savefig(os.path.join(OUT, 'fig3_sensor_count_vs_accuracy.png'), dpi=150)
plt.close(fig3)
print("  fig3: sensor_count_vs_accuracy.png")

# Fig 4: Prior sensitivity
fig4, ax = plt.subplots(figsize=(8, 5))
p_vals = [p for p in priors]
ax.plot(p_vals, [r['accuracy']*100 for r in prior_results], 'o-', color='navy', lw=2, label='Accuracy')
ax.plot(p_vals, [r['precision']*100 for r in prior_results], 's--', color='green', lw=2, label='Precision')
ax.plot(p_vals, [r['recall']*100 for r in prior_results], '^-.', color='red', lw=2, label='Recall')
ax.plot(p_vals, [r['f1']*100 for r in prior_results], 'd:', color='purple', lw=2, label='F1 Score')
ax.set_xlabel('Prior Probability (Disease Prevalence)')
ax.set_ylabel('Performance (%)')
ax.set_title('Prior Sensitivity Analysis (5-sensor fusion)')
ax.set_xlim(-0.01, 0.31)
ax.set_ylim(0, 105)
ax.grid(True, alpha=0.3)
ax.legend()
fig4.tight_layout()
fig4.savefig(os.path.join(OUT, 'fig4_prior_sensitivity.png'), dpi=150)
plt.close(fig4)
print("  fig4: prior_sensitivity.png")

# Fig 5: Sensor quality comparison
fig5, ax = plt.subplots(figsize=(10, 5.5))
qlabels = list(qual_results.keys())
x = np.arange(len(qlabels))
w = 0.2
ax.bar(x-w, [qual_results[l]['accuracy']*100 for l in qlabels], w, label='Accuracy', color='steelblue', alpha=0.85)
ax.bar(x, [qual_results[l]['precision']*100 for l in qlabels], w, label='Precision', color='green', alpha=0.85)
ax.bar(x+w, [qual_results[l]['recall']*100 for l in qlabels], w, label='Recall', color='coral', alpha=0.85)
ax.set_ylabel('Performance (%)')
ax.set_title('Sensor Quality Comparison (5-sensor fusion)')
ax.set_xticks(x)
ax.set_xticklabels(qlabels, fontsize=10)
ax.legend()
ax.set_ylim(0, 105)
fig5.tight_layout()
fig5.savefig(os.path.join(OUT, 'fig5_sensor_quality_comparison.png'), dpi=150)
plt.close(fig5)
print("  fig5: sensor_quality_comparison.png")

print("\n=== ALL SIMULATIONS COMPLETE ===")
