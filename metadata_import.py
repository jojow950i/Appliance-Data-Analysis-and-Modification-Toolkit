import server
import yaml
import os

def import_datasets():
    channels = {}
    import_REDD(channels)
    import_GREEND(channels)
    import_iAWE(channels)
    return channels

def import_REDD(channels):

    houses = os.listdir(server.redd_path)

    for house in houses:
        if house.startswith("house"):

            labels = os.path.join(server.redd_path, house, 'labels.dat')
            with open(labels, 'r') as data:

                for line in data:
                    channel = line.split(' ')[0]
                    name = line.split(' ')[1]
                    name = name.replace('\n', '')
                    name = name.replace('_', ' ')

                    if name not in channels.keys():
                        channels.update(
                            {name: {'datasets': {'REDD': {'small': [], 'medium': [], 'large': []}}, }})

                    if name != 'mains':
                        channel_name = server.redd_infos[house]['channel_' + channel]
                        channels[name]['datasets']['REDD'][channel_name].append((channel, house))

def import_GREEND(channels):

    buildings = os.listdir(os.path.join(server.greend_path, 'metadata'))

    for building in buildings:
        if building.startswith('building'):
            building_name = building.split('.')[0]
            with open(os.path.join(server.greend_path, 'metadata', building), 'r') as building_meta:
                meta_yaml = yaml.load(building_meta)

                meters = {}
                unasigned_meters = 0
                while unasigned_meters != []:
                    unasigned_meters = []
                    for meter in meta_yaml['elec_meters']:
                        submeter_of = meta_yaml['elec_meters'][meter]['submeter_of']
                        if submeter_of == 0:
                            meters.update({meter: {'submeter': []}})
                        else:
                            if submeter_of in meters.keys():
                                meters[submeter_of]['submeter'].append(meter)
                            else:
                                unasigned_meters.append(meter)

                    for unasigned_meter in unasigned_meters:
                        submeter_of = meta_yaml['elec_meters'][unasigned_meters]['submeter_of']
                        if submeter_of in meters.keys():
                            meters[submeter_of]['submeter'].append(meter)
                            unasigned_meters.remove(unasigned_meter)

                appliances = []
                try:
                    appliances = meta_yaml['appliances']
                except:
                    pass

                for meter in meters:
                    apps = []
                    for submeter in meters[meter]['submeter']:
                        submeter_apps = []

                        for appliance in appliances:
                            if appliance['meters'][0] == submeter:
                                submeter_apps.append(appliance['type'])
                                apps.append(appliance['type'])

                        submeter_apps = sorted(submeter_apps)
                        name = submeter_apps[0]
                        if len(submeter_apps) > 1:
                            for app in submeter_apps[1:]:
                                name += ' + ' + app

                        if name not in channels.keys():
                            channels.update(
                                {name: {'datasets': {'GREEND': {'small': [], 'medium': [], 'large': []}}, }})
                        elif 'GREEND' not in channels[name]['datasets']:
                            channels[name]['datasets'].update({'GREEND': {'small': [], 'medium': [], 'large': []}})


                    for appliance in appliances:
                        if meter in appliance['meters']:
                            apps.append(appliance['type'])

                    if len(apps) > 0:
                        name = apps[0]
                        if len(apps) > 1:
                            for app in apps[1:]:
                                name += ' + ' + app

                        if name not in channels.keys():
                            channels.update(
                                {name: {'datasets': {'GREEND': {'small': [], 'medium': [], 'large': []}}, }})
                        elif 'GREEND' not in channels[name]['datasets']:
                            channels[name]['datasets'].update({'GREEND': {'small': [], 'medium': [], 'large': []}})

                        channel_name = None
                        try:
                            channel_name = server.greend_infos[building.split('.')[0]]['channel_' + str(meter)]
                        except:
                            channel_name = 'medium'

                        channels[name]['datasets']['GREEND'][channel_name].append((meter, building_name))
def import_iAWE(channels):


    labels = os.path.join(server.iAWE_path, 'labels.dat')
    with open(labels, 'r') as data:

        for line in data:
            line = line.replace('\n', '')
            channel, *name_list = line.split(' ')

            name = name_list[0]
            if len(name_list) > 1:
                for c_name in name_list[1:]:
                    name += ' ' + c_name

            if name not in channels.keys():
                channels.update(
                    {name: {'datasets': {'iAWE': {'small': [], 'medium': [], 'large': []}}, }})
            elif 'iAWE' not in channels[name]['datasets']:
                            channels[name]['datasets'].update({'iAWE': {'small': [], 'medium': [], 'large': []}})

            if name != 'mains':

                channel_name = server.iawe_infos['building_1']['channel_' + channel]
                channels[name]['datasets']['iAWE'][channel_name].append((channel,'building1'))
