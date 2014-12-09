#Applience Data Analysis and Modification Toolkit

##Usage

This program can be used to create power profiles of buildings by adding appliance profiles. It is also possible to apply  data analysis functions such as resampling, filling of missing data and median filters. It is using the pandas module for the majority of the functions.
Also the states of the appliance can be calculated using numpy and pandas.

##Abilities

"Applience-Data-Analysis-and-Modification-Toolkit" has several useful qualities such as

- Basic Data Analysis functions powered by Pandas

- Gathering states by frequency of apperance 

- Gathering states by edge detection

- Calculating occurance per day

##Configuration

Settings are passed into the ´ApplianceDataset´ using the ´import_settings()´ function which takes a dictionary as an argument. The valid options can be found at the beginning of the ´ApplianceDataset´ class. 
