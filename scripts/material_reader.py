import os
import studio2021

# def read_colors(filepath):
#     fh = open(filepath, 'r')
#     lines = fh.readlines()
#     fh.close()
#     del(lines[0])
#     colors = {}
#     for line in lines:
#         color, r, g, b = line.split(',')
#         for i in r, g, b:
#             if i == 'None\n':
#                 i = None
#             else:
#                 i = int(i)
#         colors[color] = {'r':r, 'g':g, 'b':b}
#     return colors
#
#
# if __name__ == "__main__":
#     for i in range(50):print()
#     folder = studio2021.DATA
#     filepath = os.path.join(folder, 'colors.csv')
#     colors = read_colors(filepath)
#     # print(colors['Blue']['b'])
#
# for key in colors:
#     for rgb in colors[key]:
#         print(key, colors[key][rgb])

# ---------------------------------------------------------------------------------------------------------------


def read_materials(filepath):
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    materials = {}
    for line in lines:
        material, type, r_value, r_per_in, thickness_in, thickness_m, conductivity, density, sp_heat, embodied_carbon = line.split(
            ',')
        for i in type, r_value, r_per_in, thickness_in, thickness_m, conductivity, density, sp_heat, embodied_carbon:
            if i == 'None\n' or 'None':
                i = None
            else:
                i = float(i)
        materials[material] = {'type': type, 'r_value': r_value, 'r_per_in': r_per_in, 'thickness_in': thickness_in,
                               'thickness_m': thickness_m, 'conductivity': conductivity, 'density': density, 'sp_heat': sp_heat, 'embodied_carbon': embodied_carbon}
    return materials


if __name__ == "__main__":
    for i in range(50):
        print()
    folder = studio2021.DATA
    filepath = os.path.join(folder, 'materials.csv')
    materials = read_materials(filepath)

    print(materials)

    for key in materials:
        # print(key, type)
        for embodied_carbon in materials[key]:
            print(key, materials[key][embodied_carbon])
