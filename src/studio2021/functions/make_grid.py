import rhinoscriptsyntax as rs


def make_grid_structure(sp, span_x, span_y, xaxis, yaxis, height, cores):

    if not sp:
        sp = (0,0,0)
    else:
        sp = rs.PointCoordinates(sp)
    
    if not xaxis:
        vx = (1,0,0)
    else:
        vx = rs.VectorUnitize(rs.VectorCreate(rs.CurveEndPoint(xaxis), rs.CurveStartPoint(xaxis)))

    if not yaxis:
        vy = (0,1,0)
    else:
        vy = rs.VectorUnitize(rs.VectorCreate(rs.CurveEndPoint(yaxis), rs.CurveStartPoint(yaxis)))
    

    pts = []
    for x in span_x:
        sp = rs.VectorAdd(sp, rs.VectorScale(vx, x))
        sp_ = sp
        temp = []
        for y in span_y:
            sp_ = rs.VectorAdd(sp_, rs.VectorScale(vy, y))
            temp.append(sp_)
        pts.append(temp)

    columns = []
    for row in pts:
        for pt in row:
            pt[2] += height
            columns.append(rs.AddLine(pt, (pt[0], pt[1], pt[2]-height)))

    beams_x = []
    for i in range(len(span_x)):
        for j in range(len(span_y) - 1):
            a = pts[i][j]
            b = pts[i][j + 1]
            beams_x.append(rs.AddLine(a, b))

    beams_y = []
    for i in range(len(span_x) - 1):
        for j in range(len(span_y)):
            a = pts[i][j]
            c = pts[i + 1][j]
            beams_y.append(rs.AddLine(a, c))
    
    cores_ = []
    for i in range(0, len(cores), 2):
        core = cores[i], cores[i + 1]
        pts = pts[:]
        core = (pts[core[0]][core[1]],
                pts[core[0] + 1][core[1]],
                pts[core[0] + 1][core[1] + 1],
                pts[core[0]][core[1] + 1],
                pts[core[0]][core[1]])

        for pt in core[:-1]:
            pt[2] -= height

        core = rs.AddPolyline(core)
        cores_.append(core)

    return columns, beams_x, beams_y, cores_

def trim_structure(pl, columns, beams_x, beams_y, cores):
    vert = rs.PolylineVertices(pl)
    pl_ = [[p[0], p[1], 0] for p in vert]
    pl_ = rs.AddPolyline(pl_)
    srf = rs.AddPlanarSrf(pl_)
    z = (0, 0, vert[0][2])

    cols = []
    for col in columns:
        pt = rs.CurveStartPoint(col)
        pt[2] =  0
        if not rs.IsPointOnSurface(srf, pt):
            rs.DeleteObject(col)
        else:
            rs.MoveObject(col, z)
            cols.append(col)
    bx = []
    for beam in beams_x:
        beam = trim_beam(beam, srf, pl_)
        if beam:
            rs.MoveObject(beam, z)
            bx.append(beam)

    by = []
    for beam in beams_y:
        beam = trim_beam(beam, srf, pl_)
        if beam:
            rs.MoveObject(beam, z)
            by.append(beam)
    
    cores_ = []
    for core in cores:
        check = [rs.IsPointOnSurface(srf, pt) for pt in rs.PolylineVertices(core)]
        if all(check):
            rs.MoveObject(core, z)
            cores_.append(core)
        else:
            pass

    return cols, bx, by, cores_

def trim_beam(beam, srf, pl):
    a_ = rs.CurveStartPoint(beam)
    b_ = rs.CurveEndPoint(beam)
    a = [a_[0], a_[1], 0]
    b = [b_[0], b_[1], 0]
    if rs.IsPointOnSurface(srf, a) and rs.IsPointOnSurface(srf, b):
        return beam
    elif rs.IsPointOnSurface(srf, a) or rs.IsPointOnSurface(srf, b):
        beam_ = rs.AddLine(a, b)
        xpt = rs.CurveCurveIntersection(pl, beam_)
        if xpt:
            xpt = xpt[0][1]
            xpt[2] = a_[2]
            if rs.IsPointOnSurface(srf, a):
                spt = [a[0], a[1], a_[2]]
            else:
                spt = [b[0], b[1], b_[2]]
            rs.DeleteObjects([beam, beam_])

            if rs.Distance(spt, xpt) > 1:
                return rs.AddLine(spt, xpt)
            else:
                return None
    else:
        rs.DeleteObject(beam)
        return None

if __name__ == '__main__':
    pass