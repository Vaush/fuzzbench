from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
report_directory = "/home/vaush/Work/temp_reports_02_06_2021/"
data_path = os.path.join(report_directory, 'data.csv.gz')
experiment_df = pd.read_csv(data_path)
description = "from cached data"
data_utils.validate_data(experiment_df)
experiment_df = data_utils.add_bugs_covered_column(experiment_df)
fuzzers = ["afl", "aflfast", "aflplusplus", "aflsmart", "entropic", "fairfuzz", "honggfuzz", "libfuzzer", "mopt"]
experiment_df = data_utils.filter_fuzzers(experiment_df, fuzzers)
experiment_df['benchmark'] = experiment_df['benchmark'].apply(lambda x: "php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0]))
coverage_report = False
coverage_dict = {}
if coverage_report:
    coverage_dict = coverage_data_utils.get_covered_regions_dict(
        experiment_df)
fuzzer_names = experiment_df.fuzzer.unique()
plotter = plotting.Plotter(fuzzer_names, True, False)
grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
grouping2 = ['fuzzer', 'benchmark', 'trial_id']
grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']
df = experiment_df.sort_values(grouping3)
df2 = df.groupby(grouping2).time.max()
l = list(list(zip(*(df2[df2 != 82800].index)))[2])
df = df[~df.trial_id.isin(l)]
df['firsts'] = ~df.duplicated(subset=grouping1) & ~df.crash_key.isna()
df['bugs_cumsum'] = df.groupby(grouping2)['firsts'].transform('cumsum')
df_first_bug = df.loc[df['firsts'] & (df['bugs_cumsum'] == 1.0)]
df_first_bug = df_first_bug.groupby(['fuzzer', 'benchmark']).mean()['time'].unstack().transpose()
df_first_bug.to_csv(os.path.join(report_directory, 'pivot_table_expected_time_to_first_bug.csv'))
df['max_bugs'] = (df.groupby(grouping2)['bugs_cumsum'].transform('max').astype(int))
df_last_bug = df.loc[df['firsts'] & (df['bugs_cumsum'] == df['max_bugs'])]
df_last_bug = df_last_bug.groupby(['benchmark','fuzzer']).mean()['time'].unstack()
df_last_bug.to_csv(os.path.join(report_directory, 'pivot_table_expected_time_to_last_bug.csv'))
first_bug_ph = data_utils.stat_tests.friedman_posthoc_tests(df_first_bug)['nemenyi']
last_bug_ph = data_utils.stat_tests.friedman_posthoc_tests(df_last_bug)['nemenyi']
if data_utils.stat_tests.friedman_test(df_first_bug) < 0.05:
    print("Time to first bug is significant")
    first_bug_ph = first_bug_ph.apply(lambda x: (x != -1) & (x < 0.05))
    first_bug_ph.to_csv(os.path.join(report_directory, 'significance_time_to_first_bug.csv'))
else:
    print("Time to first bug is insignificant")
if data_utils.stat_tests.friedman_test(df_last_bug) < 0.05:
    print("Time to last bug is significant")
    last_bug_ph = last_bug_ph.apply(lambda x: (x != -1) & (x < 0.05))
    last_bug_ph.to_csv(os.path.join(report_directory, 'significance_time_to_last_bug.csv'))
else:
    print("Time to last bug is insignificant")


