import numpy as np
import pandas as pd
import os
import glob
import json

start_id = 1 # if subject id is already given away
subject_number = 50
practice_trials = 12

wm_trials = 160 
all_wm_trials = wm_trials + practice_trials
lm_trials = 260
ncatch = 8

out_dir = f"input_data/"
load = 4 

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

def generate_catch_trials(ncatch):
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(ncatch)])
    recognition_thetas = encoding_thetas[:,0]

    encoding_ids = np.vstack([np.random.choice(np.arange(1,500), load,replace=False)+9000 for _ in range(ncatch)])
    encoding_files = np.array([get_file_path(i) for i in encoding_ids.flatten()])
    encoding_files = encoding_files.reshape(encoding_ids.shape)
    
    catch_trial_data = dict(
        wm_id = 9999,
        condition = 9999,
        trial_id = np.arange(ncatch), 
        sample_position = 1,
        recognition_theta = recognition_thetas,
        trial_type = "catch",
        recognition_control_file = encoding_files[:,0],
        recognition_lure_file = encoding_files[:,0][::-1],
        long_encoding = np.ones(ncatch),
        left_lure = np.random.choice([0,1], ncatch, replace=True).astype(int),
        wm_block_id = np.repeat([1,2], int(ncatch/2))
    )

    for i in range(load):
        catch_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })

    catch_trial_df = pd.DataFrame(catch_trial_data)
    catch_json_data = catch_trial_df.to_dict(orient='records')
    catch_positions = np.linspace(practice_trials+10, wm_trials-20, ncatch).astype(int)

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
    sample_positions = np.array([np.random.choice(np.arange(load), 1, replace=False)[0] for _ in range(all_wm_trials)])

    # generate angles
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(all_wm_trials)])
    recognition_thetas = encoding_thetas[np.arange(all_wm_trials), sample_positions].flatten()

    # randomize distractors (Attention: avoid trials with several distractors from the same category )
    total_images = all_wm_trials * load
    wm_distractors = np.arange(total_images - all_wm_trials) + 1
    wm_distractors = [np.random.permutation(wm_distractors[i::5]) for i in np.random.permutation(range(5))]
    wm_distractors = np.concat(wm_distractors).flatten() + 9000

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
    wm_block_ids = np.concatenate([np.repeat(9999, practice_trials), wm_block_ids])
    
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
    )
    
    for i in range(load):
        wm_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })

    # conditions and condition codes 
    conditions = ["a_semantic", "a_visual", "b_visual", "b_semantic"]
    condition_codes = {k: i+1 for i,k in enumerate(conditions)}
    num_conditions = len(conditions)
    assert wm_trials%num_conditions == 0, f"Number of wm trials must be divisible by {num_conditions}"
    
    # randomize wm condition across trials
    wm_repeats = wm_trials//num_conditions
    wm_conditions = np.array(list(condition_codes.values()) * wm_repeats)
    wm_random_idx = np.random.permutation(np.arange(wm_trials))
    wm_conditions_random = wm_conditions[wm_random_idx]
    practice_conditions = np.random.permutation(list(condition_codes.values()) * (practice_trials//num_conditions))
    wm_conditions_random = np.concatenate([practice_conditions, wm_conditions_random])

    # randomize encoding time
    long_encoding = np.zeros(wm_trials)
    long_encoding[wm_trials//2:] = 1
    long_encoding = long_encoding[wm_random_idx]
    practice_long_encoding = np.random.permutation([0,1]* (practice_trials//2))

    long_encoding = np.concatenate([practice_long_encoding, long_encoding])
    wm_trial_data.update(long_encoding = long_encoding.astype(int))
    
    # left right randomization 
    wm_left_lure = np.zeros(wm_trials)
    wm_left_lure[wm_trials//2:] = 1 
    wm_left_lure = np.random.permutation(wm_left_lure)
    practice_left_lure = np.random.permutation([0,1]*(practice_trials//2))

    wm_left_lure = np.concatenate([practice_left_lure, wm_left_lure])
    wm_trial_data.update(left_lure = wm_left_lure.astype(int))

    # lm stimuli
    lm_distractors = np.random.choice(np.arange(total_images-all_wm_trials + 3, 722, 2), 
                                      lm_trials-wm_trials, replace=False)
    lm_distractors += 9000
    lm_ids = wm_ids[practice_trials::]
    
    # randomize recognition stimuli
    lm_recognition = np.concatenate([lm_ids + 1000, lm_distractors])
    lm_recognition = np.random.permutation(lm_recognition)
    lm_recognition_files = np.array([get_file_path(i) for i in lm_recognition])
    
    # get old trials and encoding trials
    old = (lm_recognition<9000).astype(int)
    encoding_trial = np.array([np.where(wm_ids==i%1e3)[0][0] if i < 9000 else 9999 for i in lm_recognition])

    # assemble ltm data
    lm_trial_data = dict(
        trial_id = np.arange(lm_trials), 
        recognition_id = lm_recognition,
        recognition_file = lm_recognition_files,
        old = old,
        encoding_trial = encoding_trial, 
        trial_type = "lm"
    )

    # catch trials
    catch_positions, catch_json_data = generate_catch_trials(ncatch)

    ## latin square randomization of conditions
    for i in range(num_conditions):  
        subject_id = counter + start_id       
        
        # working memory
        latin_wm_codes = wm_conditions_random % num_conditions + 1
        wm_conditions_random = wm_conditions_random + 1
 
        lure_codes = (latin_wm_codes < 3).astype(int) + 3
        control_codes = (latin_wm_codes % 2).astype(int) * 3 + 2

        wm_recognition_lure = wm_ids + lure_codes * 1000
        wm_recognition_lure_files = np.array([get_file_path(i) for i in wm_recognition_lure.flatten()])

        wm_recognition_control = wm_ids + control_codes * 1000
        wm_recognition_control_files = np.array([get_file_path(i) for i in wm_recognition_control.flatten()])
        
        wm_trial_data.update(
            recognition_lure_id = wm_recognition_lure.astype(int),
            recognition_lure_file = wm_recognition_lure_files,
            recognition_control_id = wm_recognition_control.astype(int),
            recognition_control_file = wm_recognition_control_files,
            condition = latin_wm_codes,
            subject_id = subject_id,
        )   

        # save 
        wm_trial_df = pd.DataFrame(wm_trial_data)
        wm_json_data = wm_trial_df.to_dict(orient='records')
        lm_trial_df = pd.DataFrame(lm_trial_data)    
        lm_json_data = lm_trial_df.to_dict(orient='records')
        
        # insert catch trials
        for p, catch_trial in zip(catch_positions, catch_json_data):
            wm_json_data.insert(p,catch_trial)
        
        # combine wm and lm data
        combined_json_data = wm_json_data + lm_json_data
        combined_file_path = os.path.join(out_dir, f"input_subject_{subject_id:03d}.json")
        with open(combined_file_path, 'w') as combined_file:
            json.dump(combined_json_data, combined_file, indent=4)

        counter += 1
        
        
    
            
