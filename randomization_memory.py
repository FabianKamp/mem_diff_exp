import numpy as np
import pandas as pd
import os
import glob
import json
import shutil
from generate_token import generate_token

def get_image_paths():
    """Load all experimental and distractor image paths into a DataFrame."""
    exp_image_paths = [os.path.join("stimuli", i.split("stimuli/", 1)[-1])
                       for i in glob.glob(os.path.join(exp_stimuli_dir, "**", "*.jpg"))]
    dist_image_paths = [os.path.join("stimuli", i.split("stimuli/", 1)[-1])
                       for i in glob.glob(os.path.join(dist_stimuli_dir, "**", "*.jpg"))]
    image_paths = exp_image_paths + dist_image_paths
    image_id = [int(i.split("/")[-1].rstrip(".jpg")) for i in image_paths]
    image_paths = pd.DataFrame(dict(image_id=image_id, image_path=image_paths)).sort_values(by="image_id")
    return image_paths

def get_file_path(image_id):
    """Return the file path for a given image ID."""
    file_path = image_paths.loc[image_paths.image_id == image_id, "image_path"]
    return file_path.iloc[0]

def generate_random_angles(n):
    """Generate a list of random angles evenly distributed around a circle."""
    angle_between = np.pi * 2 / n
    random_angles = [np.random.rand() * (np.pi * 2)]
    for _ in range(n-1):
        next_angle = (random_angles[-1] + angle_between) % (np.pi * 2)
        random_angles.append(next_angle)
    random_angles = np.random.permutation(random_angles)
    random_angles = np.round(random_angles).astype(int)
    return random_angles

def randomized_set_ids():
    """Generate randomized stimulus set IDs for all encoding trials."""
    set_ids = np.random.permutation(np.arange(all_encoding_trials) + 1)
    return set_ids

def generate_wm_mat():
    """Generate the working memory design matrix with counterbalanced conditions, 
    encoding times, and trial parameters."""
    
    design_mat = []
    for block in range(num_blocks):
        # initialize block mat
        block_mat = np.empty((7,trials_per_block))
        
        # conditions
        block_mat[0,:] = np.repeat(list(condition_codes.keys()), trials_per_stimuli_condition)
        
        # long/short encoding time
        block_mat[1,:] = np.concatenate([np.repeat([0,1], trials_per_condition) for _ in range(n_conditions)])
        
        ## counterbalancing across condition*encoding time
        # 1. wm sample positions
        assert len(position_weights) == load, "Position weights must match load"
        position_repeats = [int(trials_per_condition * weight) for weight in position_weights[:-1]]
        positions = np.repeat(np.arange(load), position_repeats + [trials_per_condition - np.sum(position_repeats)])
        block_mat[2,:] = np.concatenate([np.random.permutation(positions) 
                                         for _ in range(n_conditions_total)])
        
        # lm sample positions
        block_mat[3,:] = np.array([np.random.choice([n for n in [0,1,2] if n != m], p=[.9,.1]) 
                                   for m in block_mat[2,:]])

        # wm left/right randomization
        repeats = [int(trials_per_condition/2), trials_per_condition-int(trials_per_condition/2)]
        target_position = [np.repeat([0,1], repeats[::(-1)**(block+c)]) 
                       for c in range(n_conditions_total)]
        block_mat[4,:] = np.concatenate([np.random.permutation(p) for p in target_position]) 

        # lm left/right randomization
        block_mat[5,:] = np.concatenate([np.random.permutation(p) for p in target_position])
        
        # block id
        block_id = block+1
        block_mat[6,:] = np.repeat(block_id, trials_per_block)

        # randomize order 
        random_trial_idx = np.random.permutation(np.arange(trials_per_block))
        block_mat = block_mat[:, random_trial_idx]
        design_mat.append(block_mat.copy())

    design_mat = np.hstack(design_mat)
    encoding_trial_id = np.arange(design_mat.shape[1]).reshape(1,-1)
    design_mat = np.vstack([encoding_trial_id, design_mat]) 
    design_mat = design_mat.astype(int)
    
    row_names = [
        "encoding_trial_id",
        "condition",
        "long_encoding",
        "wm_sample_position",
        "lm_sample_position",
        "wm_left_target",
        "lm_left_target",
        "wm_block_id",
    ]
    design_mat = pd.DataFrame(design_mat, index=row_names)
    
    return design_mat

