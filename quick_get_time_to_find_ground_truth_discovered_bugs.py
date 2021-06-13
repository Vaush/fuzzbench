import ground_truth
file = open("../OSSFuzzWebScraper/bugs.csv", newline='')
bugs_read = [x for x in csv.DictReader(file)]
file.close()
bugs_map = {v['ID']:v for v in bugs_read}
projects = ground_truth.get_ground_truth_found()
#SHOW BOXPLOT
data = []
xlabels = []
#PRINT CSV
print("Project,Average ttd, Median ttd, 75th percentile ttd")
for project in sorted(projects):
    days_to_find_arr = []
    for bug_id in projects[project]:
        days_to_find_arr.append(ground_truth.get_days_to_find(bugs_map, bug_id))
    #PRINT CSV
    if not days_to_find_arr:
        continue
    print(project, np.average(days_to_find_arr), np.median(days_to_find_arr), np.quantile(days_to_find_arr, 0.75), sep=',')
    
    #PRINT ARRAY
    #print(project_name, sorted(days_to_find_arr))
    #print("\n\n\n\n")

    #SHOW BOXPLOT
    data.append(days_to_find_arr)
    xlabels.append(project)
fig, ax = plt.subplots()
ax.set_title("Time to find bugs in ground truth - Boxplots")
ax.set_ylabel("Days to find")
ax.set_xlabel("Benchmark")
#ax.set_xticks(np.arange(len(xlabels)))
ax.set_xticklabels(xlabels)
ax.boxplot(data)
plt.show()
