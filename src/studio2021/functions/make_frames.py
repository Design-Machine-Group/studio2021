import rhinoscriptsyntax as rs

def make_spaced_frames(guid, x_dist, y_dist, height, core):
    pts = rs.PolylineVertices(guid)
    if len(pts) == 5:
        del(pts[-1])
    a, b, c, d = pts
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
            try:
                p = rs.DivideCurveLength(ab, dx)[1]
                p_ = rs.DivideCurveLength(dc, dx)[1]
                l = rs.AddLine(p, p_)
            except:
                raise Exception('The spans are too large for this polyline')

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

    try:
        core = [pts[core[0]][core[1]][:],pts[core[0] + 1][core[1]][:],
                pts[core[0]+ 1][core[1] + 1][:], pts[core[0]][core[1] + 1][:],
                pts[core[0]][core[1]][:]]
        for pt in core:
            pt[2] -= height
        core = rs.AddPolyline(core)
    except:
        raise Exception('The core is in the wrong place')
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

    return cols, beams_x, beams_y, core

if __name__ == '__main__':
    pass