def generate_practice_mat():
    """Generate the practice trial design matrix with hard-coded trial parameters."""
    practice_mat = np.vstack([
        np.repeat(nan,3),
        np.array([3,2,1]), 
        np.array([0,1,0]),  
        np.array([2,1,0]),
        np.repeat(nan,3),
        np.array([1,1,0]),  
        np.repeat(nan,3),
        np.repeat(nan,3),
    ])
    practice_mat = practice_mat.astype(int)
    row_names = [
        "encoding_trial_id",
        "condition",
        "long_encoding",
        "wm_sample_position",
        "lm_sample_position",
        "wm_left_target",
        "lm_left_target",
        "wm_block_id"
    ]
    practice_mat = pd.DataFrame(practice_mat, index=row_names)
    return practice_mat

def get_distractor_stimuli():
    """Generate non-overlapping distractor stimulus sets for WM, LM, and catch trials."""
    dist_info = pd.read_csv(os.path.join(dist_stimuli_dir, "image_info.csv"))
    
    # lm 
    lm_dist_concepts = np.random.choice(dist_info.concept.unique(), lm_trials, replace=False)
    lm_dist_pool = dist_info.loc[dist_info.concept.isin(lm_dist_concepts)]
    lm_distractors = lm_dist_pool.groupby("concept")["diff_id"].first().to_numpy()
    lm_distractors = np.random.permutation(lm_distractors)
    lm_distractors += 9000
    
    # wm
    # Attention: No trials with several distractors from the same category
    all_wm_images = all_encoding_trials * load
    wm_dist_pool = dist_info.loc[~dist_info.concept.isin(lm_dist_concepts)]
    wm_dist_idx = np.arange(all_wm_images - all_encoding_trials) + 1
    wm_dist_idx = np.concat([np.random.permutation(wm_dist_idx[i::12]) 
                             for i in np.random.permutation(range(12))]).flatten() # ensures distance of 12
    wm_dist_df = wm_dist_pool.iloc[wm_dist_idx,]
    wm_dist_concepts = wm_dist_df.concept.unique()
    wm_distractors = wm_dist_df.diff_id.to_numpy()
    wm_distractors += 9000

    # catch
    catch_pool = dist_info.loc[~dist_info.concept.isin(wm_dist_concepts)&~dist_info.concept.isin(lm_dist_concepts)]
    catch_ids = np.random.choice(np.arange(0, len(catch_pool)), ncatch, replace=True)
    catch_ids = catch_pool.iloc[catch_ids,].diff_id.to_numpy()
    catch_ids += 9000

    distractors = dict(
        wm = wm_distractors,
        lm = lm_distractors,
        catch = catch_ids
    )
    return distractors

def generate_encoding_id_mat():
    """Create encoding matrix with target stimuli at sample positions and distractors at remaining positions."""
    encoding_ids = np.zeros((all_encoding_trials, load))
    encoding_ids[np.arange(all_encoding_trials), design_mat.loc["wm_sample_position",:]] = set_ids + 1000
    encoding_ids[encoding_ids == 0] = distractors["wm"]
    encoding_ids = encoding_ids.astype(int)
    return encoding_ids

def map_conditions2stimuli(conditions):
    """Map experimental conditions to target and foil stimulus codes for recognition trials."""
    condition_mapping = {
        1: (4, 3),
        2: (4, 5),
        3: (3, 5)
    }
    target_codes = np.array([condition_mapping[c][0] for c in conditions])
    foil_codes = np.array([condition_mapping[c][1] for c in conditions])
    return target_codes, foil_codes

