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
subject_ids = [1,3,4,5] #[2,3,4,5,6,7,9,10,11,21,22,23]

show = False
save = True

#%% set up colors
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

# %% LM and WM length
results = dict(
    total_duration = [], 
    LM_duration = [],
    WM_duration = []
)

for session, outdata in all_data.groupby("session_id"):   
    try:
        outdata["startTime_dt"] = pd.to_datetime(outdata.startTime,format='%Y-%m-%d %H:%M:%S')
        outdata["endTime_dt"] = pd.to_datetime(outdata.endTime,format='%Y-%m-%d %H:%M:%S')
    except:
        outdata['startTime_dt'] = pd.to_datetime(outdata.startTime, format='%I:%M:%S %p') 
        outdata['endTime_dt'] = pd.to_datetime(outdata.endTime, format='%I:%M:%S %p') 

    results["total_duration"].append(
        np.round((outdata['endTime_dt'].iloc[0]-outdata['startTime_dt'].iloc[0])
        .total_seconds()/60)
    )

    wm_trials = outdata.loc[(outdata.trial_type == "wm")]
    lm_trials = outdata.loc[(outdata.trial_type == "lm")|
                        (outdata.trial_type == "lm-recognition")]
    
    results["WM_duration"].append(np.round((wm_trials.time_elapsed.iloc[-1]-wm_trials.time_elapsed.iloc[0])/60e3))
    results["LM_duration"].append(np.round((lm_trials.time_elapsed.iloc[-1]-lm_trials.time_elapsed.iloc[0])/60e3))

def label_outlier(data, labels, ax):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    for duration, label in zip(data, labels):
        if duration < lower_bound or duration > upper_bound:
            print(f"Detected outlier {label}")
            ax.text(1.05, duration, label, fontsize=8, va='center')

fig, ax = plt.subplots(1,3,
                       sharey=True, 
                       constrained_layout=True)

i = 0
for k,data in results.items():
    ax[i].boxplot(data, widths=.8)
    ax[i].set_xlabel(k.replace("_"," ").title())
    ax[i].set_xticks([])
    label_outlier(data, labels, ax[i])
    i+=1

all_figures.append(fig)

# %% Missing Data
missing_data = []

i = 0 
for session, outdata in all_data.groupby("session_id"):  
    outdata = outdata.loc[outdata.phase=="recognition"]
    missing = dict(
        session_id = session,
        timed_out = outdata.timed_out.astype(int).sum()
        )
    missing_data.append(missing)
missing_data = pd.DataFrame(missing_data)

fig, ax = plt.subplots(constrained_layout=True)
bar = sns.barplot(
    data=missing_data,
    x="session_id",
    y="timed_out",
    ax=ax
)
bar.set_xlabel("")
bar.set_ylabel("Time Outs")

bar.tick_params(axis='x', labelrotation=90)
all_figures.append(fig)

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
bar = sns.barplot(x=all_data.session_id.unique(),
            y=attention_accuracy, 
            ax=ax)
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
sns.barplot(data=results, y="count", x="subject_id", hue="event", ax=ax, legend=False)
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

