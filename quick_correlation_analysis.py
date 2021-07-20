from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
import data_retrieval
import sys
import scipy.stats as ss
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)
df = data_retrieval.retrieve_data(t)
print(df.benchmark.unique())
df = df[~(df.edges_covered == 0)]
print(df.benchmark.unique())
df_no_grouping = df.copy()
df_bench_grouping = df.groupby(["benchmark"])
df_fuzzer_grouping = df.groupby(["fuzzer"])
df_bench_fuzzer_grouping = df.groupby(["benchmark", "fuzzer"])
df_no_grouping = df_no_grouping[["edges_covered", "bugs_covered"]]
df_bench_grouping = df_bench_grouping[["edges_covered", "bugs_covered"]]
df_fuzzer_grouping = df_fuzzer_grouping[["edges_covered", "bugs_covered"]]
df_bench_fuzzer_grouping = df_bench_fuzzer_grouping[["edges_covered", "bugs_covered"]]

with open(os.path.join(save_directory, "bug_coverage_correlation_no_grouping"), "w") as f:
    f.write(str(ss.spearmanr(df_no_grouping)))

df_bench_grouping.apply(ss.spearmanr).apply(lambda x: (round(x[0],3), round(x[1],4))).to_csv(os.path.join(save_directory,"bug_coverage_correlation_bench_grouping.csv"))
df_fuzzer_grouping.apply(ss.spearmanr).apply(lambda x: (round(x[0],3), round(x[1],4))).to_csv(os.path.join(save_directory,"bug_coverage_correlation_fuzzer_grouping.csv"))
df_bench_fuzzer_grouping.apply(lambda x: (round(ss.spearmanr(x)[0],3), round(ss.spearmanr(x)[1]), 4)).unstack().to_csv(os.path.join(save_directory,"bug_coverage_correlation_bench_fuzzer_grouping.csv"))
