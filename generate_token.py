import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime
import json

def generate_token(session_ids=None):
    # Ensure tokens are always unique by using uuid4 (independent of any random seed)
    # uuid4 uses os.urandom() which is not affected by random.seed() or np.random.seed()
    print("Generating tokens.")

    # load settings
    setting_file = "experimentSettings.json"
    with open(setting_file, "r") as file: 
        settings = json.load(file)

    wave_id = settings["wave"]["wave_id"]
    input_dir = f"input_data/{wave_id}"

    if session_ids is None:
        session_ids = [i.rstrip(".json").split("_")[1] 
                       for i in os.listdir(input_dir) 
                       if i.endswith(".json") and not i.startswith("settings")]
        session_ids = sorted(session_ids)
    
    session_ids = [sid + "-" + suffix for sid in session_ids if sid != "setting" for suffix in "ABC"]
    token = [str(uuid.uuid4()) for _ in session_ids]
    token_df = pd.DataFrame(dict(
        exp_id = "mem_diff", 
        var_name = "sid", 
        var_value = session_ids, 
        token = token
    ))

    # saving
    token_csv = os.path.join(os.getcwd(), "token", f"token_{wave_id}.csv")
    
    if os.path.isfile(token_csv): 
        key = input(f"{token_csv} exists already. Overwrite existing file?[y/n]")
        if key!="y": return

    token_df.to_csv(token_csv, index=False)

if __name__ == "__main__":
    generate_token()