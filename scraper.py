#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import os
from bs4 import BeautifulSoup as bs

DEBUG = 1
base_link = "https://www.formula1.com/en/results.html/"
dir_name = "./data"
WDC_extension = "/drivers.html"
race_list_extension = "/races.html"
start_year = 1970
end_year = 2018
race_res_extention = "/race-result.html"

def get_content_from_link(link):
    try:
        data = subprocess.check_output(["curl", "-s", "-k", link])
        return data
    except subprocess.CalledProcessError as e:
        print "Error in downloading", link
        print str(e)
        return None

def get_table(content, col_idx, rem_cnt):
    soup = bs(content)
    rows = soup.find('table', {'class':
        'resultsarchive-table'}).find("tbody").find_all("tr")

    table = []

    for row in rows:
        raw_text = row.find_all("td")[col_idx].text.strip().split('\n')
        name = " ".join(raw_text[:len(raw_text)-rem_cnt])
	name = " ".join([x.strip() for x in name.split()])
        table.append(name.encode('UTF-8'))
    return table

def make_path(dir_name, fname):
    curr_dir = os.path.join(dir_name, str(fname))

    if not os.path.exists(curr_dir):
        os.makedirs(curr_dir)

    return curr_dir


def make_WDC_file(content, dir_name, year):
    curr_dir = make_path(dir_name, year)

    table = get_table(content, 2, 1)
    outfile = open(os.path.join(curr_dir, 'WDC.csv'), 'w')
    outfile.write("\n".join(table))
    outfile.close()

def get_race_list(content):
    soup = bs(content)
    soup = soup.find_all('select', {'class' :
        "resultsarchive-filter-form-select"})[2]

    table = []

    for race in soup.find_all('option'):
        if not race['value']:
            continue
        table.append(race['value'])
    return table

def make_race_file(dir_name, race, year, idx):
    global race_res_extention
    link = base_link + str(year) + "/races/" + race + race_res_extention

    content = get_content_from_link(link)
    table = get_table(content, 3, 1)
    outfile = open(os.path.join(dir_name, str(idx) + '-' +
            race.split('/')[1] + ".csv"), 'w')
    outfile.write("\n".join(table))

def make_year_files(content, dir_name, year):
    curr_dir = make_path(dir_name, year)

    race_list = get_race_list(content)

    for idx, race in enumerate(race_list):
        make_race_file(curr_dir, race, year, idx+1)
        if DEBUG: print race.split('/')[1], 
        if year == 2018 and race.endswith('italy'):
            break
    if DEBUG: print

def process_year(year):
    global base_link
    global dir_name
    global WDC_extension

    if DEBUG: print year

    #  TODO: Uncomment next lines
    WDC_content = get_content_from_link(base_link + str(year) + WDC_extension)

    make_WDC_file(WDC_content, dir_name, year)

    if DEBUG: print "WDC"
    
    race_list_content = get_content_from_link(base_link + str(year) +
            race_list_extension)

    make_year_files(race_list_content, dir_name, year)

def main():
    for year in range(start_year, end_year + 1):
        process_year(year)

if __name__ == '__main__':
    main()
