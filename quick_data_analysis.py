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
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_kruskal_test, 'bugs_covered')
pivot_kruskal = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_median, 'bugs_covered')
pivot_median = groups_ranked.unstack()
groups_ranked = benchmark_blocks.apply(data_utils.benchmark_rank_by_mean, 'bugs_covered')
pivot_average = groups_ranked.unstack()
pivot_kruskal.to_csv(os.path.join(report_directory, 'kruskal.csv'))
pivot_median.to_csv(os.path.join(report_directory, 'median.csv'))
pivot_average.to_csv(os.path.join(report_directory, 'mean.csv'))
