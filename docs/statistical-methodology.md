# Statistical Methodology & Mathematical Foundations

This document provides the formal mathematical and methodological framework applied in:
**"Understanding the Relationship Between Pokémon Type and its Battle Role Using Official Performance Statistics: Pokémon Database, 2008–2025"** (CSD105 Data Science, Ahmedabad University).

---

## 1. Central Tendency & Dispersion Metrics

For each statistical feature $X \in \{\text{Total}, \text{HP}, \text{Attack}, \text{Defense}, \text{Sp. Atk}, \text{Sp. Def}, \text{Speed}\}$, we compute:

- **Sample Mean**:
  $$\bar{X} = \frac{1}{N} \sum_{i=1}^{N} X_i$$
- **Sample Standard Deviation**:
  $$s = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (X_i - \bar{X})^2}$$
- **Median ($Q_2$)**: The 50th percentile of the sorted distribution.
- **Interquartile Range (IQR)**:
  $$\text{IQR} = Q_3 - Q_1$$

Across $N = 1,219$ Pokémon, the Base Stat Total (BST) yields $\bar{X} = 443.68$ and $Q_2 = 465.0$. The negative skew ($\bar{X} < Q_2$) reflects the substantial base of early-stage evolutionary forms offset by high-BST Legendary forms.

---

## 2. Bivariate Correlation Analysis

To quantify linear and monotonic relationships between attribute pairs, both Pearson and Spearman correlation coefficients are evaluated.

### 2.1 Pearson Product-Moment Correlation ($r$)
Measures the strength and direction of linear association between two continuous variables $X$ and $Y$:

$$r_{XY} = \frac{\sum_{i=1}^{N} (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^{N} (X_i - \bar{X})^2} \sqrt{\sum_{i=1}^{N} (Y_i - \bar{Y})^2}}$$

### 2.2 Spearman Rank-Order Correlation ($\rho$)
Measures monotonic association by computing Pearson correlation over ranked transformations $R(X)$ and $R(Y)$:

$$\rho = 1 - \frac{6 \sum_{i=1}^{N} d_i^2}{N(N^2 - 1)}$$

where $d_i = R(X_i) - R(Y_i)$.

### Key Empirical Findings
1. **HP vs Total**: $r = 0.6596$, $\rho = 0.7316$ ($p < 10^{-150}$). Proves Hit Points represent the primary volumetric base of total battle viability.
2. **Special Attack vs Special Defence**: $r = 0.5167$, $\rho = 0.5736$ ($p < 10^{-85}$). Confirms deliberate developer symmetry in special energy combat.
3. **Attack vs Defense**: $r = 0.4695$, $\rho = 0.5278$ ($p < 10^{-67}$).
4. **Defense vs Speed**: $r = 0.0210$ ($p = 0.463$, not significant). Reveals independent orthogonal role trade-offs (heavy tanks vs agile sweepers).

---

## 3. Independent Two-Sample T-Tests

To test whether the human-defined 'Legendary' classification represents an objectively superior physical tier rather than a nominal title, independent two-sample t-tests are conducted:

- **Group 1 ($S$)**: Strong Pokémon ($451 \le \text{BST} \le 600$, $N_S = 479$)
- **Group 2 ($L$)**: Legendary Pokémon ($601 \le \text{BST} \le 1200$, $N_L = 114$)

### Hypotheses
$$H_0: \mu_{S, \text{stat}} = \mu_{L, \text{stat}}$$
$$H_1: \mu_{S, \text{stat}} < \mu_{L, \text{stat}}$$

### Test Statistic
$$t = \frac{\bar{X}_S - \bar{X}_L}{\sqrt{\frac{s_S^2}{N_S} + \frac{s_L^2}{N_L}}}$$

### Effect Size (Cohen's $d$)
$$d = \frac{\bar{X}_L - \bar{X}_S}{s_{\text{pooled}}}, \quad s_{\text{pooled}} = \sqrt{\frac{(N_S - 1)s_S^2 + (N_L - 1)s_L^2}{N_S + N_L - 2}}$$

Across all six base stats, $p < 10^{-7}$, definitively rejecting $H_0$ and proving that Legendary Pokémon constitute an elite, statistically separate power echelon.

---

## 4. One-Way Analysis of Variance (ANOVA)

To test whether the four-tier power classification system ('Weak', 'Average', 'Strong', 'Legendary') reflects distinct population means, One-Way ANOVA is performed across $k = 4$ groups.

### Partitioning Sum of Squares
$$\text{SS}_{\text{Total}} = \text{SS}_{\text{Between}} + \text{SS}_{\text{Within}}$$

$$\text{SS}_{\text{Between}} = \sum_{j=1}^{k} N_j (\bar{X}_j - \bar{X})^2$$

$$\text{SS}_{\text{Within}} = \sum_{j=1}^{k} \sum_{i=1}^{N_j} (X_{ij} - \bar{X}_j)^2$$

### F-Statistic
$$F = \frac{\text{MS}_{\text{Between}}}{\text{MS}_{\text{Within}}} = \frac{\text{SS}_{\text{Between}} / (k - 1)}{\text{SS}_{\text{Within}} / (N - k)}$$

### Results
- **Total Stats**: $F = 2551.92$, $p = 0.000e+00$.
  - Weak Mean: $261.50$
  - Average Mean: $370.14$
  - Strong Mean: $518.53$
  - Legendary Mean: $683.82$
- **Individual Stats**:
  - HP: $F = 235.57, p = 1.84 \times 10^{-120}$
  - Attack: $F = 373.57, p = 7.12 \times 10^{-172}$
  - Defense: $F = 219.94, p = 5.95 \times 10^{-114}$
  - Sp. Atk: $F = 338.02, p = 1.48 \times 10^{-159}$
  - Sp. Def: $F = 338.71, p = 8.40 \times 10^{-160}$
  - Speed: $F = 143.69, p = 1.10 \times 10^{-79}$

All $p$-values are indistinguishable from zero, establishing that each tier is an empirical reality.

---

## 5. Unsupervised K-Means Clustering

To discover latent battle archetypes without relying on pre-existing labels:
1. The 6-dimensional stat matrix $\mathbf{X} \in \mathbb{R}^{1219 \times 6}$ is standardized via z-score normalization:
   $$z_{ij} = \frac{x_{ij} - \bar{x}_j}{s_j}$$
2. K-Means clustering partitions the 1,219 observations into $K = 4$ clusters by minimizing within-cluster sum of squares (WCSS):
   $$\arg\min_{\mathbf{S}} \sum_{k=1}^{K} \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$$
3. Centroid evaluation resolves into:
   - **Cluster 0**: Low-Stat Tier (Unevolved Pokémon)
   - **Cluster 1**: Balanced / Tanks (High HP & All-Around Strength)
   - **Cluster 2**: Walls / Defensive Specialists (High Defense & Sp. Def, Low Speed)
   - **Cluster 3**: Sweepers / Apex Attackers (High Speed & Offensive Output)
