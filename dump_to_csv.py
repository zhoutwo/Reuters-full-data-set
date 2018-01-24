from __future__ import print_function

import pickle
import sys
from glob import iglob


def read(data_dir):
    count = 0
    output_filename = 'reuters.csv'
    sep = '\t'
    with open(output_filename, 'w') as w:
        for filename in iglob(data_dir + '/*.pkl'):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                for datum in data:

                    ts = datum['ts']
                    if ts is None:
                        ts = ''

                    line = str(count)
                    line += sep
                    line += '"' + ts + '"'
                    line += sep
                    line += '"' + datum['title'] + '"'
                    line += sep
                    line += '"' + datum['href'] + '"'
                    line += sep
                    line += '"' + datum['first_line'] + '"'
                    line += '\n'

                    w.write(line)
                    print(count)
                    count += 1


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage: python dump_to_csv.py reuters_pickle_output_dir'.format(sys.argv[0])
    read(sys.argv[1])
