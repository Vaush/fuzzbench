import data_retrieval
import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
df = data_retrieval.retrieve_data(t)
save_directory = data_retrieval.get_save_directory(t)
df = df[~df.duplicated(subset=['fuzzer','benchmark','trial_id', 'time'])]
df['time'] = df['time'].apply(lambda x: x/3600)
df2 = df[~df.duplicated(subset=['fuzzer', 'benchmark','trial_id'])]
df2['time'].values[:] = 0
df2['bugs_covered'].values[:] = 0
df2['edges_covered'].values[:] = 0
df2['crash_key'].values[:] = np.nan
df = pd.concat([df, df2], ignore_index=True).sort_values(by=['benchmark', 'fuzzer', 'trial_id', 'time'])
grouped = df.groupby(['benchmark'])[['fuzzer','trial_id','time','bugs_covered']]

ncols=5
nrows = int(np.ceil(grouped.ngroups/ncols))

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(32,18), sharey=False, sharex=True)

for (key, ax) in zip(grouped.groups.keys(), axes.flatten()):
    t = grouped.get_group(key).groupby(['fuzzer','time']).bugs_covered.mean()
    t = t.reset_index()
    ax.set_xlabel("Hours elapsed")
    ax.set_ylabel("Bugs discovered")
    ax.set_xticks(np.arange(0,24))
    ax.title.set_text(key)
    for k, g in t.groupby(['fuzzer']):
        ax.plot(g['time'], g['bugs_covered'], label=k)
ax.legend(bbox_to_anchor=(1.04,-0.04), loc="lower left")
fig.tight_layout()
#plt.show()
plt.savefig(os.path.join(save_directory, "behaviour_over_time_landscape.png"),dpi=300)

