import collections
import datetime
import time

import matplotlib
import matplotlib.pyplot
import numpy
import pandas
import os


class ApplianceDataset(object):


    def __init__(self):
        self.values = None
        self.states = dict()

        self.settings = {
            'sampling_rule': '1S',
            'median_n': 21,
            'sampling_how': 'mean',
            'fill_method': 'ffill',
            'power_threshold': 30,
            'histogram_bins': 500,
            'power_factor': 0.5,
            'histogram_extra': 5,
            'edge_detection_threshold': 200,
            'edge_detection_power_factor': 0.3,
            'occ_low_threshold': 10,
        }



    @staticmethod
    def print_time(description, start_time):

        output = description + " took {:.2f}s".format(time.time() - start_time)
        print(output)
        return output

    def from_REDD(self, path):
        # save start time temporally
        start_time = time.time()

        # temporary dict to store the tmp data
        tmp_dict = dict()

        # file object
        with open(path, 'r') as data:
            # read each line from the file
            for line in data:
                # timestamp and value
                c_ts, c_val = line.split()

                # converts str to float
                c_val = float(c_val)

                # datetime from unix timestamp
                c_ts = datetime.datetime.fromtimestamp(int(c_ts))

                tmp_dict.update({c_ts: c_val})

        self.values = pandas.DataFrame(list(tmp_dict.values()), index=[list(tmp_dict.keys())])
        ApplianceDataset.print_time("importing", start_time)

    def from_GREEND(self, house_path, column_name):
        # save start time temporally
        start_time = time.time()

        # temporary dict to store the tmp data
        tmp_dict = dict()

        for date in os.listdir(house_path):
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

                            c_val = c_vals[column_name-1]
                            if c_val != 'NULL':
                                try:
                                    # datetime from unix timestamp
                                    c_ts = datetime.datetime.fromtimestamp(int(float(c_ts)))
                                    tmp_dict.update({c_ts: float(c_val)})
                                except ValueError:
                                    print('Wrong Format. Skipping this line.')
                                except:
                                    print('Some errors occured while importing. Skipping this line.')

        self.values = pandas.DataFrame(list(tmp_dict.values()), index=[list(tmp_dict.keys())])
        ApplianceDataset.print_time("importing", start_time)

    def from_iAWE(self, path):
        # save start time temporally
        start_time = time.time()

        # temporary dict to store the tmp data
        tmp_dict = dict()

        # file object
        with open(path, 'r') as data:
            # read each line from the file
            for line in data:
                if not line.startswith('timestamp'):
                    line = line.replace('\n', '')

                    # timestamp and value
                    c_ts, *c_vals = line.split(',')
                    try:
                        # converts str to float
                        c_val = float(c_vals[0])

                        # datetime from unix timestamp
                        c_ts = datetime.datetime.fromtimestamp(int(c_ts))

                        tmp_dict.update({c_ts: c_val})
                    except:
                        print(line)

        self.values = pandas.DataFrame(list(tmp_dict.values()), index=[list(tmp_dict.keys())])
        ApplianceDataset.print_time("importing", start_time)

    def plot(self):
        start_time = time.time()
        self.values.hist(bins=self.settings['histogram_bins'])
        self.values.plot()
        ApplianceDataset.print_time("Plotting", start_time)

    def __calc_bins(self):

        p_values = list(self.values[0])

        # mininmum and maximum power values
        min_p = int(min(p_values))
        max_p = int(max(p_values))

        # power delta as int, minimum is 1
        delta = int(max((max_p - min_p) / self.settings['histogram_bins'], 1))
        return list(range(min_p, max_p + self.settings['histogram_extra'], delta))

    # calculate appliance states from histograms
    def get_appliance_state(self):
        start_time = time.time()

        # converts pandas series to list
        p_vals = list(self.values[0])

        # get bins for histogram
        reduced_p_vals = self.__calc_bins()

        # create histogram
        amount, label = numpy.histogram(p_vals, bins=reduced_p_vals)
        label = label[:-1]

        # save values into dictionary
        power_dict = dict(zip(label, amount))
        most_often = max(power_dict.values())

        tmp_states = dict()
        for p in power_dict.keys():
            if power_dict[p] / most_often > self.settings['power_factor']:
                tmp_states.update({p: power_dict[p]})

        to_return = dict()

        def sum_up():
            p_sum = 0
            n_states = 0

            p_states = 0

            for state in tmp_list:
                p_sum += state[0] * state[1]
                n_states += state[0]
                p_states += state[1]

            to_return.update({p_sum / n_states: p_sum / p_states})

        prev_s = None
        tmp_list = list()

        tmp_states = collections.OrderedDict(sorted(tmp_states.items()))

        for s in tmp_states:
            if prev_s is not None:
                if abs(s - prev_s) < self.settings['power_threshold']:
                    tmp_list.append((tmp_states[s], s))

                else:
                    sum_up()
                    tmp_list = list()
                    tmp_list.append((tmp_states[s], s))

            else:
                tmp_list.append((tmp_states[s], s))
            prev_s = s

        sum_up()

        ApplianceDataset.print_time("Getting states", start_time)

        return to_return

    def get_appliance_state_by_edge_detection(self):
        start_time = time.time()

        # converts pandas series to list
        p_vals = list(self.values[0])

        # get bins for histogram
        reduced_p_vals = self.__calc_bins()

        threshold = self.settings['edge_detection_threshold']

        tmp_r_f = list()

        for i in range(len(p_vals) - 1):
            if p_vals[i] - p_vals[i + 1] > threshold:  # rising edge
                tmp_r_f.append(p_vals[i])
                tmp_r_f.append(p_vals[i + 1])
            elif p_vals[i] - p_vals[i + 1] < -threshold:  # falling edge
                tmp_r_f.append(p_vals[i])
                tmp_r_f.append(p_vals[i + 1])

        a, l = numpy.histogram(tmp_r_f, bins=reduced_p_vals)

        matplotlib.pyplot.figure(0)
        matplotlib.pyplot.plot(l[:-1], a, "r")

        # find groups
        r_f_sum = 0
        r_f_states = 0

        all_r_f_states = dict()
        # noinspection PyTypeChecker
        for c in range(len(a)):
            if c != 0:
                if a[c] != 0:
                    if a[c - 1] != 0:
                        r_f_sum += a[c] * l[c]
                        r_f_states += a[c]

                    # beginning of state
                    else:
                        r_f_sum = a[c] * l[c]
                        r_f_states = a[c]
                elif a[c - 1] != 0:
                    # ---
                    all_r_f_states.update({r_f_sum / r_f_states: r_f_states})

            # end of state
            elif a[c] != 0:
                r_f_states = a[c]

        ApplianceDataset.print_time("Getting states by edge detection", start_time)

        if all_r_f_states == {}:
            return []
        else:
            r_f_max = max(all_r_f_states.values())
            to_return = list()

            r_f_factor = self.settings['edge_detection_power_factor']

            for v in all_r_f_states:
                if all_r_f_states[v] / r_f_max > r_f_factor:
                    to_return.append(v)

            return to_return

    def resample(self, sampling_rule=None, sampling_how=None):
        if sampling_rule is None:
            sampling_rule = self.settings['sampling_rule']

        if sampling_how is None:
            sampling_how = self.settings['sampling_how']

        start_time = time.time()

        self.values = self.values.resample(rule=sampling_rule, how=sampling_how)
        return ApplianceDataset.print_time("resampling", start_time)

    def fill_missing(self, fill_method=None):
        if fill_method is None:
            fill_method = self.settings['fill_method']
        start_time = time.time()
        self.values = self.values.fillna(method=fill_method)
        return ApplianceDataset.print_time("filling", start_time)

    def med(self, n=None):

        start_time = time.time()
        if n is None:
            n = self.settings['median_n']

        r = int(n / 2)
        values = []
        print(len(self.values[0]))
        op = 0
        for i in range(len(self.values[0])):

            # start point
            s = (max(i - r, 0))

            # stop point
            e = (min(i + r + 1, len(self.values[0])))

            # median = sorted(self.values[0][s:e])[r]
            median = numpy.median(self.values[0][s:e])

            p = int((i / len(self.values[0])) * 100)
            if p != op:
                print(p)
            op = p

            # tmp_frame = ((self.values[0][s:e]).to_frame())

            # the median of the temporary frame
            # median = tmp_frame.median()

            # print(s, "/", i, "/", r, "/", e, "/")
            # print(i)
            values.append(int(median.item()))

        # creates DataFrame using the medians of the preivous frames
        self.values = pandas.DataFrame(values, index=[self.values.index])
        return ApplianceDataset.print_time("Median filter", start_time)

    def get_count_per_day(self, states):
        return self.__get_occurrence_per_day(states, to_ret="count")

    def get_states_per_day(self, states):
        return self.__get_occurrence_per_day(states, to_ret="states")

    def __get_occurrence_per_day(self, states, to_ret):
        start_time = time.time()

        def get_closest_state(state):
            tmp = list()
            for s in states:
                tmp.append((abs(s - state), s))
            return min(tmp)[1]

        last_val = self.values[0][0]
        prev_date = self.values.index[0]
        prev_state = get_closest_state(last_val)

        # find states
        states_per_day = list()
        total_states_per_day = dict()
        count_per_day = 0
        total_counts = dict()
        for i in range(len(self.values[0])):
            c_date = self.values.index[i]

            # another day
            if prev_date.day != c_date.day:
                if not states_per_day:
                    count_per_day += 1
                    states_per_day.append(get_closest_state(prev_state))

                total_counts.update({c_date: count_per_day})
                total_states_per_day.update({c_date: states_per_day})

                states_per_day = list()
                count_per_day = 0

            # detect states
            c_state = get_closest_state(self.values[0][i])
            if prev_state != c_state:

                if states_per_day is []:
                    states_per_day.append(get_closest_state(prev_state))

                if prev_state < self.settings['occ_low_threshold']:
                    count_per_day += 1

                states_per_day.append(get_closest_state(c_state))

                prev_state = c_state

            # last_val = c_state
            prev_date = c_date

        ApplianceDataset.print_time("Getting Occurrence", start_time)
        if to_ret == "count":
            return total_counts
        elif to_ret == "states":
            return total_states_per_day

    def import_settings(self, settings):
        self.settings.update(settings)