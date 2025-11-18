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
wave_code = "M-PB"
subject_ids = np.arange(1,12) #[2,3,4,5,6,7,9,10,11,21,22,23]

show = False
save = True

colors_palette = ["#ef476f","#ffd166","#06d6a0","#118ab2","#073b4c"]
sns.set_palette(colors_palette)
all_figures = []

#%% load files
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files = [f"./output_data/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for i in subject_ids for suffix in "AB"]
out_files = filter(os.path.exists, out_files)

all_data = []
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)

all_data = pd.concat(all_data) 
n_subjects = len(subject_ids)
labels = all_data.session_id.unique()

all_figures = []

# %% WM & LM length
results = []

for session, subdata in all_data.groupby("session_id"):   

    wm_trials = subdata.loc[(subdata.trial_type == "wm")|(subdata.trial_type == "practice")|(subdata.trial_type == "catch")]
    distractor_trials = subdata.loc[(subdata.trial_type == "distractor-task")]
    lm_trials = subdata.loc[(subdata.trial_type == "lm")]
    
    results.append(dict(
        session_id = session, 
        instruction = np.round(wm_trials.time_elapsed.iloc[0]/60e3), 
        WM = np.round((wm_trials.time_elapsed.iloc[-1]-wm_trials.time_elapsed.iloc[0])/60e3),
        distractor = np.round((distractor_trials.time_elapsed.iloc[-1]-wm_trials.time_elapsed.iloc[-1])/60e3),
        LM = np.round((lm_trials.time_elapsed.iloc[-1]-lm_trials.time_elapsed.iloc[0])/60e3),
        total = np.round(subdata.time_elapsed.iloc[-1]/60e3)
        ))

results = pd.DataFrame(results).melt(id_vars="session_id", var_name="section", value_name="duration")

fig, ax = plt.subplots(
    1,
    figsize=(6,5),
    constrained_layout=True
    )
boxplot = sns.boxplot(
    data=results, 
    x ="section", 
    y="duration",
    color="white",
    ax=ax
)

ax.set_xlabel("")
ax.set_yticks(np.arange(0,ax.get_ylim()[1],10))
ax.grid(axis="y", alpha=.5)

def annotate_outliers(ax, data, x, y, label_col):
    categories = data[x].unique()
    for i, category in enumerate(categories):
        category_data = data[data[x] == category]
        
        Q1 = category_data[y].quantile(0.25)
        Q3 = category_data[y].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = category_data[
            (category_data[y] < lower_bound) | 
            (category_data[y] > upper_bound)
        ]
        
        # Annotate each outlier
        for _, row in outliers.iterrows():
            ax.text(
                x=i,
                y=row[y],
                s=str(row[label_col]),
                fontsize=6,
                alpha=.5
            )
annotate_outliers(
    data=results, 
    x ="section", 
    y="duration",
    label_col="session_id",
    ax=ax
)

all_figures.append(fig)
if show:
    fig.show()

# %% Reaction times
wm_rt, lm_rt = [],[]

for session_id, sub_data in all_data.groupby("session_id"):
    session_id = str(int(session_id.split("-")[-2]))
    # wm
    wm_times = sub_data.loc[
        (sub_data.trial_type=="wm") & 
        (sub_data.phase=="recognition"), 
        "rt"]/1e3
    wm_rt.append(pd.DataFrame(dict(
        session_id = [session_id] * len(wm_times), 
        trial_time = wm_times.to_list()
    )))
    # lm
    lm_times = sub_data.loc[
        (sub_data.trial_type=="lm") & 
        (sub_data.phase=="recognition"), 
        "rt"]/1e3
    lm_rt.append(pd.DataFrame(dict(
        session_id = [session_id] * len(lm_times), 
        trial_time = lm_times.to_list()
    )))

results = dict(
    WM = pd.concat(wm_rt).reset_index(),
    LM = pd.concat(lm_rt).reset_index(),
)

fig, ax = plt.subplots(
    1, 2, 
    constrained_layout=True, 
    sharey=True,
    figsize=(12,5)
    )
for i, el in enumerate(results.items()):
    bars = sns.barplot(
        data=el[1], 
        x="session_id", 
        y="trial_time",
        color="w",
        edgecolor="k",
        errorbar=None,
        ax=ax[i]
    )

    scatter = sns.scatterplot(
        data=el[1],
        x="session_id",
        y="trial_time",
        size=1,
        legend=False,
        ax=ax[i],
        facecolor='none',
        edgecolor='grey'
    )

    ax[i].set_title(el[0])
    ax[i].axhline(30)
    ax[i].axhline(15, linestyle=":", c="k", alpha=.5)
    ax[i].axhline(10, linestyle=":", c="k", alpha=.5)
    ax[i].axhline(5, linestyle=":", c="k", alpha=.5)
    
    if i == 0: 
        ax[i].set_ylabel("Reaction times")
    else: 
        ax[i].set_ylabel("")

all_figures.append(fig)


