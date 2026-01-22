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

def generate_encoding_thetas(layout_ids):
    """Convert layouts to angles using a triangle layout"""
    layouts = np.array([
        [0,3,5],
        [1,3,6],
        [1,4,7], 
        [2,5,7], 
    ])
    encoding_layouts = layouts[layout_ids]
    encoding_thetas = np.pi * encoding_layouts/4 
    encoding_thetas = np.round(encoding_thetas,4)
    return encoding_thetas

def randomize_set_ids(n_set_ids, excluded_set_ids, practice_set_ids):
    """Generate randomized stimulus set IDs for all encoding trials."""
    assert type(excluded_set_ids) == list, "Type error: excluded_set_ids should be a list."
    assert type(practice_set_ids) == list, "Type error: practice_set_ids should be a list."
    set_ids = np.arange(n_set_ids) + 1
    set_ids = set_ids[~np.isin(set_ids, excluded_set_ids+practice_set_ids)]
    set_ids = np.hstack([
        np.array(practice_set_ids),
        np.random.permutation(set_ids)
        ])
    return set_ids

def generate_wm_mat():
    """Generate the working memory design matrix with counterbalanced conditions, 
    encoding times, and trial parameters."""
    
    # initialize the design mat
    design_mat = []

    for block in range(3):
        n_trials = trials_per_block[block]
        n_conditions = len(a_levels) * len(b_levels)
        trials_per_condition = n_trials//n_conditions
        
        # initialize block mat
        block_mat = np.empty((8,n_trials))
        
        # factor stimulus (a)
        trials_per_a = n_trials//len(a_levels)
        block_mat[0,:] = np.repeat(a_index, trials_per_a)
        
        # factor encoding time (b). Conditions are stimulus X time
        block_mat[1,:] = np.concatenate([np.repeat(b_index, trials_per_condition) for _ in range(len(a_levels))])
        
        ## counterbalancing across condition*encoding time
        # sample positions (spatial)
        wm_position = np.concatenate([np.random.choice(3, trials_per_condition, replace=True) for _ in range(n_conditions)])
        block_mat[2,:] = wm_position        
        
        # lm sample positions
        lm_position = np.array([np.random.choice([n for n in np.arange(load) if n != m]) 
                                   for m in wm_position])
        block_mat[3,:] = lm_position
        
        # wm left/right randomization 
        left_repeats = [int(trials_per_condition/2), trials_per_condition-int(trials_per_condition/2)]
        target_position = [np.repeat([0,1], left_repeats[::(-1)**(block+c)]) for c in range(n_conditions)]
        block_mat[4,:] = np.concatenate([np.random.permutation(p) for p in target_position]) 

        # lm left/right randomization
        block_mat[5,:] = np.concatenate([np.random.permutation(p) for p in target_position])
        
        # block id
        block_id = block+1
        block_mat[6,:] = np.repeat(block_id, n_trials)

        # encoding layout id
        encoding_layout_id = np.concatenate([np.random.choice(4, trials_per_condition, replace=True) for _ in range(n_conditions)])
        block_mat[7,:] = encoding_layout_id

        # randomize order 
        random_trial_idx = np.random.permutation(np.arange(n_trials))
        block_mat = block_mat[:, random_trial_idx]
        design_mat.append(block_mat.copy())

    design_mat = np.hstack(design_mat)

    # stacking encoding_trial_id on top
    encoding_trial_id = np.arange(design_mat.shape[1]).reshape(1,-1)
    design_mat = np.vstack([encoding_trial_id, design_mat]) 
    design_mat = design_mat.astype(int)
    
    # convert to df
    row_names = [
        "encoding_trial_id",
        "stimulus_condition_index",
        "encoding_time_index",
        "wm_sample_position",
        "lm_sample_position",
        "wm_left_target",
        "lm_left_target",
        "wm_block_id",
        "encoding_layout_id",
    ]
    design_mat = pd.DataFrame(design_mat, index=row_names)
    
    return design_mat

