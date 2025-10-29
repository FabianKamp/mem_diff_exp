# %%
import pandas as pd 
import os
import glob
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
matplotlib.use('TkAgg')
plt.close()

#%% variable set up
wave_code = "M-PA"
subject_ids = [2,3,4,5,6,7,9,10,11,21,22,23]

show = False
save = True

#%% set up colors
colors_palette = ["#ef476f","#ffd166","#06d6a0","#118ab2","#073b4c"]
sns.set_palette(colors_palette)
all_figures = []

#%% load files
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files = [f"./output_data/{wave_code}-{i:03d}.csv" 
             for i in subject_ids]

all_data = []
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)

all_data = pd.concat(all_data) 
n_subjects = len(subject_ids)

#%% Preprocess working memory data
wm_data = all_data.loc[all_data.trial_type=='wm'].copy()
wm_data = wm_data.loc[(wm_data.phase == "recognition")]
wm_data["correct"] = (wm_data.response.astype(int) == wm_data.correct_response)
wm_data["encoding_time"] = wm_data.encoding_time.map({1200: "short", 2000: "long"})

#%% Visual vs semantic condition
vis_sem = wm_data.loc[wm_data.condition_name!='mixed']

## barplots
cols = 5
rows = n_subjects//cols+1
fig, ax = plt.subplots(rows, cols, 
                       figsize=(cols*2, rows*2), 
                       sharey=True,
                       constrained_layout=True)
all_figures.append(fig)
fig.suptitle(f"{wave_code} - WM: visual vs semantic")
fax = ax.flatten()

i = 0
all_results = []
for s, sub_df in vis_sem.groupby("session_id"):
    sub_results = (
        sub_df.groupby(["encoding_time","condition_name"])["correct"]
            .agg(lambda x: np.round(x.sum()/len(x), 2))
            .reset_index()
        )
    sub_results = sub_results.rename(
        columns= {"condition_name":"condition", 
                  "correct": "accuracy"}
                  )
    sub_results["subject_id"]= int(s.split("-")[-1])
    all_results.append(sub_results)

    bar = sns.barplot(data=sub_results, 
                      x="encoding_time", 
                      order = ["long", "short"],
                      hue="condition", 
                      hue_order=["visual", "semantic"],
                      y="accuracy", 
                      ax=fax[i])
    
    bar.axhline(.5,ls=":")
    bar.set_title(int(s.split("-")[-1]))
    bar.set_xlabel('')

    if i>0: bar.get_legend().remove()
    i+=1

# delete empty axes
for j in range(i,cols*rows): 
    fax[j].remove()

# scatter plots
all_results = pd.concat(all_results)
fig, ax = plt.subplots(1, 2, 
                       figsize=(10,3), 
                       sharey=True,
                       constrained_layout=True)
all_figures.append(fig)
fig.suptitle(f"{wave_code} - WM: visual vs semantic")

conditions = ["visual", "semantic"]
encoding_times = ["long", "short"]
for (ax, condition) in zip(ax, conditions):
    scatter = sns.boxplot(
        data=all_results.loc[all_results.condition == condition], 
        x="encoding_time", 
        y="accuracy", 
        widths=0.5, 
        order=["long","short"],
        ax=ax
        )
    
    # Plot connected lines for each subject
    for s, sub_results in all_results.groupby("subject_id"):
        condition_results = sub_results.loc[sub_results.condition==condition]
        ax.plot([0, 1],
                [condition_results.loc[condition_results.encoding_time=="long", "accuracy"], 
                condition_results.loc[condition_results.encoding_time=="short", "accuracy"]],
                'o:',  
                alpha=0.6,
                color='gray',
                markerfacecolor='none',
                linewidth=1
        )
    
    ax.set_title(condition.capitalize())
    ax.set_xlabel("Encoding Time")

# %% Mixed trials
mixed_data = wm_data.loc[wm_data.condition_name=='mixed'].copy()

mixed_data["response_stimulus"] = mixed_data.apply(
    lambda row: row.stimulus_left if row.response == 0 else row.stimulus_right, axis=1
    )
mixed_data.response_stimulus = (
    mixed_data.response_stimulus
    .str.split("/")
    .str[-1]
    .str[0]
    .map({'3': "semantic", '4': "visual"})
    )

## barplots
fig, ax = plt.subplots(
    figsize=(10,3),
    constrained_layout=True
    )
all_figures.append(fig)
fig.suptitle(f"{wave_code} - WM: mixed trials")

all_results = []
for s, sub_df in mixed_data.groupby("session_id"):
    results = (
        sub_df.groupby("encoding_time")["response_stimulus"]
        .value_counts(normalize=True)
        .reset_index())
    results = results.loc[results.response_stimulus=="visual"]
    results = (results
               .rename(columns={"proportion":"proportion_visual"})
               .drop(columns="response_stimulus")
    )
    results["session_id"] = int(s.split("-")[-1])
    all_results.append(results)

