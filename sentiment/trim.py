#! /usr/bin/env python3

import csv

# the number of tweets to add to the trimmed set.
# set at 800000 for all tweets, lower if you want the training to go faster
LIMIT = 800000
INFILE = 'training_set.csv'

print('Reducing data. This may take a long time.')

posCount = 0
negCount = 0

outfile = open('trimmed.csv', 'w')
with open(INFILE, newline='', encoding='utf8', errors='replace') as f:
    reader = csv.reader(f, delimiter=',')
    try:
        for row in reader:
            if row[0] == '0':# and negCount < 100000:
                negCount += 1
                outfile.write("\"{0}\",\"{1}\"\n".format(row[0], row[5]))
            elif row[0] == '4':# and posCount < 100000:
                posCount += 1
                outfile.write("\"{0}\",\"{1}\"\n".format(row[0], row[5]))
    except UnicodeDecodeError as err:
        print('UnicodeDecodeError: {0}'.format(err))

outfile.close()


print('\nStats:')
print('{0} positive tags'.format(posCount))
print('{0} negative tags'.format(negCount))
