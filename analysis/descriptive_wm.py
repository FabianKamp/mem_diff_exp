# %%
import pandas as pd 
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
import pickle
matplotlib.use('TkAgg')
plt.close()

#%% variable set up
wave_code = "M-PD"
subject_ids = [4,5,6] #[2,3,4,5,6,7,9,10,11,21,22,23]

show = False
save = True

#%% set up colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971","#B39CD4"]
sns.set_palette(colors_palette)
all_figures = []
figure_data = {}

#%% load files
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files = [f"./output_data/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for i in subject_ids for suffix in "ABC"]
out_files = filter(os.path.exists, out_files)

all_data = []
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)

all_data = pd.concat(all_data) 
n_subjects = len(subject_ids)

#%% Preprocess working memory data
NAN = 9999
all_data.loc[all_data.response.isna(), "response"] = NAN

wm_data = all_data.loc[(all_data.trial_type=='wm') & 
                       (all_data.phase == "recognition")].copy()

wm_data.response = wm_data.response.astype(int)
wm_data.correct_response = wm_data.correct_response.astype(int)
wm_data["correct"] = (wm_data.response == wm_data.correct_response)

wm_data.encoding_time = wm_data.encoding_time.astype(int)

#%% Visual vs semantic condition
vis_sem = wm_data.loc[wm_data.condition_name!='mixed']

## barplots for each subject individually
cols = 5
rows = n_subjects//cols+1
fig, ax = plt.subplots(rows, cols, 
                       figsize=(cols*2, rows*2), 
                       sharey=True,
                       constrained_layout=True)
title = "Fig1: Visual vs. Semantic"
fig.suptitle(f"{title}    Wave: {wave_code}")

i = 0
all_results = []
fax = ax.flatten()
for s, sub_df in vis_sem.groupby("session_id"):
    sub_results = (
        sub_df.groupby(["encoding_time","condition_name"])["correct"]
            .agg(lambda x: np.round(x.sum()/len(x), 2))
            .reset_index()
        )
    sub_results = sub_results.rename(columns= {"condition_name":"condition", "correct": "accuracy"})
    
    sub_results["subject_id"]= int(s.split("-")[-2])
    all_results.append(sub_results)

    bar = sns.barplot(data=sub_results, 
                      x="encoding_time", 
                      hue="condition", 
                      hue_order=["visual", "semantic"],
                      y="accuracy", 
                      ax=fax[i])
    
    bar.axhline(.5,ls=":")
    bar.set_title(int(s.split("-")[-2]))
    bar.set_xlabel('')

    if i>0: bar.get_legend().remove()
    i+=1

for j in range(i,cols*rows): 
    fax[j].remove()

all_figures.append(fig)
figure_data.update({
    title: all_results
    })

### scatter plots
all_results = pd.concat(all_results)
fig, ax = plt.subplots(1, 2, 
            figsize=(10,3), 
            sharey=True,
            constrained_layout=True
            )
title = "Fig2: Visual vs. Semantic"
fig.suptitle(f"{title}    Wave: {wave_code}")

conditions = ["visual", "semantic"]
encoding_times = sorted(all_results.encoding_time.unique())
for (ax, condition) in zip(ax, conditions):
    box = sns.boxplot(
        data=all_results.loc[all_results.condition == condition], 
        x="encoding_time", 
        y="accuracy", 
        widths=0.5, 
        palette=colors_palette,
        ax=ax
        )
    
    # Plot connected lines for each subject
    for s, sub_results in all_results.groupby("subject_id"):
        condition_results = sub_results.loc[sub_results.condition==condition]
        ax.plot(np.arange(len(encoding_times)),
                [condition_results.loc[condition_results.encoding_time==t, "accuracy"] 
                for t in encoding_times],
                'o:',  
                alpha=0.6,
                color='gray',
                markerfacecolor='none',
                linewidth=1
        )
    
    ax.set_title(condition.capitalize())
    ax.set_xlabel("Encoding Time")

all_figures.append(fig)
figure_data.update({
    title: all_results
    })

# %% Mixed trials
# preprocess mixed trials
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
    results["session_id"] = s.split("-")[-2]
    all_results.append(results)
all_results = pd.concat(all_results)

## barplots
fig, ax = plt.subplots(
    figsize=(10,3),
    constrained_layout=True
    )
title = "Fig3: Mixed Trials"
fig.suptitle(f"{title}    Wave: {wave_code}")

bar = sns.barplot(
    data=all_results, 
    x="session_id", 
    hue = "encoding_time",
    y="proportion_visual", 
    palette=colors_palette,
    ax=ax
)
bar.axhline(.5,ls=":")
bar.set_xlabel('')

all_figures.append(fig)
figure_data.update({
    title: all_results
    })

## scatter plot
fig, ax = plt.subplots(
    figsize=(5,3), 
    constrained_layout=True
    )
title = "Fig4: Mixed Trials"
fig.suptitle(f"{title}    Wave: {wave_code}")

box = sns.boxplot(
    data=all_results,
    x="encoding_time",
    y="proportion_visual",
    widths=0.5,
    palette=colors_palette,
)
box.axhline(.5, color='k')

encoding_times = sorted(all_results.encoding_time.unique())
for s, sub_data in all_results.groupby("session_id"):
    ax.plot(np.arange(len(encoding_times)),
            [sub_data.loc[sub_data.encoding_time==t, "proportion_visual"] for t in encoding_times],
            'o:',  
            alpha=0.6,
            color='gray',
            markerfacecolor='none',
            linewidth=1
    )

all_figures.append(fig)
figure_data.update({
    title: all_results
    })

# %%
if show:
    plt.show(block=False)
    plt.pause(60)
    plt.close('all')

if save:
    pdf_file = f"./figures/descriptive/descr_{wave_code}_wm.pdf"
    data_file = f"./figures/descriptive/descr_{wave_code}_wm.pkl"
    pickle.dump(figure_data, open(data_file, "wb"))
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)

# %%
