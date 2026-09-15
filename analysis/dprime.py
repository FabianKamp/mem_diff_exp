# %%
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


# %%
x = np.linspace(0,1,100)
y = np.sqrt(2)*norm.ppf(x)

plt.plot(x,y)
plt.plot(x,x-.5)
plt.axhline(0, c="k")
# %%
