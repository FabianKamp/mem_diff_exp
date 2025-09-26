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
parser.add_argument('--token_txt', type=str, default="./analysis/used_token.txt")
parser.add_argument('--out_dir', type=str, default="./output_data")
args = parser.parse_args()

used_token = []
with open(args.token_txt, "r") as file: 
    for line in file:
        token = line.strip()
        if token != '': 
            used_token.append(token)

def get_data(token):
    url = f"{root_url}/{token}_finished/mem_diff-results.json"
    response = requests.get(url, auth=(user, password))
    parsed = json.loads(response.json()["data"])
    dataProperties = parsed["dataProperties"]
    session_id = dataProperties["session_id"]
    
    data = pd.DataFrame(parsed["results"]["trials"])
    data.assign(**dataProperties)
    
    return session_id, data

for token in used_token:
    try:
        session_id, data = get_data(token)
        data.to_csv(f"{args.out_dir}/{session_id}.csv")
    except:
        print(f"Error while downloading {token}")
