#!/bin/bash
source .venv/bin/activate
python3 ground_truth.py
python3 quick_get_time_to_find_ground_truth_discovered_bugs.py
python3 quick_get_ground_truth_time_to_find.py
for i in {0..2}
do
	python3 quick_data_analysis.py $i
	python3 quick_behaviour_over_time_plot.py $i
	python3 quick_correlation_analysis.py $i
	python3 quick_expected_time.py $i
	python3 quick_full_friedman.py $i
	python3 quick_get_time_to_find_ground_truth_discovered_bugs.py $i
	python3 quick_median_plot.py $i
	python3 quick_vargha_delaney.py $i
	python3 quick_effectsize_aggregate_table.py $i
	python3 create_kruskal_wallis_table.py $i
done
	
