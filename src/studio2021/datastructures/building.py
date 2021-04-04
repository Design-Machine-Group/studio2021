from __future__ import print_function

import os
import math
import json

from ast import literal_eval
from copy import deepcopy

import studio2021
from studio2021.datastructures import structure
reload(structure)
from studio2021.datastructures.structure import Structure

from studio2021.datastructures import envelope
reload(envelope)
from studio2021.datastructures.envelope import Envelope

from studio2021.functions import city_carbon
reload(city_carbon)

from studio2021.functions import area_polygon
from studio2021.functions import intersection_segment_plane
from studio2021.functions import normal_polygon
from studio2021.functions import centroid_points
from studio2021.functions import scale_vector
from studio2021.functions import add_vectors
from studio2021.functions import distance_point_point
from studio2021.functions import geometric_key
from studio2021.functions import midpoint_point_point
from studio2021.functions.city_carbon import city_EUI
from studio2021.functions.city_carbon import weather


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
        self.__name__               = 'Studio2021Building'
        self.orient_dict            = {0:'n', 1:'s', 2:'e', 3:'w'}
        self.city                   = None
        self.zones                  = {}
        self.floor_surfaces         = {}
        self.ceiling_surfaces       = {}
        self.adiabatic_walls        = {}
        self.floor_areas            = {}
        self.eui_kwh                = {}
        self.eui_kbtu               = {}
        self.eui_kbtu_ft            = {}
        self.eui_kgco2e             = {}
        self.facade_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.window_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.opaque_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wwr                    = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_gc               = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_depth_h          = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_depth_v1         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shade_depth_v2         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.exterior_walls         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.height                 = None
        self.floor_area             = 0.
        self.span_x                 = None
        self.span_y                 = None
        self.beam_length            = None
        self.col_length             = None
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
        self.structure              = None
        self.building_type          = None
        self.num_floors_above       = None
        self.ceiling_condition      = None
        self.floor_condition        = None

    def __str__(self):
        return TPL.format(self.__name__)

    def to_json(self):
        filepath = os.path.join(studio2021.TEMP, '{}.json'.format(self.__name__))
        with open(filepath, 'w+') as fp:
            json.dump(self.data, fp)

    @classmethod
    def from_json(cls, filepath):
        with open(filepath, 'r') as fp:
            data = json.load(fp)
        building = cls()
        building.data = data
        return building

    @property
    def data(self):
        data = {
        'name'                   : self.__name__,
        'orient_dict'            : {0:'n', 1:'s', 2:'e', 3:'w'},
        'zones'                  : {},
        'ceiling_surfaces'       : {},
        'floor_surfaces'         : {},
        'adiabatic_walls'        : {},
        'facade_areas'           : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'window_areas'           : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'opaque_areas'           : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'wwr'                    : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'shade_gc'               : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'shade_depth'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'exterior_walls'         : {repr(key): {} for key in ['n', 's', 'e', 'w']},
        'floor_area'             : self.floor_area,
        'span'                   : self.span,
        'beam_length'            : self.beam_length,
        'col_length'             : self.col_length,
        'facade_cladding'        : self.facade_cladding,
        'external_insulation'    : self.external_insulation,
        'insulation_thickness'   : self.insulation_thickness,
        'ewall_framing'          : self.ewall_framing,
        'int_finish'             : self.int_finish,
        'glazing_system'         : self.glazing_system,
        'simulation_name'        : self.simulation_name,
        'zone_program'           : self.zone_program,
        'weather_file'           : self.weather_file,
        'sql_path'               : self.sql_path,
        'simulation_folder'      : self.simulation_folder,
        'run_simulation'         : self.run_simulation,
        'structure'              : self.structure.data,
        }


        for key in self.orient_dict:
            data['orient_dict'][repr(key)] = self.orient_dict[key]

        for key in self.zones:
            data['zones'][repr(key)] = self.zones[key]

        for key in self.ceiling_surfaces:
            data['ceiling_surfaces'][repr(key)] = self.ceiling_surfaces[key]

        for key in self.floor_surfaces:
            data['floor_surfaces'][repr(key)] = self.floor_surfaces[key]

        for key in self.adiabatic_walls:
            data['adiabatic_walls'][repr(key)] = self.adiabatic_walls[key]

        for okey in self.facade_areas:
            for zkey in self.facade_areas[okey]:
                data['facade_areas'][repr(okey)][repr(zkey)] = self.facade_areas[okey][zkey]

        for okey in self.window_areas:
            for zkey in self.window_areas[okey]:
                data['window_areas'][repr(okey)][repr(zkey)] = self.window_areas[okey][zkey]

        for okey in self.opaque_areas:
            for zkey in self.opaque_areas[okey]:
                data['opaque_areas'][repr(okey)][repr(zkey)] = self.opaque_areas[okey][zkey]

        for okey in self.wwr:
            data['wwr'][repr(okey)] = self.wwr[okey]

        for okey in self.shade_gc:
            data['shade_gc'][repr(okey)] = self.shade_gc[okey]

        for okey in self.shade_depth:
            data['shade_depth'][repr(okey)] = self.shade_depth[okey]

        for okey in self.exterior_walls:
            for zkey in self.exterior_walls[okey]:
                data['exterior_walls'][repr(okey)][repr(zkey)] = self.exterior_walls[okey][zkey]

        return data

    @data.setter
    def data(self, data):
        ceiling_surfaces = data.get('ceiling_surfaces') or {}
        floor_surfaces = data.get('floor_surfaces') or {}
        adiabatic_walls = data.get('adiabatic_walls') or {}
        facade_areas = data.get('facade_areas') or {}
        window_areas = data.get('window_areas') or {}
        opaque_areas = data.get('opaque_areas') or {}
        wwr = data.get('wwr') or {}
        shade_gc = data.get('shade_gc') or {}
        shade_depth = data.get('shade_depth') or {}
        exterior_walls = data.get('exterior_walls') or {}

        for key in ceiling_surfaces:
            self.ceiling_surfaces[literal_eval(key)] = ceiling_surfaces[key]

        for key in floor_surfaces:
            self.floor_surfaces[literal_eval(key)] = floor_surfaces[key]

        for key in adiabatic_walls:
            self.adiabatic_walls[literal_eval(key)] = adiabatic_walls[key]

        for okey in facade_areas:
            for zkey in facade_areas[okey]:
                self.facade_areas[literal_eval(okey)][literal_eval(zkey)] = facade_areas[okey][zkey]

        for okey in window_areas:
            for zkey in window_areas[okey]:
                self.window_areas[literal_eval(okey)][literal_eval(zkey)] = window_areas[okey][zkey]

        for okey in opaque_areas:
            for zkey in opaque_areas[okey]:
                self.opaque_areas[literal_eval(okey)][literal_eval(zkey)] = opaque_areas[okey][zkey]

        for okey in wwr:
            self.wwr[literal_eval(okey)] = wwr[okey]

        for okey in shade_gc:
            self.shade_gc[literal_eval(okey)] = shade_gc[okey]

        for okey in shade_depth:
            self.shade_depth[literal_eval(okey)] = shade_depth[okey]

        for okey in exterior_walls:
            for zkey in exterior_walls[okey]:
                self.exterior_walls[literal_eval(okey)][literal_eval(zkey)] = exterior_walls[okey][zkey]

        self.__name__               = data.get('name') or {}
        self.floor_area             = data.get('floor_area') or {}
        self.span                   = data.get('span') or {}
        self.beam_length            = data.get('beam_length') or {}
        self.col_length             = data.get('col_length') or {}
        self.facade_cladding        = data.get('facade_cladding') or {}
        self.external_insulation    = data.get('external_insulation') or {}
        self.insulation_thickness   = data.get('insulation_thickness') or {}
        self.ewall_framing          = data.get('ewall_framing') or {}
        self.int_finish             = data.get('int_finish') or {}
        self.glazing_system         = data.get('glazing_system') or {}
        self.zone_program           = data.get('zone_program') or {}
        self.weather_file           = data.get('weather_file') or {}
        self.sql_path               = data.get('sql_path') or {}
        self.simulation_folder      = data.get('simulation_folder') or {}
        self.run_simulation         = data.get('run_simulation') or {}  
        self.simulation_name        = data.get('simulation_name') or {}
        self.zone_program           = data.get('zone_program') or {}
        self.weather_file           = data.get('weather_file') or {}
        self.sql_path               = data.get('sql_path') or {}
        self.simulation_folder      = data.get('simulation_folder') or {}
        self.run_simulation         = data.get('run_simulation') or {}
        self.structure              = data.get('structure') or {}

    @classmethod
    def from_gh_data(cls, data):
        import rhinoscriptsyntax as rs

        znames                  = data['znames']
        exterior_walls_n        = data['exterior_walls_n']
        exterior_walls_s        = data['exterior_walls_s']
        exterior_walls_e        = data['exterior_walls_e']
        exterior_walls_w        = data['exterior_walls_w']
        adiabatic_walls         = data['adiabatic_walls']
        floor_surfaces          = data['floor_surfaces']
        ceiling_surfaces        = data['ceiling_surfaces']
        wwr                     = data['wwr']
        shade_gc                = data['shade_gc']
        shade_depth_h           = data['shade_depth_h']
        shade_depth_v1          = data['shade_depth_v1']
        shade_depth_v2          = data['shade_depth_v2']
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

        for k in range(exterior_walls_n.BranchCount):
            walls = exterior_walls_n.Branch(k)
            b.exterior_walls['n'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                b.exterior_walls['n'][b.zones[k]].append(p)

        for k in range(exterior_walls_s.BranchCount):
            walls = exterior_walls_s.Branch(k)
            b.exterior_walls['s'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                b.exterior_walls['s'][b.zones[k]].append(p)

        for k in range(exterior_walls_e.BranchCount):
            walls = exterior_walls_e.Branch(k)
            b.exterior_walls['e'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                b.exterior_walls['e'][b.zones[k]].append(p)

        for k in range(exterior_walls_w.BranchCount):
            walls = exterior_walls_w.Branch(k)
            b.exterior_walls['w'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                b.exterior_walls['w'][b.zones[k]].append(p)


        # adiabatic walls - - -
        for k in range(adiabatic_walls.BranchCount):
            walls = adiabatic_walls.Branch(k)
            b.adiabatic_walls[b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                b.adiabatic_walls[b.zones[k]].append(p)

        # floor surfaces - - -
        for i in range(floor_surfaces.BranchCount):
            srf = floor_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.PolylineVertices(srf[0])
                b.floor_surfaces[b.zones[i]] = p

        # ceiling surfaces - - -
        for i in range(ceiling_surfaces.BranchCount):
            srf = ceiling_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.PolylineVertices(srf[0])
                b.ceiling_surfaces[b.zones[i]] = p

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
        for i in range(shade_depth_h.BranchCount):
            shade_depth_ = shade_depth_h.Branch(i)
            if shade_depth_:
                b.shade_depth_h[b.orient_dict[i]] = shade_depth_[0]

        for i in range(shade_depth_v1.BranchCount):
            shade_depth_ = shade_depth_v1.Branch(i)
            if shade_depth_:
                b.shade_depth_v1[b.orient_dict[i]] = shade_depth_[0]

        for i in range(shade_depth_v2.BranchCount):
            shade_depth_ = shade_depth_v2.Branch(i)
            if shade_depth_:
                b.shade_depth_v2[b.orient_dict[i]] = shade_depth_[0]

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


        # floor - ceiling data - - -
        b.height            = data['height']
        b.ceiling_condition = data['ceiling_condition']
        b.floor_condition   = data['floor_condition']

        # embodied - - -

        b.add_structure(data)

        b.building_type         = data['building_type']
        b.num_floors_above      = data['num_floors_above']
        b.composite_slab        = data['composite_slab']
       
        # city - - - -
        b.csv               = data['csv']
        b.city              = data['city']
        b.kgCo2e_kwh        = city_EUI(b.city)['kg/kWh']
        b.weather_file      = weather(b.city)
       
        return b

    def add_structure(self, data):
        columns = data['columns']
        beams_x = data['beams_x']
        beams_y = data['beams_y']
        core    = data['core']

        cmap = []
        cols = []
        for col in columns:
            mpt = midpoint_point_point(col[0], col[1])
            gk = geometric_key(mpt)
            if gk not in cmap:
                cols.append(col)
                cmap.append(gk)

        cmap = []
        bx = []
        for b in beams_x:
            mpt = midpoint_point_point(b[0], b[1])
            gk = geometric_key(mpt)
            if gk not in cmap:
                bx.append(b)
                cmap.append(gk)

        cmap = []
        by = []
        for b in beams_y:
            mpt = midpoint_point_point(b[0], b[1])
            gk = geometric_key(mpt)
            if gk not in cmap:
                by.append(b)
                cmap.append(gk)
        
        self.columns = cols
        self.beams_x = bx
        self.beams_y = by
        self.core    = core

    def compute_areas(self):
        for okey in self.exterior_walls:
            for zkey in self.exterior_walls[okey]:
                srfs = self.exterior_walls[okey][zkey]
                area = 0
                for srf in srfs:
                    area += abs(area_polygon(srf[:-1]))
                # area = area_polygon(pts[:-1])
                self.facade_areas[okey][zkey] = area
                self.window_areas[okey][zkey] = area * self.wwr[okey]
                self.opaque_areas[okey][zkey] = area * (1 - self.wwr[okey])
        
        for zkey in self.floor_surfaces:
            srf = self.floor_surfaces[zkey]
            area = abs(area_polygon(srf))
            self.floor_areas[zkey] = area
            self.floor_area += area

    def fix_normals(self):
        import rhinoscriptsyntax as rs

        for zkey in self.zones:
            srfs = []
            zkey = self.zones[zkey]
            if zkey in self.adiabatic_walls:
                adiabatic = self.adiabatic_walls[zkey]
                for srf in adiabatic:
                    srfs.append(srf)

            if zkey in self.ceiling_surfaces:
                srfs.append(self.ceiling_surfaces[zkey])
            
            if zkey in self.floor_surfaces:
                srfs.append(self.floor_surfaces[zkey])
            
            for okey in self.exterior_walls:
                if zkey in self.exterior_walls[okey]:
                    srfs_ = self.exterior_walls[okey][zkey]
                    for srf in srfs_:
                        srfs.append(srf)
                    # if srf:
                    #     srfs.append(srf)

            if srfs:
                cpts = [centroid_points(srf[:-1]) for srf in srfs]
                zone_cpt = centroid_points(cpts)

                for i, srf in enumerate(srfs):
                    cpt = cpts[i]
                    n = normal_polygon(srf[:-1], unitized=True)
                    n_ = scale_vector(normal_polygon(srf[:-1], unitized=True), -1)
                    d = distance_point_point(add_vectors(cpt, n), zone_cpt)
                    d_ = distance_point_point(add_vectors(cpt, n_), zone_cpt)
                    if d < d_:
                        srf.reverse()

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
            for j, zkey in enumerate(self.facade_areas[okey]):
                areas[j] = [self.facade_areas[okey][zkey]]
            data['facade_areas'][okey] = th.list_to_tree(areas, source=[])

        # exterior walls - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['exterior_walls'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            walls = [[] for _ in range(len(self.exterior_walls[okey]))]
            for j, zkey in enumerate(self.zones):
                zkey = self.zones[zkey]
                if zkey in self.exterior_walls[okey]:
                    pls = self.exterior_walls[okey][zkey]
                    walls[j] = []
                    for pl in pls:
                        pl = rs.AddPolyline(pl)
                        walls[j].append(rs.AddPlanarSrf(pl)[0])
            data['exterior_walls'][okey] = th.list_to_tree(walls, source=[])

        # cieling - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        ceiling_surfaces = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.ceiling_surfaces:
                pl = rs.AddPolyline(self.ceiling_surfaces[zone])
                ceiling_surfaces[i].append(rs.AddPlanarSrf(pl)[0])
        data['ceiling_surfaces'] = th.list_to_tree(ceiling_surfaces, source=[])

        # floor_surfaces - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        floor_surfaces = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.floor_surfaces:
                pl = rs.AddPolyline(self.floor_surfaces[zone])
                floor_surfaces[i].append(rs.AddPlanarSrf(pl)[0])
        data['floor_surfaces'] = th.list_to_tree(floor_surfaces, source=[])

        # adiabatic_walls - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        adiabatic_walls = [[] for _ in range(len(zones))]
        for i, zone in enumerate(zones):
            if zone in self.adiabatic_walls:
                srfs = self.adiabatic_walls[zone]
                for srf in srfs:
                    pl = rs.AddPolyline(srf)
                    adiabatic_walls[i].append(rs.AddPlanarSrf(pl)[0])
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

        shade_depth = [[] for _ in range(len(self.shade_depth_h))]
        for i in range(4):
            o = self.orient_dict[i]
            shade_depth[i].append(self.shade_depth_h[o])
        data['shade_depth_h'] = th.list_to_tree(shade_depth, source=[])

        shade_depth = [[] for _ in range(len(self.shade_depth_v1))]
        for i in range(4):
            o = self.orient_dict[i]
            shade_depth[i].append(self.shade_depth_v1[o])
        data['shade_depth_v1'] = th.list_to_tree(shade_depth, source=[])

        shade_depth = [[] for _ in range(len(self.shade_depth_v2))]
        for i in range(4):
            o = self.orient_dict[i]
            shade_depth[i].append(self.shade_depth_v2[o])
        data['shade_depth_v2'] = th.list_to_tree(shade_depth, source=[])

        # opaque_areas - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['opaque_areas'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            areas = [[] for _ in range(len(self.opaque_areas[okey]))]
            for j, zkey in enumerate(self.opaque_areas[okey]):
                areas[j] = [self.opaque_areas[okey][zkey]]
            data['opaque_areas'][okey] = th.list_to_tree(areas, source=[])


        # window_areas - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['window_areas'] = {}
        for i in range(4):
            okey = self.orient_dict[i]
            areas = [[] for _ in range(len(self.window_areas[okey]))]
            for j, zkey in enumerate(self.window_areas[okey]):
                areas[j] = [self.window_areas[okey][zkey]]
            data['window_areas'][okey] = th.list_to_tree(areas, source=[])

        data['city']                    = self.city

        # facade data - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['height']                  = self.height
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

        # floor - ceiling data - - - - - - - - - - - - - - - - - - - - - - - - -

        data['ceiling_condition']       = self.ceiling_condition
        data['floor_condition']         = self.floor_condition

        return data

    def compute_structure_embodied(self):
        area = self.floor_area
        columns = self.columns
        bx = self.beams_x
        by = self.beams_y
        core = self.core
        composite = self.composite_slab
        btype = self.building_type
        numf = self.num_floors_above
        self.structure = Structure(area, columns, bx, by, composite, btype, numf, core)
        self.structure.compute_embodied()

    def compute_envelope_embodied(self):
        self.envelope = Envelope(self.opaque_areas,
                                 self.window_areas,
                                 self.external_insulation,
                                 self.insulation_thickness,
                                 self.facade_cladding,
                                 self.glazing_system)

        self.envelope.compute_embodied()
     
    def draw_structure(self):
        import rhinoscriptsyntax as rs

        c_th = self.structure.conc_thick 
        t_th = self.structure.timber_thick
        pls = [self.ceiling_surfaces[zkey] for zkey in self.ceiling_surfaces]
        slabs = []
        for pl in pls:
            pl = rs.AddPolyline(pl)
            srf = rs.ExtrudeCurveStraight(pl, [0, 0, 0], [0, 0, -c_th])
            rs.CapPlanarHoles(srf)
            slabs.append(srf)
            rs.MoveObject(pl, [0, 0, -c_th])
            srf = rs.ExtrudeCurveStraight(pl, [0, 0, -c_th], [0, 0, - c_th -t_th])
            rs.CapPlanarHoles(srf)
            slabs.append(srf)

        side = self.structure.col_side

        sh = self.structure.timber_thick + self.structure.conc_thick

        columns = []
        for sp, ep in self.columns:
            sp_ = rs.VectorAdd(sp, [-side/2., -side/2.,0])
            b = rs.VectorAdd(sp_, [1,0,0])
            c = rs.VectorAdd(sp_, [0,1,0])
            ep_ = ep[0], ep[1], ep[2] - sh

            plane = rs.PlaneFromPoints(sp_, b, c)
            sec = rs.AddRectangle(plane, side, side)
            col = rs.AddLine(sp, ep_)
            columns.append(rs.ExtrudeCurve(sec, col))

        bw = self.structure.beam_width
        bh = self.structure.beam_height


        beams = []
        for sp, ep in self.structure.main_beams:
            x = rs.VectorCreate(ep, sp)
            z = [0,0,1]
            y = rs.VectorCrossProduct(x, z)
            y_ = rs.VectorScale(rs.VectorUnitize(y), bw / -2.)
            
            sp_ = rs.VectorAdd(sp, y_)
            sp_ = rs.VectorAdd(sp_, [0,0,-bh -sh])    
            b = rs.VectorAdd(sp_, y)
            c = rs.VectorAdd(sp_, z)
            plane = rs.PlaneFromPoints(sp_, b, c)
            sec = rs.AddRectangle(plane, bw, bh)
            beam = rs.AddLine(sp, ep)
            beams.append(rs.ExtrudeCurve(sec, beam))

        bh_ = bh *.5
        for sp, ep in self.structure.second_beams:
            x = rs.VectorCreate(ep, sp)
            z = [0,0,1]
            y = rs.VectorCrossProduct(x, z)
            y_ = rs.VectorScale(rs.VectorUnitize(y), bw / -2.)
            
            sp_ = rs.VectorAdd(sp, y_)
            sp_ = rs.VectorAdd(sp_, [0,0,-bh_ -sh])    
            b = rs.VectorAdd(sp_, y)
            c = rs.VectorAdd(sp_, z)
            plane = rs.PlaneFromPoints(sp_, b, c)
            sec = rs.AddRectangle(plane, bw, bh_)
            beam = rs.AddLine(sp, ep)
            beams.append(rs.ExtrudeCurve(sec, beam))

        core = rs.ExtrudeCurve(rs.AddPolyline(self.core), col)

        return slabs, columns, beams, core

    def add_eui_results(self, cool, heat, light, eq, hot):
        totals = 0
        for i in range(len(cool)):
            c = sum(cool[i])
            h = sum(heat[i])
            l = sum(light[i])
            e = sum(eq[i])
            w = sum(hot[i])
            tot = sum([c, h, l, e, w])
            totals += tot
            self.eui_kwh[self.zones[i]] = {'cooling':c,
                                           'heating':h,
                                           'lighting':l,
                                           'equipment':e,
                                           'hot_water':w,
                                           'total':tot}
        self.eui_kwh_total = totals

        for zkey in self.eui_kwh:
            temp = {}
            for key in self.eui_kwh[zkey]:
                temp[key] = self.eui_kwh[zkey][key] * 3.41214
            self.eui_kbtu[zkey] = temp
        
        totals = [self.eui_kbtu[zkey]['total'] for zkey in self.eui_kbtu]
        self.eui_kbtu_total = sum(totals)
        
        for zkey in self.eui_kbtu:
            temp = {}
            for key in self.eui_kbtu[zkey]:
                temp[key] = self.eui_kbtu[zkey][key] / self.floor_areas[zkey]
            self.eui_kbtu_ft[zkey] = temp

        totals = [self.eui_kbtu_ft[zkey]['total'] for zkey in self.eui_kbtu_ft]
        self.eui_kbtu_ft_total = sum(totals)

        for zkey in self.eui_kwh:
            temp = {}
            for key in self.eui_kwh[zkey]:
                temp[key] = self.eui_kwh[zkey][key] * self.kgCo2e_kwh
            self.eui_kgco2e[zkey] = temp

        totals = [self.eui_kgco2e[zkey]['total'] for zkey in self.eui_kgco2e]
        self.eui_kgco2e_total = sum(totals)

    def write_csv_result(self):
        # fn = self.simulation_name+ '.csv'
        fn = self.csv
        filepath = os.path.join(self.simulation_folder, fn)
        fh = open(filepath, 'w')

        fh.write('{}\n'.format(self.simulation_name))
        fh.write('Program,{}\n'.format(self.zone_program))
        fh.write('Location,{}\n'.format(self.city))
        fh.write('\n')

        fh.write('Height (ft),{}\n'.format(self.height))
        fh.write('Wall Assembly R Value,{}\n'.format('Not yet'))
        fh.write('U Value window,{}\n'.format('Not yet'))
        fh.write('\n')

        fh.write('N WWR,{}\n'.format(self.wwr['n']))
        fh.write('N SHGC,{}\n'.format(self.shade_gc['n']))
        fh.write('N Shade depth h,{}\n'.format(self.shade_depth_h['n']))
        fh.write('N Shade depth v1,{}\n'.format(self.shade_depth_v1['n']))
        fh.write('N Shade depth v2,{}\n'.format(self.shade_depth_v2['n']))

        fh.write('S WWR,{}\n'.format(self.wwr['s']))
        fh.write('S SHGC,{}\n'.format(self.shade_gc['s']))
        fh.write('S Shade depth h,{}\n'.format(self.shade_depth_h['s']))
        fh.write('S Shade depth v1,{}\n'.format(self.shade_depth_v1['s']))
        fh.write('S Shade depth v2,{}\n'.format(self.shade_depth_v2['s']))

        fh.write('E WWR,{}\n'.format(self.wwr['e']))
        fh.write('E SHGC,{}\n'.format(self.shade_gc['e']))
        fh.write('E Shade depth h,{}\n'.format(self.shade_depth_h['e']))
        fh.write('E Shade depth v1,{}\n'.format(self.shade_depth_v1['e']))
        fh.write('E Shade depth v2,{}\n'.format(self.shade_depth_v2['e']))

        fh.write('W WWR,{}\n'.format(self.wwr['w']))
        fh.write('W SHGC,{}\n'.format(self.shade_gc['w']))
        fh.write('W Shade depth h,{}\n'.format(self.shade_depth_h['w']))
        fh.write('W Shade depth v1,{}\n'.format(self.shade_depth_v1['w']))
        fh.write('W Shade depth v2,{}\n'.format(self.shade_depth_v2['w']))
        fh.write('\n')

        fh.write(',Slab,Beams & Columns,Core,Window,Opaque Wall,Total\n')
        s = 'Embodied (eq CO2 kg total),{0},{1},{2},{3},{4},{5}\n'
        tot = self.structure.slab_embodied + self.structure.beam_embodied 
        tot += self.structure.column_embodied + self.envelope.window_embodied 
        tot += self.envelope.wall_embodied + self.structure.core_embodied
        tot += self.structure.connections_embodied
        
        fh.write(s.format(self.structure.slab_embodied,
                          self.structure.beam_embodied + self.structure.column_embodied + self.structure.connections_embodied,
                          self.structure.core_embodied,
                          self.envelope.window_embodied,
                          self.envelope.wall_embodied,
                          tot))
        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        s = 'Floor Area (ft2),{0},{1},{2},{3},{4},{5}\n'
        areas = []
        tot = 0
        for i in range(5):
            if self.zones[i] in self.floor_areas:
                areas.append(self.floor_areas[self.zones[i]])
                tot += self.floor_areas[self.zones[i]]
            else:
                areas.append(0)
        fh.write(s.format(areas[0], areas[1], areas[2], areas[3], areas[4], tot))
        
        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        
        s = 'North Facade Area (ft2),{0},{1},{2},{3},{4},{5}\n'
        areas = []
        tot = 0
        for i in range(5):
            if self.zones[i] in self.facade_areas['n']:
                areas.append(self.facade_areas['n'][self.zones[i]])
                tot += self.facade_areas['n'][self.zones[i]]
            else:
                areas.append(0)
        fh.write(s.format(areas[0], areas[1], areas[2], areas[3], areas[4], tot))

        s = 'South Facade Area (ft2),{0},{1},{2},{3},{4},{5}\n'
        areas = []
        tot = 0
        for i in range(5):
            if self.zones[i] in self.facade_areas['s']:
                areas.append(self.facade_areas['s'][self.zones[i]])
                tot += self.facade_areas['s'][self.zones[i]]
            else:
                areas.append(0)
        fh.write(s.format(areas[0], areas[1], areas[2], areas[3], areas[4], tot))

        s = 'East Facade Area (ft2),{0},{1},{2},{3},{4},{5}\n'
        areas = []
        tot = 0
        for i in range(5):
            if self.zones[i] in self.facade_areas['e']:
                areas.append(self.facade_areas['e'][self.zones[i]])
                tot += self.facade_areas['e'][self.zones[i]]
            else:
                areas.append(0)
        fh.write(s.format(areas[0], areas[1], areas[2], areas[3], areas[4], tot))

        s = 'West Facade Area (ft2),{0},{1},{2},{3},{4},{5}\n'
        areas = []
        tot = 0
        for i in range(5):
            if self.zones[i] in self.facade_areas['w']:
                areas.append(self.facade_areas['w'][self.zones[i]])
                tot += self.facade_areas['w'][self.zones[i]]
            else:
                areas.append(0)
        fh.write(s.format(areas[0], areas[1], areas[2], areas[3], areas[4], tot))

        names = ['Cooling', 'Heating', 'Lighting', 'Equipment', 'Hot Water', 'Total']
        dkeys = ['cooling','heating','lighting','equipment','hot_water','total']

        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        
        s = '{0} EUI (kBtu/sf/year),{1},{2},{3},{4},{5},{6}\n'
        for j, name in enumerate(names):
            dkey = dkeys[j]
            data = []
            tot = 0
            for i in range(5):
                if self.zones[i] in self.eui_kbtu_ft:
                    data.append(self.eui_kbtu_ft[self.zones[i]][dkey])
                    tot += self.eui_kbtu_ft[self.zones[i]][dkey]
                else:
                    data.append(0)
            fh.write(s.format(name, data[0], data[1], data[2], data[3], data[4], tot))

        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')

        s = '{0} EUI (kBtu/year),{1},{2},{3},{4},{5},{6}\n'
        for j, name in enumerate(names):
            dkey = dkeys[j]
            data = []
            tot = 0
            for i in range(5):
                if self.zones[i] in self.eui_kbtu:
                    data.append(self.eui_kbtu[self.zones[i]][dkey])
                    tot += self.eui_kbtu[self.zones[i]][dkey]
                else:
                    data.append(0)
            fh.write(s.format(name, data[0], data[1], data[2], data[3], data[4], tot))


        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')

        s = '{0} EUI (kWh/year),{1},{2},{3},{4},{5},{6}\n'
        for j, name in enumerate(names):
            dkey = dkeys[j]
            data = []
            tot = 0
            for i in range(5):
                if self.zones[i] in self.eui_kwh:
                    data.append(self.eui_kwh[self.zones[i]][dkey])
                    tot += self.eui_kwh[self.zones[i]][dkey]
                else:
                    data.append(0)
            fh.write(s.format(name, data[0], data[1], data[2], data[3], data[4], tot))


        fh.write('\n')
        fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')

        s = '{0} EUI (kg CO2/year),{1},{2},{3},{4},{5},{6}\n'
        for j, name in enumerate(names):
            dkey = dkeys[j]
            data = []
            tot = 0
            for i in range(5):
                if self.zones[i] in self.eui_kgco2e:
                    data.append(self.eui_kgco2e[self.zones[i]][dkey])
                    tot += self.eui_kgco2e[self.zones[i]][dkey]
                else:
                    data.append(0)
            fh.write(s.format(name, data[0], data[1], data[2], data[3], data[4], tot))

        slab = self.structure.slab_embodied
        beam = self.structure.beam_embodied
        col = self.structure.column_embodied
        win = self.envelope.window_embodied
        wall = self.envelope.wall_embodied

        emb = sum([slab, beam, col, win, wall])
        op = self.eui_kgco2e_total * 30

        fh.write('\n')
        fh.write(',Embodied,Operational,Total\n')
        fh.write('Emissions Total 30 years (kg),{0},{1},{2}\n'.format(emb, op, emb + op))

        fh.close()

if __name__ == '__main__':
    for i in range(50): print('')
    filepath = os.path.join(studio2021.TEMP, 'Studio2021Building.json')
    b = Building.from_json(filepath)