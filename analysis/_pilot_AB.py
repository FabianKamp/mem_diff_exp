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
subject_ids = np.arange(1,25)

show = True
save = True

#%% set up colors
colors_palette = ["#ef476f","#ffd166","#06d6a0","#118ab2","#073b4c"]
sns.set_palette(colors_palette)
all_figures = []
figure_data = {}

#%% load files
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files_A = [f"./output_data/M-PA/M-PA-{i:03d}.csv" for i in subject_ids]
out_files_B = [f"./output_data/M-PB/M-PB-{i:03d}-{suffix}.csv" for i in subject_ids for suffix in "AB"]
out_files = filter(os.path.exists, out_files_A+out_files_B)

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
fig.suptitle(f"WM: visual vs semantic")
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
    sub_results["subject_id"]= s
    all_results.append(sub_results)

    bar = sns.barplot(data=sub_results, 
                      x="encoding_time", 
                      order = ["long", "short"],
                      hue="condition", 
                      hue_order=["visual", "semantic"],
                      y="accuracy", 
                      ax=fax[i])
    
    bar.axhline(.5,ls=":")
    bar.set_title(s)
    bar.set_xlabel('')

    if i>0: bar.get_legend().remove()
    i+=1

# delete empty axes
for j in range(i,cols*rows): 
    fax[j].remove()
figure_data.update(fig1=all_results)

if show: fig.show()

# %% Scatter plots
all_results = pd.concat(all_results)
fig, ax = plt.subplots(1, 2, 
                       figsize=(10,3), 
                       sharey=True,
                       constrained_layout=True)
all_figures.append(fig)
fig.suptitle(f"WM: visual vs semantic")

conditions = ["visual", "semantic"]
encoding_times = ["long", "short"]
for (ax, condition) in zip(ax, conditions):
    box = sns.boxplot(
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

figure_data.update(fig2=all_results)
if show: fig.show()

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
fig.suptitle(f"WM: mixed trials")

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
    results["session_id"] = s
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
bar.tick_params(axis='x', labelrotation=90)

figure_data.update(fig3=all_results)
if show: fig.show()
# %% scatter plot
fig, ax = plt.subplots(
    figsize=(5,3), 
    constrained_layout=True
    )

all_figures.append(fig)
fig.suptitle(f"WM: mixed trials")
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

figure_data.update(fig4=all_results)
if show: fig.show()

# %% saving
if save:
    pdf_file = f"./figures/descriptive/descr_M-PAB.pdf"
    data_file = f"./figures/descriptive/descr_M-PAB.pkl"
    pickle.dump(figure_data, open(data_file, "wb"))
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)