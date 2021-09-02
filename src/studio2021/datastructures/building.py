from __future__ import print_function

import os
import math
import json

from ast import literal_eval
import shutil

import studio2021
from studio2021.datastructures import structure
try:
    reload(structure)
except:
    pass
from studio2021.datastructures.structure import Structure

from studio2021.datastructures import envelope
try:
    reload(envelope)
except:
    pass
from studio2021.datastructures.envelope import Envelope

from studio2021.functions import city_carbon
try:
    reload(city_carbon)
except:
    pass

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
        self.csv                    = None
        self.city                   = None
        self.zones                  = {}
        self.floor_surfaces         = {}
        self.ceiling_surfaces       = {}
        self.adiabatic_walls        = {}
        self.floor_areas            = {}
        self.eui_kwh                = {}
        self.eui_kwh_hourly         = {}
        self.eui_kbtu               = {}
        self.eui_kbtu_ft            = {}
        self.eui_kgco2e             = {}
        self.max_heating            = {}
        self.max_cooling            = {}
        self.max_lighting           = {}
        self.max_equipment          = {}
        self.max_hot_water          = {}
        self.max_solar              = {}
        self.monthly_euis           = {}
        self.monthly_solar          = {}
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
        self.interior_insul_mat     = None
        self.int_ins_thickness      = None
        self.ewall_framing          = None
        self.int_finish             = None
        self.glazing_system         = None
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
        self.context                = None
        self.window_u               = None
        self.wall_r                 = None
        self.win_geometry           = None
        self.total_shade_len        = None
        self.inf_rate               = None

    def __str__(self):
        return TPL.format(self.__name__)

    def to_json(self):
        fn = os.path.splitext(self.csv)[0]
        filepath = os.path.join(studio2021.TEMP, '{}.json'.format(fn))
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
        data = {'name'                      : self.__name__,
                'orient_dict'               : {0:'n', 1:'s', 2:'e', 3:'w'},
                'zones'                     : {},
                'ceiling_surfaces'          : {},
                'floor_surfaces'            : {},
                'adiabatic_walls'           : {},
                'eui_kwh'                   : {},
                'eui_kwh_hourly'            : {},
                'eui_kbtu'                  : {},
                'eui_kbtu_ft'               : {},
                'eui_kgco2e'                : {},
                'max_lighting'              : {},
                'max_heating'               : {},
                'max_equipment'             : {},
                'max_hot_water'             : {},
                'max_cooling'               : {},
                'max_solar'                 : {},
                'monthly_euis'              : {},
                'monthly_solar'             : {},
                'facade_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'window_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'opaque_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'wwr'                       : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'shade_gc'                  : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'exterior_walls'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'shade_depth_h'             : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'shade_depth_v1'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'shade_depth_v2'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
                'csv'                       : self.csv,
                'floor_area'                : self.floor_area,
                'simulation_name'           : self.simulation_name,
                'zone_program'              : self.zone_program,
                'weather_file'              : self.weather_file,
                'sql_path'                  : self.sql_path,
                'simulation_folder'         : self.simulation_folder,
                'run_simulation'            : self.run_simulation,
                'structure'                 : self.structure.data,
                'envelope'                  : self.envelope.data,
                'city'                      : self.city,
                'floor_areas'               : {},
                'height'                    : self.height,
                'span_x'                    : self.span_x,
                'span_y'                    : self.span_y,
                'beam_length'               : self.beam_length,
                'col_length'                : self.col_length,
                'facade_cladding'           : self.facade_cladding,
                'external_insulation'       : self.external_insulation,
                'insulation_thickness'      : self.insulation_thickness,
                'interior_insul_mat'        : self.interior_insul_mat,
                'int_ins_thickness'         : self.int_ins_thickness,
                'ewall_framing'             : self.ewall_framing,
                'int_finish'                : self.int_finish,
                'glazing_system'            : self.glazing_system,
                'building_type'             : self.building_type,
                'num_floors_above'          : self.num_floors_above,
                'ceiling_condition'         : self.ceiling_condition,
                'floor_condition'           : self.floor_condition,
                'context'                   : self.context,
                'win_geometry'              : self.win_geometry,
                'total_shade_len'           : self.total_shade_len,
                'wall_r'                    : self.wall_r,
                'inf_rate'                  : self.inf_rate,
                }


        for key in self.orient_dict:
            data['orient_dict'][repr(key)] = self.orient_dict[key]

        for key in self.zones:
            data['zones'][repr(key)] = self.zones[key]

        for key in self.ceiling_surfaces:
            data['ceiling_surfaces'][repr(key)] = self.ceiling_surfaces[key]

        for key in self.floor_areas:
            data['floor_areas'][repr(key)] = self.floor_areas[key]

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

        for okey in self.shade_depth_h:
            data['shade_depth_h'][repr(okey)] = self.shade_depth_h[okey]

        for okey in self.shade_depth_v1:
            data['shade_depth_v1'][repr(okey)] = self.shade_depth_v1[okey]

        for okey in self.shade_depth_v2:
            data['shade_depth_v2'][repr(okey)] = self.shade_depth_v2[okey]

        for zkey in self.eui_kwh:
            data['eui_kwh'][repr(zkey)] = self.eui_kwh[zkey]
        
        for zkey in self.eui_kwh_hourly:
            data['eui_kwh_hourly'][repr(zkey)] = self.eui_kwh_hourly[zkey]
        
        for zkey in self.eui_kbtu:
            data['eui_kbtu'][repr(zkey)] = self.eui_kbtu[zkey]
        
        for zkey in self.eui_kbtu_ft:
            data['eui_kbtu_ft'][repr(zkey)] = self.eui_kbtu_ft[zkey]

        for zkey in self.eui_kgco2e:
            data['eui_kgco2e'][repr(zkey)] = self.eui_kgco2e[zkey]

        for zkey in self.max_cooling:
            data['max_cooling'][repr(zkey)] = {}
            for vk in self.max_cooling[zkey]:
                data['max_cooling'][repr(zkey)][repr(vk)] = self.max_cooling[zkey][vk]

        for zkey in self.max_heating:
            data['max_heating'][repr(zkey)] = {}
            for vk in self.max_heating[zkey]:
                data['max_heating'][repr(zkey)][repr(vk)] = self.max_heating[zkey][vk]

        for zkey in self.max_lighting:
            data['max_lighting'][repr(zkey)] = {}
            for vk in self.max_lighting[zkey]:
                data['max_lighting'][repr(zkey)][repr(vk)] = self.max_lighting[zkey][vk]

        for zkey in self.max_equipment:
            data['max_equipment'][repr(zkey)] = {}
            for vk in self.max_equipment[zkey]:
                data['max_equipment'][repr(zkey)][repr(vk)] = self.max_equipment[zkey][vk]

        for zkey in self.max_hot_water:
            data['max_hot_water'][repr(zkey)] = {}
            for vk in self.max_hot_water[zkey]:
                data['max_hot_water'][repr(zkey)][repr(vk)] = self.max_hot_water[zkey][vk]

        for zkey in self.max_solar:
            data['max_solar'][repr(zkey)] = {}
            for vk in self.max_solar[zkey]:
                data['max_solar'][repr(zkey)][repr(vk)] = self.max_solar[zkey][vk]

        for zkey in self.monthly_euis:
            data['monthly_euis'][repr(zkey)] = {}
            for vk in self.monthly_euis[zkey]:
                data['monthly_euis'][repr(zkey)][repr(vk)] = self.monthly_euis[zkey][vk]

        for zkey in self.monthly_solar:
            data['monthly_solar'][repr(zkey)] = {}
            for vk in self.monthly_solar[zkey]:
                data['monthly_solar'][repr(zkey)][repr(vk)] = self.monthly_solar[zkey][vk]

        for okey in self.exterior_walls:
            for zkey in self.exterior_walls[okey]:
                data['exterior_walls'][repr(okey)][repr(zkey)] = self.exterior_walls[okey][zkey]

        

        return data

    @data.setter
    def data(self, data):
        ceiling_surfaces        = data.get('ceiling_surfaces') or {}
        floor_surfaces          = data.get('floor_surfaces') or {}
        adiabatic_walls         = data.get('adiabatic_walls') or {}
        facade_areas            = data.get('facade_areas') or {}
        window_areas            = data.get('window_areas') or {}
        opaque_areas            = data.get('opaque_areas') or {}
        wwr                     = data.get('wwr') or {}
        zones                   = data.get('zones') or {}
        shade_gc                = data.get('shade_gc') or {}
        shade_depth_h           = data.get('shade_depth_h') or {}
        shade_depth_v1          = data.get('shade_depth_v1') or {}
        shade_depth_v2          = data.get('shade_depth_v2') or {}
        exterior_walls          = data.get('exterior_walls') or {}

        eui_kwh                 = data.get('eui_kwh') or {}
        eui_kwh_hourly          = data.get('eui_kwh_hourly') or {}
        eui_kbtu                = data.get('eui_kbtu') or {}
        eui_kbtu_ft             = data.get('eui_kbtu_ft') or {}
        eui_kgco2e              = data.get('eui_kgco2e') or {}

        max_cooling             = data.get('max_cooling') or {}
        max_heating             = data.get('max_heating') or {}
        max_lighting            = data.get('max_lighting') or {}
        max_equipment           = data.get('max_equipment') or {}
        max_hot_water           = data.get('max_hot_water') or {}
        max_solar               = data.get('max_solar') or {}
        monthly_euis            = data.get('monthly_euis') or {}
        monthly_solar            = data.get('monthly_solar') or {}

        for key in max_cooling:
            self.max_cooling[literal_eval(key)] = {}
            for rk in max_cooling[key]: 
                self.max_cooling[literal_eval(key)][literal_eval(rk)] = max_cooling[key][rk]

        for key in max_heating:
            self.max_heating[literal_eval(key)] = {}
            for rk in max_heating[key]: 
                self.max_heating[literal_eval(key)][literal_eval(rk)] = max_heating[key][rk]

        for key in max_lighting:
            self.max_lighting[literal_eval(key)] = {}
            for rk in max_lighting[key]: 
                self.max_lighting[literal_eval(key)][literal_eval(rk)] = max_lighting[key][rk]

        for key in max_equipment:
            self.max_equipment[literal_eval(key)] = {}
            for rk in max_equipment[key]: 
                self.max_equipment[literal_eval(key)][literal_eval(rk)] = max_equipment[key][rk]

        for key in max_hot_water:
            self.max_hot_water[literal_eval(key)] = {}
            for rk in max_hot_water[key]: 
                self.max_hot_water[literal_eval(key)][literal_eval(rk)] = max_hot_water[key][rk]

        for key in max_solar:
            self.max_solar[literal_eval(key)] = {}
            for rk in max_solar[key]: 
                self.max_solar[literal_eval(key)][literal_eval(rk)] = max_solar[key][rk]

        for key in monthly_euis:
            self.monthly_euis[literal_eval(key)] = {}
            for rk in monthly_euis[key]: 
                self.monthly_euis[literal_eval(key)][literal_eval(rk)] = monthly_euis[key][rk]

        for key in monthly_solar:
            self.monthly_solar[literal_eval(key)] = {}
            for rk in monthly_solar[key]: 
                self.monthly_solar[literal_eval(key)][literal_eval(rk)] = monthly_solar[key][rk]


        for key in eui_kwh:
            self.eui_kwh[literal_eval(key)] = eui_kwh[key]

        for key in eui_kwh_hourly:
            self.eui_kwh_hourly[literal_eval(key)] = eui_kwh_hourly[key]

        for key in eui_kbtu:
            self.eui_kbtu[literal_eval(key)] = eui_kbtu[key]

        for key in eui_kbtu_ft:
            self.eui_kbtu_ft[literal_eval(key)] = eui_kbtu_ft[key]

        for key in eui_kgco2e:
            self.eui_kgco2e[literal_eval(key)] = eui_kgco2e[key]

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

        for k in zones:
            self.zones[literal_eval(k)] = zones[k]

        for okey in wwr:
            self.wwr[literal_eval(okey)] = wwr[okey]

        for okey in shade_gc:
            self.shade_gc[literal_eval(okey)] = shade_gc[okey]

        for okey in shade_depth_h:
            self.shade_depth_h[literal_eval(okey)] = shade_depth_h[okey]
        for okey in shade_depth_v1:
            self.shade_depth_v1[literal_eval(okey)] = shade_depth_v1[okey]
        for okey in shade_depth_v1:
            self.shade_depth_v2[literal_eval(okey)] = shade_depth_v2[okey]

        for okey in exterior_walls:
            for zkey in exterior_walls[okey]:
                self.exterior_walls[literal_eval(okey)][literal_eval(zkey)] = exterior_walls[okey][zkey]
                
        self.__name__               = data.get('name') or {}
        self.csv                    = data.get('csv') or {}
        self.city                   = data.get('city') or {}
        self.floor_area             = data.get('floor_area') or {}
        self.facade_cladding        = data.get('facade_cladding') or {}
        self.external_insulation    = data.get('external_insulation') or {}
        self.insulation_thickness   = data.get('insulation_thickness') or {}
        self.interior_insul_mat     = data.get('interior_insul_mat') or {}
        self.int_ins_thickness      = data.get('int_ins_thickness') or {}
        self.ewall_framing          = data.get('ewall_framing') or {}
        self.int_finish             = data.get('int_finish') or {}
        self.glazing_system         = data.get('glazing_system') or {}
        self.zone_program           = data.get('zone_program') or {}
        self.weather_file           = data.get('weather_file') or {}
        self.sql_path               = data.get('sql_path') or {}
        self.simulation_folder      = data.get('simulation_folder') or {}
        self.run_simulation         = data.get('run_simulation') or {}  
        self.simulation_name        = data.get('simulation_name') or {}
        self.context                = data.get('context') or {}
        self.win_geometry           = data.get('win_geometry') or {}
        self.total_shade_len        = data.get('total_shade_len') or {}
        self.wall_r                 = data.get('wall_r') or {}
        self.inf_rate               = data.get('inf_rate') or {}
        structure                   = data.get('structure') or {}
        envelope                    = data.get('envelope') or {}  
        self.structure              = Structure.from_data(structure)
        self.envelope               = Envelope.from_data(envelope)

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
        interior_insul_mat      = data['interior_insul_mat']
        int_ins_thickness       = data['int_ins_thickness']
        ewall_framing           = data['ewall_framing']
        int_finish              = data['int_finish']
        glazing_system          = data['glazing_system']
        simulation_name         = data['simulation_name']
        zone_program            = data['zone_program']
        weather_file            = data['weather_file']
        sql_path                = data['sql_path']
        simulation_folder       = data['simulation_folder']
        run_simulation          = data['run_simulation']
        context                 = data['context']
        win_geometry            = data['win_geometry']
        total_shade_len         = data['total_shade_len']

        b = cls()

        num_zones = znames.BranchCount
        b.zones = {i: znames.Branch(i)[0] for i in range(num_zones)}

        for k in range(exterior_walls_n.BranchCount):
            walls = exterior_walls_n.Branch(k)
            b.exterior_walls['n'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                p = [list(pt) for pt in p]
                b.exterior_walls['n'][b.zones[k]].append(p)

        for k in range(exterior_walls_s.BranchCount):
            walls = exterior_walls_s.Branch(k)
            b.exterior_walls['s'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                p = [list(pt) for pt in p]
                b.exterior_walls['s'][b.zones[k]].append(p)

        for k in range(exterior_walls_e.BranchCount):
            walls = exterior_walls_e.Branch(k)
            b.exterior_walls['e'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                p = [list(pt) for pt in p]
                b.exterior_walls['e'][b.zones[k]].append(p)

        for k in range(exterior_walls_w.BranchCount):
            walls = exterior_walls_w.Branch(k)
            b.exterior_walls['w'][b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                p = [list(pt) for pt in p]
                b.exterior_walls['w'][b.zones[k]].append(p)


        # adiabatic walls - - -
        for k in range(adiabatic_walls.BranchCount):
            walls = adiabatic_walls.Branch(k)
            b.adiabatic_walls[b.zones[k]] = []
            for wall in walls:
                p = rs.PolylineVertices(wall)
                p = [list(pt) for pt in p]
                b.adiabatic_walls[b.zones[k]].append(p)

        # floor surfaces - - -
        for i in range(floor_surfaces.BranchCount):
            srf = floor_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.PolylineVertices(srf[0])
                p = [list(pt) for pt in p]
                b.floor_surfaces[b.zones[i]] = p

        # ceiling surfaces - - -
        for i in range(ceiling_surfaces.BranchCount):
            srf = ceiling_surfaces.Branch(i)
            if len(srf) > 0:
                p = rs.PolylineVertices(srf[0])
                p = [list(pt) for pt in p]
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

        # general stuff - - -

        b.__name__ = simulation_name

        # facade areas - - -
        b.compute_areas()

        # fix normals - - - 
        b.fix_normals()

        # facade data - - -
        b.total_shade_len       = total_shade_len
        b.win_geometry          = win_geometry
        b.facade_cladding       = facade_cladding
        b.external_insulation   = external_insulation
        b.insulation_thickness  = insulation_thickness
        b.interior_insul_mat    = interior_insul_mat
        b.int_ins_thickness     = int_ins_thickness
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
        b.height            = float(data['height'])
        b.ceiling_condition = data['ceiling_condition']
        b.floor_condition   = data['floor_condition']

        # city - - - -
        b.csv               = data['csv']
        b.city              = data['city']
        b.kgCo2e_kwh        = city_EUI(b.city)['kg/kWh']
        b.weather_file      = weather(b.city)
        b.context           = context

        # embodied - - -
        b.add_structure(data)
        b.add_envelope(data)
        b.building_type         = data['building_type']
        b.num_floors_above      = data['num_floors_above']
        b.composite_slab        = data['composite_slab']
        b.inf_rate              = data['inf_rate']
        return b

    def add_structure(self, data):
        self.structure = Structure.from_geometry(data, self)

    def add_envelope(self, data):
        self.envelope = Envelope.from_geometry(self.opaque_areas,
                                               self.window_areas,
                                               self.external_insulation,
                                               self.insulation_thickness,
                                               self.facade_cladding,
                                               self.glazing_system,
                                               self.height,
                                               self.shade_depth_h,
                                               self.shade_depth_v1,
                                               self.shade_depth_v2,
                                               self.wwr,
                                               self.city,
                                               self.int_finish,
                                               self.ewall_framing,
                                               self.interior_insul_mat,
                                               self.int_ins_thickness,
                                               self.total_shade_len)

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
            # print('i', i)
            okey = self.orient_dict[i]
            walls = [[] for _ in range(len(self.exterior_walls[okey]))]
            # print(self.zones)
            for j, zkey in enumerate(self.zones):
                # print('j', j, 'zkey', zkey)
                zkey = self.zones[zkey]
                if zkey in self.exterior_walls[okey]:
                    pls = self.exterior_walls[okey][zkey]
                    walls[j] = []
                    for pl in pls:
                        pl = rs.AddPolyline(pl)
                        walls[j].append(rs.AddPlanarSrf(pl)[0])
                        # print(rs.AddPlanarSrf(pl)[0])
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

        # city stuff - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data['city'] = self.city
        surfaces = []
        for pt in self.context:
            surfaces.append(rs.AddSrfPt(pt))
        data['context'] = surfaces

        # facade data - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data['height']                  = self.height
        data['facade_cladding']         = self.facade_cladding
        data['external_insulation']     = self.external_insulation
        data['insulation_thickness']    = self.insulation_thickness
        data['int_ins_thickness']       = self.int_ins_thickness
        data['ewall_framing']           = self.ewall_framing
        data['int_finish']              = self.int_finish
        data['glazing_system']          = self.glazing_system
        data['simulation_name']         = self.simulation_name
        data['zone_program']            = self.zone_program
        data['weather_file']            = self.weather_file
        data['sql_path']                = self.sql_path
        data['simulation_folder']       = self.simulation_folder
        data['run_simulation']          = self.run_simulation
        data['interior_insul_mat']      = self.interior_insul_mat
        data['inf_rate']                = self.inf_rate

        # if self.ewall_framing == '2x4 Wood Studs':
        #     int_ins_thick = 4. / 12.
        # elif self.ewall_framing == '2x6 Wood Studs':
        #     int_ins_thick = 6. / 12.
        # elif self.ewall_framing == '2x8 Wood Studs':
        #     int_ins_thick = 8. / 12.
        # elif self.ewall_framing == '2x10 Wood Studs':
        #     int_ins_thick = 10. / 12.
        # elif self.ewall_framing == '2x12 Wood Studs':
        #     int_ins_thick = 12. / 12. 
        # else:
        #     int_ins_thick = 0.
        # data['int_ins_thick']    = int_ins_thick

        # floor - ceiling data - - - - - - - - - - - - - - - - - - - - - - - - -

        data['ceiling_condition']       = self.ceiling_condition
        data['floor_condition']         = self.floor_condition
        return data

    def compute_structure_embodied(self):
        self.structure.compute_embodied()

    def compute_envelope_embodied(self):
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
        for sp, ep in self.structure.columns:
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
        cores = []
        for core in self.structure.cores:
            sp = core[0]
            ep = (core[0][0], core[0][1], core[0][2]+ self.height)
            core = rs.ExtrudeCurveStraight(rs.AddPolyline(core), sp, ep)
            cores.append(core)

        return slabs, columns, beams, cores

    def add_eui_results(self, cool, heat, light, eq, hot, solar, wallr, winu,
                        hourly=True, monthly=True):
        
        self.window_u = winu
        self.wall_r = wallr

        if not cool:
            print('there is no cooling for some reason')
            cool = [[0]*8760 for _ in range(len(cool))]
        if not heat:
            print('there is no heating for some reason')
            heat = [[0]*8760 for _ in range(len(cool))]
        if not light:
            print('there is no light for some reason')
            light = [[0]*8760 for _ in range(len(cool))]
        if not eq:
            print('there is no equipment for some reason')
            eq = [[0]*8760 for _ in range(len(cool))]
        if not hot:
            print('there is no hot water for some reason')
            hot = [[0]*8760 for _ in range(len(cool))]

        if not solar:
            print('there is no solar gain for some reason')
            solar = [[0]*8760 for _ in range(len(cool))]
        if len(solar) == 8760:
            solar = [solar]

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
            
            self.max_cooling[self.zones[i]] = {'max': max(cool[i]), 'hour': cool[i].values.index(max(cool[i].values))}
            self.max_heating[self.zones[i]] = {'max': max(heat[i]), 'hour': heat[i].values.index(max(heat[i].values))}
            self.max_lighting[self.zones[i]] = {'max': max(light[i]), 'hour': light[i].values.index(max(light[i].values))}
            self.max_equipment[self.zones[i]] = {'max': max(eq[i]), 'hour': eq[i].values.index(max(eq[i].values))}
            # self.max_hot_water[self.zones[i]] = {'max': max(hot[i]), 'hour': hot[i].values.index(max(hot[i].values))}
            self.max_solar[self.zones[i]] = {'max': solar[i].max, 'hour': solar[i].values.index(solar[i].max)}
            
            if monthly:
                cool_am  = cool[i].average_monthly().values
                heat_am  = heat[i].average_monthly().values
                light_am = light[i].average_monthly().values
                eq_am    = eq[i].average_monthly().values
                # hot_am   = hot[i].average_monthly().values
                solar_am = solar[i].average_monthly().values
                
                cool_tm  = cool[i].total_monthly().values
                heat_tm  = heat[i].total_monthly().values
                light_tm = light[i].total_monthly().values
                eq_tm    = eq[i].total_monthly().values
                # hot_tm   = hot[i].total_monthly().values
                solar_tm = solar[i].total_monthly().values

                self.monthly_euis[self.zones[i]] = {'cooling_avg':cool_am,
                                                    'heating_avg':heat_am,
                                                    'lighting_avg':light_am,
                                                    'equipment_avg': eq_am,
                                                    # 'hot_water_avg': hot_am,
                                                    'cooling_tot':cool_tm,
                                                    'heating_tot':heat_tm,
                                                    'lighting_tot':light_tm,
                                                    'equipment_tot': eq_tm,
                                                    # 'hot_water_tot': hot_tm,
                                                    }

                self.monthly_solar[self.zones[i]] = {'average': solar_am, 'total': solar_tm}


            if hourly:
                self.eui_kwh_hourly[self.zones[i]] = {'cooling':list(cool[i]),
                                                    'heating':list(heat[i]),
                                                    'lighting':list(light[i]),
                                                    'equipment':list(eq[i]),
                                                    'hot_water':list(hot[i])}
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

    def write_results(self, csv=True, json_=True, delete=False):
        if csv:
            self.write_csv_result()
        if json_:
            self.to_json()
        if delete:
            fn = os.path.splitext(self.csv)[0]
            folder = os.path.join(self.simulation_folder, fn)
            shutil.rmtree(folder) 

    def write_csv_result(self):
        # fn = self.csv
        # filepath = os.path.join(self.simulation_folder, fn)
        filepath = self.csv
        fh = open(filepath, 'w')

        fh.write('{}\n'.format(self.simulation_name))
        fh.write('Program,{}\n'.format(self.zone_program))
        fh.write('Location,{}\n'.format(self.city))
        fh.write('\n')

        fh.write('Height (ft),{}\n'.format(self.height))
        fh.write('Wall Assembly R Value,{}\n'.format(self.wall_r))
        fh.write('Window U value,{}\n'.format(self.window_u))
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
        z = [self.zones[k] for k in self.zones]
        zones_str = ',{0},{1},{2},{3},{4},Total\n'.format(z[0], z[1], z[2], z[3], z[4])
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)
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
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)
        
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
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)
        
        s = '{0} EUI (kBtu/sf/year),{1},{2},{3},{4},{5},{6}\n'
        for j, name in enumerate(names):
            dkey = dkeys[j]
            data = []
            tot = 0
            for i in range(5):
                if self.zones[i] in self.eui_kbtu_ft:
                    data.append(self.eui_kbtu_ft[self.zones[i]][dkey])
                    # tot += self.eui_kbtu_ft[self.zones[i]][dkey]
                    tot += self.eui_kbtu[self.zones[i]][dkey]
                else:
                    data.append(0)
            tot /= self.floor_area
            fh.write(s.format(name, data[0], data[1], data[2], data[3], data[4], tot))

        fh.write('\n')
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)

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
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)

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
        # fh.write(',Zone1,Zone2,Zone3,Zone4,Zone5,Total\n')
        fh.write(zones_str)

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
        conn = self.structure.connections_embodied
        core = self.structure.core_embodied
        
        win = self.envelope.window_embodied
        wall = self.envelope.wall_embodied

        emb = sum([slab, beam, col, conn, core, win, wall])
        op = self.eui_kgco2e_total * 30

        fh.write('\n')
        fh.write(',Embodied,Operational,Total\n')
        fh.write('Emissions Total 30 years (kg),{0},{1},{2}\n'.format(emb, op, emb + op))

        fh.close()

if __name__ == '__main__':
    for i in range(50): print('')
    # filepath = os.path.join(studio2021.TEMP, 'Studio2021Building.json')
    # b = Building.from_json(filepath)