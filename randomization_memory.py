import numpy as np
import pandas as pd
import os
import glob
import json
import shutil
from generate_token import generate_token

# set seed
np.random.seed(42) 

# load settings
setting_file = "experimentSettings.json"
with open(setting_file, "r") as file: 
    settings = json.load(file)

# ids
wave_id = settings["wave"]["wave_id"]
assert wave_id.startswith("M"), "Version ID has to be M"
subject_number = settings["wave"]["subject_number"]

# output path
out_dir = f"input_data/{wave_id}"
if os.path.exists(out_dir):
    k = input(f"Overwrite {out_dir} [y/n]?");
    if k!="y": raise(FileExistsError("Outdir exists. Delete before regenerating input data."))
    shutil.rmtree(out_dir)
os.mkdir(out_dir)

# save snapshot of the experimental settings
snapshot_path = os.path.join(out_dir, "settings.json")
with open(snapshot_path, "w") as file: 
    json.dump(settings, file, indent=4)

# trial numbers
practice_trials = settings["memory_experiment"]["practice_trials"]
wm_trials = settings["memory_experiment"]["wm_trials"]
lm_trials = settings["memory_experiment"]["lm_trials"]
ncatch = settings["memory_experiment"]["ncatch"]

exp_stimuli_dir = settings["stimuli"]["exp_stimuli_dir"]
dist_stimuli_dir = settings["stimuli"]["dist_stimuli_dir"]

num_blocks = 3
all_wm_trials = wm_trials + practice_trials

# weightings for sequential presentation
position_weights = settings["memory_experiment"]["position_weights"]

# load and encoding time 
load = settings["memory_experiment"]["load"]
encoding_time_short = settings["timing"]["encoding_time_short"]
encoding_time_long = settings["timing"]["encoding_time_long"]
encoding_time_catch = settings["timing"]["encoding_time_catch"]

# checks
if not os.path.exists(out_dir): 
    os.mkdir(out_dir)

def get_image_paths(): 
    exp_image_paths = [os.path.join("stimuli", i.split("stimuli/", 1)[-1]) 
                       for i in glob.glob(os.path.join(exp_stimuli_dir, "**", "*.jpg"))]
    dist_image_paths = [os.path.join("stimuli", i.split("stimuli/", 1)[-1]) 
                       for i in glob.glob(os.path.join(dist_stimuli_dir, "**", "*.jpg"))]
    image_paths = exp_image_paths + dist_image_paths
    image_id = [int(i.split("/")[-1].rstrip(".jpg")) for i in image_paths]
    image_paths = pd.DataFrame(dict(image_id=image_id, image_path=image_paths)).sort_values(by="image_id")
    return image_paths
image_paths = get_image_paths()

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

def generate_catch_trials(catch_ids):   
    ncatch = len(catch_ids)
    encoding_thetas = np.random.rand(ncatch) * (np.pi * 2) 

    encoding_ids = np.random.permutation(catch_ids)
    encoding_files = np.array([get_file_path(i) for i in encoding_ids])
    
    control_ids = [np.random.choice([c for c in encoding_ids if (c<=e-3) | (c>=e+3)]) 
                   for e in encoding_ids]
    recognition_control_files = np.array([get_file_path(i) for i in control_ids])

    left_target = np.random.choice([0,1], ncatch, replace=True).astype(int)
    correct_response = (left_target==0).astype(int)

    n_per_block = ncatch // num_blocks
    catch_block_ids = np.repeat(np.arange(num_blocks)+1, [n_per_block, n_per_block, ncatch - 2*n_per_block])

    catch_trial_data = dict(
        wm_id = nan,
        condition = nan,
        sample_position = 1,
        recognition_theta = encoding_thetas,
        trial_type = "catch",
        recognition_control_file = recognition_control_files,
        recognition_target_file = encoding_files,
        long_encoding = np.zeros(ncatch),
        left_target = left_target,
        target_correct = np.ones(ncatch),
        correct_response = correct_response,
        wm_block_id = catch_block_ids,
        condition_name = "no_catch", 
        encoding = encoding_ids,
        encoding_file_1 = encoding_files,
        encoding_theta_1 = encoding_thetas,
        encoding_time = encoding_time_catch,
        n_encoding = 1,
        subject_id = subject_id,
    )

    catch_positions = np.linspace(practice_trials+5, wm_trials-5, ncatch).astype(int)
    catch_trial_df = pd.DataFrame(catch_trial_data)
    catch_json_data = catch_trial_df.to_dict(orient='records')

    return catch_positions, catch_json_data