all_results = pd.concat(all_results)
bar = sns.barplot(
    data=all_results, 
    x="session_id", 
    hue = "encoding_time",
    hue_order = ["long", "short"],
    y="proportion_visual", 
    ax=ax
)
bar.axhline(.5,ls=":")
bar.set_xlabel('')

## scatter plot
fig, ax = plt.subplots(figsize=(5,3))
all_figures.append(fig)
fig.suptitle(f"{wave_code} - WM: mixed trials")
box = sns.boxplot(
    data=all_results, 
    x="encoding_time", 
    y="proportion_visual", 
    widths=0.5, 
    order=["long", "short"], 
)
box.axhline(.5, color='k')

for s, sub_data in all_results.groupby("session_id"):
    ax.plot([0, 1],
            [sub_data.loc[sub_data.encoding_time=="long", "proportion_visual"], 
             sub_data.loc[sub_data.encoding_time=="short", "proportion_visual"]],
            'o:',  
            alpha=0.6,
            color='gray',
            markerfacecolor='none',
            linewidth=1
    )

# %% LM preprocessing
def recode_response(old, response): 
    if old: 
        if response >=3: 
            return "hit"
        else: 
            return "miss"
    else: 
        if response >=3: 
            return "fa"
        else:
            return "correct_rejection"

lm_data = all_data.loc[
    (all_data.trial_type=="lm-recognition")|
    (all_data.trial_type=="lm")].copy()

lm_data.response = lm_data.response.astype(int)
possible_responses = [5,20,35,65,80,95]
lm_data.response = lm_data.response.map({
    k: i for i,k in enumerate(possible_responses)
})

# recoding 
lm_data["response_code"] = lm_data.apply(
    lambda row: recode_response(row.image_old, row.response),
    axis=1
)

# %% LM hit rate
## barplot
cols = 5
rows = n_subjects//cols+1
fig, ax = plt.subplots(rows, cols, 
                       figsize=(cols*2, rows*2), 
                       sharey=True,
                       constrained_layout=True)
all_figures.append(fig)
fig.suptitle(f"{wave_code} - LM: hit rate")
fax = ax.flatten()

i = 0
all_results = []
for s, sub_data in lm_data.groupby("session_id"): 
    # hit rate
    old = sub_data.loc[sub_data.image_old==1].copy()
    
    old["encoding_time"] = old["encoding_time"].map({
        1200: "short",
        9999: "short",
        2000: "long",
    })
    
    old = (
        old.groupby("encoding_time")["response_code"]
        .agg(lambda x: (x=="hit").sum()/len(x))
        .reset_index()
    )

    old = old.rename(columns={"response_code":"hit_rate"})
    old["session_id"] = int(s.split("-")[-1])    
    all_results.append(old)
    
    # fa rate 
    new = sub_data.loc[sub_data.image_old==0]
    fa_rate = (new.response_code=="fa").sum()/len(new)

    fax[i].bar(
        [0,1,2], 
        [old.loc[old.encoding_time=="long","hit_rate"].item(),
         old.loc[old.encoding_time=="short","hit_rate"].item(),
         fa_rate], 
        color=[colors_palette[1], colors_palette[1], colors_palette[0]]
        )

    fax[i].set_xticks([0,1,2], labels=["HR long", "HR short", "FA"])
    fax[i].axhline(.5, c='k')
    fax[i].set_title(int(s.split("-")[-1]))
    i += 1
all_results = pd.concat(all_results)

# delete empty axes
for j in range(i,cols*rows): 
    fax[j].remove()

# boxplot
fig, ax = plt.subplots(figsize=(5,3))
all_figures.append(fig)
fig.suptitle(f"{wave_code} - LM: hit rate")

box = sns.boxplot(
    data=all_results, 
    x="encoding_time", 
    y="hit_rate", 
    widths=0.5, 
    order=["long", "short"], 
)
box.axhline(.5, color='k')

for s, sub_data in all_results.groupby("session_id"):
    ax.plot([0, 1],
            [sub_data.loc[sub_data.encoding_time=="long", "hit_rate"], 
             sub_data.loc[sub_data.encoding_time=="short", "hit_rate"]],
            'o:',  
            alpha=0.6,
            color='gray',
            markerfacecolor='none',
            linewidth=1
    )

# %%
if show:
    plt.show(block=False)
    plt.pause(10)
    plt.close('all')

if save:
    pdf_file = f"./figures/qc/qc_{wave_code}.pdf"
    plt.tight_layout()
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)
