import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime

input_dir = f"input_data/"

def generate_token(subject_ids=None):
    if subject_ids is None:
        subject_ids = set([i.split("_")[-1].rstrip(".json") for i in os.listdir(input_dir) if i.endswith(".json")])
        subject_ids = sorted(subject_ids)
    token = [str(uuid.uuid4()) for _ in subject_ids]

    token_df = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "sid", 
        var_value = subject_ids, 
        token = token
    ))
    
    date = datetime.now().strftime("%Y%m%d")
    token_csv = os.path.join("token", f"token_{date}.csv")
    token_df.to_csv(token_csv, index=False)

generate_token()