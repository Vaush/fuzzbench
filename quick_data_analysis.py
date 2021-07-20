from analysis import data_utils
import data_retrieval
import sys
import os
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)
df = data_retrieval.retrieve_data(t) 
experiment_snapshots_df = df[df.time == 82800]
benchmark_blocks = experiment_snapshots_df.groupby('benchmark')
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_kruskal_test, 'bugs_covered')
pivot_kruskal = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_median, 'bugs_covered')
pivot_median = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_mean, 'bugs_covered')
pivot_average = groups_ranked.unstack()
pivot_kruskal.to_csv(os.path.join(save_directory, 'kruskal.csv'))
pivot_median.to_csv(os.path.join(save_directory, 'median.csv'))
pivot_average.to_csv(os.path.join(save_directory, 'mean.csv'))
