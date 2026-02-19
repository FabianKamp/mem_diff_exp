# %%
import pandas as pd 
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pickle

#%% variable set up
wave_code = "M-PF"
subject_ids = [1,2,3,4,5,6,7,8,9] #[2,3,4,5,6,7,9,10,11,21,22,23]

show = False
save = True

#%% set up colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)
all_figures = []
figure_data = {}

#%% load files
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for i in subject_ids for suffix in "ABC"]
out_files = filter(os.path.exists, out_files)

all_data = []
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)

all_data = pd.concat(all_data) 
n_subjects = len(subject_ids)

#%% Preprocess working memory data
# NAN = 9999
# all_data.loc[all_data.response.isna(), "response"] = NAN
wm_data = all_data.loc[
    (all_data.trial_type=='wm') & 
    (all_data.phase == "recognition")
    ].copy()
print("NA responses: ", np.sum(wm_data.response.isna()))

wm_data.response = wm_data.response.astype('Int64')
wm_data.correct_response = wm_data.correct_response.astype('Int64')
wm_data["correct"] = (wm_data.response == wm_data.correct_response)

wm_data.encoding_time = wm_data.encoding_time.astype('Int64')
wm_data.condition = wm_data.condition.astype('Int64')


#%% aggregate visual vs semantic data
vis_sem = wm_data.loc[wm_data.condition_name!='mixed']

vis_sem_agg = (
    vis_sem.groupby(["session_id","encoding_time","condition_name","condition"])
        .agg(
            hits = ("correct", "sum"),
            valid_responses = ("correct", "count"),
            accuracy = ("correct", "mean")
        )
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )

# %%
## barplots for each subject individually
# valid responses
cols = 5
rows = n_subjects//cols+1
fig, ax = plt.subplots(rows, cols, 
                       figsize=(cols*2, rows*2), 
                       sharey=True,
                       constrained_layout=True)
title = "Fig1a: Visual vs. Semantic"
fig.suptitle(f"{title}    Wave: {wave_code}")

i = 0
fax = ax.flatten()
for s, sub_df in vis_sem_agg.groupby("session_id"):
    bar = sns.barplot(data=sub_df, 
                      x="encoding_time", 
                      hue="condition_name", 
                      hue_order=["visual", "semantic"],
                      y="valid_responses", 
                      ax=fax[i])
    bar.axhline(.5,ls=":")
    bar.set_title(int(s.split("-")[-2]))
    bar.set_xlabel('')
    fax[i].axhline(y=13, color="r")
    if i>0: bar.get_legend().remove()
    i+=1

for j in range(i,cols*rows): 
    fax[j].remove()
all_figures.append(fig)

# accuracy 
cols = 5
rows = n_subjects//cols+1
fig, ax = plt.subplots(rows, cols, 
                       figsize=(cols*2, rows*2), 
                       sharey=True,
                       constrained_layout=True)
title = "Fig1b: Visual vs. Semantic"
fig.suptitle(f"{title}    Wave: {wave_code}")

i = 0
fax = ax.flatten()
for s, sub_df in vis_sem_agg.groupby("session_id"):
    bar = sns.barplot(data=sub_df, 
                      x="encoding_time", 
                      hue="condition_name", 
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
    title: vis_sem_agg
    })

# %%
### box plots
fig, ax = plt.subplots(1, 2, 
            figsize=(10,3), 
            sharey=True,
            constrained_layout=True
            )
title = "Fig2: Visual vs. Semantic"
fig.suptitle(f"{title}    Wave: {wave_code}")

conditions = ["visual", "semantic"]
encoding_times = sorted(vis_sem_agg.encoding_time.unique())
for (ax, condition) in zip(ax, conditions):
    box = sns.boxplot(
        data=vis_sem_agg.loc[vis_sem_agg.condition_name == condition], 
        x="encoding_time", 
        y="accuracy", 
        widths=0.5, 
        palette=colors_palette,
        legend=False,
        ax=ax,
        )
    
    for s, sub_results in vis_sem_agg.groupby("subject_id"):
        condition_results = sub_results.loc[sub_results.condition_name==condition]
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
    title: vis_sem_agg
    })

# %% Mixed trials
# preprocess mixed trials
mixed_data = wm_data.loc[
    (wm_data.condition_name=='mixed') &
    (wm_data.response.notna())
    ].copy()

mixed_data["response_stimulus"] = mixed_data.apply(
    lambda row: row.stimulus_left if row.response == 0 else row.stimulus_right, axis=1
    )

mixed_data.response_stimulus = pd.Categorical(
    mixed_data.response_stimulus
    .str.split("/")
    .str[-1]
    .str[0]
    .map({'3': "semantic", '4': "visual"})
)


response_counts = (
    mixed_data
    .groupby(["session_id", "encoding_time"])
    .response_stimulus
    .value_counts()
    .reset_index()
)

valid_responses = (
    response_counts
    .groupby(["session_id", "encoding_time"])
    .agg(sum = ("count", "sum"))
    .reset_index()
)

mixed_data_agg = pd.merge(
    response_counts,
    valid_responses, 
    on=["session_id", "encoding_time"] 
)

mixed_data_agg["proportion"] = mixed_data_agg["count"]/mixed_data_agg["sum"]
mixed_data_vision = mixed_data_agg.loc[mixed_data_agg.response_stimulus == "visual"]

# %%
## barplots 
# trial counts
fig, ax = plt.subplots(
    figsize=(10,3),
    constrained_layout=True
    )
title = "Fig3a: Mixed Trials"
fig.suptitle(f"{title}    Wave: {wave_code}")

bar = sns.barplot(
    data=mixed_data_vision, 
    x="session_id", 
    hue="encoding_time",
    y="sum", 
    palette=colors_palette,
    ax=ax
)
bar.axhline(.5,ls=":")
bar.set_ylabel('valid responses')
bar.set_xlabel('')

all_figures.append(fig)
figure_data.update({
    title: mixed_data_agg
    })

# proportions
fig, ax = plt.subplots(
    figsize=(10,3),
    constrained_layout=True
    )
title = "Fig3b: Mixed Trials"
fig.suptitle(f"{title}    Wave: {wave_code}")

bar = sns.barplot(
    data=mixed_data_vision, 
    x="session_id", 
    hue = "encoding_time",
    y="proportion", 
    palette=colors_palette,
    ax=ax
)
bar.axhline(.5,ls=":")
bar.set_xlabel('')
bar.set_ylabel('proportion vision')

all_figures.append(fig)
figure_data.update({
    title: mixed_data_agg
    })

## box plots
fig, ax = plt.subplots(
    figsize=(5,3), 
    constrained_layout=True
    )
title = "Fig4: Mixed Trials"
fig.suptitle(f"{title}    Wave: {wave_code}")

box = sns.boxplot(
    data=mixed_data_vision,
    x="encoding_time",
    y="proportion",
    widths=0.5,
    palette=colors_palette,
)
box.axhline(.5, color='k')

encoding_times = sorted(mixed_data_vision.encoding_time.unique())
for s, sub_data in mixed_data_vision.groupby("session_id"):
    box.plot(np.arange(len(encoding_times)),
            [sub_data.loc[sub_data.encoding_time==t, "proportion"] for t in encoding_times],
            'o:',  
            alpha=0.6,
            color='gray',
            markerfacecolor='none',
            linewidth=1
    )
box.set_ylabel("proportion visual")

all_figures.append(fig)
figure_data.update({
    title: mixed_data_vision
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
