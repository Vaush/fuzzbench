def a12(lst1,lst2,rev=True):
  "how often is x in lst1 more than y in lst2?"
  more = same = 0.0
  for x in lst1:
    for y in lst2:
      if   x==y : same += 1
      elif rev     and x > y : more += 1
      elif not rev and x < y : more += 1
  return (more + 0.5*same)  / (len(lst1)*len(lst2))


def f(arg):
    def g(arg2):
        return arg2['bugs_covered'].values.tolist()
    by_fuzzer = arg.groupby('fuzzer').apply(g).reset_index().values.tolist()    
    fuzzers = [x for x in arg['fuzzer'].unique()]
    benchmark = str(arg['benchmark'].unique()[0])
    new_list = [[x[0]]+x[1] for x in by_fuzzer]
    final_list = []
    for l1 in new_list:
        res = []
        for l2 in new_list:
            res.append( a12(l1[1:], l2[1:]))
        final_list.append(res)    
    df = pd.DataFrame(final_list)
    df.columns = fuzzers
    df.index = fuzzers
    df.to_csv(os.path.join(report_directory, benchmark + "_vargha-delaney.csv"))
    return df

from analysis import plotting, data_utils, experiment_results, coverage_data_utils
import os
import pandas as pd
report_directory = "/home/vaush/Work/temp_reports/"
data_path = os.path.join(report_directory, 'data.csv.gz')
experiment_df = pd.read_csv(data_path)
description = "from cached data"
data_utils.validate_data(experiment_df)
experiment_df = data_utils.add_bugs_covered_column(experiment_df)
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
        "2020-12-19-bug")
experiment_snapshots_df = experiment_ctx._experiment_snapshots_df
benchmark_blocks = experiment_snapshots_df.groupby('benchmark')
groups_ranked = benchmark_blocks.apply(f)

