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
    encoding_time_count = wm_data.groupby(["condition"]).value_counts(subset=["encoding_time"]).reset_index()
    left_target_count = wm_data.groupby(["condition", "encoding_time"]).value_counts(subset=["left_target"]).reset_index()
    left_target_count = left_target_count.sort_values(by=["condition", "encoding_time", "left_target"])
    recognition_theta = wm_data.groupby(["condition"]).value_counts(subset=["recognition_theta"]).reset_index()
    recognition_theta = recognition_theta.sort_values(by=["condition","count"])

    print("="*60)
    print("WM data check")
    print("="*60)

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
    
    print("="*60)
    print("LM data check")
    print("="*60)

    print("\nEncoding Time Count:")
    print(encoding_time_count)
    print("\nLeft Target Count:")
    print(left_target_count)

    print("="*60)
    print("\n")

def latin_square_check(file_list): 
        conditions = []
        
        # check to previous 
        previous_data = []
        identical_columns = [
            "set_id",
            "encoding_time",
            "encoding_1", 
            "encoding_2", 
            "encoding_3", 
            "encoding_theta_1", 
            "encoding_theta_2",
            "encoding_theta_3",
            "encoding_file_1", 
            "encoding_file_2",
            "encoding_file_3",
            "recognition_theta", 
            "sample_position",
            "sample_file",
        ]

        latin_colums = [
            "condition",
            "condition_name"
        ]

        for f in file_list: 
            data = pd.read_json(f)
            current_data = data.loc[data.trial_type=="wm"]
            conditions.append(current_data.condition.to_numpy()[:,np.newaxis])
            
            if len(previous_data)==0 :
                previous_data = current_data.copy()
                continue

            # check identical columns
            for col in identical_columns: 
                assert (previous_data[col] == current_data[col]).all(), f"Latin Square Error: {col} are not idential."            
            
            # check columns that should have been changed
            for col in latin_colums: 
                assert (previous_data[col] != current_data[col]).all(), f"Latin Square Error: {col} are idential."            
            
            previous_data = current_data.copy()


        conditions = np.hstack(conditions)
        nconditions = [len(np.unique(trial)) for trial in conditions]
        
        if not all([trial==3 for trial in nconditions]):
            session_id = os.path.basename(f).rstrip(".json").lstrip("input_")
            print(f"\nLatin Square Error while checking f{session_id}")
            raise Exception("")
        
        print(" -> ok")

if __name__ == "__main__":

    prefix = "M-PG"
    files = sorted(glob.glob(f"./input_data/{prefix}/*{prefix}*.json"))
    files = [f for f in files if '999' not in os.path.basename(f)]

    old_dict = {}
    latin_list = []
    for i, f in enumerate(files):
        if i == 0:
            print(f"Count check: {f} ...", end="", flush=True)
            check_wm_input(f)
            check_lm_input(f)
        
        latin_list.append(f)
        if len(latin_list) == 3:
            print("Latin square check: ", latin_list, end="\t", flush=True)
            latin_square_check(latin_list)
            latin_list = []
        


