import os
import studio2021


def read_materials(material_name):
    filepath = os.path.join(studio2021.DATA, 'materials.csv')
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    materials = {}
    for line in lines:
        data = line.split(',')
        for i in range(len(data)):
            try:
                data[i] = float(data[i])
            except:
                continue
        materials[data[0]]   = {'mtype': data[1],
                                'r_value': data[2],
                                'r_per_in': data[3],
                                'thickness_in': data[4],
                                'thickness_m': data[5], 
                                'conductivity': data[6], 
                                'density': data[7],
                                'sp_heat': data[8],
                                'embodied_carbon': data[9]}
    return materials[material_name]


if __name__ == "__main__":
    for i in range(50):
        print()
    material = read_materials("Plywood")
    print(material)
