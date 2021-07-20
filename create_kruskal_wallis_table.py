import csv
import data_retrieval
import sys
import os
if len(sys.argv) > 1:
    t = int(sys.argv[1])
else:
    t = 0
save_directory = data_retrieval.get_save_directory(t)

with open(os.path.join(save_directory, 'table.csv'), "w") as csvfile:
    reader = csv.reader(open(os.path.join(save_directory,'kruskal.csv')))
    reader2 = csv.reader(open(os.path.join(save_directory, 'mean.csv')))
    writer = csv.writer(csvfile)
    writer.writerow(next(reader))
    next(reader2)
    for row1, row2 in zip(reader,reader2):
        newrow = []
        skipfirst = True
        for el1, el2 in zip(row1, row2):
            if skipfirst:
                skipfirst = False
                newrow.append(el1)
                continue
            newrow.append(str(round(float(el1))) + " (" + str(round(float(el2),2)) + ")")
        writer.writerow(newrow)
