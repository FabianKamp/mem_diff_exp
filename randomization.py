import numpy as np
import pandas as pd
import os
import glob

load_condition = "low-load"
response_format = "2afc"
version = "_".join([load_condition, response_format])

# TODO change the number of trials back to the original values
subject_number = 20
wm_trials = 120 #48 # or 120
lm_trials = 54 # 24 # or 54 # or 56

out_dir = f"input_data/{version}/"
load = 5 if load_condition != "high-load" else 7

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

# randomization
nan = 9999
counter = 1

while counter < subject_number:    
    # randomize images ids for wm and lm
    wm_ids = np.random.permutation(np.arange(wm_trials) +   1)
    lm_ids = np.random.permutation(np.arange(lm_trials) + 201) # lm items have index over 200

    wm_encoding = wm_ids + 1000
    lm_encoding = lm_ids + 1000
    
    # randomize lm trials during wm block
    lm_encoding_trials = np.random.choice(np.arange(wm_trials), size=lm_trials, replace=False)
    lm_ids_long = np.zeros(wm_trials) + nan
    lm_ids_long[lm_encoding_trials] = lm_ids

    # randomize sequential positions
    seq_positions = np.vstack([np.random.choice(np.arange(load), 2, replace=False) for _ in range(wm_trials)])
    wm_positions, lm_positions = seq_positions[:,0], seq_positions[:,1]
    lm_positions[lm_ids_long==nan] = nan

    # generate angles
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(wm_trials)])
    recognition_thetas = encoding_thetas[np.arange(wm_trials), wm_positions].flatten()

    # randomize distractors
    total_images = wm_trials * load
    random_distractors = np.arange(total_images - wm_trials - lm_trials) + 1
    random_distractors = [np.random.permutation(random_distractors[i::5]) for i in np.random.permutation(range(5))]
    random_distractors = np.concat(random_distractors).flatten() + 9000

    # assemble encoding images
    encoding_ids = np.zeros((wm_trials, load))
    encoding_ids[np.arange(wm_trials), wm_positions] = wm_encoding
    encoding_ids[lm_encoding_trials, lm_positions[lm_encoding_trials]] = lm_encoding
    encoding_ids[encoding_ids == 0] = random_distractors
    encoding_ids = encoding_ids.astype(int)

    encoding_files = np.array([get_file_path(i) for i in encoding_ids.flatten()])
    encoding_files = encoding_files.reshape(encoding_ids.shape)

    # positions start at 1
    wm_positions += 1 
    lm_positions[lm_positions!=9999] += 1 

    # block ids 
    wm_block_ids = np.ones(wm_trials).astype(int)
    wm_block_ids[wm_trials//2:] = 2
    lm_block_ids = np.ones(lm_trials).astype(int)
    lm_block_ids[lm_encoding_trials>=wm_trials//2] = 2

    # assemble together
    wm_trial_data = dict(
        wm_trial_id = np.arange(wm_trials), 
        wm_id = wm_ids.astype(int),
        wm_position = wm_positions,
        lm_id = lm_ids_long.astype(int),
        lm_position = lm_positions, 
        recognition_theta = recognition_thetas,
        wm_block_id = wm_block_ids,
    )
    
    for i in range(load):
        wm_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })
    
    # lm trial data
    lm_encoding_files = np.array([get_file_path(i) for i in lm_encoding.flatten()])
    lm_encoding_files = lm_encoding_files.reshape(lm_encoding_files.shape)
    
    lm_trial_data = dict(
        lm_trial_id = np.arange(lm_trials), 
        lm_id = lm_ids,
        lm_encoding_file = lm_encoding_files,
        encoding_trial_id = lm_encoding_trials,
        lm_block_id = lm_block_ids,
    )

    ## latin square randomization of conditions/recognition images
    # conditions and condition codes 
    
    if response_format == "2afc": 
        conditions = ["control", "semantic", "perceptual"]
    else: 
        conditions = ["same", "control", "semantic", "perceptual"]
    
    condition_codes = {k: i+1 for i,k in enumerate(conditions)}
    
    num_conditions = len(conditions)
    assert wm_trials%num_conditions == 0, f"Number of wm trials must be divisible by {num_conditions}"
    assert lm_trials%num_conditions == 0, f"Number of lm trials must be divisible by {num_conditions}"
    
    # randomize wm condition across trials
    wm_repeats = wm_trials//num_conditions
    wm_conditions = list(condition_codes.values()) * wm_repeats
    wm_conditions_random = np.random.permutation(wm_conditions)
    
    # randomize lm conditions across images
    lm_repeats = lm_trials//num_conditions
    lm_conditions = list(condition_codes.values()) * lm_repeats
    lm_conditions_random = np.random.permutation(lm_conditions)

    # left right randomization for 2afc
    if response_format == "2afc": 
        wm_left_correct = np.zeros(wm_trials)
        wm_left_correct[wm_trials//2:] = 1 
        wm_left_correct = np.random.permutation(wm_left_correct)
        wm_trial_data.update(left_correct = wm_left_correct.astype(int))

        lm_left_correct = np.zeros(lm_trials)
        lm_left_correct[lm_trials//2:] = 1 
        lm_left_correct = np.random.permutation(lm_left_correct)
        lm_trial_data.update(left_correct = lm_left_correct.astype(int))


    ## latin square randomization of conditions
    for i in range(num_conditions):  
        subject_id = counter       
        
        # working memory
        latin_wm_codes = wm_conditions_random % num_conditions + 1
        wm_conditions_random = wm_conditions_random + 1
        
        if response_format == "2afc": 
            latin_wm_codes += 1
        
        wm_recognition = wm_ids + latin_wm_codes * 1000
        wm_recognition_files = np.array([get_file_path(i) for i in wm_recognition.flatten()])
        wm_recognition_files = wm_recognition_files.reshape(wm_recognition_files.shape)
        
        wm_trial_data.update(
            wm_recognition = wm_recognition.astype(int),
            wm_condition = (wm_recognition/1e3).astype(int),
            wm_recognition_file = wm_recognition_files,
            subject_id = subject_id,
            trial_type = "wm",
            version = version,
        )   

        # long term memory
        latin_lm_codes = lm_conditions_random % num_conditions + 1
        lm_conditions_random = lm_conditions_random + 1
        
        if response_format == "2afc": 
            latin_lm_codes += 1

        lm_recognition = lm_ids + latin_lm_codes * 1000
        lm_recognition_files = np.array([get_file_path(i) for i in lm_recognition.flatten()])
        lm_recognition_files = lm_recognition_files.reshape(lm_recognition_files.shape) 

        lm_trial_data.update( 
            lm_recognition = lm_recognition.astype(int), 
            lm_condition = (lm_recognition/1e3).astype(int), 
            lm_recognition_file = lm_recognition_files,
            subject_id = subject_id,
            trial_type = "lm", 
            version = version,
        )

        # save 
        wm_trial_df = pd.DataFrame(wm_trial_data)
        lm_trial_df = pd.DataFrame(lm_trial_data)    
        
        wm_json = wm_trial_df.to_json(orient='records', indent=4)
        wm_file_path = os.path.join(out_dir, f"wm_input_subject_{subject_id:03d}.json")
        with open(wm_file_path, 'w') as wm_file:
            wm_file.write(wm_json)
    
        lm_json = lm_trial_df.to_json(orient='records', indent=4)
        lm_file_path = os.path.join(out_dir, f"lm_input_subject_{subject_id:03d}.json")
        with open(lm_file_path, 'w') as lm_file:
            lm_file.write(lm_json)

        counter += 1
        
        
    
            
