import os 
import pandas as pd 
import uuid
import numpy as np
from datetime import datetime
import json
import argparse

def generate_token(wave_id, session_ids=None, suffix=None):
    # Ensure tokens are always unique by using uuid4 (independent of any random seed)
    # uuid4 uses os.urandom() which is not affected by random.seed() or np.random.seed()
    
    print("Generating tokens.")
    if session_ids is None:
        input_dir = f"input_data/{wave_id}"
        assert os.path.isdir(input_dir), f"{wave_id} not found in input_data/"
        
        session_ids = [fname.rstrip(".json").split("_")[1] 
                       for fname in os.listdir(input_dir) 
                       if fname.endswith(".json") and not fname.startswith("_settings")]
        session_ids = sorted(session_ids)
    
    if suffix is None: 
        suffix = "ABCD"

    if type(session_ids) != list: 
        session_ids = [session_ids]
    
    session_ids = [sid + "-" + sx for sid in session_ids if sid != "setting" for sx in suffix]
    
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
        key = input(f"{token_csv} exists already. Overwrite [o], add new token [a], create new csv [n], or cancel [c]?")
        assert key in "oanc", "Input has to be o,a or c."
        
        if key == "c": 
            print("Cancel token generation")
            return
        elif key == "o": 
            print("Overwriting existing file.")
        elif key == "a": 
            print("Adding new token to existing file.")
            old_token_df = pd.read_csv(token_csv)
            token_df = pd.concat([old_token_df, token_df])
        elif key == "n": 
            print("Create new csv file")
            token_csv = token_csv.rstrip(".csv") + "_2.csv"

    # write to csv
    token_df.to_csv(token_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate tokens for experiment wave.')
    parser.add_argument(
        '--wave_id', 
        type=str,
        help='ID of the wave (e.g. "M-PD")',
        required=True
        )
    parser.add_argument(
        '--session_ids', 
        type=str,
        help='Session IDs (e.g. "M-PD-001") for which tokens are generated. Default is None',
        default=None
        )
    parser.add_argument(
        '--suffix', 
        type=str,
        help='Suffixes (e.g. DEF) Default is None',
        default=None
        )
    args = parser.parse_args()
    
    generate_token(args.wave_id, args.session_ids, args.suffix)