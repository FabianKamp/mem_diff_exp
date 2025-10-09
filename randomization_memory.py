import numpy as np
import pandas as pd
import os
import glob
import json

# set seed
np.random.seed(42) 

out_dir = f"input_data/"
image_dir = "stimuli"

# load settings
setting_file = "experimentSettings.json"
with open(setting_file, "r") as file: 
    settings = json.load(file)

wave_id = settings["wave"]["wave_id"]
subject_number = settings["wave"]["subject_number"]

load = settings["memory_experiment"]["load"]
practice_trials = settings["memory_experiment"]["practice_trials"]
wm_trials = settings["memory_experiment"]["wm_trials"]
lm_trials = settings["memory_experiment"]["lm_trials"]
ncatch = settings["memory_experiment"]["ncatch"]

all_wm_trials = wm_trials + practice_trials

if not os.path.exists(out_dir): 
    os.mkdir(out_dir)

def get_image_paths(stimuli_folder): 
    image_path = list(glob.glob(os.path.join(stimuli_folder, "**", "*.jpg"), recursive=True))
    image_path = [os.path.join(stimuli_folder, i.split("stimuli/", 1)[-1]) for i in image_path 
                  if ("instruction" not in i) & ("_archive" not in i)]
    image_id = [int(i.split("/")[-1].rstrip(".jpg")) for i in image_path]
    image_paths = pd.DataFrame(dict(image_id=image_id, image_path=image_path)).sort_values(by="image_id")
    return image_paths
image_paths = get_image_paths(image_dir)

def get_file_path(image_id):
    file_path = image_paths.loc[image_paths.image_id == image_id, "image_path"]
    return file_path.iloc[0]

def generate_random_angles(n):
    """
    Generate a list of random angles evenly distributed around a circle.

    This function generates `n` angles such that they are evenly spaced 
    around a circle, starting from a random initial angle. The angles 
    are then randomly permuted and rounded to three decimal places.

    Parameters:
        n (int): The number of angles to generate.

    Returns:
        numpy.ndarray: A 1D array of `n` random angles (in radians), 
        evenly distributed and randomly permuted, rounded to three decimal places.
    """
    angle_between = np.pi * 2 / n
    random_angles = [np.random.rand() * (np.pi * 2)]
    for _ in range(n-1):
        next_angle = (random_angles[-1] + angle_between) % (np.pi * 2)
        random_angles.append(next_angle)
    random_angles = np.random.permutation(random_angles)
    random_angles = np.round(random_angles, 3)
    return random_angles

def generate_catch_trials(ncatch, catch_ids):   
    encoding_thetas = np.random.rand(ncatch) * (np.pi * 2) 
    
    encoding_ids = catch_ids[:ncatch]
    encoding_files = np.array([get_file_path(i) for i in encoding_ids])
    
    control_ids = catch_ids[ncatch:]
    recognition_control_files = np.array([get_file_path(i) for i in control_ids])

    left_target = np.random.choice([0,1], ncatch, replace=True).astype(int)
    correct_response = (left_target==0).astype(int)

    catch_trial_data = dict(
        wm_id = nan,
        condition = nan,
        trial_id = np.arange(ncatch), 
        sample_position = 1,
        recognition_theta = encoding_thetas,
        trial_type = "catch",
        recognition_control_file = recognition_control_files,
        recognition_target_file = encoding_files,
        long_encoding = np.zeros(ncatch),
        left_target = left_target,
        target_correct = np.ones(ncatch),
        correct_response = correct_response,
        wm_block_id = np.repeat([1,2], int(ncatch/2)),
        condition_name = "no_catch", 
        encoding = encoding_ids,
        encoding_file_1 = encoding_files,
        encoding_theta_1 = encoding_thetas,
        n_encoding = 1,
        subject_id = subject_id,
    )

    catch_positions = np.linspace(practice_trials+5, wm_trials-5, ncatch).astype(int)
    catch_trial_df = pd.DataFrame(catch_trial_data)
    catch_json_data = catch_trial_df.to_dict(orient='records')

    return catch_positions, catch_json_data

# randomization
nan = 9999
counter = 0

