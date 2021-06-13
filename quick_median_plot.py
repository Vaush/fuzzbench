from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
report_directory = "/home/vaush/Work/temp_reports_02_06_2021/"
data_path = os.path.join(report_directory, 'data.csv.gz')
experiment_df = pd.read_csv(data_path)
description = "from cached data"
data_utils.validate_data(experiment_df)
experiment_df = data_utils.add_bugs_covered_column(experiment_df)
fuzzers = ['afl', 'aflfast', 'aflsmart', 'aflplusplus', 'mopt', 'entropic', 'fairfuzz', 'libfuzzer', 'honggfuzz']
experiment_df = data_utils.filter_fuzzers(experiment_df, fuzzers)
benchmarks = experiment_df.benchmark.unique()
benchmarks = list(benchmarks)
if len(sys.argv) > 1 and sys.argv[1] == "compress":
    benchmarks.remove("njs_njs_process_script_fuzzer")
    benchmarks.remove("proj4_standard_fuzzer")
    benchmarks.remove("tpm2_tpm2_execute_command_fuzzer")
    benchmarks.remove("libarchive_libarchive_fuzzer")
experiment_df = data_utils.filter_benchmarks(experiment_df, benchmarks)
coverage_report = False
coverage_dict = {}
if coverage_report:
    coverage_dict = coverage_data_utils.get_covered_regions_dict(
        experiment_df)
fuzzer_names = experiment_df.fuzzer.unique()
plotter = plotting.Plotter(fuzzer_names, True, False)
experiment_ctx = experiment_results.ExperimentResults(
        experiment_df,
        coverage_dict,
        report_directory,
        plotter,
        "joined_experiment")
grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
grouping2 = ['fuzzer', 'benchmark', 'trial_id']
grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']
df = experiment_df.sort_values(grouping3)
df2 = df.groupby(grouping2).time.max()
l = list(list(zip(*(df2[df2 != 82800].index)))[2])
df = df[~df.trial_id.isin(l)]
df = df[df.time == 82800]
experiment_snapshots_df = df
experiment_snapshots_df['benchmark'] = experiment_snapshots_df['benchmark'].apply(lambda x: "php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0]))
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
plt.show()
