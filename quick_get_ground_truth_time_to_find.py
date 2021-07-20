import glob
import json
import sys, getopt
from sortedcontainers import SortedDict
import csv
import datetime
import numpy as np
import statistics
import matplotlib.pyplot as plt
import os
import ground_truth
import data_retrieval
file = open("../OSSFuzzWebScraper/bugs.csv", newline='')
bugs_read = [x for x in csv.DictReader(file)]
file.close()
bugs_map = {v['ID']:v for v in bugs_read}
projects, reverse_lookup, all_ids = ground_truth.get_ground_truth_data()
#SHOW BOXPLOT
data = []
xlabels = []
#PRINT CSV
print("Project,Average ttd, Median ttd, 75th percentile ttd")
for project in sorted(projects):
    project_name = "php-execute" if ("php-fuzz-execute" in project) else ("php-parser" if ("php-fuzz-parser" in project) else str(project).split("_")[0])
    days_to_find_arr = []
    for bug_id in projects[project]:
        days_to_find_arr.append(ground_truth.get_days_to_find(bugs_map, bug_id[0]))
    #PRINT CSV
    print(project_name, np.average(days_to_find_arr), np.median(days_to_find_arr), np.quantile(days_to_find_arr, 0.75), sep=',')
    
    #PRINT ARRAY
    #print(project_name, sorted(days_to_find_arr))
    #print("\n\n\n\n")

    #SHOW BOXPLOT
    data.append(days_to_find_arr)
    xlabels.append(project_name)
fig, ax = plt.subplots()
ax.set_title("Time to find Boxplots")
ax.set_ylabel("Days to find")
ax.set_xlabel("Benchmark")
#ax.set_xticks(np.arange(len(xlabels)))
ax.set_xticklabels(xlabels)
ax.boxplot(data)
figure = plt.gcf()  # get current figure

figure.set_size_inches(32, 18)
plt.savefig(os.path.join(data_retrieval.report_directory, "time_to_find_ground_truth_boxplot.png"), dpi=300, bbox_inches='tight')


