# %%
import numpy as np
import matplotlib.pyplot as plt

# %%
def project_point_on_line(p, theta_deg):
    """Projects a 2D point p onto a line through the origin at theta_deg."""
    rad = np.radians(theta_deg)
    v = np.array([np.cos(rad), np.sin(rad)])  # Unit vector
    proj = np.dot(p, v) * v                   # (p · v) * v
    return proj

def plot_scheme(p1, p2, thetas, ax, colors=None):
    """Plot projection scheme for two points onto multiple lines.

    Args:
        p1, p2: 2D points as numpy arrays
        thetas: list of angles in degrees
        ax: matplotlib axes
        colors: optional list of colors (defaults to tab10 colormap)
    """
    if colors is None:
        cmap = plt.cm.get_cmap('tab10')
        colors = [cmap(i) for i in range(len(thetas))]

    line_len = 2.0

    # Scatter original points
    ax.scatter(p2[0], p2[1], color='#EF5350', s=90, label='Point 1 (semantic)', zorder=5)
    ax.scatter(p1[0], p1[1], color='#26C6DA', s=90, label='Point 2 (visual)', zorder=5)

    for i, theta in enumerate(thetas):
        color = colors[i]
        rad = np.radians(theta)

        # Compute projections
        p1_proj = project_point_on_line(p1, theta)
        p2_proj = project_point_on_line(p2, theta)

        # Draw infinite line through origin
        ax.plot([-line_len*np.cos(rad), line_len*np.cos(rad)],
                [-line_len*np.sin(rad), line_len*np.sin(rad)],
                color=color, linestyle='--', label=f'Line {i+1} (θ = {theta}°)')

        # Scatter projected points
        ax.scatter([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]],
                   color=color, s=70, label=f'Projections on Line {i+1}', zorder=5)

        # Draw dotted perpendicular drop lines
        ax.plot([p1[0], p1_proj[0]], [p1[1], p1_proj[1]], color=color, linestyle=':', alpha=0.6)
        ax.plot([p2[0], p2_proj[0]], [p2[1], p2_proj[1]], color=color, linestyle=':', alpha=0.6)

        # Line between projections
        ax.plot([p1_proj[0], p2_proj[0]], [p1_proj[1], p2_proj[1]],
                linewidth=4, color=color, solid_capstyle="round")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

# %% 
# plot 1
# 1. Define Points and Angles

p1 = np.array([0.3, 0.3])
p2 = np.array([0.6, 0.5])

p3 = np.array([0.1, 0.9])
p4 = np.array([0.9, 0.1])

# colors
color_dict = {
    "semantic": "#EF5350",
    "visual": "#26C6DA",
    "45deg": "#BDBDBD",
}

from matplotlib.backends.backend_pdf import PdfPages

with PdfPages('./figures/explanatory/decision_axis.pdf') as pdf:
    fig, ax = plt.subplots(figsize=(6,6))
    plot_scheme(p3, p4, [30.0, 45.0], ax, colors=[color_dict["semantic"], color_dict["45deg"]])
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6,6))
    plot_scheme(p3, p4, [60.0, 45.0], ax, colors=[color_dict["visual"], color_dict["45deg"]])
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# %%
# Percent correct to d-prime simulation
from scipy.stats import norm

# Percent correct range (must be > 0.5 for 2AFC, and < 1.0)
pc = np.linspace(0.51, 0.90, 100)

# Calculate d-prime: d' = √2 × z(Pc)
dprime = np.sqrt(2) * norm.ppf(pc)

# Calculate slope: d(d')/d(Pc) = √2 / φ(Φ⁻¹(Pc))
slope = np.sqrt(2) / norm.pdf(norm.ppf(pc))

fig, ax1 = plt.subplots(figsize=(6, 5))

# Plot d-prime on left y-axis
ax1.plot(pc * 100, dprime, linewidth=2, color='#1976D2', label="d'")
ax1.set_xlabel('Percent Correct (%)')
ax1.set_ylabel("d' (d-prime)", color='#1976D2')
ax1.tick_params(axis='y', labelcolor='#1976D2')
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax1.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
ax1.set_xlim(50, 90)

# Plot slope on right y-axis
ax2 = ax1.twinx()
ax2.plot(pc * 100, slope, linewidth=2, color='#E53935', label="slope")
ax2.set_ylabel("d(d')/d(Pc)", color='#E53935')
ax2.tick_params(axis='y', labelcolor='#E53935')

ax1.set_title("d' = √2 × Φ⁻¹(Pc) and its slope")
ax1.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %%

