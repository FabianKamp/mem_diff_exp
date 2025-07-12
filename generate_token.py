import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime

load_condition = "low-load"
response_format = "2afc"

version = "_".join([load_condition, response_format])
input_dir = f"input_data/{version}"

def generate_token():
    subject_ids = set([i.split("_")[-1].rstrip(".json") for i in os.listdir(input_dir) if i.endswith(".json")])
    subject_ids = sorted(subject_ids)
    token = [str(uuid.uuid4()) for _ in subject_ids]
    
    sequential = np.ones(len(subject_ids))
    sequential[:len(subject_ids)//2] = 0

    var1 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "subject_id", 
        var_value = subject_ids, 
        token = token
    ))
    
    var2 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "load_condition", 
        var_value = load_condition, 
        token = token
    ))

    var3 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "response_format", 
        var_value = response_format, 
        token = token
    ))

    var4 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "seq", 
        var_value = sequential, 
        token = token
    ))
    
    token_df = pd.concat([var1, var2, var3, var4])

    date = datetime.now().strftime("%Y%m%d")
    token_csv = os.path.join("token", f"token_{date}.csv")

    token_df.to_csv(token_csv, index=False)

generate_token()