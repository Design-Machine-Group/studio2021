import rhinoscriptsyntax as rs
import studio2021
import os


def i_to_rgb(i, normalize=False):
    i = max(i, 0.0)
    i = min(i, 1.0)
    if i == 0.0:
        r, g, b = 0, 0, 255
    elif 0.0 < i < 0.25:
        r, g, b = 0, int(255 * (4 * i)), 255
    elif i == 0.25:
        r, g, b = 0, 255, 255
    elif 0.25 < i < 0.5:
        r, g, b = 0, 255, int(255 - 255 * 4 * (i - 0.25))
    elif i == 0.5:
        r, g, b = 0, 255, 0
    elif 0.5 < i < 0.75:
        r, g, b = int(0 + 255 * 4 * (i - 0.5)), 255, 0
    elif i == 0.75:
        r, g, b = 255, 255, 0
    elif 0.75 < i < 1.0:
        r, g, b,  = 255, int(255 - 255 * 4 * (i - 0.75)), 0
    elif i == 1.0:
        r, g, b = 255, 0, 0
    else:
        r, g, b = 0, 0, 0
    if not normalize:
        return r, g, b
    return r / 255.0, g / 255.0, b / 255.0

def make_plot(filename, scale):
    filepath = os.path.join(studio2021.TEMP, filename)
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()

    data = []
    for line in lines:
        line = line.split(',')
        data.append([float(i) for i in line])

    x = data[0]
    y = [i[0] for i in data]

    nx = len(x)
    ny = len(y)

    # count = 0
    pts = []
    zs = []
    for i in range(1, nx):
        for j in range(1, ny):
            z = data[j][i]
            pts.append([x[i]*scale[0], y[j]*scale[1], z*scale[2]])
            zs.append(z)
            # rs.AddTextDot(str(count), [x[i], y[j], z])
            # count += 1

    faces = []
    for i in range(nx - 2):
        for j in range(ny - 2):
            a = j + (i * (ny - 1))
            b = j + ((1 + i) * (ny - 1))
            c = j + ((1 + i) * (ny - 1)) + 1
            d = j + (i * (ny - 1)) + 1
            faces.append([a, b, c, d])
            # print(a, b, c, d)

    m = min(zs)
    M = max(zs)
    colors = [i_to_rgb((z-m)/(M-m)) for z in zs]

    mesh = rs.AddMesh(pts, faces)
    rs.MeshVertexColors(mesh, colors)
    a, b, c = (x[1] * scale[0], y[1] * scale[1] - 2, 0)
    n = 10
    delta = (M - m) / n
    s = (x[-1]*scale[0] - x[1] * scale[1]) / (n + 1)
    print(x[-1], x[1], s)
    for i in range(n + 1):
        v = [[a + (i * s), b, c],
             [a + (i * s) + s, b, c],
             [a + (i * s) + s, b + s, c],
             [a + (i * s), b + s, c]]
        f = [[0, 1, 2, 3]]
        mesh = rs.AddMesh(v, f)
        color = i_to_rgb((i-0)/((n)-0))
        rs.ObjectColor(mesh, color)
        z = round(m + (i * delta), 2)
        rs.AddText(str(z), [a + (i * s) + s / 2, b + s / 2, c], s / 4, font='Arial', justification=131072+2)

if __name__ == '__main__':
    for i in range(20): print('')
    rs.DeleteObjects(rs.ObjectsByLayer('Default'))

    scale = 1, 1, .11
    make_plot('landscape.csv', scale)
