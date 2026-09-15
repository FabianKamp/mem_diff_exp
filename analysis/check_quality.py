# %%
import ast
import pandas as pd 
import os
import glob
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import textwrap

#%% 
# variable set up
wave_code = "M-V1"
subject_ids = np.arange(1,120) #[2,3,4,5,6,7,9,10,11,21,22,23]

# exclude 34
subject_ids = subject_ids[subject_ids!=34]

all_figures = []
save = True

#%% 
# load files
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
labels = all_data.session_id.unique()

all_figures = []

# %% 
# bot checks 
bot_checks = all_data.loc[(all_data.trial_type == "bot-check")]

fig, ax = plt.subplots(
    figsize=(6, 6),
    constrained_layout=True
    )

# header
header_pos = 0.95  
ax.text(0.05, header_pos, "Bot Check", transform=ax.transAxes, fontsize=14, verticalalignment='top')

# text
text_pos = .85
for sid, bot_check in bot_checks.groupby("session_id"):
    text = "   ".join([sid, bot_check.response.to_string(index=False)])
    ax.text(0.05, text_pos, text, transform=ax.transAxes, fontsize=9, verticalalignment='top')
    text_pos -= 0.04 
ax.axis('off')  

all_figures.append(fig)

# %%
# captcha 
survey_data = all_data.loc[(all_data.trial_type == "survey")|(all_data.trial_type == "captcha-check")]

# fig
fig, ax = plt.subplots(
    figsize=(6, 6),
    constrained_layout=True
    )

# header
header_pos = 0.95  
ax.text(0.05, header_pos, "Captcha Response", transform=ax.transAxes, fontsize=14, verticalalignment='top')

# text
text_pos = .85
for (sid, response) in survey_data.groupby("session_id")["response"]:
    response_dict = ast.literal_eval(response.iloc[0])
    for key in ['captcha_input',  'Type the word you see in the image above']: 
        if key not in response_dict: continue
        captcha_response = response_dict[key]
        text = "   ".join([sid, captcha_response])
        ax.text(0.05, text_pos, text, transform=ax.transAxes, fontsize=9, verticalalignment='top')
        text_pos -= 0.04

ax.axis('off')  
all_figures.append(fig)


# %% 
# feedback form 
feedback_data = all_data.loc[(all_data.trial_type == "feedback-slide")]
fig, ax = plt.subplots(
    figsize=(6, 6),
    constrained_layout=True
    )

# header
header_pos = 0.95   
ax.text(0.05, header_pos , "Feedback", transform=ax.transAxes, fontsize=14, verticalalignment='top')

# text
text_pos = .85
for sid, session_feedback in feedback_data.groupby("session_id"):
    feedback = ast.literal_eval(session_feedback.response.item())["feedback"]
    if feedback is not None: 
        text = "   ".join([sid, feedback])
        text = "   ".join([sid, feedback])
        wrapped = textwrap.fill(text, width=80)  
        ax.text(0.05, text_pos, wrapped, transform=ax.transAxes, fontsize=9, verticalalignment='top')
        text_pos -= 0.05 * (wrapped.count('\n') + 1) 

ax.axis('off')  
all_figures.append(fig)

# %% 
# annotating function
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
# %% 
# plot section lengths
results = []
for session, subdata in all_data.groupby("session_id"):   
    wm_trials = subdata.loc[(subdata.trial_type == "wm")]
    lm_trials = subdata.loc[(subdata.trial_type == "lm")]
    
    try:
        time_dict = dict(
            session_id = session, 
            instruction = np.round(wm_trials.time_elapsed.iloc[0]/60e3), 
            WM = np.round((wm_trials.time_elapsed.iloc[-1]-wm_trials.time_elapsed.iloc[0])/60e3),
            LM = np.round((lm_trials.time_elapsed.iloc[-1]-lm_trials.time_elapsed.iloc[0])/60e3),
            total = np.round(subdata.time_elapsed.iloc[-1]/60e3)
            )

        results.append(time_dict)

    except: 
        print(f"Error processing {session}")


results = pd.DataFrame(results).melt(
    id_vars="session_id", 
    var_name="section", 
    value_name="duration"
    )

print(results.groupby("section").median("duration"))

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
annotate_outliers(
    data=results, 
    x ="section", 
    y="duration",
    label_col="session_id",
    ax=ax
)
all_figures.append(fig)

# %% 
# time outs
time_outs = []

i = 0 
for session, outdata in all_data.groupby("session_id"):  
    outdata = outdata.loc[outdata.phase=="recognition"]
    missing = dict(
        session_id = session,
        timed_out = outdata.timed_out.astype(int).sum())
    time_outs.append(missing)
    print(session)
time_outs = pd.DataFrame(time_outs)

