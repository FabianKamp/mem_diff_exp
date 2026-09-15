# %% 
# loading packages
import os
import json
import numpy as np
import pandas as pd

# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %%
# load data - visual vs. semantic
vs_data = pd.read_csv("./output_data/aggregated/aggregated_v1.csv")

with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "r") as file:
    to_exclude = json.load(file)["to_exclude"]

good_sessions = vs_data.loc[~vs_data.session_id.isin(to_exclude), "session_id"].unique()
good_ids = [int(s.split('-')[-2]) for s in good_sessions]

# %%
# get list of for new credentials 

new_credentials = [f"{i:03d}-B" for i in np.arange(1,100) if i not in good_ids]
print(new_credentials)
# %%
