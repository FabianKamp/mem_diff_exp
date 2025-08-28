import numpy as np
import pandas as pd
import os
import glob
import json

prefix_id = "v"
start_id = 1 # if subject id is already given away
subject_number = 12
trials = 185

out_dir = f"input_data/vision/"

# script start
if subject_number%4!=0:
    print("Subject number will be higher due to latin square randomization")
          
if not os.path.exists(out_dir): 
    os.mkdir(out_dir)

def get_image_paths(stimuli_folder): 
    image_path = list(glob.glob(os.path.join(stimuli_folder, "**", "*.jpg"), recursive=True))
    image_path = [os.path.join("stimuli", i.split("stimuli/", 1)[-1]) for i in image_path 
                  if "instruction" not in i]
    image_id = [int(i.split("/")[-1].rstrip(".jpg")) for i in image_path]
    image_paths = pd.DataFrame(dict(image_id=image_id, image_path=image_path)).sort_values(by="image_id")
    return image_paths
image_paths = get_image_paths("stimuli/")

def get_file_path(image_id):
    file_path = image_paths.loc[image_paths.image_id == image_id, "image_path"]
    return file_path.iloc[0]

nan = 9999
counter = 0

while counter < subject_number:    
    set_ids = np.random.permutation(np.arange(trials) + 1)
    sample_ids = set_ids + 1000
    sample_files = np.array([get_file_path(i) for i in sample_ids])
    
    # conditions and condition codes 
    # conditions = [(3,2), (3,5), (4,2), (4,5)]
    conditions = [(4,2), (4,2), (4,2), (4,2)]
    num_conditions = len(conditions)
    
    # randomize wm condition across trials
    repeats = trials//num_conditions
    vision_conditions = np.repeat(np.arange(num_conditions), repeats + 1)[:trials]

    random_idx = np.random.permutation(np.arange(trials))
    random_conditions = vision_conditions[random_idx]
    
    ## latin square randomization 
    for i in range(num_conditions):  
        subject_id = prefix_id + str(counter + start_id).zfill(3)       
        
        # working memory
        latin_conditions = random_conditions % num_conditions
        random_conditions += 1

        exp_ids = set_ids + np.array([conditions[c][0] for c in latin_conditions]) * 1e3
        exp_files = np.array([get_file_path(i) for i in exp_ids.flatten()])

        context_ids = set_ids + np.array([conditions[c][1] for c in latin_conditions]) * 1e3
        context_files = np.array([get_file_path(i) for i in context_ids.flatten()])

        condition_codes = np.array([conditions[c][0]*10 + conditions[c][1] for c in latin_conditions])
        
        context_correct = (context_ids<3000).astype(int)
        exp_correct = (context_ids>5000).astype(int)

        exp_left = np.random.choice([0,1], trials)
        left_correct = (exp_left & exp_correct) | (~exp_left & ~exp_correct)
        correct_response = ~left_correct

        trial_data = dict(
            trial_id = np.arange(trials),
            set_id = set_ids.astype(int),
            sample_file = sample_files,
            exp_file = exp_files,
            exp_left = exp_left,
            context_file = context_files, 
            correct_response = correct_response, 
            condition_code = condition_codes
        )   

        # save 
        trial_df = pd.DataFrame(trial_data)
        json_data = trial_df.to_dict(orient='records')
        
        file_path = os.path.join(out_dir, f"input_subject_{subject_id}.json")
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

        counter += 1
        
        
    
            