fig, ax = plt.subplots(constrained_layout=True)
bar = sns.barplot(
    data=time_outs.loc[time_outs.timed_out>0],
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


# %% 
# attention checks
attention_accuracy = []
i = 0 
for session, outdata in all_data.groupby("session_id"):  
    catch_trials = outdata.loc[
        (outdata.trial_type=="catch")&
        (outdata.phase=="recognition")].copy()
    print("No response catch trials:", catch_trials.response.isna().sum())
    catch_trials = catch_trials.loc[catch_trials.response.notna()]
    
    catch_trials["correct"] = (catch_trials.correct_response.astype(int) == catch_trials.response.astype(int)).astype(int)
    if i>0: assert len(catch_trials) == ncatch, "Number of catch trials is not equal across sessions."
    
    ncatch = len(catch_trials)
    accuracy = (catch_trials.correct.sum()/ncatch)
    errors = (ncatch-catch_trials.correct.sum())
    if accuracy<.8: print(f"Warning: {session} - {accuracy}")
    
    attention_accuracy.append(dict(
        session_id = session,
        accuracy = accuracy,
        errors = errors
    ))

attention_checks = pd.DataFrame(attention_accuracy)
fig, ax = plt.subplots(constrained_layout=True)
bar = sns.barplot(
    data=attention_checks.loc[attention_checks.accuracy<1],
    x="session_id",
    y="errors", 
    color="w",
    edgecolor="k",
    ax=ax
)
bar.tick_params(axis='x', labelrotation=90)
all_figures.append(fig)

# %% 
# Browser interaction
record_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}-{suffix}_browser_records.csv" 
               for i in subject_ids for suffix in "ABC"]
record_files = filter(os.path.exists, record_files)

all_records = []
for file in record_files: 
    records = pd.read_csv(file)
    records["session_id"] = os.path.basename(file.rstrip("_ir.csv"))
    all_records.append(records)
all_records = pd.concat(all_records)
all_records["session_id"] = all_records.session_id.str.rstrip("_browser_record")

i, browser_counts = 0, []
for session, records in all_records.groupby("session_id"): 
    records = records.loc[records.trial>1]
    
    time_other_window = records.loc[records.event.isin(["blur","focus"])].time.diff()
    time_other_window = time_other_window.iloc[1::2].sum()/60e3
    
    count_df = records.groupby("event").trial.count().reset_index()
    count_df = count_df.rename(columns={"trial":"count"})
    count_df["session_id"] = session
    count_df["time_other_window"] = time_other_window
    
    browser_counts.append(count_df)

browser_counts = (
    pd.concat(browser_counts)
    .pivot(index="session_id", columns="event",values="count")
    .reset_index()
)

fig, ax = plt.subplots(constrained_layout=True)
sns.barplot(
    data=browser_counts, 
    y="blur", 
    x="session_id", 
    facecolor="none",
    edgecolor="black",
    ax=ax, 
    legend=False)
ax.tick_params(axis='x', labelrotation=90)

fig, ax = plt.subplots(constrained_layout=True)
sns.barplot(
    data=browser_counts, 
    y="fullscreenexit", 
    x="session_id", 
    facecolor="none",
    edgecolor="black",
    ax=ax, 
    legend=False)
ax.tick_params(axis='x', labelrotation=90)


all_figures.append(fig)

# %% 
# # reaction times
wm_rt =[]

for session_id, sub_data in all_data.groupby("session_id"):
    # wm
    wm_times = sub_data.loc[
        (sub_data.trial_type=="wm") & 
        (sub_data.phase=="recognition"), 
        "rt"]/1e3
    wm_rt.append(pd.DataFrame(dict(
        session_id = [session_id] * len(wm_times), 
        trial_time = wm_times.to_list()
    )))

wm_rt = pd.concat(wm_rt).reset_index()

fig, ax = plt.subplots(
    constrained_layout=True, 
    sharey=True,
    figsize=(12,5)
    )

bars = sns.barplot(
    data=wm_rt, 
    x="session_id", 
    y="trial_time",
    color="w",
    edgecolor="k",
    errorbar=None,
    ax=ax
)

scatter = sns.scatterplot(
    data=wm_rt,
    x="session_id",
    y="trial_time",
    size=1,
    legend=False,
    ax=ax,
    facecolor='none',
    edgecolor='grey'
)

ax.set_title("WM")
ax.axhline(30)
ax.axhline(15, linestyle=":", c="k", alpha=.5)
ax.axhline(10, linestyle=":", c="k", alpha=.5)
ax.axhline(5, linestyle=":", c="k", alpha=.5)
ax.set_ylabel("Reaction times")
ax.set_ylabel("")
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right')

all_figures.append(fig)

