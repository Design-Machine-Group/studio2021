import os
import studio2021


def city_EUI(city_name):
    filepath = os.path.join(studio2021.DATA, 'cities.csv')
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    cities = {}
    for line in lines:
        data = line.split(',')
        for i in range(len(data)):
            try:
                data[i] = float(data[i])
            except:
                pass
        cities[data[0]] = {'lb/MWh': data[1],
                           'lb/kWh': data[2],
                           'kg/kWh': data[3]}
    return cities[city_name]

def weather(city_name):
    # se = 'https://energyplus.net/weather-download/north_and_central_america_wmo_region_4/USA/WA/USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3/all'
    # mi = 'https://energyplus.net/weather-download/north_and_central_america_wmo_region_4/USA/WI/USA_WI_Milwaukee-Mitchell.Intl.AP.726400_TMY3/all'
    # sa = 'https://energyplus.net/weather-download/north_and_central_america_wmo_region_4/USA/TX/USA_TX_San.Antonio.Intl.AP.722530_TMY3/all'

    se = os.path.join(studio2021.DATA, 'USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw')
    mi = os.path.join(studio2021.DATA, 'USA_WI_Milwaukee-Mitchell.Intl.AP.726400_TMY3.epw')
    sa = os.path.join(studio2021.DATA, 'USA_TX_San.Antonio.Intl.AP.722530_TMY3.epw')
    la = os.path.join(studio2021.DATA, 'USA_CA_Los.Angeles.Intl.AP.722950_TMY3.epw')
    ny = os.path.join(studio2021.DATA, 'USA_NY_New.York-Central.Park.725033_TMY3.epw')
    at = os.path.join(studio2021.DATA, 'USA_GA_Atlanta-Hartsfield-Jackson.Intl.AP.722190_TMY3.epw')

    weather = {'Seattle': se, 'Milwaukee': mi, 'San Antonio':sa, 'Los Angeles':la, 'New York':ny, 'Atlanta':at}
    return weather[city_name]

if __name__ == '__main__':
    for i in range(50):
        print()
    EUI_test = 1200  # example value
    EUI_updated = city_EUI('San Antonio')
    print(EUI_updated)
