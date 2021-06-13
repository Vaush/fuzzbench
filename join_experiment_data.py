import sys
import gzip
import csv
first_data = sys.argv[1]
second_data = sys.argv[2]
joined_data = sys.argv[3]
exp_name = sys.argv[4] if len(sys.argv) > 4 else None
with gzip.open(joined_data, "wt", newline="") as w:
    fieldnames = []
    writer = None
    with gzip.open(first_data, "rt", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()
        for line in reader:
            if exp_name is None:
                exp_name = line["experiment"]
            line["experiment"] = exp_name
            writer.writerow(line)
    with gzip.open(second_data, "rt", newline="") as f:
        reader = csv.DictReader(f)
        for line in reader:
            line["experiment"] = exp_name
            writer.writerow(line)