# %% Trial times
encoding_times, recognition_times, lm_times = [], [], []
for session_id, sub_data in all_data.groupby("session_id"):
    session_id = str(int(session_id.split("-")[-2]))
    sub_data["trial_time"] = sub_data["time_elapsed"].diff()/1e3

    # wm
    ## encoding
    break_mask = (sub_data['phase'] == 'encoding') & (sub_data['phase'].shift(1) != 'recognition')
    sub_data.loc[break_mask, 'trial_time'] = np.nan
    encoding_time = sub_data.loc[(sub_data.trial_type=="wm") & (sub_data.phase=="encoding"), 
                                 "trial_time"]
    encoding_time = encoding_time.loc[~encoding_time.isna()]
    encoding_times.append(pd.DataFrame(dict(
        session_id = [session_id] * len(encoding_time), 
        trial_time = encoding_time.to_list()
    )))

    ## recognition
    recognition_time = sub_data.loc[(sub_data.trial_type=="wm") & (sub_data.phase=="recognition"), 
                                    "trial_time"]
    recognition_times.append(pd.DataFrame(dict(
        session_id = [session_id] * len(recognition_time), 
        trial_time = recognition_time.to_list()
    )))
    
    # lm
    lm_time = sub_data.loc[(sub_data.trial_type=="lm") & (sub_data.phase=="recognition"), 
                           "trial_time"]
    lm_time = lm_time.loc[~lm_time.isna()]
    lm_times.append(pd.DataFrame(dict(
        session_id = [session_id] * len(lm_time), 
        trial_time = lm_time.to_list()
    )))

results = dict(
    encoding = pd.concat(encoding_times),
    recognition = pd.concat(recognition_times),
    lm_trials = pd.concat(lm_times),
)

fig, ax = plt.subplots(
    1,3,
    constrained_layout=True, 
    sharey=True,
    figsize=(12,5)
    )

for i, el in enumerate(results.items()):
    bars = sns.barplot(
        data=el[1], 
        x="session_id", 
        y="trial_time",
        color="w",
        edgecolor="k",
        errorbar=None,
        ax=ax[i]
    )

    scatter = sns.scatterplot(
        data=el[1],
        x="session_id",
        y="trial_time",
        size=1,
        legend=False,
        ax=ax[i],
        facecolor='none',
        edgecolor='grey'
    )

    ax[i].set_title(el[0])
    ax[i].axhline(30)
    ax[i].axhline(15, linestyle=":", c="k", alpha=.5)
    ax[i].axhline(10, linestyle=":", c="k", alpha=.5)
    ax[i].axhline(5, linestyle=":", c="k", alpha=.5)
    if i == 0: 
        ax[i].set_ylabel("Trial times")
    else: 
        ax[i].set_ylabel("")

all_figures.append(fig)
if show: 
    fig.show()

# %% Time outs
missing_data = []

i = 0 
for session, outdata in all_data.groupby("session_id"):  
    outdata = outdata.loc[outdata.phase=="recognition"]
    missing = dict(
        session_id = session,
        timed_out = outdata.timed_out.astype(int).sum())
    missing_data.append(missing)
    print(session)
missing_data = pd.DataFrame(missing_data)

fig, ax = plt.subplots(constrained_layout=True)
bar = sns.barplot(
    data=missing_data,
    x="session_id",
    y="timed_out",
    color="w",
    edgecolor="k",
    ax=ax
)

bar.set_xlabel("")
bar.set_ylabel("Time Outs")
bar.tick_params(axis='x', labelrotation=90)
all_figures.append(fig)
if show: 
    fig.show()

# %% Attention checks
attention_accuracy = []

i = 0 
for session, outdata in all_data.groupby("session_id"):  
    catch_trials = outdata.loc[
        (outdata.trial_type=="catch")&
        (outdata.phase=="recognition")].copy()
    catch_trials["correct"] = (catch_trials.correct_response.astype(int) == catch_trials.response.astype(int)).astype(int)
    if i>0: assert len(catch_trials) == ncatch, "Number of catch trials is not equal across sessions."
    
    ncatch = len(catch_trials)
    accuracy = (catch_trials.correct.sum()/ncatch)
    if accuracy<.8: print(f"Warning: {session} - {accuracy}")
    
    attention_accuracy.append(accuracy)

fig, ax = plt.subplots(constrained_layout=True)
session_ids = all_data.loc[~all_data.session_id.isna(), "session_id"].unique().astype(str)

bar = sns.barplot(
    x=session_ids,
    y=attention_accuracy, 
    color="w",
    edgecolor="k",
    ax=ax
)
bar.tick_params(axis='x', labelrotation=90)
all_figures.append(fig)

# %% Browser interaction
record_files = [f"./output_data/{wave_code}/{wave_code}-{i:03d}-{suffix}_browser_records.csv" 
               for i in subject_ids for suffix in "AB"]
record_files = filter(os.path.exists, record_files)

all_records = []
for file in record_files: 
    print(file)
    records = pd.read_csv(file)
    records["session_id"] = os.path.basename(file.rstrip("_ir.csv"))
    all_records.append(records)
all_records = pd.concat(all_records)
all_records["session_id"] = all_records.session_id.str.rstrip("_browser_record")

i, results = 0, []
for session, records in all_records.groupby("session_id"): 
    records = records.loc[records.trial>1]
    
    time_other_window = records.loc[records.event.isin(["blur","focus"])].time.diff()
    time_other_window = time_other_window.iloc[1::2].sum()/60e3
    
    count_df = records.groupby("event").trial.count().reset_index()
    count_df = count_df.rename(columns={"trial":"count"})
    count_df["subject_id"] = session
    count_df["time_other_window"] = time_other_window
    
    results.append(count_df)

results = pd.concat(results)
results = results.loc[results.event=="blur"]

fig, ax = plt.subplots(constrained_layout=True)
sns.barplot(
    data=results, 
    y="count", 
    x="subject_id", 
    hue="event", 
    ax=ax, 
    legend=False)
ax.set_ylabel("Count of tasks events")
all_figures.append(fig)

# %%
if show:
    plt.show(block=False)
    plt.pause(10)
    plt.close('all')

if save:
    pdf_file = f"./figures/quality_check/qc_{wave_code}.pdf"
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)

