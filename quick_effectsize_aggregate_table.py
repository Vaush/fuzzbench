import csv
import numpy as np
import glob
import pandas as pd
vargha_delaney_csv_files = glob.glob('*_vargha-delaney.csv')
fuzzer_pair_count = {}
fuzzer_benchmark_count = {}
for filename in vargha_delaney_csv_files:
    benchmark_name = "_".join(filename.split("_")[:-1])
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fuzzer_name = row['']
            if fuzzer_name not in fuzzer_pair_count:
                fuzzer_pair_count[fuzzer_name] = {}
            if fuzzer_name not in fuzzer_benchmark_count:
                fuzzer_benchmark_count[fuzzer_name] = {}
            benchmark_count = np.array([0,0,0,0])
            for fuzzer in row:
                if fuzzer:
                    val = abs(float(row[fuzzer])-0.5)
                    if fuzzer not in fuzzer_pair_count[fuzzer_name]:
                        fuzzer_pair_count[fuzzer_name][fuzzer] = np.array([0,0,0,0])
                    to_add = None
                    if val < 0.147:
                        to_add = np.array([1,0,0,0])
                    elif val < 0.33:
                        to_add = np.array([0,1,0,0])
                    elif val < 0.474:
                        to_add = np.array([0,0,1,0])
                    else:
                        to_add = np.array([0,0,0,1])
                    benchmark_count += to_add
                    fuzzer_pair_count[fuzzer_name][fuzzer] += to_add
            fuzzer_benchmark_count[fuzzer_name][benchmark_name] = benchmark_count
fuzzer_pair_df = pd.DataFrame({k1:{k2:str(list(v2))[1:-1] for k2,v2 in v1.items()} for k1,v1 in fuzzer_pair_count.items()})
fuzzer_benchmark_df = pd.DataFrame({k1:{k2:str(list(v2))[1:-1] for k2,v2 in v1.items()} for k1,v1 in fuzzer_benchmark_count.items()})
fuzzer_pair_df.to_csv("fuzzer_fuzzer_effectsize_aggregate.csv")
fuzzer_benchmark_df.to_csv("fuzzer_benchmark_effectsize_aggregate.csv")

