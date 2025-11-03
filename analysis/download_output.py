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

parser = argparse.ArgumentParser()
parser.add_argument('--token_csv', type=str, default="./token/token_M-PA.csv")
parser.add_argument('--out_dir', type=str, default="./output_data")
args = parser.parse_args()

# make out dir
if not os.path.exists(args.out_dir): 
    os.mkdir(args.out_dir)

def get_data(token):
    url = f"{root_url}/{token}_finished/mem_diff-results.json"
    head_response = requests.head(url, auth=(user, password))
    if head_response.status_code == 200: 
        response = requests.get(url, auth=(user, password))
    else: 
        print(f"{url} not accessible. Status {head_response.status_code}")
        return 
    
    parsed = json.loads(response.json()["data"])
    dataProperties = parsed["dataProperties"]
    session_id = dataProperties["session_id"]
    
    data = pd.DataFrame(parsed["results"]["trials"])
    data.assign(**dataProperties)

    interaction_records = pd.DataFrame(parsed["interactionRecords"]["trials"])
    
    return session_id, data, interaction_records

token_df = pd.read_csv(args.token_csv)
for token in token_df.token.unique():
    output = get_data(token)
    if output is None:
        continue
    session_id, data, interaction_records = output
    data.to_csv(f"{args.out_dir}/{session_id}.csv")
    interaction_records.to_csv(f"{args.out_dir}/{session_id}_ir.csv")
