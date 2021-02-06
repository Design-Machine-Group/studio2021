from __future__ import print_function

import os
import math
import json

from studio2021.functions import area_polygon
from studio2021.functions import intersection_segment_plane
from studio2021.functions import normal_polygon
from studio2021.functions import centroid_points

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
        self.__name__               = 'Studio 2021 Building'
        self.orient_dict            = {0:'n', 1:'s', 2:'e', 3:'w'}
        self.zones                  = {}
        self.ceiling_surfaces       = {}
        self.floor_surfaces         = {}
        self.zone_fa                = {}
        self.adiabatic_walls        = {}
        self.facade_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.window_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.opaque_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wwr                    = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_gc               = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_depth            = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.exterior_walls         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.facade_cladding        = None
        self.external_insulation    = None
        self.insulation_thickness   = None
        self.ewall_framing          = None
        self.int_finish             = None
        self.glazing_system         = None
        self.zone_program           = None
        self.weather_file           = None
        self.sql_path               = None
        self.simulation_folder      = None
        self.run_simulation         = False  
        self.simulation_name        = None
        self.zone_program           = None
        self.weather_file           = None
        self.sql_path               = None
        self.simulation_folder      = None
        self.run_simulation         = None


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

        znames                  = data['znames']
        ceiling_surfaces        = data['ceiling_surfaces']
        exterior_walls_n        = data['exterior_walls_n']
        exterior_walls_s        = data['exterior_walls_s']
        exterior_walls_e        = data['exterior_walls_e']
        exterior_walls_w        = data['exterior_walls_w']
        adiabatic_walls         = data['adiabatic_walls']
        floor_surfaces          = data['floor_surfaces']
        wwr                     = data['wwr']
        shade_gc                = data['shade_gc']
        shade_depth             = data['shade_depth']
        facade_cladding         = data['facade_cladding']
        external_insulation     = data['external_insulation']
        insulation_thickness    = data['insulation_thickness']
        ewall_framing           = data['ewall_framing']
        int_finish              = data['int_finish']
        glazing_system          = data['glazing_system']
        simulation_name         = data['simulation_name']
        zone_program            = data['zone_program']
        weather_file            = data['weather_file']
        sql_path                = data['sql_path']
        simulation_folder       = data['simulation_folder']
        run_simulation          = data['run_simulation'] 


        b = cls()

        num_zones = znames.BranchCount
        b.zones = {i: znames.Branch(i)[0] for i in range(num_zones)}

        # ceiling - - -
        for i in range(ceiling_surfaces.BranchCount):
            srf = ceiling_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.ceiling_surfaces[b.zones[i]] = p

        # exterior walls - - -
        # north - 
        for i in b.zones:
            if i < exterior_walls_n.BranchCount:
                srf = exterior_walls_n.Branch(i)
                if len(srf) > 0:
                    p = rs.SurfacePoints(srf[0])
                    p = [p[0], p[2], p[3], p[1]]
                    b.exterior_walls['n'][b.zones[i]] = p

        # south - 
        for i in b.zones:
            if i < exterior_walls_s.BranchCount:
                srf = exterior_walls_s.Branch(i)
                if len(srf) > 0:
                    p = rs.SurfacePoints(srf[0])
                    p = [p[0], p[2], p[3], p[1]]
                    b.exterior_walls['s'][b.zones[i]] = p

        # east - 
        for i in b.zones:
            if i < exterior_walls_e.BranchCount:
                srf = exterior_walls_e.Branch(i)
                if len(srf) > 0:
                    p = rs.SurfacePoints(srf[0])
                    p = [p[0], p[2], p[3], p[1]]
                    b.exterior_walls['e'][b.zones[i]] = p

        # west - 
        for i in b.zones:
            if i < exterior_walls_w.BranchCount:
                srf = exterior_walls_w.Branch(i)
                if len(srf) > 0:
                    p = rs.SurfacePoints(srf[0])
                    p = [p[0], p[2], p[3], p[1]]
                    b.exterior_walls['w'][b.zones[i]] = p

        # adiabatic walls - - -
        for i in range(adiabatic_walls.BranchCount):
            srf = adiabatic_walls.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.adiabatic_walls[b.zones[i]] = p

        # floor surfaces - - -
        for i in range(floor_surfaces.BranchCount):
            srf = floor_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.SurfacePoints(srf[0])
                p = [p[0], p[2], p[3], p[1]]
                b.floor_surfaces[b.zones[i]] = p

        # wwr - - -
        for i in range(wwr.BranchCount):
            wwr_ = wwr.Branch(i)
            if wwr_:
                b.wwr[b.orient_dict[i]] = wwr_[0]

        # shgc - - -
        for i in range(shade_gc.BranchCount):
            shade_gc_ = shade_gc.Branch(i)
            if shade_gc_:
                b.shade_gc[b.orient_dict[i]] = shade_gc_[0]
            

        # shade depth - - -
        for i in range(shade_depth.BranchCount):
            shade_depth_ = shade_depth.Branch(i)
            if shade_depth_:
                b.shade_depth[b.orient_dict[i]] = shade_depth_[0]

        # facade areas - - -
        b.compute_areas()

        # fix normals - - - 
        b.fix_normals()

        # facade data - - -
        b.facade_cladding       = facade_cladding
        b.external_insulation   = external_insulation
        b.insulation_thickness  = insulation_thickness
        b.ewall_framing         = ewall_framing
        b.int_finish            = int_finish
        b.glazing_system        = glazing_system
        b.simulation_name       = simulation_name
        b.zone_program          = zone_program
        b.weather_file          = weather_file
        b.sql_path              = sql_path
        b.simulation_folder     = simulation_folder
        b.run_simulation        = run_simulation

        return b

    def compute_areas(self):
        for okey in self.exterior_walls:
            for zkey in self.exterior_walls[okey]:
                pts = self.exterior_walls[okey][zkey]
                area = area_polygon(pts)
                self.facade_areas[okey][zkey] = area
                self.window_areas[okey][zkey] = area * self.wwr[okey]
                self.opaque_areas[okey][zkey] = area * (1 - self.wwr[okey])

    def fix_normals(self):
        import rhinoscriptsyntax as rs

        # srf = self.exterior_walls['s']['ZONE1']

        self.out = {}
        for zkey in self.zones:
            srfs = []
            zkey = self.zones[zkey]
            if zkey in self.adiabatic_walls:
                srfs.append(self.adiabatic_walls[zkey])
            if zkey in self.ceiling_surfaces:
                srfs.append(self.ceiling_surfaces[zkey])
            if zkey in self.floor_surfaces:
                srfs.append(self.floor_surfaces[zkey])
            for okey in self.exterior_walls:
                # print(zkey, okey, self.exterior_walls[okey])
                # print('')
                if zkey in self.exterior_walls[okey]:
                    srf = self.exterior_walls[okey][zkey]
                    if srf:
                        srfs.append(srf)
            
            self.out[zkey] = srfs

            # planes = []
            # for srf in srfs:
            #     n = normal_polygon(srf, unitized=True)
            #     # n = rs.SurfaceNormal(srf, (1,1))
            #     # cpt = rs.SurfaceAreaCentroid(srf)[0]
            #     cpt = centroid_points(srf)
            #     planes.append((cpt, n))
            # print(zkey, len(planes))
            # for srf in srfs:
            #     for i, srf_ in enumerate(srfs):
            #         if srf != srf_:
            #             n = rs.VectorScale(rs.SurfaceNormal(srf, (1,1)), 1000000)
            #             cpt = rs.SurfaceAreaCentroid(srf)[0]
            #             segment = cpt, rs.VectorAdd(cpt, n)
            #             x = intersection_segment_plane(segment, planes[i])
                        
            #             if x:
            #                 if (rs.FlipSurface(srf, False)):
            #                     pass
            #                 else:
            #                     rs.FlipSurface(srf, True)

    def to_gh_data(self):
        import rhinoscriptsyntax as rs
        import ghpythonlib.treehelpers as th

        data = {}

        # zones - - - - - - - - - - - - - - - - - - - - - - - - - - 

        zones = [self.zones[i] for i in range(len(self.zones))]

        zones_ = [[zone] for zone in zones]
        data['zones'] = th.list_to_tree(zones_, source=[])

        # facade areas - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['facade_areas'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            areas = [[] for _ in range(len(self.facade_areas[okey]))]
            for i, zkey in enumerate(self.facade_areas[okey]):
                areas[i] = [self.facade_areas[okey][zkey]]
            data['facade_areas'][okey] = th.list_to_tree(areas, source=[])

        # exterior walls - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['exterior_walls'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            walls = [[] for _ in range(len(self.exterior_walls[okey]))]
            for i, zkey in enumerate(self.exterior_walls[okey]):
                walls[i] = [rs.AddSrfPt(self.exterior_walls[okey][zkey])]
            data['exterior_walls'][okey] = th.list_to_tree(walls, source=[])

        # cieling - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        ceiling_surfaces = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.ceiling_surfaces:
                ceiling_surfaces[i].append(rs.AddSrfPt(self.ceiling_surfaces[zone]))
        data['ceiling_surfaces'] = th.list_to_tree(ceiling_surfaces, source=[])

        # floor_surfaces - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        floor_surfaces = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.floor_surfaces:
                floor_surfaces[i].append(rs.AddSrfPt(self.floor_surfaces[zone]))
        data['floor_surfaces'] = th.list_to_tree(floor_surfaces, source=[])

        # adiabatic_walls - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        adiabatic_walls = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.adiabatic_walls:
                adiabatic_walls[i].append(rs.AddSrfPt(self.adiabatic_walls[zone]))
        data['adiabatic_walls'] = th.list_to_tree(adiabatic_walls, source=[])

        # wwr - - - - - - - - - - - - - - - - - - - - - - - - - - -

        wwr = [[] for _ in range(len(self.wwr))]
        for i in range(4):
            o = self.orient_dict[i]
            wwr[i].append(self.wwr[o])
        data['wwr'] = th.list_to_tree(wwr, source=[])


        # shgc - - - - - - - - - - - - - - - - - - - - - - - - - - -

        shade_gc = [[] for _ in range(len(self.shade_gc))]
        for i in range(4):
            o = self.orient_dict[i]
            shade_gc[i].append(self.shade_gc[o])
        data['shade_gc'] = th.list_to_tree(shade_gc, source=[])

        # shd - - - - - - - - - - - - - - - - - - - - - - - - - - -

        shade_depth = [[] for _ in range(len(self.shade_depth))]
        for i in range(4):
            o = self.orient_dict[i]
            shade_depth[i].append(self.shade_depth[o])
        data['shade_depth'] = th.list_to_tree(shade_depth, source=[])

        # opaque_areas - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['opaque_areas'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            areas = [[] for _ in range(len(self.opaque_areas[okey]))]
            for i, zkey in enumerate(self.opaque_areas[okey]):
                areas[i] = [self.opaque_areas[okey][zkey]]
            data['opaque_areas'][okey] = th.list_to_tree(areas, source=[])


        # window_areas - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['window_areas'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            areas = [[] for _ in range(len(self.window_areas[okey]))]
            for i, zkey in enumerate(self.window_areas[okey]):
                areas[i] = [self.window_areas[okey][zkey]]
            data['window_areas'][okey] = th.list_to_tree(areas, source=[])


        # facade data - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['facade_cladding']         = self.facade_cladding
        data['external_insulation']     = self.external_insulation
        data['insulation_thickness']    = self.insulation_thickness
        data['ewall_framing']           = self.ewall_framing
        data['int_finish']              = self.int_finish
        data['glazing_system']          = self.glazing_system
        data['simulation_name']         = self.simulation_name
        data['zone_program']            = self.zone_program
        data['weather_file']            = self.weather_file
        data['sql_path']                = self.sql_path
        data['simulation_folder']       = self.simulation_folder
        data['run_simulation']          = self.run_simulation
        return data