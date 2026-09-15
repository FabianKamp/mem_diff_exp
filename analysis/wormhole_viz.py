# %%
import numpy as np
import matplotlib.pyplot as plt

# %%
# U-shaped bent plane
u = np.linspace(0, np.pi, 80)
v = np.linspace(-2, 2, 40)

U, V = np.meshgrid(u, v)

# U extends far in X, flat in Z
x_scale = 10.0  # Wide in X
z_scale = 0.2   # Flat in Z

X = x_scale * np.sin(U) + 1.0  # Shift right along X
Y = V
Z_shift = .5
Z = z_scale * np.cos(U) + Z_shift  # Shift up along Z

# Plot - minimal style for print
fig = plt.figure(figsize=(10, 8), facecolor='white')
ax = fig.add_subplot(111, projection='3d', facecolor='white')

# Transparent surface, no mesh lines
ax.plot_surface(X, Y, Z, color='lightgray', edgecolor='none', alpha=0.3)

# Plot outline of the plane
ax.plot(X[0, :], Y[0, :], Z[0, :], 'k-', linewidth=1.5)   # Bottom edge
ax.plot(X[-1, :], Y[-1, :], Z[-1, :], 'k-', linewidth=1.5) # Top edge
ax.plot(X[:, 0], Y[:, 0], Z[:, 0], 'k-', linewidth=1.5)   # Left edge
ax.plot(X[:, -1], Y[:, -1], Z[:, -1], 'k-', linewidth=1.5) # Right edge

# Hide default axes
ax.set_axis_off()

# Draw custom axes from origin (0,0,0) scaled to data extent
ax.plot([0, X.max()], [0, 0], [0, 0], 'k-', linewidth=1.5)  # X axis
ax.plot([0, 0], [0, Y.max()], [0, 0], 'k-', linewidth=1.5)  # Y axis
ax.plot([0, 0], [0, 0], [0, 2 * Z_shift], 'k-', linewidth=1.5)  # Z axis



ax.view_init(elev=4, azim=-90, roll=0)

plt.tight_layout()
plt.savefig('./figures/explanatory/visual_plane.pdf', bbox_inches='tight')
plt.show()

# %%
