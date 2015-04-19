__author__ = 'johannesholzl'
import  appliance_dataset
from matplotlib.pyplot import *

if __name__ == '__main__':
    ap = appliance_dataset.ApplianceDataset()

    ap.from_iAWE('/Users/johannesholzl/Documents/work_uni/iAWE/'+str(12)+'.csv')
    ap.values.plot()
    show()
    #savefig('/Users/johannesholzl/Documents/'+str(i)+'.png')