def generate_practice_mat():
    """Generate the practice trial design matrix with hard-coded trial parameters."""
    practice_mat = np.vstack([
        np.repeat(nan,3),
        np.array([2,1,0]), 
        np.array([1,0,2]),  
        np.array([2,1,0]),
        np.repeat(nan,3),
        np.array([1,1,0]),  
        np.repeat(nan,3),
        np.repeat(nan,3),
        np.arange(3)
    ])

    practice_mat = practice_mat.astype(int)
    row_names = [
        "encoding_trial_id",
        "stimulus_condition_index",
        "encoding_time_index",
        "wm_sample_position",
        "lm_sample_position",
        "wm_left_target",
        "lm_left_target",
        "wm_block_id",
        "encoding_layout_id",
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
        0: (4, 3),
        1: (4, 5),
        2: (3, 5)
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
    target_codes, foil_codes = map_conditions2stimuli(design_mat.loc["stimulus_condition_index",:])
    wm_recognition_target = set_ids + target_codes * 1e3
    wm_recognition_target_files = np.array([get_file_path(i) for i in wm_recognition_target.flatten()])
    wm_recognition_foil = set_ids + foil_codes * 1e3
    wm_recognition_foil_files = np.array([get_file_path(i) for i in wm_recognition_foil.flatten()])

    # assign correct response (mixed condition --> both options are correct)
    target_correct = (design_mat.loc["stimulus_condition_index",:] != 0).astype(int) # 0 == mixed condition
    wm_correct_response = (design_mat.loc["wm_left_target",:]==0).astype(int)
    wm_correct_response[design_mat.loc["stimulus_condition_index",:] == 0] = nan # 0 == mixed condition

    # display
    # generate angles 
    encoding_thetas = generate_encoding_thetas(design_mat.loc["encoding_layout_id",:])
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
        encoding_time = np.array([b_levels[i] for i in design_mat.loc["encoding_time_index"]]).astype(int),
        condition = design_mat.loc["stimulus_condition_index"].to_numpy(),
        condition_name = np.array([a_levels[i] for i in design_mat.loc["stimulus_condition_index"]]),
        recognition_theta = recognition_thetas,
        recognition_target_id = wm_recognition_target.astype(int),
        recognition_target_file = wm_recognition_target_files,
        recognition_foil_id = wm_recognition_foil.astype(int),
        recognition_foil_file = wm_recognition_foil_files,
        left_target = design_mat.loc["wm_left_target"].to_numpy(),
        target_correct = target_correct, 
        correct_response = wm_correct_response, 
        encoding_layout_id = design_mat.loc["encoding_layout_id",:].to_numpy()
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
    encoding_time_catch = settings["timing"]["encoding_time_catch"]
    # encoding/recognition slides
    encoding_ids = np.random.permutation(catch_ids)
    encoding_files = np.array([get_file_path(i) for i in encoding_ids])    
    recognition_foil_ids = [np.random.choice([c for c in encoding_ids if (c<=e-3) | (c>=e+3)]) 
                for e in encoding_ids]
    recognition_foil_files = np.array([get_file_path(i) for i in recognition_foil_ids])

    # display angle
    catch_thetas = np.round([np.random.choice(8)/4 * np.pi for _ in range(ncatch)], 4)
    
    # left/right
    left_target = np.random.choice([0,1], ncatch, replace=True).astype(int)
    correct_response = (left_target==0).astype(int)

    # catch positions and block ids
    catch_positions = np.linspace(practice_trials+5, wm_trials-5, ncatch).astype(int)
    catch_block_ids = np.digitize(
        catch_positions, 
        bins=[wm_block1_trials, wm_block1_trials+wm_block2_trials]
        ) + 1

    # assemble
    catch_trial_data = dict(
        subject_id = subject_id,
        encoding_trial_id = np.repeat(nan,ncatch),
        set_id = np.repeat(nan,ncatch),
        wm_block_id = catch_block_ids,
        n_encoding = 1,
        sample_position = 1,
        trial_type = "catch",
        encoding_time = encoding_time_catch,
        condition = nan,
        condition_name = "no_catch", 
        recognition_theta = catch_thetas,
        recognition_target_id = nan,
        recognition_target_file = encoding_files,
        recognition_foil_id = recognition_foil_ids,
        recognition_foil_file = recognition_foil_files,
        left_target = left_target,
        target_correct = np.ones(ncatch),
        correct_response = correct_response,
        encoding_1 = encoding_ids,
        encoding_file_1 = encoding_files,
        encoding_theta_1 = catch_thetas,
        encoding_layout_id = nan
    )

    catch_trial_data = pd.DataFrame(catch_trial_data)
    catch_trial_data = catch_trial_data.to_dict(orient='records')

    ## insert the catch trials into the wm_trial_data
    # in reverse order --> index doesn't shift
    for p, catch_trial in zip(reversed(catch_positions), reversed(catch_trial_data)):
        wm_trial_data.insert(p,catch_trial)

    return wm_trial_data

def get_lm_target_ids():
    """Identify long memory target stimuli from cued and uncued WM encoding trials."""

    # mixed trials -> lm_sample != wm_sample
    uncued_trials = np.where((wm_mat.loc["stimulus_condition_index"] == 0) & (wm_mat.loc["wm_block_id"] < 3))[0]
    lm_ids_uncued = encoding_ids[uncued_trials, wm_mat.loc["lm_sample_position", uncued_trials]]

    # other trials -> lm_sample == wm_sample
    cued_trials = np.where((wm_mat.loc["stimulus_condition_index"] != 0) & (wm_mat.loc["wm_block_id"] < 3))[0]
    lm_ids_cued = encoding_ids[cued_trials, wm_mat.loc["wm_sample_position", cued_trials]]

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
        encoding_time = np.array([b_levels[i] for i in wm_mat.loc["encoding_time_index", lm_encoding_trials_random]]
                                  ).astype(int),
        condition = wm_mat.loc["stimulus_condition_index",lm_encoding_trials_random],
        condition_name = np.array([a_levels[i] for i in wm_mat.loc["stimulus_condition_index", lm_encoding_trials_random]]), 
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
    session_id = f"{wave_id}-{subject_id:03d}" 
    _ = [trial_dict.update(session_id = session_id) for trial_dict in input_data]
    
    # save
    file_path = os.path.join(out_dir, f"input_{session_id}.json")
    with open(file_path, 'w') as file:
        json.dump(input_data, file, indent=4)
    
    # save testing version
    if subject_id == 1: 
        session_id = f"{wave_id}-999" 
        _ = [trial_dict.update(session_id = session_id) for trial_dict in input_data]
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
    snapshot_path = os.path.join(out_dir, "_settings.json")
    with open(snapshot_path, "w") as file: 
        json.dump(settings, file, indent=4)

    # stimuli and stimuli paths
    exp_stimuli_dir = settings["stimuli"]["exp_stimuli_dir"]
    dist_stimuli_dir = settings["stimuli"]["dist_stimuli_dir"]
    n_set_ids = settings["stimuli"]["n_set_ids"]
    practice_set_ids = settings["stimuli"]["practice_set_ids"]
    excluded_set_ids = settings["stimuli"]["excluded_set_ids"]
    image_paths = get_image_paths()
    
    # trial numbers
    ncatch = settings["memory_experiment"]["ncatch"]
    practice_trials = settings["memory_experiment"]["practice_trials"]
    wm_trials = settings["memory_experiment"]["wm_trials"]
    wm_block1_trials = settings["memory_experiment"]["wm_block1_trials"]
    wm_block2_trials = settings["memory_experiment"]["wm_block2_trials"]
    wm_block3_trials = settings["memory_experiment"]["wm_block3_trials"]
    lm_trials = settings["memory_experiment"]["lm_trials"]
    assert lm_trials == wm_block1_trials + wm_block2_trials, "LM trials not twice the WM block 1+2 length"

    trials_per_block = [wm_block1_trials, wm_block2_trials, wm_block3_trials]
    all_encoding_trials = practice_trials + wm_trials
   
    # set up conditions and condition codes 
    ## factor a is the stimulus condition (i.e. mixed, semantic, vision)
    a_levels = settings["memory_experiment"]["encoding_conditions"]
    assert len(a_levels)==3, "There must be 3 encoding (stimulus) conditions."
    a_index = [0,1,2] 
    
    ## factor b is the encoding time
    b_levels = settings["timing"]["encoding_times"]
    assert len(b_levels)==4, "There must be 4 encoding time."
    b_index = [0,1,2,3]

    # squared design (also within each experimental block)
    n_conditions = len(a_levels)*len(b_levels)
    assert wm_block1_trials%(n_conditions) == 0, f"Number of wm trials must be divisible by {n_conditions}"
    assert wm_block2_trials%(n_conditions) == 0, f"Number of wm trials must be divisible by {n_conditions}"
    assert wm_block3_trials%(n_conditions) == 0, f"Number of wm trials must be divisible by {n_conditions}"

    if subject_number%len(a_levels)!=0:
        print("Subject number will be higher due to latin square randomization")

    # load and encoding time 
    load = settings["memory_experiment"]["load"]
    assert load == 3, f"Load == {load} is not yet implemented. Set load to 3."

    # start randomization
    nan = 9999
    subject_id = 0

    while subject_id < subject_number:    
        # randomize image ids
        set_ids = randomize_set_ids(n_set_ids, excluded_set_ids, practice_set_ids)

        # generate the design mat for wm and practice trials
        wm_mat = generate_wm_mat()
        practice_mat = generate_practice_mat()

        # distractors
        distractors = get_distractor_stimuli()

        # lm randomization (used during lm data assambling)
        lm_random_idx = np.random.permutation(np.arange(lm_trials))

        ## latin square randomization of conditions
        condition_wheel = wm_mat.loc["stimulus_condition_index"].to_numpy().copy()

        n_latin_sq = len(a_levels)
        for i in range(n_latin_sq):  
            subject_id += 1
            print(f"{wave_id} - Generating input data for {subject_id} .. ")

            # turn the condition wheel
            condition_wheel += 1

            # get current conditions & update the wm mat
            current_condition_indices = (condition_wheel % n_latin_sq)
            wm_mat.loc["stimulus_condition_index"] = current_condition_indices

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
