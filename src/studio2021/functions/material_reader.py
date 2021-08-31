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
                pass
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

def read_materials_city(material, city):
    # city_dict = {'National': 2, 'Seattle':3, 'Milwaukee':4, 'San Antonio':5}
    filepath = os.path.join(studio2021.DATA, 'materials_embodied.csv')
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    data = {}
    del(lines[0])
    for l in lines:
        l = l.split(',')
        data[l[0]] = {'National': float(l[2]),
                      'Seattle': float(l[3]),
                      'Milwaukee': float(l[4]),
                      'San Antonio': float(l[5]),
                      'Los Angeles': float(l[6]),
                      'Atlanta': float(l[7]),
                      'New York': float(l[8])}

    if data[material][city] == 0:
        return data[material]['National']
    else:
        return data[material][city]

if __name__ == "__main__":
    for i in range(50):
        print()
    material = read_materials("Plywood")
    print(material)
