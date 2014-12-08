from appliance_dataset import *
import json

#main function only when this script is called
def main():
    print('Appliance Data Analysis and Modification Toolkit...')
    
    #config file is stored into config dict
    config = json.load(open("path/to/config.json","r"))
    print(config)
    appliances_config = config["Appliances"]
    appliances = list()
    print("")
    print(appliances_config)
    for app in range(len(appliances_config)):
        appliance = ApplianceDataset()
        if appliances_config[app]["dataset"] == "REDD":
            appliance.from_REDD(appliances_config[app]["path"])
    
        print(appliance.settings)
        appliance.import_settings(appliances_config[app])
        print(appliance.settings)
        appliance.fill_missing()
        appliance.resample()
        appliance.med()
        appliance.plot()
        appliance.get_appliance_state()
        states = appliance.get_appliance_state_by_edge_detection()
        print(appliance.get_states_per_day(states))


    appliances.append(appliance)

    matplotlib.pyplot.show()


if __name__ == '__main__':
    main()
