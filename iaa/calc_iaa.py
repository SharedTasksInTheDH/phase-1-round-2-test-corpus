import sys
import segeval
import os
import csv

# read in directory that contains the files and prepare infrastructure
dir = sys.argv[1]
mirrow_dir = os.path.basename(dir)
if not os.path.exists(mirrow_dir):
    os.mkdir(mirrow_dir)


# get all the filenames of the files in dir
conts = os.walk(dir)
filenames = next(conts)[2]
filenames = [os.path.join(dir, f) for f in filenames]


# create datasets for every file
datanames = []
for fn in filenames:
    if fn[-2:] == "md":
        continue
    with open(fn, newline="") as csvfile:
        file = csv.reader(csvfile, delimiter=",")
        next(file)
        for row in file:
            pass


# calculate statistics
results = []
for i in range(13):
    n = str(i+1).zfill(2)
    r = {}
    datasets = [dn for dn in datanames if n == dn[:2]]
    r["name"] = os.path.basename(datasets[0])[3:-7]
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
with open(os.path.join(mirrow_dir, "results.csv") , "w") as of:
    of.write("Text, Category, SegSim, BoundSim\n")
    for r in results:
        for cat in r["evals"]:
            of.write(f"{r['name']}, {cat}, {r['evals'][cat]['segsim']}, {r['evals'][cat]['boundsim']}\n")