def assemble_wm_trial_data():
    """Assemble complete working memory trial data including encoding, recognition, and response parameters."""
    wm_sample_files = np.array([get_file_path(i) for i in  set_ids + 1000])
    encoding_files = np.array([get_file_path(i) for i in encoding_ids.flatten()])
    encoding_files = encoding_files.reshape(encoding_ids.shape)

    # recognition
    # get ids and files
    target_codes, foil_codes = map_conditions2stimuli(design_mat.loc["condition",:])
    wm_recognition_target = set_ids + target_codes * 1e3
    wm_recognition_target_files = np.array([get_file_path(i) for i in wm_recognition_target.flatten()])
    wm_recognition_foil = set_ids + foil_codes * 1e3
    wm_recognition_foil_files = np.array([get_file_path(i) for i in wm_recognition_foil.flatten()])

    # assign correct response (mixed condition --> both options are correct)
    target_correct = (design_mat.loc["condition",:] != 1).astype(int)
    wm_correct_response = (design_mat.loc["wm_left_target",:]==0).astype(int)
    wm_correct_response[design_mat.loc["condition",:] == 1] = nan

    # display
    # generate angles 
    encoding_thetas = np.vstack([generate_random_angles(load) for _ in range(all_encoding_trials)])
    recognition_thetas = encoding_thetas[np.arange(all_encoding_trials), design_mat.loc["wm_sample_position",:]].flatten()
    
    # data dict --> wmTask.js
    wm_trial_data = dict(
        trial_type = np.repeat(["practice", "wm"], repeats=[practice_trials, wm_trials]),
        subject_id = subject_id,
        encoding_trial_id = design_mat.loc["encoding_trial_id"],
        wm_block_id = design_mat.loc["wm_block_id"], 
        n_encoding = load, 
        set_id = set_ids.astype(int),
        sample_file = wm_sample_files,
        sample_position = design_mat.loc["wm_sample_position",:].to_numpy() + 1,
        long_encoding = design_mat.loc["long_encoding"].to_numpy(),
        encoding_time = np.where(design_mat.loc["long_encoding"]==1, 
                                 encoding_time_long, 
                                 encoding_time_short).astype(int),
        condition = design_mat.loc["condition"].to_numpy(),
        condition_name = np.array([condition_codes[i] for i in design_mat.loc["condition"]]),
        recognition_theta = recognition_thetas,
        recognition_target_id = wm_recognition_target.astype(int),
        recognition_target_file = wm_recognition_target_files,
        recognition_foil_id = wm_recognition_foil.astype(int),
        recognition_foil_file = wm_recognition_foil_files,
        left_target = design_mat.loc["wm_left_target"].to_numpy(),
        target_correct = target_correct, 
        correct_response = wm_correct_response
    )

    for i in range(load):
        wm_trial_data.update({
            f"encoding_{i+1}": encoding_ids[:,i],
            f"encoding_file_{i+1}": encoding_files[:,i],
            f"encoding_theta_{i+1}": encoding_thetas[:,i],
        })
    
    wm_trial_data = pd.DataFrame(wm_trial_data)
    wm_trial_data = wm_trial_data.to_dict(orient='records')

    return wm_trial_data

def insert_catch_trials():
    """Generate catch trial data and insert them at evenly-spaced positions into the WM trial sequence."""
    catch_ids = distractors["catch"]
    ncatch = len(catch_ids)
    
    # encoding/recognition slides
    encoding_ids = np.random.permutation(catch_ids)
    encoding_files = np.array([get_file_path(i) for i in encoding_ids])    
    recognition_foil_ids = [np.random.choice([c for c in encoding_ids if (c<=e-3) | (c>=e+3)]) 
                for e in encoding_ids]
    recognition_foil_files = np.array([get_file_path(i) for i in recognition_foil_ids])

    # display angle
    encoding_thetas = np.random.rand(ncatch) * (np.pi * 2) 
    
    # left/right
    left_target = np.random.choice([0,1], ncatch, replace=True).astype(int)
    correct_response = (left_target==0).astype(int)

    # block ids
    n_per_block = ncatch // num_blocks
    catch_block_ids = np.repeat(np.arange(num_blocks)+1, [n_per_block, n_per_block, ncatch - 2*n_per_block])

    # assemble
    catch_trial_data = dict(
        subject_id = subject_id,
        encoding_trial_id = np.repeat(nan,ncatch),
        set_id = np.repeat(nan,ncatch),
        wm_block_id = catch_block_ids,
        n_encoding = 1,
        wm_sample_position = 1,
        trial_type = "catch",
        encoding_time = encoding_time_catch,
        condition = nan,
        condition_name = "no_catch", 
        long_encoding = np.zeros(ncatch),
        recognition_theta = encoding_thetas,
        recognition_target_id = nan,
        recognition_target_file = encoding_files,
        recognition_foil_id = recognition_foil_ids,
        recognition_foil_file = recognition_foil_files,
        left_target = left_target,
        target_correct = np.ones(ncatch),
        correct_response = correct_response,
        encoding_1 = encoding_ids,
        encoding_file_1 = encoding_files,
        encoding_theta_1 = encoding_thetas,
    )
    catch_trial_data = pd.DataFrame(catch_trial_data)
    catch_trial_data = catch_trial_data.to_dict(orient='records')

    ## insert the catch trials into the wm_trial_data
    # in reverse order --> index doesn't shift
    catch_positions = np.linspace(practice_trials+5, wm_trials-5, ncatch).astype(int)
    for p, catch_trial in zip(reversed(catch_positions), reversed(catch_trial_data)):
        wm_trial_data.insert(p,catch_trial)

    return wm_trial_data

