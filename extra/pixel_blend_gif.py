"""
Script to create a GIF that linearly blends every pixel value from imgA to imgB.
"""

#%%
import numpy as np
from PIL import Image
from tqdm import tqdm

# %%

def create_gif(set_id, start_index=0):
    # Define input images
    imgA_path = f"../stimuli/exp_stimuli_pilot/{set_id:03d}/{1000+set_id}.jpg"
    imgB_path = f"../stimuli/exp_stimuli_pilot/{set_id:03d}/{4000+set_id}.jpg"

    # Number of steps/frames in the animation
    n_steps = 50

    imgA = np.array(Image.open(imgA_path).convert("RGB"), dtype=np.float32)
    imgB = np.array(Image.open(imgB_path).convert("RGB"), dtype=np.float32)

    assert imgA.shape == imgB.shape, "imgA and imgB must have the same dimensions"

    frames = []
    for i in range(n_steps + 1):
        t = i / n_steps
        t_eased = 0.5 - 0.5 * np.cos(np.pi * t)  # ease-in-out: slow at t=0/1, fast at t=0.5
        frame = (1 - t_eased) * imgA + t_eased * imgB
        frames.append(Image.fromarray(frame.astype(np.uint8)))

    frames = frames + frames[::-1]

    # frames form a closed loop (A->B->A); rotate so playback starts at start_index instead of frame 0
    start_index = start_index % len(frames)
    frames = frames[start_index:] + frames[:start_index]

    frames[0].save(
        f"../figures/explanatory/pixel_blend_{set_id:03d}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=120,
        loop=0,
    )

# %%
for i in tqdm(range(1, 10)):
    create_gif(i, start_index= i * 6)
# %%
