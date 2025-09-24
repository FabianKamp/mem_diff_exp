import numpy as np
import pandas as pd
import os
import glob
import json

image_dir = "stimuli/"
out_dir = f"input_data/"

# load settings
setting_file = "experimentSettings.json"
with open(setting_file, "r") as file: 
    settings = json.load(file)

wave_id = settings["wave"]["wave_id"]
subject_number = settings["wave"]["subject_number"]

vision_trials = settings["vision_experiment"]["vision_trials"]
ncatch = settings["vision_experiment"]["ncatch"]

# script start         
if not os.path.exists(out_dir): 
    os.mkdir(out_dir)

def get_image_paths(stimuli_folder): 
    image_path = list(glob.glob(os.path.join(stimuli_folder, "**", "*.jpg"), recursive=True))
    image_path = [os.path.join(stimuli_folder, i.split("stimuli/", 1)[-1]) for i in image_path 
                  if ("instruction" not in i) & ("_archive" not in i)]
    image_id = [int(i.split("/")[-1].rstrip(".jpg")) for i in image_path]
    image_paths = pd.DataFrame(dict(image_id=image_id, image_path=image_path)).sort_values(by="image_id")
    return image_paths
image_paths = get_image_paths(image_dir) # change back to stimuli

def get_file_path(image_id):
    file_path = image_paths.loc[image_paths.image_id == image_id, "image_path"]
    try: 
        return file_path.iloc[0]
    except: 
        return nan

def generate_catch_trials(ncatch):   
    catch_ids = np.random.choice(np.arange(0,700), ncatch*2, replace=False) + 9000
    catch_ids = catch_ids.reshape(-1,2)

    sample_files = np.array([get_file_path(i) for i in catch_ids[:,0]])
    exp_files = sample_files
    context_files = np.array([get_file_path(i) for i in catch_ids[:,1]])

    # left right randomization & correct response
    exp_right = np.random.choice([0,1], ncatch)
    correct_response = exp_right

    catch_trial_data = dict(
        subject_id = subject_id,
        trial_id = np.arange(ncatch),
        trial_type = "catch_trial", 
        set_id = nan,
        sample_file = sample_files,
        exp_file = exp_files,
        exp_right = exp_right,
        context_file = context_files, 
        correct_response = correct_response, 
        condition_code = nan,
    )

    catch_trial_df = pd.DataFrame(catch_trial_data)
    catch_json_data = catch_trial_df.to_dict(orient='records')
    catch_positions = np.linspace(10, vision_trials-10, ncatch).astype(int)
    
    return catch_positions, catch_json_data


nan = 9999
counter = 0

while counter < subject_number:    
    set_ids = np.random.permutation(np.arange(vision_trials) + 1)
    sample_ids = set_ids + 1000
    sample_files = np.array([get_file_path(i) for i in sample_ids])
    
    # conditions and condition codes 
    # conditions = [(3,2), (3,5), (4,2), (4,5)]
    conditions = [(4,3), (4,5), (3,5)]
    num_conditions = len(conditions)
    
    if subject_number%num_conditions!=0:
        print("Subject number will be higher due to latin square randomization")
    
    # randomize wm condition across trials
    repeats = vision_trials//num_conditions
    vision_conditions = np.repeat(np.arange(num_conditions), repeats + 1)[:vision_trials]

    random_idx = np.random.permutation(np.arange(vision_trials))
    random_conditions = vision_conditions[random_idx]

    ## latin square randomization 
    for i in range(num_conditions):  
        subject_id = counter+1       
        session_id = f"V-{wave_id}-{subject_id:03d}"       
        
        # working memory
        latin_conditions = random_conditions % num_conditions
        random_conditions += 1

        exp_ids = set_ids + np.array([conditions[c][0] for c in latin_conditions]) * 1e3
        exp_files = np.array([get_file_path(i) for i in exp_ids.flatten()])

        context_ids = set_ids + np.array([conditions[c][1] for c in latin_conditions]) * 1e3
        context_files = np.array([get_file_path(i) for i in context_ids.flatten()])

        condition_codes = np.array([conditions[c][0]*10 + conditions[c][1] for c in latin_conditions])
        
        # left right randomization
        exp_right = np.random.choice([0,1], vision_trials)

        # correct response
        exp_correct = (context_ids>5000)
        right_correct = (exp_right.astype(bool) & exp_correct)
        correct_response = right_correct.astype(int)
        correct_response[(context_ids<5000)] = nan

        trial_data = dict(
            subject_id = subject_id,
            session_id = session_id,
            trial_id = np.arange(vision_trials),
            trial_type = "vision_trial", 
            set_id = set_ids.astype(int),
            sample_file = sample_files,
            exp_file = exp_files,
            exp_right = exp_right,
            context_file = context_files, 
            correct_response = correct_response, 
            condition_code = condition_codes
        )   

        # save 
        trial_df = pd.DataFrame(trial_data)
        json_data = trial_df.to_dict(orient='records')

        # insert catch trials
        catch_positions, catch_json_data = generate_catch_trials(ncatch)
        for p, catch_trial in zip(reversed(catch_positions), reversed(catch_json_data)):
            json_data.insert(p,catch_trial)
        
        file_path = os.path.join(out_dir, f"input_{session_id}.json")
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

        counter += 1
        
        
    
            
