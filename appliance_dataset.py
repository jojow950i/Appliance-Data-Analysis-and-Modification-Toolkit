import collections
import datetime
import json
import matplotlib
import numpy
import pandas
import time
import scipy
import sys

class ApplianceDataset(object):
    def __init__(self):
        self.values = None
        self.states = dict()
    
        self.settings = {
            'sampling_rule' : '1H',
            'median_n' : 20, 
            'sampling_how' : 'mean', 
            'fill_method':'ffill', 
            'power_threshold':30, 
            'histogram_bins':500, 
            'power_factor' : 0.5, 
            'histogram_extra':5
        }
    
    def print_time(description, start_time):
        print(description+" took {:.2f}s".format(time.time()-start_time))
    
    def from_REDD(self, path):
        #save start time temporarely
        start_time = time.time()
        
        #temporary dict to store the tmp data
        tmp_dict = dict()
        
        #file obejct
        #data = open(path, 'r')
        with open(path, 'r') as data:

            #read each line from the file
            for line in data:
                #timestamp and value
                c_ts, c_val = line.split()
            
                #converts str to float
                c_val = float(c_val)
            
                #datetime from unix timestamp
                c_ts = datetime.datetime.fromtimestamp(int(c_ts))
            
                tmp_dict.update({c_ts:c_val})
        
        self.values = pandas.DataFrame(list(tmp_dict.values()), index=[list(tmp_dict.keys())])
        ApplianceDataset.print_time("importing", start_time)
    
    def plot(self):
        start_time = time.time()
        self.values.hist(bins=self.settings['histogram_bins'])
        ApplianceDataset.print_time("plotting", start_time)
    
    #calculate appliance states from histograms
    def get_appliance_state(self):


        #converts pandas series to list
        p_vals = list(self.values[0])

        #mininmum and maximum power values
        min_p = int(min(p_vals))
        max_p = int(max(p_vals))
   
        #power delta as int, minimum is 1
        delta = int(max((max_p - min_p) / self.settings['histogram_bins'], 1))
        reduced_p_vals = list(range(min_p, max_p+self.settings['histogram_extra'], delta))

        #create histogram
        amount, label = numpy.histogram(p_vals, bins = reduced_p_vals)
        label = label[:-1]

        #save values into dictionary
        power_dict = dict(zip(label, amount))
        most_often = max(power_dict.values())

        tmp_states = dict()
        for p in power_dict.keys():
            if power_dict[p]/most_often > self.settings['power_factor']:
                tmp_states.update({p: power_dict[p]})

  
        def sum_up():
            p_sum = 0
            n_states = 0
            
            p_states = 0
            
            for s in tmp_list:
                p_sum += s[0]*s[1]
                n_states += s[0]
                p_states += s[1]
                
            self.states.update({p_sum/n_states : p_sum/p_states})
            print(p_sum/p_states)


        prev_s = None
        tmp_list = list()
        
        tmp_states = collections.OrderedDict(sorted(tmp_states.items())) 
        print(tmp_states)

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
    
    def resample(self, sampling_rule = None, sampling_how = None):
        if sampling_rule == None:
            sampling_rule = self.settings['sampling_rule']

        if sampling_how == None:
            sampling_how = self.settings['sampling_how']

        start_time = time.time()

        self.values = self.values.resample(rule=sampling_rule, how=sampling_how)
        ApplianceDataset.print_time("resampling", start_time)

    
    def fill_missing(self, fill_method = None):
        if fill_method == None:
            fill_method = self.settings['fill_method']
        start_time = time.time()
        self.values = self.values.fillna(method = fill_method)
        ApplianceDataset.print_time("filling", start_time)
    
    def med(self, n = None):
        if n == None:
            n = self.settings['median_n']
        
        r = int(n/2)
        vals = []
        old_p = 0
        for i in range(len(self.values[0])):
            
            #start point
            s = (max(i-r,0))
            
            #stop point
            e = (min(i+r+1, len(self.values[0])))
            
            #creation of a temporary pandas dataframe for representing the current data
            tmp_frame = ((self.values[0][s:e]).to_frame())
            
            #the median of the temporary frame
            median = tmp_frame.median()
            
            vals.append(median)
        
        #creates DataFrame using the medians of the preivous frames
        self.values = pandas.DataFrame(vals, index=[self.values.index])

    
    def import_settings(self, settings):
        self.settings.update(settings)

