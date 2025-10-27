import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime
import json

def generate_token(session_ids=None):
    # load settings
    setting_file = "experimentSettings.json"
    with open(setting_file, "r") as file: 
        settings = json.load(file)

    version_id = settings["wave"]["version_id"]
    wave_id = settings["wave"]["wave_id"]
    input_dir = f"input_data/"

    if session_ids is None:
        session_ids = [i.rstrip(".json").split("_")[1] for i in os.listdir(input_dir) if i.endswith(".json")]
        session_ids = sorted(session_ids)
        session_ids = [s for s in session_ids if s.split("-")[0] == version_id]
        session_ids = [s for s in session_ids if s.split("-")[1] == wave_id]
    
    token = [str(uuid.uuid4()) for _ in session_ids]
    token_df = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "sid", 
        var_value = session_ids, 
        token = token
    ))

    # saving
    token_csv = os.path.join(os.getcwd(), "token", f"token_{version_id}-{wave_id}.csv")
    if os.path.isfile(token_csv): 
        key = input(f"{token_csv} exists already. Overwrite existing file?[y/n]")
        if key=="y":
            token_df.to_csv(token_csv, index=False)
        else:
            return

if __name__ == "__main__":
    generate_token()