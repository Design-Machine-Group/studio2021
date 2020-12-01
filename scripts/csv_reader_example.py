import os
import studio2021

def read_colors(fileapth):
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    colors = {}
    for line in lines:
        color, r, g, b = line.split(',')
        for i in r, g, b:
            if i == 'None\n':
                i = None
            else:
                i = int(i)
        colors[color] = {'r':r, 'g':g, 'b':b}
    return colors


if __name__ == "__main__":
    for i in range(50):print()
    folder = studio2021.DATA
    filepath = os.path.join(folder, 'colors.csv')
    colors = read_colors(filepath)
    # print(colors['Blue']['b'])

    for key in colors:
        for rgb in colors[key]:
            print(key, colors[key][rgb])