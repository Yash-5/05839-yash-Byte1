from scipy.stats import spearmanr
from scraper import start_year, end_year, make_path
import os
import numpy as np

base_dir = "./data"
cnt = 0

def get_table(dirname, filename):
    table = []

    with open(os.path.join(dirname, filename)) as infile:
        for line in infile:
            table.append(line.strip())

    return table

def get_race_list(dirname, year):
    race_list = []
    curr_dir = os.path.join(base_dir, str(year))
    for f in os.listdir(curr_dir):
        if f.startswith("WDC"):
            continue
        x = f[:-4].split('-')
        race_list.append([int(x[0]), x[1], f])
    race_list.sort(key=lambda k: k[0]) 
    return race_list

def get_key_standings(race_standings, positions, top10_cnt):
    global cnt

    key_standings = []
    for i, x in enumerate(race_standings):
        if i < 10:
            inc(top10_cnt, x)
        try:
            key_standings.append(positions[x])
        except KeyError as e:
            cnt += 1
            continue
    for i in xrange(len(positions)):
        if i+1 not in key_standings:
            key_standings.append(i+1)
    return key_standings

def get_corel(standings):
    ref_list = [i+1 for i in xrange(len(standings))]
    return spearmanr(ref_list, standings)

def inc(d, x):
    if x in d:
        d[x] += 1
    else:
        d[x] = 1

def process_year(year):
    global base_dir

    curr_dir = os.path.join(base_dir, str(year))

    WDC_table = get_table(curr_dir, 'WDC.csv')

    positions = {}
    for i,name in enumerate(WDC_table):
        positions[name] = i + 1

    # race_list has race number, Name of country, filename
    race_list = get_race_list(base_dir, year)

    corels = []

    top10_cnt = {}

    for race in race_list:
        race_standings = get_table(curr_dir, race[2])
        key_standings = get_key_standings(race_standings, positions, top10_cnt)
        corels.append([race[1], get_corel(key_standings)])

    for x in top10_cnt:
	top10_cnt[x] = float(top10_cnt[x]) / len(race_list)
    return corels, top10_cnt.values()

def make_corel_files():
    base_dir = "./results"
    make_path(base_dir, "")

    agg_corel = []
    agg_top10 = []

    for year in xrange(start_year, end_year + 1):
        corel_table, top10_cnt = process_year(year)
	agg_top10.append([year, np.mean(top10_cnt)])
        with open(os.path.join(base_dir, str(year)), 'w') as corelfile:
            for i,x in enumerate(corel_table):
                corelfile.write(x[0])
                corelfile.write(",")
                corelfile.write(str(x[1][0]))
                corelfile.write("\n")
		agg_corel.append([str(year) + "-" + str(i+1), x[1][0]])

    with open(os.path.join(base_dir, "aggregate_corel"), 'w') as aggfile:
	for x in agg_corel:
	    aggfile.write(str(x[0]) + "," + str(x[1]) + "\n")
    
    with open(os.path.join(base_dir, "aggregate_top10"), 'w') as aggfile:
	for x in agg_top10:
	    aggfile.write(str(x[0]) + "," + str(x[1]) + "\n")

def main():
    make_corel_files()

if __name__ == '__main__':
    main()
