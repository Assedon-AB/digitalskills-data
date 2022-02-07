import csv
import re
""" Reads in whitelist """
file = open("./old_whitelist.csv")
csvreader = csv.reader(file)
header = next(csvreader)
rows = []
for row in csvreader:
    rows.append(row)
file.close()

skills = {}
for row in rows:
    if row[2] in skills:
        skills[row[2]]["words"].append(row[0])
    else:
        skills[row[2]] = {}
        skills[row[2]]["words"] = [row[0]]
        skills[row[2]]["subgroup"] = row[3]
        skills[row[2]]["maingroup"] = row[4]

new_rows = []
for skill in skills.keys():
    new_rows.append([
        f'[\\s_-]({"|".join(skills[skill]["words"])})[\\.\\s_-]',
        skill,
        skills[skill]["subgroup"],
        skills[skill]["maingroup"]
    ])


file = open("./whitelist-regex.csv", "w")
csvwriter = csv.writer(file)
csvwriter.writerows(new_rows)
file.close()
