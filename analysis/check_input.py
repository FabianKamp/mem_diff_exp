import pandas as pd
import glob
import os
import numpy as np

# Display all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def check_wm_input(file):
    data = pd.read_json(file)
    wm_data = data.loc[(data.trial_type=="wm")]
    encoding_time_count = wm_data.groupby(["wm_block_id", "condition"]).value_counts(subset=["encoding_time"]).reset_index()
    left_target_count = wm_data.groupby(["wm_block_id", "condition", "encoding_time"]).value_counts(subset=["left_target"]).reset_index()
    left_target_count = left_target_count.sort_values(by=["wm_block_id", "condition", "encoding_time", "left_target"])
    recognition_theta = wm_data.groupby(["wm_block_id", "condition"]).value_counts(subset=["recognition_theta"]).reset_index()

    print("\nEncoding Time Count:")
    print(encoding_time_count)
    print("\nLeft Target Count:")
    print(left_target_count)
    print("\nRecognition Theta:")
    print(recognition_theta)

def check_lm_input(file):
    data = pd.read_json(file)
    lm_data = data.loc[(data.trial_type=="lm")]
    encoding_time_count = lm_data.groupby("condition").value_counts(subset=["encoding_time"]).reset_index()
    left_target_count = lm_data.groupby(["condition", "encoding_time"]).value_counts(subset=["left_target"]).reset_index()
    left_target_count = left_target_count.sort_values(by=["condition", "encoding_time", "left_target"])
 
    print("\nEncoding Time Count:")
    print(encoding_time_count)
    print("\nLeft Target Count:")
    print(left_target_count)

def latin_square_check(file_list): 
        print(f"Latin square check:", end="\t", flush=True)
        conditions, set_ids = [],[]
        for f in file_list: 
            data = pd.read_json(f)
            wm_data = data.loc[data.trial_type=="wm"]
            conditions.append(wm_data.condition.to_numpy()[:,np.newaxis])
            # check set ids
            if len(set_ids)>0 :
                assert np.all(set_ids == wm_data.set_id), "Randomization Error. Set ids should be the same."
            set_ids = wm_data.set_id.copy()

        conditions = np.hstack(conditions)
        nconditions = [len(np.unique(trial)) for trial in conditions]
        
        if not all([trial==3 for trial in nconditions]):
            session_id = os.path.basename(f).rstrip(".json").lstrip("input_")
            print(f"\nLatin Square Error while checking f{session_id}")
            raise Exception("")
        
        print(" -> ok")

if __name__ == "__main__":

    prefix = "M-PD"
    files = sorted(glob.glob(f"./input_data/{prefix}/*{prefix}*.json"))
    files = [f for f in files if '999' not in os.path.basename(f)]

    old_dict = {}
    latin_list = []
    for i, f in enumerate(files):
        print(f"Count check: {f} ...", end="", flush=True)
        if i == 0:
            check_wm_input(f)
            check_lm_input(f)
        
        latin_list.append(f)
        if len(latin_list) == 3:
            latin_square_check(latin_list)
            latin_list = []
        


