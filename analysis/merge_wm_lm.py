# %% 
# loading packages
import os
import pandas as pd
import seaborn as sns

# set colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)
# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %% 
# load data
bin_width = .25
bin_width_per_item = .1
out_name = "aggregated_v1"

# define pilots
session_dict = {
    "M-V1": list(range(1,120))
}

# %%
# load data
def load_data(session_dict):
    out_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
                for wave_code in session_dict.keys()
                for i in session_dict[wave_code] 
                for suffix in "ABCD" 
                ]
    out_files = filter(os.path.exists, out_files)

    # concat data
    all_data = [] 
    for file in out_files: 
        data = pd.read_csv(file)   
        all_data.append(data)
    all_data = pd.concat(all_data) 
    return all_data

all_data = load_data(session_dict)

# %% 
# vs data
vs_data = all_data.loc[
    (all_data.trial_type=='wm') & 
    (all_data.condition_name!='mixed') & 
    (all_data.phase == "recognition") 
    ].copy()

# set the response data
vs_data.response = vs_data.response.astype("Int64")
vs_data.correct_response = vs_data.correct_response.astype("Int64")
vs_data["correct_wm"] = (vs_data.response == vs_data.correct_response)

# mixed data
mixed_data = all_data.loc[
    (all_data.trial_type=='wm') & 
    (all_data.condition_name=='mixed') & 
    (all_data.response.notna()) &
    (all_data.phase == "recognition") 
    ].copy()
mixed_data.response = mixed_data.response.astype("Int64")
mixed_data["response_mixed"] = (
    mixed_data
    .apply(lambda row: row.stimulus_left if row.response == 0 else row.stimulus_right, axis=1)
    .str.split("/").str[-1].str[0]
    .map({'3': "semantic", '4': "visual"})
)

# lm data 
lm_data = all_data.loc[
    (all_data.trial_type=="lm")
    ].copy()

# set response data
lm_data["response_lm"] = lm_data.response.astype('Int64')
lm_data["correct_response_lm"] = lm_data.correct_response.astype('Int64')
lm_data["correct_lm"] = (lm_data.response_lm == lm_data.correct_response_lm)

# %%
# wm data
wm_data = pd.concat([vs_data, mixed_data])
wm_data = wm_data[[
    "session_id",
    "encoding_trial_id",
    "condition_name", 
    "encoding_time", 
    "correct_wm",
    "response_mixed",
    "rt"
]]

lm_data = lm_data[[
    "session_id",
    "encoding_trial_id",
    "correct_lm",
    "rt",
]]

# %%
combined_data = wm_data.merge(
    lm_data, 
    on=[
        "session_id", 
        "encoding_trial_id"
        ], 
    suffixes = ["_wm", "_lm"]
    )
combined_data.to_csv("./output_data/long/combined_data.csv", index=False)

