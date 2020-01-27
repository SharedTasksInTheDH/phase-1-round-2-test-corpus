import sys
import segeval
import os
import csv
from collections import defaultdict
import itertools

def conv2mass(bounds, size):
    # just look at boundaries for each category
    bounds = {key: sorted(list(set(value))) for key, value in bounds.items()}
    # create mass (delta) based version of data
    mass = defaultdict(list)
    for cat, marks in bounds.items():
        if len(marks) == 0:
            mass[cat] = []
        else:
            if marks[0] != 0:
                marks.append(0)
                marks.append(size-1)
                marks.sort()
            for i in range(len(marks)-1):
                mass[cat].append(marks[i+1] - marks[i])
    return mass



# handle flag for existence of json
json_exists = sys.argv[1] == "-j"

# read in directory that contains the files and prepare infrastructure
n = 2 if json_exists else 1
input_file = sys.argv[n]
dirname = os.path.basename(os.path.dirname(input_file))
json_dir = os.path.join("../json", dirname)
result_dir = os.path.join("../results", dirname)

if not os.path.exists(json_dir):
    os.makedirs(json_dir)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)


# check for correct files
if json_exists and input_file[-4:] != "json":
    raise ValueError("Expected json file. Use -c flag for csv files.")
if not json_exists and input_file[-3:] != "csv":
    raise ValueError("Expected csv file. Don't use -c flag for json files.")


# create datasets for every file if needed
if not json_exists:
    json_name = os.path.basename(input_file)[:-3] + "json"
    dataset = segeval.Dataset()
    characters = os.popen(f"wc -c ../txt/{os.path.basename(input_file)[:-3]}txt").read()
    characters = int(characters.split(" ")[0])

    with open(input_file, newline="") as csvfile:
        data = list(csv.reader(csvfile, delimiter=","))
    try:
        annotator = data[0][1]
    except IndexError as Er:
        print("\nError in file: " + input_file, file=sys.stderr)
        raise Er
    tmpmass = defaultdict(list)
    # iterate over data entries
    for row in data:
        # safe masses and prepare stuff if annotator changes
        if row[1] != annotator:
            dataset[annotator] = conv2mass(tmpmass, characters)
            annotator = row[1]
            tmpmass = defaultdict(list)
        tmpmass[row[2]].append(int(row[4]))
        tmpmass[row[2]].append(int(row[5]) + 1)  # +1 because always wants first char of new segment
    if annotator not in dataset:
        dataset[annotator] = conv2mass(tmpmass, characters)
    segeval.output_linear_mass_json(os.path.join(json_dir, json_name), dataset)


# calculate statistics
if json_exists:
    dataset = segeval.input_linear_mass_json(input_file)

results = {}
# get all the annotators's names and all the categories
annotators = list(dataset.keys())
cats = [list(dataset[a].keys()) for a in annotators]
cats = list(set([e for l in cats for e in l]))
cats.sort()
for cat in cats:
    for a1, a2 in itertools.combinations(annotators, 2):
        l1 = dataset[a1][cat]
        l2 = dataset[a2][cat]
        if l1 != [] and l2 != []:
            try:
                segsim = segeval.segmentation_similarity(l1, l2)
                boundsim = segeval.boundary_similarity(l1, l2)
            except segeval.util.SegmentationMetricError as Er:
                print("\nError on file: " + input_file, file=sys.stderr)
                raise Er
        else:
            segsim = boundsim = "N/A"

        results[cat] = {"a1": a1, "a2": a2, "segsim": segsim, "boundsim": boundsim}

# writing results
of_name = os.path.basename(input_file)
with open(os.path.join(result_dir, of_name), "w") as of:
    of.write("Category, Annotator 1, Annotator 2, SegSim, BoundSim\n")
    for cat in results:
        of.write(f"{cat}, {results[cat]['a1']}, {results[cat]['a2']}, {results[cat]['segsim']}, {results[cat]['boundsim']}\n")
