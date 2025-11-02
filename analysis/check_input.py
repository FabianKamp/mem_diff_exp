import pandas as pd
import seaborn as sns
import glob
import os
import numpy as np

prefix = "M-PC"
files = sorted(glob.glob(f"./input_data/{prefix}/*{prefix}*.json"))
files = [f for f in files if '999' not in os.path.basename(f)]

old_dict = {}
for i, f in enumerate(files):
    print(f"Count check: {f} ...", end="", flush=True)
    session_id = os.path.basename(f).rstrip(".json").lstrip("input_")
    data = pd.read_json(f)

    new_dict = {
        f"n_wm_trials": np.sum(data.trial_type=="wm"),
        f"n_lm_trials": np.sum(data.trial_type=="lm"),
    }

    for condition in range(1, 4):
        for long_enc in range(2):
            # Filter data for current condition and encoding
            mask = (data.condition == condition) & \
                   (data.long_encoding == long_enc) & \
                   (data.trial_type == "wm")
            wm_data = data.loc[mask]

            # Calculate counts
            key_prefix = f"condition_{condition}{long_enc}"
            new_dict.update({
                f"{key_prefix}_count": len(wm_data),
                f"{key_prefix}_left_target": wm_data.left_target.sum(),
                f"{key_prefix}_right_target": len(wm_data)-wm_data.left_target.sum(),
                f"{key_prefix}_sample_position_1": (wm_data.sample_position == 1).sum(),
                f"{key_prefix}_sample_position_2": (wm_data.sample_position == 2).sum(),
                f"{key_prefix}_sample_position_3": (wm_data.sample_position == 3).sum(),
            })

            # Filter data for current condition and encoding
            mask = (data.condition == condition) & \
                   (data.long_encoding == long_enc) & \
                   (data.trial_type == "lm")
            lm_data = data.loc[mask]

            # Calculate counts
            key_prefix = f"condition_{condition}{long_enc}"
            new_dict.update({
                f"{key_prefix}_lm_count": len(lm_data),
                f"{key_prefix}_lm_left_target": lm_data.left_target.sum(),
                f"{key_prefix}_lm_right_target": len(lm_data)-lm_data.left_target.sum(),
            })

    if i>0:
        for key in new_dict.keys():
            if not (old_dict[key] == new_dict[key]):
                print(f"\n{key} {old_dict[key]}")
                print(f"{key} {new_dict[key]}")
                raise Exception("")

    print(" -> ok")
    old_dict = new_dict.copy()

# ======================
# Latin square check
# ======================

for suffix in ["A","B"]: 
    file_list = [f for f in files if os.path.basename(f).endswith(f"{suffix}.json")]
    while len(file_list)>0:
        conditions = []
        for i in range(3): 
            last_check = []
            current_file = file_list[0]
            print(f"Latin square check: {os.path.basename(current_file)}  ", end="", flush=True)
            
            wm_data = pd.read_json(current_file)
            wm_data = wm_data.loc[data.trial_type=="wm"]
            conditions.append(wm_data.condition.to_numpy()[:,np.newaxis])
            last_check.append(current_file)
            file_list.pop(0)
        conditions = np.hstack(conditions)
        nconditions = [len(np.unique(trial)) for trial in conditions]
        
        if not all([trial==3 for trial in nconditions]):
            print(f"\nLatin Square Error while checking f{last_check}")
            raise Exception("")
        
        print(" -> ok")

# ======================
# print count sumary 
# ======================
def print_summary_table(data_dict):
    """Print formatted summary tables for all metrics."""
    print(f"\n{'='*80}")
    print(f"SUMMARY | WM trials: {data_dict['n_wm_trials']} | LM trials: {data_dict['n_lm_trials']}")
    print('='*80)

    # All metrics in one row
    metrics = [
        ("count", "Count"),
        ("left_target", "Left"),
        ("right_target", "Right"),
        ("lm_count", "LM Count"),
        ("lm_left_target", "LM Left"),
        ("lm_right_target", "LM Right"),
        ("sample_position_1", "P1"),
        ("sample_position_2", "P2"),
        ("sample_position_3", "P3")
    ]

    # Print header
    header = "    |"
    for _, label in metrics:
        header += f"{label:^10}|"
    print(f"\n{header}")

    # Print column labels
    cols = "    |"
    for _ in metrics:
        cols += "LE0|LE1|  |"
    print(cols)

    # Print separator
    sep = "----+" + ("---+---+--+" * len(metrics))
    print(sep)

    # Print data for each condition
    for condition in range(1, 4):
        row = f"C{condition}  |"
        for field_key, _ in metrics:
            v0 = data_dict[f'condition_{condition}0_{field_key}']
            v1 = data_dict[f'condition_{condition}1_{field_key}']
            row += f"{v0:3d}|{v1:3d}|  |"
        print(row)

    print(sep)

print_summary_table(new_dict)


