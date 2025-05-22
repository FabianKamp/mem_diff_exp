import numpy as np
import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser(description="Randomization script for memory diffusion experiment.")
parser.add_argument("--subject_number", type=int, default=4, help="Number of subjects")
parser.add_argument("--wm_trials", type=int, default=180, help="Number of working memory trials")
parser.add_argument("--lm_trials", type=int, default=60, help="Number of long-term memory trials")
parser.add_argument("--workload", type=int, default=3, help="Workload parameter")
parser.add_argument("--out_directory", type=str, default="input_data", help="Output directory")
parser.add_argument("--out_format", type=str, default="json", help="Output format")
args = parser.parse_args()

subject_number = args.subject_number
wm_trials = args.wm_trials
lm_trials = args.lm_trials
workload = args.workload
out_dir = args.out_directory
out_format = args.out_format

if not os.path.exists(out_dir): 
    os.mkdir(out_dir)

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
    for i in range(n-1):
        next_angle = (random_angles[-1] + angle_between) % (np.pi * 2)
        random_angles.append(next_angle)
    random_angles = np.random.permutation(random_angles)
    random_angles = np.round(random_angles, 3)
    return random_angles

subject_id = 1
while subject_id <= subject_number: 
    # randomize wm and lm images & their order
    total_trials = wm_trials + lm_trials
    random_pair_id = np.random.permutation(np.arange(total_trials))
    
    # conditions and condition codes 
    conditions = ["same", "control", "semantic", "perceptual"]
    condition_codes = {"same": 1, "control": 2, "semantic": 3, "perceptual": 4}

    # randomize which images are used for wm and lm
    wm_pair_id = random_pair_id[:wm_trials]
    lm_pair_id = random_pair_id[wm_trials:]
    
    # checks
    num_conditions = len(conditions)
    assert wm_trials%num_conditions == 0, f"Number of trials must be divisible by {num_conditions}"
    assert lm_trials%num_conditions == 0, f"Number of trials must be divisible by {num_conditions}"
    
    # randomize wm condition across trials
    wm_repeats = wm_trials//num_conditions
    wm_conditions = conditions * wm_repeats
    wm_condition_codes = np.random.permutation([condition_codes[wm_conditions[i]] for i in range(wm_trials)])
    
    # randomize lm conditions across images
    lm_repeats = lm_trials//num_conditions
    lm_conditions = conditions * lm_repeats
    lm_condition_codes = np.random.permutation([condition_codes[lm_conditions[i]] for i in range(lm_trials)])
    
    # randomize when lm images are presented during the wm block
    lm_encoding_trials = np.random.choice(np.arange(wm_trials), size=lm_trials, replace=False)

    # randomize sequential positions of wm and lm images
    positions = [{"wm":i, "lm":j} for i in range(workload) for j in range(workload) if i!=j]
    num_positions = len(positions)
    assert wm_trials%num_positions == 0, f"Number of trials must be divisible by {num_positions}"
    position_repeats = wm_trials//num_positions
    positions = positions * position_repeats
    randomized_positions = np.random.permutation(positions)

    # generate random angles angles
    theta = np.array([generate_random_angles(workload) for _ in range(wm_trials)])
    
    # randomize distractors
    total_images = wm_trials * workload
    random_distractors = np.random.permutation(np.arange(total_images - wm_trials - lm_trials)) + 9000

    ## latin square randomization
    for i in range(num_conditions): 
        # working memory
        latin_wm_codes = wm_condition_codes%num_conditions + 1
        wm_recognition = wm_pair_id + latin_wm_codes * 1000
        wm_condition_codes = wm_condition_codes + 1
        wm_input_data = []
        distractor_pool = random_distractors.copy()

        for i in range(wm_trials):
            # wm positions
            wm_position_index = randomized_positions[i]["wm"]
            
            trial_data = {
                "wm_trial_id": i,
                "subject_id": subject_id,
                "wm_pair_id": wm_pair_id[i],
                "wm_position": wm_position_index + 1,
                "wm_condition": latin_wm_codes[i],
                "recognition":  wm_recognition[i],
                "recognition_theta":  theta[i, wm_position_index],
                "lm_pair_id": 999, 
                "lm_position": 999
            }
            
            # generate the enoding images
            images_encoding = np.full(workload, 999)
            images_encoding[wm_position_index] = wm_pair_id[i] + 1000
            
            # add lm image if lm trial
            if i in lm_encoding_trials:
                lm_position_index = randomized_positions[i]["lm"]
                lm_encoding_image = lm_pair_id[lm_encoding_trials==i][0]
                images_encoding[lm_position_index] = lm_encoding_image
                trial_data.update({
                    "lm_pair_id": lm_encoding_image,
                    "lm_position": lm_position_index + 1
                })
            
            # distractors
            num_distractors = np.sum(images_encoding == 999)
            images_encoding[images_encoding == 999] = distractor_pool[:num_distractors]
            distractor_pool = distractor_pool[num_distractors:]
            
            for j in range(workload):
                trial_data.update({
                    f"encoding_{j+1:02d}": images_encoding[j],
                    f"encoding_theta_{j+1:02d}": theta[i,j]
                })
            wm_input_data.append(trial_data)    
    
        # long term memory data
        latin_lm_codes = lm_condition_codes%num_conditions + 1
        lm_recognition = lm_pair_id + latin_lm_codes * 1000
        lm_condition_codes = lm_condition_codes + 1
        
        lm_input_data = []
        for i in range(lm_trials):
            encoding_trial = lm_encoding_trials[i]
            encoding_position_index = randomized_positions[encoding_trial]["lm"]
            lm_input_data.append({
                "lm_trial_id": i,
                "subject_id": subject_id,
                "lm_pair_id": lm_pair_id[i],
                "lm_condition": latin_lm_codes[i],
                "recognition": lm_recognition[i],
                "wm_trial_id": encoding_trial,
                "encoding_position": encoding_position_index + 1
            })
        
        # save 
        wm_input_data = pd.DataFrame(wm_input_data)
        lm_input_data = pd.DataFrame(lm_input_data)   

        if out_format == "csv": 
            wm_csv_file_path = os.path.join(out_dir, f"wm_input_subject_{subject_id:03d}.csv")            
            wm_input_data.to_csv(wm_csv_file_path, index=False)
            lm_csv_file_path = os.path.join(out_dir, f"lm_input_subject_{subject_id:03d}.csv")
            lm_input_data.to_csv(lm_csv_file_path, index=False)
        
        elif out_format == "json":    
            wm_json = wm_input_data.to_json(orient='records', indent=4)
            wm_file_path = os.path.join(out_dir, f"wm_input_subject_{subject_id:03d}.json")
            with open(wm_file_path, 'w') as wm_file:
                wm_file.write(wm_json)
        
            lm_json = lm_input_data.to_json(orient='records', indent=4)
            lm_file_path = os.path.join(out_dir, f"lm_input_subject_{subject_id:03d}.json")
            with open(lm_file_path, 'w') as lm_file:
                lm_file.write(lm_json)
    
        # update subject id to the next
        subject_id += 1
            
