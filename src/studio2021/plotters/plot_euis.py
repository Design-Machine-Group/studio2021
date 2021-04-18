import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
from studio2021.datastructures import Building

def plot_eui_curves(building, time):
    # this is probably incorrect, data is ordered by year, not day!!!!!
    ndict = {'hour':1, 'day':24, 'week':168, 'month': 370}
    data = building.eui_kwh_hourly['ZONE1']['cooling']
    cool = []
    for i in range(0, len(data), ndict[time]):
        cool.append(np.mean(data[i:i+ndict[time]]))
    x = range(len(cool))
    color = 'b'
    label = 'cooling'
    lw = 1.
    ls = '-'
    plt.plot(x, cool, color=color, label=label, linewidth=lw, linestyle=ls)
    
    data = building.eui_kwh_hourly['ZONE1']['heating']
    heat = []
    for i in range(0, len(data), ndict[time]):
        heat.append(np.mean(data[i:i+ndict[time]]))
    x = range(len(heat))
    color = 'r'
    label = 'heating'
    plt.plot(x, heat, color=color, label=label, linewidth=lw, linestyle=ls)

    plt.grid(which='both', linestyle=':', linewidth=.5)
    plt.legend()
    plt.show()
    plt.close()

def plot_eui_map(building):
    x = np.arange(0, 365, 1)
    y = np.arange(0, 24, 1)
    num_zones = len(building.eui_kwh_hourly)
    
    
    plt.rcParams['font.size'] = '8'
    cmap = plt.get_cmap('bwr')
    fig, axes = plt.subplots(num_zones, 1)
    
    zkeys = [building.zones[i] for i in range(len(building.eui_kwh_hourly))]
    maxcool = [max(building.eui_kwh_hourly[zkey]['cooling']) for zkey in zkeys]
    maxheat = [max(building.eui_kwh_hourly[zkey]['heating']) for zkey in zkeys]
    vmax = max(max(maxcool), max(maxheat))

    for i, zkey in enumerate(zkeys):
        ax = axes[i]
        data = building.eui_kwh_hourly[zkey]['heating']
        z = np.array(data)
        z = z.reshape(365, 24)

        data = building.eui_kwh_hourly[zkey]['cooling']
        z_ = np.array(data)
        z_ = z_.reshape(365, 24) * -1
        z += z_
        z = z.transpose()

        norm = None
        im = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, shading='auto', vmin=vmax * -1, vmax=vmax)
        ax.set_title('{}'.format(zkey), fontsize='medium')

    fig.suptitle('{} - {} EUI'.format(building.simulation_name, building.city), fontsize=16)
    fig.subplots_adjust(right=.86)
    cbar_ax = fig.add_axes([.9, .01, .01, .9])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('EUI (kWh)', rotation=0)

    ticks = cbar.get_ticks().tolist()
    ticks = [abs(t) for t in ticks]
    ticks[0] = '{} Cooling'.format(str(ticks[0]))
    ticks[-1] = '{} Heating'.format(str(ticks[-1]))
    cbar.ax.set_yticklabels(ticks)

    plt.show()

if __name__ == '__main__':
    for i in range(20): print('')
    import studio2021

    name = 'awesome_name_202104111448.json'
    filepath = os.path.join(studio2021.TEMP, name)
    building = Building.from_json(filepath)
    time = 'hour'
    plot_eui_curves(building, time)
    # plot_eui_map(building)