def get_lm_target_ids():
    """Identify long memory target stimuli from cued and uncued WM encoding trials."""
    cued_trials = np.where((wm_mat.loc["condition"] != 1) & (wm_mat.loc["wm_block_id"] < 3))[0]
    lm_ids_cued = encoding_ids[cued_trials, wm_mat.loc["lm_sample_position", cued_trials]]
    
    uncued_trials = np.where((wm_mat.loc["condition"] == 1) & (wm_mat.loc["wm_block_id"] < 3))[0]
    lm_ids_uncued = encoding_ids[uncued_trials, wm_mat.loc["lm_sample_position", uncued_trials]]
    
    lm_encoding_trials = np.concat([cued_trials, uncued_trials])
    lm_recognition_target = np.concat([lm_ids_cued, lm_ids_uncued])

    return lm_encoding_trials, lm_recognition_target

def assemble_lm_trial_data():
    """Assemble randomized long memory trial data with target and foil stimuli."""
    lm_encoding_trials_random = lm_encoding_trials[lm_random_idx]
    lm_recognition_target_random = lm_recognition_target[lm_random_idx]
    set_ids = np.array([s if s < 9000 else nan for s in lm_recognition_target_random]).astype(int)
    lm_recognition_target_files = np.array([get_file_path(i) for i in lm_recognition_target_random])

    lm_left_target = wm_mat.loc["lm_left_target",lm_encoding_trials_random]
    lm_correct_response = (lm_left_target==0).astype(int)
    
    # get the sequential position during encoding (starts with 1)
    lm_sample_positions = wm_mat.loc["lm_sample_position",lm_encoding_trials_random]
    lm_sample_positions += 1

    # assemble lm data
    lm_trial_data = dict(
        trial_type = "lm",
        subject_id = subject_id,
        trial_id = np.arange(lm_trials), 
        encoding_trial_id = lm_encoding_trials_random,
        set_id = set_ids,
        sample_position = lm_sample_positions,
        long_encoding = wm_mat.loc["long_encoding",lm_encoding_trials_random],
        encoding_time = np.where(wm_mat.loc["long_encoding",lm_encoding_trials_random], 
                            encoding_time_long, 
                            encoding_time_short).astype(int),
        condition = wm_mat.loc["condition",lm_encoding_trials_random],
        condition_name = np.array([condition_codes[i] for i in wm_mat.loc["condition",lm_encoding_trials_random]]),
        recognition_target_id = lm_recognition_target_random.astype(int),
        recognition_target_file = lm_recognition_target_files,
        recognition_foil_id = distractors["lm"].astype(int),
        recognition_foil_file = np.array([get_file_path(i) for i in distractors["lm"]]),
        left_target = lm_left_target.astype(int),
        correct_response = lm_correct_response,
    )

    lm_trial_data = pd.DataFrame(lm_trial_data)    
    lm_trial_data = lm_trial_data.to_dict(orient='records')

    return lm_trial_data

