#! /usr/bin/env python3

import csv


infile = 'training_set.csv'

print('Reducing data. This may take a long time.')

posCount = 0
negCount = 0
netrualCount = 0

outfile = open('trimmed.csv', 'w')
with open(infile, newline='', encoding='utf8', errors='replace') as f:
    reader = csv.reader(f, delimiter=',')
    try:
        for row in reader:
            if row[0] == '0':
                negCount += 1
            if row[0] == '2':
                netrualCount += 1
            if row[0] == '4':
                posCount += 1

            outfile.write("\"{0}\",\"{1}\"\n".format(row[0], row[5]))
    except UnicodeDecodeError as err:
        print('UnicodeDecodeError: {0}'.format(err))

outfile.close()


print('\nStats:')
print('{0} positive tags'.format(posCount))
print('{0} negative tags'.format(negCount))
print('{0} netrual tags'.format(netrualCount))
