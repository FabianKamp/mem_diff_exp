# %%
import pandas as pd 
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pickle

#%% variable set up
wave_code = "M-V1"
subject_ids = np.arange(1,100) #[2,3,4,5,6,7,9,10,11,21,22,23]

# exclude = 6
# subject_ids = subject_ids[subject_ids!=exclude]

save = True

#%% set up colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971","#B39CD4"]
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
n_subjects = all_data.session_id.nunique()

# %%
lm_data = all_data.loc[(all_data.trial_type=="lm")].copy()

lm_data.response = lm_data.response.astype('Int64')
lm_data.correct_response = lm_data.correct_response.astype('Int64')
lm_data.encoding_time = lm_data.encoding_time.astype('Int64')
lm_data.condition = lm_data.condition.astype('Int64')

# include only valid trials
NAN = 9999
lm_data.loc[lm_data.response.isna(), "response"] = NAN
print("NA responses: ", np.sum(lm_data.response==NAN))

# add col with correct
lm_data["correct"] = (lm_data.response == lm_data.correct_response)


# %% LM short vs long conditions
## barplots
cols = 5
rows = n_subjects//cols+1
fig_lm, ax = plt.subplots(
    rows, 
    cols, 
    figsize=(cols*2, rows*2), 
    sharey=True,
    constrained_layout=True)
all_figures.append(fig_lm)
fig_lm.suptitle(f"{wave_code} - LM: visual vs semantic")
fax = ax.flatten()

i = 0
all_results = []
for s, sub_df in lm_data.groupby("session_id"):
    sub_results = (
        sub_df.groupby(["encoding_time", "condition_name"])["correct"]
            .agg(lambda x: np.round(x.sum()/len(x), 2))
            .reset_index()
        )
    sub_results = sub_results.rename(
        columns= {"correct": "accuracy"})
    
    sub_results["subject_id"]= int(s.split("-")[-2])
    all_results.append(sub_results)

    bar = sns.barplot(data=sub_results, 
                      x="encoding_time", 
                      hue = "condition_name",
                      y="accuracy", 
                      ax=fax[i])
    
    bar.axhline(.5,ls=":")
    bar.set_title(int(s.split("-")[-2]))
    bar.set_xlabel('')
    if i>0: 
        bar.get_legend().remove()
    else:
        bar.legend(fontsize=6, markerscale=0.5)
        bar.get_legend().set_title('')


    i+=1

# delete empty axes
for j in range(i,cols*rows): 
    fax[j].remove()

all_results = pd.concat(all_results)
figure_data.update(fig5=all_results)

# %%
if save:
    pdf_file = f"./figures/descriptive/descr_{wave_code}_lm.pdf"
    data_file = f"./figures/descriptive/descr_{wave_code}_lm.pkl"
    pickle.dump(figure_data, open(data_file, "wb"))
    with PdfPages(pdf_file) as pdf:
        for f in all_figures:
            pdf.savefig(f)

# %%
