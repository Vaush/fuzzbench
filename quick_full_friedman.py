from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
report_directory = "/home/vaush/Work/temp_reports_02_06_2021/"
data_path = os.path.join(report_directory, 'data.csv.gz')
experiment_df = pd.read_csv(data_path)
description = "from cached data"
data_utils.validate_data(experiment_df)
experiment_df = data_utils.add_bugs_covered_column(experiment_df)
fuzzers = ['afl', 'aflfast', 'aflsmart', 'aflplusplus', 'mopt', 'entropic', 'fairfuzz', 'libfuzzer', 'honggfuzz']
experiment_df = data_utils.filter_fuzzers(experiment_df, fuzzers)
experiment_df['benchmark'] = experiment_df['benchmark'].apply(lambda x: "php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0]))
grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
grouping2 = ['fuzzer', 'benchmark', 'trial_id']
grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']

df = experiment_df.sort_values(grouping3)
df2 = df.groupby(grouping2).time.max()
l = list(list(zip(*(df2[df2 != 82800].index)))[2])
df = df[~df.trial_id.isin(l)]
benchmarks = list(df.benchmark.unique())
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
if data_utils.stat_tests.friedman_test(new_df) < 0.05:
    print("Friedman was significant")
    ph = data_utils.stat_tests.friedman_posthoc_tests(new_df)
    truth_table = lambda x: True if (x != -1 and x < 0.05) else False
    ph['conover'].applymap(truth_table).to_csv(os.path.join(report_directory, 'friedman_ph_conover_truth_table.csv'))
    ph['nemenyi'].applymap(truth_table).to_csv(os.path.join(report_directory, 'friedman_ph_nemenyi_truth_table.csv'))
else:
    print("Friedman was not significant")
