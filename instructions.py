import numpy as np
import pandas as pd
import os

version = "test"
wm_positions = [1,1,3] # hard coded positions of the wm stimuli

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

nan = 9999 
instruction_df = []
for i in range(3): 
    angles = generate_random_angles(5)
    files = sorted([os.path.join("stimuli", "instructions", f"practice_{i+1:03d}", f) 
                    for f in os.listdir(f"stimuli/instructions/practice_{i+1:03d}") if f.endswith(".jpg")])
    recognition_angle = [angles[wm_positions[i]]]
    instruction_df.append(np.concat([files, angles, recognition_angle]))

columns = [f"encoding_file_{i+1}" for i in range(5)] + ["wm_recognition_file"]
columns += [f"encoding_theta_{i+1}" for i in range(5)] + ["recognition_theta"]

instruction_df = pd.DataFrame(instruction_df, columns=columns)

instruction_df["wm_trial_id"] = nan
instruction_df["wm_id"] = nan
instruction_df["wm_condition"] = nan
instruction_df["wm_position"] = wm_positions
instruction_df["lm_position"] = nan
instruction_df["trial_type"] = "practice"
instruction_df["version"] = version

instruction_json = instruction_df.to_json(orient='records', indent=4)
file_path = os.path.join("input_data", "instructions", f"instructions_{version}.json")
with open(file_path, 'w') as file:
    file.write(instruction_json)

                   
