import csv
import numpy as np
import glob
import pandas as pd
import sys
import os
import data_retrieval
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)
vargha_delaney_csv_files = glob.glob(os.path.join(save_directory, '*_vargha-delaney.csv'))
fuzzer_pair_count = {}
fuzzer_benchmark_count = {}
for filename in vargha_delaney_csv_files:
    x = os.path.basename(filename)
    benchmark_name = "php-execute" if ("php-fuzz-execute" in x) else ("php-parser" if ("php-fuzz-parser" in x) else str(x).split("_")[0])
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fuzzer_name = row['']
            if fuzzer_name not in fuzzer_pair_count:
                fuzzer_pair_count[fuzzer_name] = {"Total": np.array([0,0,0,0])}
            if fuzzer_name not in fuzzer_benchmark_count:
                fuzzer_benchmark_count[fuzzer_name] = {"Total": np.array([0,0,0,0])}
            benchmark_count = np.array([0,0,0,0])
            for fuzzer in row:
                if fuzzer:
                    val = float(row[fuzzer])-0.5
                    if fuzzer not in fuzzer_pair_count[fuzzer_name]:
                        fuzzer_pair_count[fuzzer_name][fuzzer] = np.array([0,0,0,0])
                    to_add = None
                    if val <= 0:
                        to_add = np.array([0,0,0,0])
                    elif val < 0.147:
                        to_add = np.array([0,0,0,1])
                    elif val < 0.33:
                        to_add = np.array([0,0,1,0])
                    elif val < 0.474:
                        to_add = np.array([0,1,0,0])
                    else:
                        to_add = np.array([1,0,0,0])
                    benchmark_count += to_add
                    fuzzer_pair_count[fuzzer_name][fuzzer] += to_add
                    fuzzer_pair_count[fuzzer_name]['Total'] += to_add
            fuzzer_benchmark_count[fuzzer_name][benchmark_name] = benchmark_count
            fuzzer_benchmark_count[fuzzer_name]["Total"] += benchmark_count
fuzzer_pair_df = pd.DataFrame({k1:{k2:str(list(v2))[1:-1] for k2,v2 in v1.items()} for k1,v1 in fuzzer_pair_count.items()})
fuzzer_benchmark_df = pd.DataFrame({k1:{k2:str(list(v2))[1:-1] for k2,v2 in v1.items()} for k1,v1 in fuzzer_benchmark_count.items()})
fuzzer_pair_df.sort_index().to_csv(os.path.join(save_directory, "fuzzer_fuzzer_effectsize_aggregate.csv"))
fuzzer_benchmark_df.sort_index().to_csv(os.path.join(save_directory, "fuzzer_benchmark_effectsize_aggregate.csv"))

import pathlib
import shutil
pathlib.Path(os.path.join(save_directory, 'vargha-delaney')).mkdir(parents=True, exist_ok=True)
for f in glob.glob(os.path.join(save_directory, "*_vargha-delaney.csv")):
    shutil.move(os.path.join(save_directory, f), os.path.join(save_directory, "vargha-delaney", f))