while counter < subject_number:    
    # randomize images ids for wm and lm
    wm_ids = np.random.permutation(np.arange(all_wm_trials) +   1)
    wm_encoding = wm_ids + 1000
    wm_sample_files = np.array([get_file_path(i) for i in wm_encoding])
    
    # randomize sequential position
    sample_positions = np.array([np.random.choice(np.arange(load), 1, replace=False)[0] 
                                 for _ in range(all_wm_trials)])

    # generate angles
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(all_wm_trials)])
    recognition_thetas = encoding_thetas[np.arange(all_wm_trials), sample_positions].flatten()

    # randomize distractors 
    # distractor concepts should not overlap between wm and lm

    dist_info = pd.read_csv("./stimuli/dist_stimuli/image_info.csv")
    
    # lm_dist_concepts = np.random.choice(dist_info.concept.unique(), lm_trials-wm_trials, replace=False)
    lm_dist_concepts = np.random.choice(dist_info.concept.unique(), lm_trials, replace=False)
    lm_dist_pool = dist_info.loc[dist_info.concept.isin(lm_dist_concepts)]
    lm_distractors = lm_dist_pool.groupby("concept")["diff_id"].first().to_numpy()
    lm_distractors += 9000
    
    # Attention: No trials with several distractors from the same category
    all_wm_images = all_wm_trials * load
    wm_dist_pool = dist_info.loc[~dist_info.concept.isin(lm_dist_concepts)]
    wm_dist_idx = np.arange(all_wm_images - all_wm_trials) + 1
    wm_dist_idx = np.concat([np.random.permutation(wm_dist_idx[i::5]) for i in np.random.permutation(range(5))]).flatten() # ensures distance of 5
    wm_dist_df = wm_dist_pool.iloc[wm_dist_idx,]
    wm_dist_concepts = wm_dist_df.concept.unique()
    wm_distractors = wm_dist_df.diff_id.to_numpy()
    wm_distractors += 9000

    catch_pool = dist_info.loc[~dist_info.concept.isin(wm_dist_concepts)&~dist_info.concept.isin(lm_dist_concepts)]
    catch_ids = np.random.choice(np.arange(0, len(catch_pool)), ncatch*2, replace=False)
    catch_ids = catch_pool.iloc[catch_ids,].diff_id.to_numpy()
    catch_ids += 9000

    # get all images for encoding
    encoding_ids = np.zeros((all_wm_trials, load))
    encoding_ids[np.arange(all_wm_trials), sample_positions] = wm_encoding
    encoding_ids[encoding_ids == 0] = wm_distractors
    encoding_ids = encoding_ids.astype(int)
    encoding_files = np.array([get_file_path(i) for i in encoding_ids.flatten()])
    encoding_files = encoding_files.reshape(encoding_ids.shape)

    # positions start at 1
    sample_positions += 1 

    # block ids 
    wm_block_ids = np.ones(wm_trials).astype(int)
    wm_block_ids[wm_trials//2:] = 2
    wm_block_ids = np.concatenate([np.repeat(nan, practice_trials), wm_block_ids])
    
    # trial type = practice/wm
    wm_trial_type = ["practice"]*practice_trials + ["wm"]*wm_trials

    # assemble together
    wm_trial_data = dict(
        trial_id = np.arange(all_wm_trials), 
        wm_id = wm_ids.astype(int),
        wm_sample_file = wm_sample_files,
        sample_position = sample_positions,
        recognition_theta = recognition_thetas,
        wm_block_id = wm_block_ids, 
        trial_type = wm_trial_type,
        n_encoding = load
    )
    
    for i in range(load):
        wm_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })

    # conditions and condition codes 
    conditions = ["mixed", "semantic", "visual"]
    condition_codes = {i+1: k for i,k in enumerate(conditions)}
    num_conditions = len(conditions)
    assert wm_trials%num_conditions == 0, f"Number of wm trials must be divisible by {num_conditions}"
    
    if subject_number%len(conditions)!=0:
        print("Subject number will be higher due to latin square randomization")

    # randomize wm condition across trials
    wm_repeats = wm_trials//num_conditions
    wm_conditions = np.array(list(condition_codes.keys()) * wm_repeats)
    wm_random_idx = np.random.permutation(np.arange(wm_trials))
    wm_conditions_random = wm_conditions[wm_random_idx]
    practice_conditions = np.random.permutation(list(condition_codes.keys()) * (practice_trials//num_conditions))
    wm_conditions_random = np.concatenate([practice_conditions, wm_conditions_random])

    # randomize encoding time
    long_encoding = np.zeros(wm_trials)
    long_encoding[wm_trials//2:] = 1
    long_encoding = long_encoding[wm_random_idx]
    practice_long_encoding = np.random.permutation([0,1]* (practice_trials//2))

    long_encoding = np.concatenate([practice_long_encoding, long_encoding])
    wm_trial_data.update(long_encoding = long_encoding.astype(int))
    
    # left right randomization 
    wm_left_target = np.zeros(wm_trials)
    wm_left_target[wm_trials//2:] = 1 
    wm_left_target = np.random.permutation(wm_left_target)
    practice_left_target = np.random.permutation([0,1]*(practice_trials//2))

    wm_left_target = np.concatenate([practice_left_target, wm_left_target])
    wm_left_target = wm_left_target.astype(int)
    wm_trial_data.update(left_target = wm_left_target)

    # lm stimuli
    lm_ids = wm_ids[practice_trials::]
    
    # randomize recognition stimuli
    lm_recognition_target = np.random.permutation(lm_ids+1000)
    lm_recognition_target_files = np.array([get_file_path(i) for i in lm_recognition_target])
    lm_recognition_control = np.random.permutation(lm_distractors)
    lm_recognition_control_files = np.array([get_file_path(i) for i in lm_recognition_control])
    
    # left right randomization for lm
    lm_left_target = np.zeros(lm_trials)
    lm_left_target[lm_trials//2:] = 1 
    lm_left_target = np.random.permutation(lm_left_target)
    lm_correct_response = (lm_left_target==0).astype(int)

    # get encoding trials
    lm_encoding_trial = np.array([np.where(wm_ids==i%1e3)[0][0] for i in lm_recognition_target])
    lm_long_encoding = np.array([long_encoding[t] for t in lm_encoding_trial])

    # assemble lm data
    lm_trial_data = dict(
        trial_id = np.arange(lm_trials), 
        recognition_id = lm_recognition_target.astype(int),
        recognition_file = lm_recognition_target_files,
        encoding_trial = lm_encoding_trial, 
        recognition_control_id = lm_recognition_control.astype(int),
        recognition_control_file = lm_recognition_control_files,
        long_encoding = lm_long_encoding, 
        left_target = lm_left_target,
        lm_correct_response = lm_correct_response,
        trial_type = "lm"
    )

    ## latin square randomization of conditions
    for i in range(num_conditions):  
        subject_id = counter+1   
        session_id = f"M-{wave_id}-{subject_id:03d}"       
       
        # working memory
        latin_conditions = wm_conditions_random % num_conditions + 1
        wm_conditions_random = wm_conditions_random + 1
        latin_condition_names = [condition_codes[i] for i in latin_conditions]
 
        #conditions: 1 -> (4,3), 2 -> (4,5), 3 -> (3,5)
        target_codes = (latin_conditions < 3).astype(int) + 3
        control_codes = (latin_conditions > 1).astype(int) * 2 + 3
        
        # target is correct if control image is 5
        target_correct = (control_codes == 5).astype(int)
        
        # assign correct response
        wm_correct_response = (wm_left_target==0).astype(int)
        wm_correct_response[control_codes != 5] = nan

        wm_recognition_target = wm_ids + target_codes * 1000
        wm_recognition_target_files = np.array([get_file_path(i) for i in wm_recognition_target.flatten()])

        wm_recognition_control = wm_ids + control_codes * 1000
        wm_recognition_control_files = np.array([get_file_path(i) for i in wm_recognition_control.flatten()])
        
        wm_trial_data.update(
            subject_id = subject_id,
            session_id = session_id,
            recognition_target_id = wm_recognition_target.astype(int),
            recognition_target_file = wm_recognition_target_files,
            recognition_control_id = wm_recognition_control.astype(int),
            recognition_control_file = wm_recognition_control_files,
            condition = latin_conditions,
            condition_name = latin_condition_names,
            target_correct = target_correct, 
            correct_response = wm_correct_response
        )   

        # update lm (encoding) condition 
        lm_conditions = np.array([latin_conditions[t] for t in lm_encoding_trial])
        lm_condition_names = np.array([latin_condition_names[t] for t in lm_encoding_trial])
        lm_trial_data.update(
            condition = lm_conditions,
            condition_name = lm_condition_names
        ) 

        # save 
        wm_trial_df = pd.DataFrame(wm_trial_data)
        wm_json_data = wm_trial_df.to_dict(orient='records')
        lm_trial_df = pd.DataFrame(lm_trial_data)    
        lm_json_data = lm_trial_df.to_dict(orient='records')
        
        # insert catch trials, this has to be done reverse order os the indexed don't get shifted
        catch_positions, catch_json_data = generate_catch_trials(ncatch, catch_ids)
        for p, catch_trial in zip(reversed(catch_positions), reversed(catch_json_data)):
            wm_json_data.insert(p,catch_trial)
        
        # combine wm and lm data
        combined_json_data = wm_json_data + lm_json_data
        combined_file_path = os.path.join(out_dir, f"input_{session_id}.json")
               
        with open(combined_file_path, 'w') as combined_file:
            json.dump(combined_json_data, combined_file, indent=4)

        counter += 1
        
        
    
            
