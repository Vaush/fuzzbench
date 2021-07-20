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
    df.to_csv(os.path.join(save_directory, benchmark + "_vargha-delaney.csv"))
    return df

df = data_retrieval.retrieve_data(t)
experiment_snapshots_df = df[df.time == 82800].copy()
experiment_snapshots_df['benchmark'] = experiment_snapshots_df['benchmark'].apply(lambda x: "php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0]))
benchmark_blocks = experiment_snapshots_df.groupby('benchmark')
groups_ranked = benchmark_blocks.apply(f)

