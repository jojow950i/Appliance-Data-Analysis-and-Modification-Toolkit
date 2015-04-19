__author__ = 'johannesholzl'
import os
import datetime
import pandas
from matplotlib.pyplot import *


if __name__ == '__main__':
    # save start time temporally

    # temporary dict to store the tmp data
    tmp_dict = list()
    house_path = '/Users/johannesholzl/Documents/work_uni/GREEND_0-1_311014/building7'
    for date in os.listdir(house_path)[:100]:
        print(date)
        if date.startswith('dataset'):

            # file object
            with open(house_path+'/'+date, 'r') as data:
                # read each line from the file

                for line in data:
                    if not line.startswith('timestamp'):
                        line = line.replace('\n', '')
                        # timestamp and value
                        c_ts, *c_vals = line.split(',')

                        # converts str to float
                        try:
                            c_ts = datetime.datetime.fromtimestamp(int(float(c_ts)))
                        except:
                            print('couldnt read timestamp')

                        for column in range(len(c_vals)):
                            c_val = c_vals[column]
                            if c_val != 'NULL':
                                try:
                                    try:
                                        tmp_dict[column].update({c_ts: float(c_val)})
                                    except IndexError:
                                        print('new column!!')
                                        tmp_dict.append((dict()))
                                        tmp_dict[column].update({c_ts: float(c_val)})
                                except ValueError:
                                    print('Wrong Format. Skipping this line.')
                                except:
                                    print('Some errors occurred while importing. Skipping this line.')

    for i in tmp_dict:
        values = pandas.DataFrame(list(i.values()), index=[list(i.keys())])
        values.plot()
        savefig('/Users/johannesholzl/Documents/'+str(tmp_dict.index(i)) + '.png')

def a():
    l = list()
    for i in range(10):
        l.append(datetime.datetime.now())
    values = pandas.DataFrame([1,2,3,4,5,6,7,8,9,10], index=[l])
    values.plot()
    show()
