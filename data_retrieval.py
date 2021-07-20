report_directory = "/home/vaush/Work/temp_reports_02_06_2021/"


def retrieve_data(t = 0):
    if t == 0:
        return retrieve_normal_data()
    elif t == 1:
        return retrieve_gt_hit_or_miss_data()
    else:
        return retrieve_gt_hit_or_miss_data(False)


def get_save_directory(t = 0):
    import os
    import pathlib
    paths = ["unique_crashes", "ground_truth_bugs_hit", "ground_truth_bugs_missed"]
    p = os.path.join(report_directory, paths[t])
    pathlib.Path(p).mkdir(parents=True, exist_ok=True) 
    return p


def retrieve_normal_data():
    from analysis import plotting, data_utils, experiment_results, coverage_data_utils
    import os
    import pandas as pd
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
    grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
    grouping2 = ['fuzzer', 'benchmark', 'trial_id']
    grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']
    df = experiment_df.sort_values(grouping3)
    df2 = df.groupby(grouping2).time.max()
    l = list(list(zip(*(df2[df2 != 82800].index)))[2])
    df = df[~df.trial_id.isin(l)]
    return df

def retrieve_gt_hit_or_miss_data(hit=True):
    from ground_truth import get_ground_truth_data
    df = retrieve_normal_data()
    projects, reverse_lookup, all_ids = get_ground_truth_data()
    grouping1 = ['fuzzer', 'benchmark', 'trial_id', 'crash_key']
    grouping2 = ['fuzzer', 'benchmark', 'trial_id']
    grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']
    df["firsts"] = ~df.duplicated(subset=grouping1) & ~df.crash_key.isna() & ~(hit ^ df.crash_key.isin(reverse_lookup))
    df["bugs_cumsum"] = df.groupby(grouping2)['firsts'].transform("cumsum")
    df["bugs_covered"] = (df.groupby(grouping3)['bugs_cumsum'].transform('max').astype(int))
    new_df = df.drop(columns=['bugs_cumsum', 'firsts'])
    return new_df