# set up conditions and condition codes 
conditions = ["mixed", "semantic", "visual"]
condition_codes = {i+1: k for i,k in enumerate(conditions)}
num_conditions = len(conditions)
assert wm_trials%(num_conditions*2) == 0, f"Number of wm trials must be divisible by {num_conditions*2}"
if subject_number%len(conditions)!=0:
    print("Subject number will be higher due to latin square randomization")

# randomization
nan = 9999
counter = 0
while counter < subject_number:    
    # randomize images ids for wm and lm
    wm_ids = np.random.permutation(np.arange(all_wm_trials) + 1)
    wm_encoding = wm_ids + 1000
    wm_sample_files = np.array([get_file_path(i) for i in wm_encoding])

    # randomize wm condition across trials
    wm_random_idx = np.random.permutation(np.arange(wm_trials))
    
    trials_per_condition = wm_trials//num_conditions
    wm_conditions = np.repeat(list(condition_codes.keys()), trials_per_condition)
    wm_conditions_random = wm_conditions[wm_random_idx]
    
    practice_conditions = np.random.permutation(list(condition_codes.keys()) * (practice_trials//num_conditions))
    wm_conditions_random = np.concatenate([practice_conditions, wm_conditions_random])
    
    # randomize sequential position
    assert len(position_weights) == load, "Position weights must match load"
    sample_positions = np.concatenate([np.random.choice(
        np.arange(load), 
        size=trials_per_condition, 
        p=position_weights,
        replace=True
        ) 
        for _ in range(num_conditions)])
    sample_positions = sample_positions[wm_random_idx]

    practice_positions = np.random.choice(
        np.arange(load), 
        size=practice_trials, 
        p=position_weights,
        replace=True
    )
    sample_positions = np.concatenate([practice_positions,sample_positions])

    # generate angles
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(all_wm_trials)])
    recognition_thetas = encoding_thetas[np.arange(all_wm_trials), sample_positions].flatten()

    # randomize distractors 
    # distractor concepts should not overlap between wm and lm
    dist_info = pd.read_csv(os.path.join(dist_stimuli_dir,"image_info.csv"))
    
    # lm 
    lm_trials = wm_trials
    lm_dist_concepts = np.random.choice(dist_info.concept.unique(), lm_trials, replace=False)
    lm_dist_pool = dist_info.loc[dist_info.concept.isin(lm_dist_concepts)]
    lm_distractors = lm_dist_pool.groupby("concept")["diff_id"].first().to_numpy()
    lm_distractors += 9000
    
    # wm
    # Attention: No trials with several distractors from the same category
    all_wm_images = all_wm_trials * load
    wm_dist_pool = dist_info.loc[~dist_info.concept.isin(lm_dist_concepts)]
    wm_dist_idx = np.arange(all_wm_images - all_wm_trials) + 1
    wm_dist_idx = np.concat([np.random.permutation(wm_dist_idx[i::10]) 
                             for i in np.random.permutation(range(10))]).flatten() # ensures distance of 10
    wm_dist_df = wm_dist_pool.iloc[wm_dist_idx,]
    wm_dist_concepts = wm_dist_df.concept.unique()
    wm_distractors = wm_dist_df.diff_id.to_numpy()
    wm_distractors += 9000

    # catch
    catch_pool = dist_info.loc[~dist_info.concept.isin(wm_dist_concepts)&~dist_info.concept.isin(lm_dist_concepts)]
    catch_ids = np.random.choice(np.arange(0, len(catch_pool)), ncatch, replace=True)
    catch_ids = catch_pool.iloc[catch_ids,].diff_id.to_numpy()
    catch_ids += 9000

    # get all images for encoding
    encoding_ids = np.zeros((all_wm_trials, load))
    encoding_ids[np.arange(all_wm_trials), sample_positions] = wm_encoding
    encoding_ids[encoding_ids == 0] = wm_distractors
    encoding_ids = encoding_ids.astype(int)
    encoding_files = np.array([get_file_path(i) for i in encoding_ids.flatten()])
    encoding_files = encoding_files.reshape(encoding_ids.shape)

    # block ids - divide trials into 3 equal blocks
    block_size = wm_trials // num_blocks
    wm_block_ids = np.repeat(np.arange(num_blocks)+1, [block_size, block_size, wm_trials - 2*block_size])
    wm_block_ids = np.concatenate([np.repeat(nan, practice_trials), wm_block_ids])
    
    # trial type = practice/wm
    wm_trial_type = ["practice"]*practice_trials + ["wm"]*wm_trials

    # positions start at 1
    sample_positions += 1 

    # assemble together
    wm_trial_data = dict(
        wm_id = wm_ids.astype(int),
        wm_sample_file = wm_sample_files,
        sample_position = sample_positions,
        recognition_theta = recognition_thetas,
        wm_block_id = wm_block_ids, 
        trial_type = wm_trial_type,
        n_encoding = load, 
    )
    
    for i in range(load):
        wm_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })

    # randomize encoding time
    long_encoding = np.concatenate([
        np.repeat([0,1], trials_per_condition//2)
        for _ in range(num_conditions)
    ])
    long_encoding = long_encoding[wm_random_idx]
    
    practice_long_encoding = np.zeros(practice_trials)
    practice_long_encoding[practice_trials//2:] = 1
    practice_long_encoding = np.random.permutation(practice_long_encoding)

    long_encoding = np.concatenate([practice_long_encoding, long_encoding])
    encoding_times = np.array([encoding_time_long if t==1 else encoding_time_short for t in long_encoding])
    
    wm_trial_data.update(
        long_encoding = long_encoding.astype(int),
        encoding_time = encoding_times.astype(int)
        )
    
    # left right randomization 
    wm_left_target = np.zeros(wm_trials)
    wm_left_target[wm_trials//2:] = 1 
    wm_left_target = np.random.permutation(wm_left_target)
    
    practice_left_target = np.zeros(practice_trials)
    practice_left_target[practice_trials//2:] = 1 
    practice_left_target = np.random.permutation(practice_left_target)

    wm_left_target = np.concatenate([practice_left_target, wm_left_target])
    wm_left_target = wm_left_target.astype(int)
    wm_trial_data.update(left_target = wm_left_target)

    # prepare LM
    # randomize recognition stimuli
    lm_recognition_control = np.random.permutation(lm_distractors)
    lm_recognition_control_files = np.array([get_file_path(i) for i in lm_recognition_control])
    
    # left right randomization for lm
    lm_left_target = np.zeros(lm_trials)
    lm_left_target[lm_trials//2:] = 1 
    lm_left_target = np.random.permutation(lm_left_target)
    lm_correct_response = (lm_left_target==0).astype(int)

    # assemble lm data
    lm_trial_data = dict(
        trial_id = np.arange(lm_trials), 
        recognition_control_id = lm_recognition_control.astype(int),
        recognition_control_file = lm_recognition_control_files,
        left_target = lm_left_target.astype(int),
        correct_response = lm_correct_response,
        trial_type = "lm"
    )

    ## latin square randomization of conditions
    for i in range(num_conditions):  
        subject_id = counter+1         
       
        # latin randomization
        latin_conditions = wm_conditions_random % num_conditions + 1
        wm_conditions_random = wm_conditions_random + 1
        latin_condition_names = np.array([condition_codes[i] for i in latin_conditions])
 
        # Update WM
        # latin_conditions -> (target, control): 1 -> (4,3), 2 -> (4,5), 3 -> (3,5)
        condition_mapping = {
            1: (4, 3),
            2: (4, 5),
            3: (3, 5)
        }
        target_codes = np.array([condition_mapping[c][0] for c in latin_conditions])
        control_codes = np.array([condition_mapping[c][1] for c in latin_conditions])
        
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
            recognition_target_id = wm_recognition_target.astype(int),
            recognition_target_file = wm_recognition_target_files,
            recognition_control_id = wm_recognition_control.astype(int),
            recognition_control_file = wm_recognition_control_files,
            condition = latin_conditions,
            condition_name = latin_condition_names,
            target_correct = target_correct, 
            correct_response = wm_correct_response
        )   

        # update LM       
        # fetch stimuli ids from overt/covert trials
        lm_encoding_trials = np.arange(all_wm_trials)
        lm_encoding_trials_overt = lm_encoding_trials[(lm_encoding_trials>=practice_trials) & (latin_conditions>1)]
        lm_ids_overt = wm_ids[lm_encoding_trials_overt]
        
        lm_encoding_trials_covert = lm_encoding_trials[(lm_encoding_trials>=practice_trials) & (latin_conditions==1)]
        lm_ids_covert = [np.random.choice([img_id for img_id in trial if img_id>=9000], 1, p=[.9,.1]) 
                                    for trial in encoding_ids[lm_encoding_trials_covert]]
        lm_ids_covert = np.array(lm_ids_covert).flatten()
        
        # concat
        lm_ids = np.concat([lm_ids_overt, lm_ids_covert])
        lm_encoding_trials = np.concat([lm_encoding_trials_overt, lm_encoding_trials_covert])
        lm_recognition_target = np.concat([lm_ids_overt + 1000, lm_ids_covert])

        # randomize
        assert len(lm_recognition_target) == lm_trials, "lm trials and encoding trials don't have the same length"
        lm_random_idx = np.random.permutation(np.arange(lm_trials))

        lm_ids = lm_ids[lm_random_idx]
        lm_encoding_trials = lm_encoding_trials[lm_random_idx]
        lm_recognition_target = lm_recognition_target[lm_random_idx]
        lm_recognition_target_files = np.array([get_file_path(i) for i in lm_recognition_target])
        
        lm_conditions = latin_conditions[lm_encoding_trials][lm_random_idx]
        lm_condition_names = latin_condition_names[lm_encoding_trials][lm_random_idx]
        lm_long_encoding = long_encoding[lm_encoding_trials][lm_random_idx]
        
        # get the sequential position during encoding (starts with 1)
        lm_sample_positions = np.array([np.where(encoding_ids==target)[1].item() 
                                        for target in lm_recognition_target])
        lm_sample_positions += 1 

        lm_trial_data.update(
            subject_id = subject_id,
            lm_id = lm_ids,
            recognition_target_id = lm_recognition_target.astype(int),
            recognition_target_file = lm_recognition_target_files,
            condition = lm_conditions,
            condition_name = lm_condition_names, 
            long_encoding = lm_long_encoding,
            sample_position = lm_sample_positions,
            )

        # save 
        wm_trial_df = pd.DataFrame(wm_trial_data)
        wm_json_data = wm_trial_df.to_dict(orient='records')
        lm_trial_df = pd.DataFrame(lm_trial_data)    
        lm_json_data = lm_trial_df.to_dict(orient='records')
        
        # insert catch trials, this has to be done reverse order os the indexed don't get shifted
        catch_positions, catch_json_data = generate_catch_trials(catch_ids)
        for p, catch_trial in zip(reversed(catch_positions), reversed(catch_json_data)):
            wm_json_data.insert(p,catch_trial)
        
        # update wm trial_ids
        _ = [trial_dict.update(trial_id = trial_id) for (trial_id,trial_dict) in enumerate(wm_json_data)]

        # combine wm and lm data
        json_data = wm_json_data + lm_json_data

        # save twice (B -> backup token)
        for backup_code in ["A","B"]:
            # create session id
            session_id = f"{wave_id}-{subject_id:03d}-{backup_code}" 
            _ = [trial_dict.update(session_id = session_id) for trial_dict in json_data]
            
            # save
            file_path = os.path.join(out_dir, f"input_{session_id}.json")
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

        counter += 1

# Generate tokens 
generate_token()