# %% 
# trial times
preload_times, recognition_times = [], []
for session_id, sub_data in all_data.groupby("session_id"):
    session_id = str(int(session_id.split("-")[-2]))
    sub_data["trial_time"] = sub_data["time_elapsed"].diff()/1e3

    ## loading
    preload_time = sub_data.loc[sub_data.trial_type=="preload", "preload_duration"]
    preload_time = preload_time.loc[~preload_time.isna()]/1e3
    preload_times.append(pd.DataFrame(dict(
        session_id = [session_id] * len(preload_time), 
        trial_time = preload_time.to_list()
    )))

    ## recognition
    recognition_time = sub_data.loc[
        (sub_data.trial_type=="wm") & 
        (sub_data.phase=="recognition"), 
        "trial_time"
        ]
    recognition_times.append(pd.DataFrame(dict(
        session_id = [session_id] * len(recognition_time), 
        trial_time = recognition_time.to_list()
    )))

results = {
    "preload time": pd.concat(preload_times),
    "recognition time": pd.concat(recognition_times),
}

fig, ax = plt.subplots(
    constrained_layout=True, 
    sharey=True,
    figsize=(12,5)
    )

bars = sns.barplot(
    data=results["preload time"], 
    x="session_id", 
    y="trial_time",
    color="w",
    edgecolor="k",
    errorbar=None,
    ax=ax
)

scatter = sns.scatterplot(
    data=results["preload time"], 
    x="session_id",
    y="trial_time",
    size=1,
    legend=False,
    facecolor='none',
    edgecolor='grey',
    ax=ax
)

ax.set_title("Preload Time")
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right')
ax.axhline(15, linestyle=":", c="k", alpha=.5)
ax.axhline(10, linestyle=":", c="k", alpha=.5)
ax.axhline(5, linestyle=":", c="k", alpha=.5)
ax.axhline(2, linestyle=":", c="k", alpha=.5)
all_figures.append(fig)

# %% 
# mouse checks
# def path_straightness(x, y):
#     direct = np.sqrt((x[-1]-x[0])**2 + (y[-1]-y[0])**2)
#     path_len = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
#     return direct / path_len if path_len > 0 else 1 

# def velocity_variance(x, y):
#     distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
#     return np.std(distances) / np.mean(distances) if np.mean(distances) > 0 else 0

# def angular_changes(x, y):
#     dx, dy = np.diff(x), np.diff(y)
#     angles = np.arctan2(dy, dx)
#     angle_changes = np.abs(np.diff(angles))
#     return np.mean(angle_changes)

# def acceleration_pattern(x, y):
#     distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
#     acceleration = np.diff(distances)
#     return np.std(acceleration)


# mouse_data = all_data.loc[all_data.trial_type == "mouse-movement-check"]

# cols = 3
# rows = n_subjects//cols+1
# fig, ax = plt.subplots(rows, cols, 
#             figsize=(cols*4, rows*4), 
#             sharey=True,
#             sharex=True,
#             constrained_layout=True
#         )
# fax = ax.flatten()

# error_count, i = 0, 0
# for sid, mouse_session in mouse_data.groupby("session_id"): 
#     mouse_summary = []
#     for _, row in mouse_session.iterrows():
#         if type(row.mouse_movement_x) != str or type(row.mouse_movement_y) != str:
#             error_count += 1
#             continue

#         x = ast.literal_eval(row.mouse_movement_x)
#         x = np.array(x)
#         x_centered = x - x[0]
#         y = ast.literal_eval(row.mouse_movement_y)
#         y = np.array(y) 
#         y_centered = y - y[0]

#         if len(x)<5: 
#             continue

#         fax[i].plot(x_centered, y_centered, 'k-o', markersize=1.5, linewidth=.3)
#         fax[i].plot(0, 0, 'ro', markersize=2) 
#         fax[i].set_title(sid)

#         mouse_summary.append(dict(
#           straightness = path_straightness(x,y), 
#           velocity_var = velocity_variance(x,y),  
#           angular_changes = angular_changes(x,y),  
#           acc_pattern = acceleration_pattern(x,y)  
#         ))

#     mouse_summary = pd.DataFrame(mouse_summary).mean().round(2)
#     # Simple approach
#     fax[i].text(
#         0.05, 0.99, 
#         mouse_summary.to_string(), 
#         transform=fax[i].transAxes,
#         fontsize=10, 
#         verticalalignment='top', 
#         family='monospace'
#         )

#     i += 1

# _ = [ax.remove() for ax in fax[i:]]
# all_figures.append(fig)

# %% 
# aggregate into data quality file
data_quality = (time_outs
    .merge(attention_checks, on="session_id", how="outer")
    .rename(columns=dict(
        timed_out = "time_outs",
        accuracy = "attention_check_accuracy", 
        errors = "attention_check_errors"
        ))
    .merge(browser_counts[["session_id", "blur", "fullscreenexit"]], on="session_id", how="outer")
    .fillna(0)
)
data_quality.to_csv(f"./output_data/data_quality/qc_{wave_code}.csv", index=False)

# %%
# save
if save:
    pdf_file = f"./figures/quality_check/qc_{wave_code}_wm.pdf"
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)

# %%
