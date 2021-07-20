import glob
from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
import json
import sys, getopt
from sortedcontainers import SortedDict
import csv
import datetime
import numpy as np
import statistics
import matplotlib.pyplot as plt

report_directory = "/home/vaush/Work/temp_reports_02_06_2021/"


def to_datetime(string):
    return datetime.datetime.strptime(string, "%Y%m%d%H%M")


def get_days_to_find(bugs, bug_id):
    x = to_datetime(bugs[bug_id]['report_date']) - to_datetime(bugs[bug_id]['regression_range_end'])
    #print(bug_id, bugs[bug_id]['report_date'], bugs[bug_id]['regression_range_end'])
    x = x.days + x.seconds/86400
    return max(0,x)


def get_ground_truth_data():
    projects = {}
    reverse_lookup = {}
    all_ids = []
    for filename in glob.glob("/home/vaush/Work/temp_reports_02_06_2021/ground_truth_logs/all_experiments/*.log"):
        f = open(filename, mode="r")
        content = f.read()
        f.close()
        ids,keys = content.split("\n\n\n\n\n\n\n\n")
        ids = ids.split("\n")
        keys = keys.split("\n\n\n\n")
        keys = [x + "\n" for x in keys]
        all_ids += ids
        project_name = filename.split("/")[-1].split(".")[0]
        projects[project_name] = set(zip(ids,keys))
        reverse_lookup = {**reverse_lookup, **{x[1]:(x[0], project_name) for x in zip(ids, keys)}}
    return projects, reverse_lookup, all_ids

def get_bugs_found(groupby_trial=True):
    data_path = os.path.join(report_directory, 'data.csv.gz')
    experiment_df = pd.read_csv(data_path)
    description = "from cached data"
    data_utils.validate_data(experiment_df)
    experiment_df = data_utils.add_bugs_covered_column(experiment_df)
    fuzzers = ["afl", "aflfast", "aflplusplus", "aflsmart", "entropic", "fairfuzz", "honggfuzz", "libfuzzer", "mopt"]
    experiment_df = data_utils.filter_fuzzers(experiment_df, fuzzers)
    benchmarks = experiment_df.benchmark.unique()
    benchmarks = list(benchmarks)
    experiment_df = data_utils.filter_benchmarks(experiment_df, benchmarks)
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
    final_grouping = grouping2 if groupby_trial else ['benchmark','fuzzer']
    grouping3 = ['fuzzer', 'benchmark', 'trial_id', 'time']
    df = experiment_df.sort_values(grouping3)
    df = df.apply(lambda x: np.where(x.isna(),"",x))
    df = df[~df.duplicated(subset=grouping1)]
    df2 = df.groupby(final_grouping)['crash_key'].apply(lambda x: set(x)-{""})
    bugs_found = df2.to_dict()
    return bugs_found

def save_hits_misses():
    projects, reverse_lookup, all_ids = get_ground_truth_data()
    bugs_found = get_bugs_found()
    ground_truth_found = []
    for key in bugs_found:
        hit = 0
        miss = 0
        for crash_key in bugs_found[key]:
            if crash_key in reverse_lookup:
                hit += 1
            else:
                miss += 1
        #if hit > 0:
            #print(key)
        ground_truth_found.append([*key,hit,miss])
    df = pd.DataFrame(ground_truth_found, columns=['fuzzer','benchmark','trial_id','hits', 'misses'])
    df2 = df.copy()
    df = df.groupby(["benchmark", "fuzzer"]).median()[["hits", "misses"]]
    df["Hits, Misses"] = df["hits"].astype(str) + ", " + df["misses"].astype(str)
    df = df["Hits, Misses"].unstack()
    df.to_csv(os.path.join(report_directory, "hits_and_misses.csv"))
    return df2

def get_ground_truth_found():
    projects, reverse_lookup, all_ids = get_ground_truth_data()
    bugs_found = get_bugs_found()
    ground_truth_found = []
    res_projects = {"php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0]):set() for x in projects}
    for key in bugs_found:
        hit = 0
        miss = 0
        for crash_key in bugs_found[key]:
            if crash_key in reverse_lookup:
                if key[1] not in res_projects:
                    res_projects[key[1]] = set()
                res_projects[key[1]].add(reverse_lookup[crash_key][0])
    return res_projects

def main():
    save_hits_misses()

if __name__ == "__main__":
    main()
