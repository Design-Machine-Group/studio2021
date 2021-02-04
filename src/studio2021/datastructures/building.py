from __future__ import print_function

import os
import math
import json

from studio2021.functions import area_polygon

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"


TPL = """
#########################################
Building data structure: {}
#########################################
"""

class Building(object):

    def __init__(self):
        self.__name__       = 'Studio2021_Building'
        self.orient_dict    = {0:'n', 1:'s', 2:'e', 3:'w'}
        self.zones          = {}
        self.ceil           = {}
        self.floor          = {}
        self.zone_fa        = {}
        self.adia_w         = {}
        self.facade_areas   = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wa             = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.oa             = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wwr            = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shgc           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shd            = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.exterior_walls = {'n':{}, 's':{}, 'e':{}, 'w':{}}

    def __str__(self):
        return TPL.format(self.__name__)

    def to_json(self, path, filename):
        data = self.data
        data['filename'] = filename
        filepath = os.path.join(path, filename)
        with open(filepath, 'w+') as f:
            json.dump(data, f)

    def from_json(self):
        pass
    
    @property
    def data(self):
        data = {}
        return data

    @classmethod
    def from_gh_data(cls, data):
        import rhinoscriptsyntax as rs

        znames              = data['znames']
        ceilings            = data['ceilings']
        exterior_walls_n    = data['exterior_walls_n']
        exterior_walls_s    = data['exterior_walls_s']
        exterior_walls_e    = data['exterior_walls_e']
        exterior_walls_w    = data['exterior_walls_w']
        aw                  = data['aw']
        fs                  = data['fs']
        # fan               = data['fan']
        # fas               = data['fas']
        # fae               = data['fae']
        # faw               = data['faw']
        wa                  = data['wa']
        oa                  = data['oa']
        wwr                 = data['wwr']
        shgc                = data['shgc']
        shd                 = data['shd']

        b = cls()

        num_zones = znames.BranchCount
        b.zones = {i: znames.Branch(i)[0] for i in range(num_zones)}

        # ceiling - - -
        for i in range(ceilings.BranchCount):
            srf = ceilings.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.ceil[b.zones[i]] = p

        # exterior walls - - -
        # north - 
        for i in range(exterior_walls_n.BranchCount):
            srf = exterior_walls_n.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.exterior_walls['n'][b.zones[i]] = p

        # south - 
        for i in range(exterior_walls_s.BranchCount):
            srf = exterior_walls_s.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.exterior_walls['s'][b.zones[i]] = p

        # east - 
        for i in range(exterior_walls_e.BranchCount):
            srf = exterior_walls_e.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.exterior_walls['e'][b.zones[i]] = p

        # west - 
        for i in range(exterior_walls_w.BranchCount):
            srf = exterior_walls_w.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.exterior_walls['w'][b.zones[i]] = p

        # adiabatic walls - - -
        for i in range(aw.BranchCount):
            srf = aw.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.adia_w[b.zones[i]] = p

        # floor surfaces - - -
        for i in range(fs.BranchCount):
            srf = fs.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.floor[b.zones[i]] = p
    
        # window areas - - -
        for i in range(wa.BranchCount):
            wa_ = (wa.Branch(i))
            if wa:
                if i == 0:
                    b.wa['n'] = wa_[0]
                if i == 1:
                    b.wa['s'] = wa_[0]
                if i == 2:
                    b.wa['e'] = wa_[0]
                if i == 3:
                    b.wa['w'] = wa_[0]

        # opaque areas - - -
        for i in range(oa.BranchCount):
            oa_ = (oa.Branch(i))
            if oa:
                if i == 0:
                    b.oa['n'] = oa_[0]
                if i == 1:
                    b.oa['s'] = oa_[0]
                if i == 2:
                    b.oa['e'] = oa_[0]
                if i == 3:
                    b.oa['w'] = oa_[0]

        # wwr - - -
        for i in range(wwr.BranchCount):
            wwr_ = wwr.Branch(i)
            if wwr_:
                b.wwr[b.orient_dict[i]] = wwr_[0]

        # shgc - - -
        for i in range(shgc.BranchCount):
            shgc_ = shgc.Branch(i)
            if shgc_:
                b.shgc[b.orient_dict[i]] = shgc_[0]
            

        # shade depth - - -
        for i in range(shd.BranchCount):
            shd_ = shd.Branch(i)
            if shgc_:
                b.shd[b.orient_dict[i]] = shd_[0]


        # facade areas - - -
        b.compute_areas()

        # for i in range(fan.BranchCount):
        #     fa = fan.Branch(i)
        #     if fa:
        #         b.fa['n'][b.zones[i]] = fa[0]

        # # facade areas south - - - 
        # for i in range(fas.BranchCount):
        #     fa = fas.Branch(i)
        #     if fa:
        #         b.fa['s'][b.zones[i]] = fa[0]

        # # facade areas east - - - 
        # for i in range(fae.BranchCount):
        #     fa = fae.Branch(i)
        #     if fa:
        #         b.fa['e'][b.zones[i]] = fa[0]        

        # # facade areas west - - - 
        # for i in range(faw.BranchCount):
        #     fa = faw.Branch(i)
        #     if fa:
        #         b.fa['w'][b.zones[i]] = fa[0]

        return b

    def compute_areas(self):
        for okey in self.exterior_walls:
            for zkey in self.exterior_walls[okey]:
                pts = self.exterior_walls[okey][zkey]
                self.facade_areas[okey][zkey] = area_polygon(pts)

    def to_gh_data(self):
        import rhinoscriptsyntax as rs
        import ghpythonlib.treehelpers as th

        data = {}

        # zones - - - - - - - - - - - - - - - - - - - - - - - - - - 

        zones = [self.zones[i] for i in range(len(self.zones))]

        zones_ = [[zone] for zone in zones]
        data['zones'] = th.list_to_tree(zones_, source=[])

        # fcade areas - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['facade_areas'] = {}
        for okey in self.facade_areas:
            areas = [self.facade_areas[okey][zkey] for zkey in self.facade_areas[okey]]
            data['facade_areas'][okey] = th.list_to_tree(areas, source=[])

        # exterior walls - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['exterior_walls'] = {}
        for okey in self.exterior_walls:
            walls = []
            for zkey in self.exterior_walls[okey]:
                walls.append(rs.AddSrfPt(self.exterior_walls[okey][zkey]))
            data['exterior_walls'][okey] = th.list_to_tree(walls, source=[])


        # ew_n = [[] for _ in range(len(zones))]
        # for i, zone in enumerate(zones):
        #     if zone in self.ew['n']:
        #         ew_n[i].append(rs.AddSrfPt(self.ew['n'][zone]))
        # data['ew_n'] = th.list_to_tree(ew_n, source=[])

        # ew_s = [[] for _ in range(len(zones))]
        # for i, zone in enumerate(zones):
        #     if zone in self.ew['s']:
        #         ew_s[i].append(rs.AddSrfPt(self.ew['s'][zone]))
        # data['ew_s'] = th.list_to_tree(ew_s, source=[])

        # ew_e = [[] for _ in range(len(zones))]
        # for i, zone in enumerate(zones):
        #     if zone in self.ew['e']:
        #         ew_e[i].append(rs.AddSrfPt(self.ew['e'][zone]))
        # data['ew_e'] = th.list_to_tree(ew_e, source=[])

        # ew_w = [[] for _ in range(len(zones))]
        # for i, zone in enumerate(zones):
        #     if zone in self.ew['w']:
        #         ew_w[i].append(rs.AddSrfPt(self.ew['w'][zone]))
        # data['ew_w'] = th.list_to_tree(ew_w, source=[])

        # cieling - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        ceil = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.ceil:
                ceil[i].append(rs.AddSrfPt(self.ceil[zone]))
        data['ceil'] = th.list_to_tree(ceil, source=[])

        # fs - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        fs = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.floor:
                fs[i].append(rs.AddSrfPt(self.floor[zone]))
        data['fs'] = th.list_to_tree(fs, source=[])

        # aw - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        aw = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.adia_w:
                aw[i].append(rs.AddSrfPt(self.adia_w[zone]))
        data['aw'] = th.list_to_tree(aw, source=[])

        # wwr - - - - - - - - - - - - - - - - - - - - - - - - - - -

        wwr = [[] for _ in range(len(self.wwr))]
        for i, o in enumerate(self.wwr):
            wwr[i].append(self.wwr[o])
        data['wwr'] = th.list_to_tree(wwr, source=[])


        # shgc - - - - - - - - - - - - - - - - - - - - - - - - - - -

        shgc = [[] for _ in range(len(self.shgc))]
        for i, o in enumerate(self.shgc):
            shgc[i].append(self.shgc[o])
        data['shgc'] = th.list_to_tree(shgc, source=[])

        # shd - - - - - - - - - - - - - - - - - - - - - - - - - - -

        shd = [[] for _ in range(len(self.shd))]
        for i, o in enumerate(self.shd):
            shd[i].append(self.shd[o])
        data['shd'] = th.list_to_tree(shd, source=[])

        # oa - - - - - - - - - - - - - - - - - - - - - - - - - - -

        oa = [[] for _ in range(len(self.oa))]
        for i, o in enumerate(self.oa):
            oa[i].append(self.oa[o])
        data['oa'] = th.list_to_tree(oa, source=[])

        # wa - - - - - - - - - - - - - - - - - - - - - - - - - - -

        wa = [[] for _ in range(len(self.wa))]
        for i, o in enumerate(self.wa):
            wa[i].append(self.wa[o])
        data['wa'] = th.list_to_tree(wa, source=[])

        return data