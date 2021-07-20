from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
import data_retrieval
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)
df = data_retrieval.retrieve_data(t)
benchmarks = df.benchmark.unique()
benchmarks = list(benchmarks)
compressed = len(sys.argv) > 1 and sys.argv[1] == "compress"
if compressed:
    benchmarks.remove("njs")
    benchmarks.remove("proj4")
    benchmarks.remove("tpm2")
    benchmarks.remove("libarchive")
df = data_utils.filter_benchmarks(df, benchmarks)
experiment_snapshots_df = df[df.time == 82800]
fuzzer_names = experiment_snapshots_df.fuzzer.unique()
benchmark_blocks = experiment_snapshots_df.groupby('benchmark')
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_kruskal_test, 'bugs_covered')
pivot_kruskal = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_median, 'bugs_covered')
pivot_median = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_mean, 'bugs_covered')
pivot_average = groups_ranked.unstack()
#fig, ax = plt.subplots()
ax = pivot_median.plot()
ax.set_xticks(np.arange(len(experiment_snapshots_df.benchmark.unique())))
ax.set_xticklabels(experiment_snapshots_df.benchmark.unique())
figure = plt.gcf()  # get current figure

figure.set_size_inches(32, 18)
filename = "pivot_median_plot" + ("_excluding_zeros" if compressed else "") + ".png"
plt.savefig(os.path.join(save_directory, filename), dpi=300, bbox_inches='tight')

