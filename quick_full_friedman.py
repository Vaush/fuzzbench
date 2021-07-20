from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd

import data_retrieval
import sys
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)
df = data_retrieval.retrieve_data(t)
benchmarks = list(df.benchmark.unique())
fuzzers = ["afl", "aflfast", "aflplusplus", "aflsmart", "entropic", "fairfuzz", "honggfuzz", "libfuzzer", "mopt"]
df = data_utils.drop_uninteresting_columns(df)
df = df.groupby(['benchmark','fuzzer','trial_id']).max()
benchmark_data = {}
for index, row in df.iterrows():
    b = row.name[0]
    f = row.name[1]
    if b not in benchmark_data:
        benchmark_data[b] = {}
    if f not in benchmark_data[b]:
        benchmark_data[b][f] = []
    benchmark_data[b][f].append((row.name[2], row['bugs_covered']))
rows = []
row_names = []
for benchmark in benchmark_data:
    stop = False
    i = 0
    while not stop:
        row = []
        for fuzzer in fuzzers:
            l = benchmark_data[benchmark][fuzzer]
            if not l:
                stop = True
                break
            v = l.pop()
            row.append(v[1])
        else:
            rows.append(row)
            row_names.append(benchmark + "_" + str(i))
            i += 1
new_df = pd.DataFrame(rows, columns=fuzzers, index=row_names)
p_value = data_utils.stat_tests.friedman_test(new_df) 
print("P_VALUE", "=", p_value)
if p_value < 0.05:
    print("Friedman was significant")
    ph = data_utils.stat_tests.friedman_posthoc_tests(new_df)
    truth_table = lambda x: ("\cellcolor{lightgrey}"+str(round(x,3))) if (x != -1 and x < 0.05) else round(x,3)
    ph['conover'].applymap(truth_table).to_csv(os.path.join(save_directory, 'friedman_ph_conover_truth_table.csv'))
    ph['nemenyi'].applymap(truth_table).to_csv(os.path.join(save_directory, 'friedman_ph_nemenyi_truth_table.csv'))
else:
    print("Friedman was not significant")
