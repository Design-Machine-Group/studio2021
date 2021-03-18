import rhinoscriptsyntax as rs


def make_spaced_frames(guid, x_dist, y_dist, height):
    a, b, c, d, _ = rs.PolylineVertices(guid)
    ab = rs.AddLine(a, b)
    dc = rs.AddLine(d, c)

    cols = []
    pts = []
    dx = 0
    for i in range(len(x_dist)):
        dx += x_dist[i]
        if dx == 0:
            l = rs.AddLine(a, d)
        else:
            p = rs.DivideCurveLength(ab, dx)[1]
            p_ = rs.DivideCurveLength(dc, dx)[1]
            l = rs.AddLine(p, p_)
        dy = 0
        temp = []
        for j in range(len(y_dist)):
            dy += y_dist[j]
            if dy == 0:
                p = rs.CurveStartPoint(l)
            else:
                p = rs.DivideCurveLength(l, dy)[1]
            temp.append([p[0], p[1], p[2] + height])
            cols.append(rs.AddLine(p, [p[0], p[1], p[2] + height]))
        rs.DeleteObject(l)
        pts.append(temp)

    rs.DeleteObjects([ab, dc])

    beams_x = []
    for i in range(len(x_dist)):
        for j in range(len(y_dist) - 1):
            a = pts[i][j]
            b = pts[i][j + 1]
            beams_x.append(rs.AddLine(a, b))

    beams_y = []
    for i in range(len(x_dist) - 1):
        for j in range(len(y_dist)):
            a = pts[i][j]
            c = pts[i + 1][j]
            beams_y.append(rs.AddLine(a, c))

    return cols, beams_x, beams_y





if __name__ == '__main__':
    rs.DeleteObjects(rs.ObjectsByLayer('Default'))
    for i in range(30): print('')
    quad = rs.ObjectsByLayer('rec')
    xdist = [0, 10, 20, 30]
    ydist = [0, 20, 40, 10, 20, 10]
    height = 15
    make_spaced_frames(quad, xdist, ydist, height)
