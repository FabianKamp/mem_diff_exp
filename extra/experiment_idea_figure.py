"""
Script to create an exemplary figure of the underlying idea of the memory experiment.
"""

#%%
import matplotlib.pyplot as plt
import numpy as np
colors_palette = ["#F2857D","#7EBDC3","#A9A9A9"]
# Define the points
points = {
    'origin': (0, 0),
    'point1': (0.12, 0.6),
    'point2': (0.5, 0.1),
    'point3': (0.7, 0.8)
}

# Create figure
fig, ax = plt.subplots(figsize=(6, 6))

# Add subtle dot grid in background
# grid_x, grid_y = np.meshgrid(np.arange(0, 1.1, 0.1), np.arange(0, 1.1, 0.1))
# ax.scatter(grid_x, grid_y, s=60, c='k', marker='+', alpha=0.3, zorder=1, linewidths=.3)

# Draw lines from origin to each other point
for key in ['point1', 'point2', 'point3']:
    ax.plot([points['origin'][0], points[key][0]],
            [points['origin'][1], points[key][1]],
            c='black', linewidth=0.5, zorder=2, linestyle=(0, (5, 10)),)

# Connect point1-point3 and point2-point3
ax.plot([points['point1'][0], points['point3'][0]],
        [points['point1'][1], points['point3'][1]],
        c='black', linewidth=0.5, zorder=2)
ax.plot([points['point2'][0], points['point3'][0]],
        [points['point2'][1], points['point3'][1]],
        c='black', linewidth=0.5, zorder=2)

# Plot the origin point (larger, white filled)
ax.scatter(points['origin'][0], points['origin'][1],
           s=200, facecolors='white', edgecolors='black', linewidths=2, zorder=3)

# Plot the other three points (filled) with colors from palette
markers = ['D', 'D', 'o']  # diamond for point1 & point2, circle for point3
for i, key in enumerate(['point1', 'point2', 'point3']):
    ax.scatter(points[key][0], points[key][1],
               s=100, c=colors_palette[i], marker=markers[i],
               edgecolors='black', linewidths=.5, zorder=3)

# Set axis limits to show full circle at origin
ax.set_xlim(-0.1, 1.0)
ax.set_ylim(-0.1, 1.0)

# Set equal aspect ratio
ax.set_aspect('equal')

# Clean up the plot - seaborn style with offset spines that start at 0
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_position(('outward', 5))
ax.spines['bottom'].set_position(('outward', 5))
ax.spines['left'].set_bounds(0, 1.0)
ax.spines['bottom'].set_bounds(0, 1.0)

plt.tight_layout()
fig.savefig('../figures/explanatory/experiment_idea_2d.svg', bbox_inches='tight')
plt.show()

# %%
# Second plot - 1D representation
# Define the 1D points
points_1d = {
    'origin': 0,
    'diamond': 0.3,
    'circle': 0.8
}

fig2, ax2 = plt.subplots(figsize=(6, 2))

# Draw line from origin to diamond (dashed)
ax2.plot([points_1d['origin'], points_1d['diamond']], [0, 0], c='black', linewidth=0.5, linestyle=(0, (5, 10)), zorder=2)

# Draw line from diamond to circle (solid)
ax2.plot([points_1d['diamond'], points_1d['circle']], [0, 0], c='black', linewidth=0.5, zorder=2)

# Plot the origin point (white filled)
ax2.scatter(points_1d['origin'], 0, s=200, facecolors='white', edgecolors='black', linewidths=2, zorder=3)

# Plot diamond
ax2.scatter(points_1d['diamond'], 0, s=100, c='darkgray', marker='D', edgecolors='black', linewidths=.5, zorder=3)

# Plot circle
ax2.scatter(points_1d['circle'], 0, s=100, c='darkgray', marker='o', edgecolors='black', linewidths=.5, zorder=3)

# Set axis limits
ax2.set_xlim(-0.1, 1.0)
ax2.set_ylim(-0.5, 1.0)

# Clean up the plot - only x spine
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.spines['bottom'].set_position(('outward', 5))
ax2.spines['bottom'].set_bounds(0, 1.0)

# Hide y-axis ticks and labels
ax2.set_yticks([])
fig2.savefig('../figures/explanatory/experiment_idea_1d.svg', bbox_inches='tight')
plt.show()

# %%
