# %%
import numpy as np
import matplotlib.pyplot as plt

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


