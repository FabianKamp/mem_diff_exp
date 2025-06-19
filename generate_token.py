import os 
import pandas as pd 
import uuid
import numpy as np

version = "test"
input_dir = f"input_data/{version}"

def generate_token():
    subject_ids = set([i.split("_")[-1].rstrip(".json") for i in os.listdir(input_dir) if i.endswith(".json")])
    subject_ids = sorted(subject_ids)
    token = [str(uuid.uuid4()) for _ in subject_ids]
    
    var1 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "subject_id", 
        var_value = subject_ids, 
        token = token
    ))
    
    var2 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "version", 
        var_value = version, 
        token = token
    ))
    
    token_df = pd.concat([var1, var2])

    i = 1
    while True:
        token_csv = os.path.join("token", f"token_{i:02d}.csv")
        if not os.path.exists(token_csv): break
        i += 1

    token_df.to_csv(token_csv, index=False)

generate_token()