import requests
import pandas as pd
import os 
import json
from dotenv import load_dotenv, find_dotenv
import argparse
load_dotenv(find_dotenv()); 

user= os.getenv("EXP_USER")
password= os.getenv("EXP_PASSWORD")
root_url = os.getenv("EXP_URL")

wave_id = "M-PD"
default_csv = f"./token/token_{wave_id}.csv"
default_out_dir = f"./output_data/{wave_id}"

parser = argparse.ArgumentParser()
parser.add_argument('--token_csv', type=str, default=default_csv)
parser.add_argument('--out_dir', type=str, default=default_out_dir)
args = parser.parse_args()

# make out dir
if not os.path.exists(args.out_dir): 
    os.mkdir(args.out_dir)

def get_data(token):
    url = f"{root_url}/{token}_finished/mem_diff-results.json"
    head_response = requests.head(url, auth=(user, password))
    if head_response.status_code == 200: 
        response = requests.get(url, auth=(user, password))
        print(f"Downloading {token} ...")
    else: 
        return 
    
    parsed = json.loads(response.json()["data"])

    if "dataProperties" in parsed:
        dataProperties = parsed["dataProperties"]
        session_id = dataProperties["session_id"]
        data = pd.DataFrame(parsed["results"]["trials"])
        data.assign(**dataProperties)
        interaction_records = pd.DataFrame(parsed["interactionRecords"]["trials"])
        interaction_records["session_id"] = session_id
        return dict(
            session_id = session_id, 
            data = data, 
            interaction_records = interaction_records
        )
    
    else:
        data = pd.DataFrame(parsed["trials"])
        return dict(
            data = data
        )

token_df = pd.read_csv(args.token_csv)
for token in token_df.token.unique():
    output = get_data(token)
    if output is None:
        continue
    
    # save
    if "session_id" in output:
        output["data"].to_csv(f"{args.out_dir}/{output["session_id"]}.csv")
        output["interaction_records"].to_csv(f"{args.out_dir}/{output["session_id"]}_browser_records.csv")
    else: 
        output["data"].to_csv(f"{args.out_dir}/{token}.csv")
