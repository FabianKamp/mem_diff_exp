import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime

load_condition = "low-load"
response_format = "2afc"

version = "_".join([load_condition, response_format])
input_dir = f"input_data/{version}"

sequential = "Y" # N
encoding_time = "short" # long

vc = f"L{load_condition[0]}R{response_format[0]}S{sequential}E{encoding_time[0]}"
vc = vc.upper()

def generate_token():
    subject_ids = set([i.split("_")[-1].rstrip(".json") for i in os.listdir(input_dir) if i.endswith(".json")])
    subject_ids = sorted(subject_ids)
    token = [str(uuid.uuid4()) for _ in subject_ids]

    var1 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "sid", 
        var_value = subject_ids, 
        token = token
    ))

    var2 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "vc", 
        var_value = vc, 
        token = token
    ))

    var3 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "load", 
        var_value = load_condition, 
        token = token
    ))

    var4 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "etime", 
        var_value = encoding_time, 
        token = token
    ))

    var5 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "response", 
        var_value = response_format, 
        token = token
    ))

    var6 = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "seq", 
        var_value = sequential, 
        token = token
    ))
    
    token_df = pd.concat([var1, var2, var3, var4, var5, var6])

    date = datetime.now().strftime("%Y%m%d")
    token_csv = os.path.join("token", f"token_{date}.csv")

    token_df.to_csv(token_csv, index=False)

generate_token()