import sys
import segeval
import os
import csv
from collections import defaultdict


# handle flag for existence of json
json_exists = sys.argv[1] == "-j"

# read in directory that contains the files and prepare infrastructure
n = 2 if json_exists else 1
dir = sys.argv[n]
dirname = os.path.basename(os.path.dirname(dir))
json_dir = "../json"
result_dir = "../results"

if not os.path.exists(json_dir):
    os.makedirs(json_dir)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)


# get all the filenames of the files in dir
conts = os.walk(dir)
filenames = next(conts)[2]
filenames = [os.path.join(dir, f) for f in filenames]

# check for correct files
for fn in filenames:
    if json_exists and fn[-4:] != "json":
        raise ValueError("Expected json file. Use -c flag for csv files.")
    if not json_exists and fn[-3:] != "csv":
        raise ValueError("Expected csv file. Don't use -c flag for json files.")


# create datasets for every file if needed
if not json_exists:
    json_name = dirname + ".json"
    dataset = segeval.Dataset()
    for fn in filenames:
        dataset[os.path.basename(fn)[:-4]] = {}
        with open(fn, newline="") as csvfile:
            data = list(csv.reader(csvfile, delimiter=","))
        annotator = data[0][1]
        tmpmass = defaultdict(list)
        # iterate over data entries
        for row in data:
            # safe masses and prepare stuff if annotator changes
            if row[1] != annotator:
                # just look at boundaries for each category
                tmpmass = {key:sorted(list(set(value))) for key, value in tmpmass.items()}
                dataset[os.path.basename(fn)[:-4]][annotator] = tmpmass
                annotator = row[1]
                tmpmass = defaultdict(list)
            tmpmass[row[2]].append(int(row[4]))
            tmpmass[row[2]].append(int(row[5]) + 1)  # +1 because always wants first char of new segment
    segeval.output_linear_mass_json(os.path.join(json_dir, json_name), dataset)


# calculate statistics
if json_exists:
    dataset = segeval.input_linear_mass_json(dir)
results = []
for fn in filenames:
    r = {}
    datasets = [dn for dn in datanames if n == dn[:2]]
    r["name"] = os.path.basename(datasets[0])
    ds0 = segeval.input_linear_mass_json(datasets[0])[r["name"]]
    ds1 = segeval.input_linear_mass_json(datasets[1])[r["name"]]
    evals = {}
    cats = set(list(ds0.keys()) + list(ds1.keys()))
    for cat in cats:
        segsim = segeval.segmentation_similarity(ds0[cat], ds1[cat])
        boundsim = segeval.boundary_similarity(ds0[cat], ds1[cat])
        evals[cat] = {"segsim": segsim, "boundsim": boundsim}
    r["evals"] = evals


# writing results
of_name = dirname + "_results.csv"
with open(os.path.join(result_dir, of_name), "w") as of:
    of.write("Text, Category, SegSim, BoundSim\n")
    for r in results:
        for cat in r["evals"]:
            of.write(f"{r['name']}, {cat}, {r['evals'][cat]['segsim']}, {r['evals'][cat]['boundsim']}\n")