def save_input_data():
    """Save trial data to JSON files with A/B backup codes and create test session for first subject."""
    for backup_code in ["A","B"]:
        # create session id
        session_id = f"{wave_id}-{subject_id:03d}-{backup_code}" 
        _ = [trial_dict.update(session_id = session_id) for trial_dict in input_data]
        
        # save
        file_path = os.path.join(out_dir, f"input_{session_id}.json")
        with open(file_path, 'w') as file:
            json.dump(input_data, file, indent=4)
        
        # save testing session
        if subject_id == 1: 
            session_id = f"{wave_id}-999-{backup_code}" 
            _ = [trial_dict.update(session_id = session_id) for trial_dict in input_data]
            
            # save
            file_path = os.path.join(out_dir, f"input_{session_id}.json")
            with open(file_path, 'w') as file:
                json.dump(input_data, file, indent=4)
   
if __name__ == "__main__":
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

    # stimuli paths
    exp_stimuli_dir = settings["stimuli"]["exp_stimuli_dir"]
    dist_stimuli_dir = settings["stimuli"]["dist_stimuli_dir"]
    image_paths = get_image_paths()
    
    # trial numbers
    practice_trials = settings["memory_experiment"]["practice_trials"]
    wm_trials = settings["memory_experiment"]["wm_trials"]
    lm_trials = settings["memory_experiment"]["lm_trials"]
    ncatch = settings["memory_experiment"]["ncatch"]

    num_blocks = 3
    all_encoding_trials = wm_trials + practice_trials
    trials_per_block = wm_trials//num_blocks
    assert lm_trials == 2*trials_per_block, "LM trials not twice the WM block length"
   
    # set up conditions and condition codes 
    conditions = ["mixed", "semantic", "visual"]
    condition_codes = {i+1: k for i,k in enumerate(conditions)}
    n_conditions = len(conditions)
    n_conditions_total = n_conditions*2
    assert wm_trials%(n_conditions_total*num_blocks) == 0, f"Number of wm trials must be divisible by {n_conditions_total*num_blocks}"

    trials_per_stimuli_condition = (wm_trials//n_conditions)//num_blocks
    trials_per_condition = trials_per_stimuli_condition//2

    # weightings for sequential presentation
    position_weights = settings["memory_experiment"]["position_weights"]

    # load and encoding time 
    load = settings["memory_experiment"]["load"]
    encoding_time_short = settings["timing"]["encoding_time_short"]
    encoding_time_long = settings["timing"]["encoding_time_long"]
    encoding_time_catch = settings["timing"]["encoding_time_catch"]

    if subject_number%len(conditions)!=0:
        print("Subject number will be higher due to latin square randomization")

    # start randomization
    nan = 9999
    subject_id = 0

    while subject_id < subject_number:    
        # randomize image ids
        set_ids = randomized_set_ids()

        # generate the design mat for wm and practice trials
        wm_mat = generate_wm_mat()
        practice_mat = generate_practice_mat()

        # distractors
        distractors = get_distractor_stimuli()

        # lm randomization (used during lm data assambling)
        lm_random_idx = np.random.permutation(np.arange(lm_trials))

        ## latin square randomization of conditions
        condition_wheel = wm_mat.loc["condition"].to_numpy().copy()

        for i in range(n_conditions):  
            subject_id += 1
            print(f"{wave_id} - Generating input data for {subject_id} .. ")

            # turn the condition wheel
            condition_wheel += 1

            # get current conditions & update the wm mat
            current_conditions = (condition_wheel % n_conditions) + 1
            wm_mat.loc["condition"] = current_conditions

            # assemble trial data for the wm trials
            design_mat = practice_mat.join(wm_mat, lsuffix="_practice") 
            encoding_ids = generate_encoding_id_mat()
            wm_trial_data = assemble_wm_trial_data()

            # insert catch trials
            wm_trial_data = insert_catch_trials()

            # update wm trial_ids
            _ = [trial_dict.update(trial_id = trial_id) for (trial_id, trial_dict) in enumerate(wm_trial_data)]

            # assemble lm
            lm_encoding_trials, lm_recognition_target = get_lm_target_ids()
            lm_trial_data = assemble_lm_trial_data()

            # combine wm and lm data
            input_data = wm_trial_data + lm_trial_data
            save_input_data()

    # Generate tokens 
    generate_token()
