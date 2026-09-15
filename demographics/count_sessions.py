# %%
import numpy as np
import os 
import pandas as pd
import glob

# %% 

all_sessions = set([os.path.basename(f).replace(".", "_").split("_")[0]
       for f in glob.glob("../output_data/raw/**/M-*.csv", recursive=True)
       ])


n_pilots = {key: len([session for session in all_sessions if f"P{key}" in session]) 
            for key in list("ABCDEFG")}
n_v1 = len([session for session in all_sessions if f"V1" in session])

print("Pilots total: ", sum(n_pilots.values()))
print("Pilots: ", n_pilots)
print("V1: ", n_v1)

# %%
