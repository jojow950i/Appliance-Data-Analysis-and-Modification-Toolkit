import appliance_dataset
import pandas
import random
import datetime
import complexity
import os
import server


class GenerateOrder:

    def __init__(self, gotten_id, timeframe, apps, noise, missing, calcTotalComplexity, waiters, redd_path, channels):
        self.gotten_id = gotten_id
        self.timeframe = timeframe
        self.apps = apps
        self.noise = noise
        self.missing = missing
        self.calcTotalComplexity = calcTotalComplexity
        self.waiters = waiters
        self.redd_path = redd_path
        self.channels = channels
        self.c_buffer = self.waiters[self.gotten_id]['buffer']

        self.aggregated = {}

    def generate(self):
        self.generation_process()
        self.write_csv()
        self.calc_complexity()

        self.c_buffer.output_status("Finished</br>")
        self.c_buffer.output_status("<finished>")


    def generation_process(self):
        self.aggregated = {}
        # print('GOTTEN ID:', gotten_id)
        random_time_start = random.randint(1000000000, 1500000000)
        random_time = pandas.Timestamp(pandas.Timestamp(datetime.datetime.fromtimestamp(random_time_start)))
        self.appliance_objects = []



        self.c_buffer.output_status("Generating Started</br>")

        c = 0
        apps_l = len(self.apps['appliances'])
        for app in self.apps['appliances']:

            all_app_datasets = []
            current_app = self.apps['appliances'][app]
            app_datasets = current_app['datasets']
            app_name = current_app['name']
            app_size = current_app['size']
            self.c_buffer.output_status("importing " + str(app_name) + ' (' + str(app) + ')' + '</br>')

            app_resampling = current_app['resampling']
            app_median = current_app['median']
            app_fill = current_app['fill']

            for dataset in app_datasets:
                print('app:',app_datasets)
                if app_datasets[dataset] and dataset in self.channels[app_name]['datasets']:
                    for item in self.channels[app_name]['datasets'][dataset][app_size.lower()]:
                        all_app_datasets.append({'dataset': dataset, 'channel': item[0], 'house': item[1]})

            app_selected = random.choice(all_app_datasets)

            current_app = None
            print(app_selected)
            tmp_app = appliance_dataset.ApplianceDataset()
            if app_selected['dataset'] == 'REDD':
                path = self.redd_path + '/' + app_selected['house'] + '/channel_' + app_selected['channel'] + '.dat'
                tmp_app.from_REDD(path)
            elif app_selected['dataset'] == 'GREEND':
                house_path = os.path.join(server.greend_path, app_selected['house'])
                tmp_app.from_GREEND(house_path, app_selected['channel'])
            elif app_selected['dataset'] == 'iAWE':
                tmp_app.from_iAWE(os.path.join(server.iAWE_path, app_selected['channel']+'.csv'))


            if app_fill != 'None':
                tmp_app.fill_missing(fill_method=app_fill)

            if app_median != '':
                try:
                    median = int(app_median)
                    output = tmp_app.med(n=median)
                    self.c_buffer.output_status(output + '</br>')
                except:
                    self.c_buffer.output_status('median filter argument not valid </br>')

            if app_resampling != '':
                try:
                    output = tmp_app.resample(sampling_rule=app_resampling)
                    self.c_buffer.output_status(output + '</br>')
                except:
                    self.c_buffer.output_status('sampling rule argument not valid </br>')

            # i+=1
            output = tmp_app.fill_missing()
            self.c_buffer.output_status(output + '</br>')

            current_app = tmp_app

            self.appliance_objects.append(tmp_app)

            self.c_buffer.output_status("Computing " + str(app_name) + '</br>')
            values = current_app.values[0]
            data = values.keys()
            start = data[0]
            end = data[-1]

            app_length = end - start

            tmp_dr = pandas.date_range('', periods=2, freq=self.timeframe)
            tmp_dt = tmp_dr[1] - tmp_dr[0]

            max_start = start + (app_length - tmp_dt)

            found = None
            tmp_delta = datetime.timedelta(0, 0)
            while found is None:
                try:
                    tmp_delta += datetime.timedelta(0, 1)
                    tmp = current_app.values.index.get_loc(max_start - tmp_delta)
                    found = tmp
                except:
                    pass

            start_random = random.choice(current_app.values[0].keys()[:found - 1])
            start_random_index = current_app.values.index.get_loc(start_random)

            result = dict()

            for current_date in data[start_random_index:]:
                if current_date - start_random < tmp_dt:
                    key = random_time + (current_date - start_random)
                    value = current_app.values.index.get_loc(current_date)
                    result.update({key: values[value]})
                    pass
                else:
                    break

            for r in result:

                if r in self.aggregated.keys():
                    # print("HAS", r)
                    self.aggregated[r][1] += result[r]
                else:
                    self.aggregated.update({r: [list(), result[r]]})
                self.aggregated[r][0].append(result[r])

            c += 1
            p = int(c * 100 / apps_l)
            self.c_buffer.output_status('% ' + str(p))

        if self.noise != 0:
            self.add_noise()

        if self.missing > 0:
            self.add_missing()

        # aggregated_dataset.plot()
        # matplotlib.pyplot.show()



    def calc_complexity(self):
        appliances = []
        comp = complexity.Complexity()

        for app in self.appliance_objects:
            states = app.get_appliance_state_by_edge_detection()
            if states == []:
                states = [0,]
            appliance = complexity.Appliance()
            appliance.add_states_as_collection(states)
            appliances.append(appliance)
            comp.add_appliance(appliance)
            print(states)

        comp.generate_pdfs()
        comp.calc_areas()
        comp.calc_subcomplexities()
        comp.plot_complexity()
        self.c_buffer.output_status('Mean Complexity: {0:10.2f}</br>'.format((comp.complexity_sum / len(comp.all_pdfs))))


        if self.calcTotalComplexity == 'true':
            comp.power_vals = pandas.DataFrame(list(self.aggregated.values()), index=[list(self.aggregated.keys())])
            comp.generate_pdfs()
            self.c_buffer.output_status('Total Dataset Complexity: {0:.2f}</br>'.format(comp.calc_total_complexity()))

    def add_missing(self):
        print('missing')
        to_del = []
        for val in self.aggregated:
            if random.randint(0,self.missing) == self.missing:
                to_del.append(val)
        print(to_del)
        for c_del in to_del:
            del self.aggregated[c_del]


    def add_noise(self):
        for val in self.aggregated:
            self.aggregated[val] += (random.random() * self.noise * 2) - self.noise
            self.aggregated[val] = max(self.aggregated[val], 0)

    def write_csv(self):
        self.c_buffer.output_status("Generating csv file</br>")
        with open('download/' + self.gotten_id + '.csv', 'w') as f:
            for c_line in sorted(self.aggregated.keys()):
                f.write(str(c_line.timestamp()) + ", ")
                value=''
                for app in self.aggregated[c_line][0]:
                    value+='{0:f}, '.format(app)
                value += '{0:f}'.format(self.aggregated[c_line][1])
                f.write(str(value) + '\r\n')
            f.close()

