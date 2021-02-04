import os
import studio2021


def read_glazing(filepath):
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    glazing = {}
    for line in lines:
        name, frame_type, glass_type, u_value, t_vis, embodied_carbon_metric, embodied_carbon_imperial = line.split('.')
        glazing[name] = {'frame_type': frame_type, 'u_value': u_value, 't_vis': t_vis,
                         'embodied_carbon_metric': embodied_carbon_metric, 'embodied_carbon_imperial': embodied_carbon_imperial}
    return glazing


if __name__ == '__main__':
    for i in range(50):
        print()
    folder = studio2021.DATA
    filepath = os.path.join(folder, 'glazing.csv')
    glazing = read_glazing(filepath)
