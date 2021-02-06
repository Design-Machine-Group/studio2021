import rhinoscriptsyntax as rs

from geometry import intersection_segment_plane


def fix_room_normals(srfs):
    planes = []
    for srf in srfs:
        n = rs.SurfaceNormal(srf, (1,1))
        cpt = rs.SurfaceAreaCentroid(srf)[0]
        planes.append((cpt, n))

    for srf in srfs:
        for i, srf_ in enumerate(srfs):
            if srf != srf_:
                n = rs.VectorScale(rs.SurfaceNormal(srf, (1,1)), 1000000)
                cpt = rs.SurfaceAreaCentroid(srf)[0]
                segment = cpt, rs.VectorAdd(cpt, n)
                x = intersection_segment_plane(segment, planes[i])
                if x:
                    if (rs.FlipSurface(srf, False)):
                        pass
                    else:
                        rs.FlipSurface(srf, True)

if __name__ == '__main__':
    for i in range(50): print('')
    rs.DeleteObjects(rs.ObjectsByLayer('Default'))

    srfs  =rs.ObjectsByLayer('srfs')
    fix_room_normals(srfs)
