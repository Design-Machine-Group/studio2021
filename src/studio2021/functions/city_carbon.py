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
        cities[data[0]] = {'city_name': data[1],
                           'CO2e (lb/MWh)': data[2],
                           'CO2e (lb/kWh)': data[3],
                           'CO2e (kg/MWh)': data[4]}
    return cities[city_name]


if __name__ == "__main__":
    for i in range(50):
        print()
    EUI_test = 1200  # example value
    EUI_updated = city_EUI("Seattle")
    print(EUI_updated)
