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
grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
grouping2 = ['fuzzer', 'benchmark', 'trial_id']
grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']

df['min_bugs'] = (df[df.bugs_covered > 0].groupby(grouping2)['bugs_covered'].transform("min").astype(int))
df['firsts'] = ~df.duplicated(subset=(grouping2+['bugs_covered'])) & (df.bugs_covered == df.min_bugs) & (df.bugs_covered != 0)
df_first_bug = df[df.firsts].groupby(['fuzzer', 'benchmark']).mean()['time'].unstack().transpose().apply(lambda x: round(x/60,2))
df_first_bug.to_csv(os.path.join(save_directory, 'pivot_table_expected_time_to_first_bug.csv'))
df['max_bugs'] = (df.groupby(grouping2)['bugs_covered'].transform('max').astype(int))
df['firsts'] = ~df.duplicated(subset=(grouping2 + ['bugs_covered'])) & (df.bugs_covered == df.max_bugs) & (df.bugs_covered != 0)
df_last_bug = df[df.firsts].groupby(['benchmark','fuzzer']).mean()['time'].unstack().apply(lambda x: round(x/60,2))
df_last_bug.to_csv(os.path.join(save_directory, 'pivot_table_expected_time_to_last_bug.csv'))
first_bug_ph = data_utils.stat_tests.friedman_posthoc_tests(df_first_bug)['nemenyi']
last_bug_ph = data_utils.stat_tests.friedman_posthoc_tests(df_last_bug)['nemenyi']
truth_table = lambda x: ("\cellcolor{lightgrey}"+str(round(x,3))) if (x != -1 and x < 0.05) else round(x,3)
if data_utils.stat_tests.friedman_test(df_first_bug) < 0.05:
    print("Time to first bug is significant")
    first_bug_ph = first_bug_ph.applymap(truth_table)
    first_bug_ph.to_csv(os.path.join(save_directory, 'significance_time_to_first_bug.csv'))
else:
    print("Time to first bug is insignificant")
if data_utils.stat_tests.friedman_test(df_last_bug) < 0.05:
    print("Time to last bug is significant")
    last_bug_ph = last_bug_ph.applymap(truth_table)
    last_bug_ph.to_csv(os.path.join(save_directory, 'significance_time_to_last_bug.csv'))
else:
    print("Time to last bug is insignificant")


