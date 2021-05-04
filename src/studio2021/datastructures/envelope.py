from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from ast import literal_eval

from studio2021.functions import read_materials
from studio2021.functions import read_materials_city
from studio2021.functions import read_glazing


TPL = """
################################################################################
Envelope datastructure: {}
################################################################################

window-to-wall ratio:   {}
window: {}
wall: {}
embodied: {}

"""



class Envelope(object):
    
    def __init__(self):
        self.opaque_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.window_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.city                   = None
        self.external_insulation    = None
        self.insulation_thickness   = None
        self.facade_cladding        = None
        self.glazing_system         = None
        self.height                 = None
        self.shade_depth_h          = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.shade_depth_v1         = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.shade_depth_v2         = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.wwr                    = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.wall_embodied          = None
        self.window_embodied        = None
        self.shading_embodied       = None
        self.int_finish             = None
        self.ewall_framing          = None
        self.interior_insul_mat     = None

    @classmethod
    def from_data(cls, data):
        env = cls()
        env.data = data
        return env

    @classmethod
    def from_geometry(cls,
                      opaque_areas,
                      window_areas,
                      external_insulation,
                      insulation_thickness,
                      facade_cladding,
                      glazing_system,
                      height,
                      shade_depth_h,
                      shade_depth_v1,
                      shade_depth_v2,
                      wwr,
                      city,
                      int_finish,
                      ewall_framing,
                      interior_insul_mat):

        env = cls()
        env.opaque_areas            = opaque_areas
        env.window_areas            = window_areas
        env.external_insulation     = external_insulation
        env.insulation_thickness    = insulation_thickness
        env.facade_cladding         = facade_cladding
        env.glazing_system          = glazing_system
        env.height                  = height
        env.shade_depth_h           = shade_depth_h
        env.shade_depth_v1          = shade_depth_v1
        env.shade_depth_v2          = shade_depth_v2
        env.wwr                     = wwr
        env.city                    = city 
        env.int_finish              = int_finish
        env.ewall_framing           = ewall_framing
        env.interior_insul_mat      = interior_insul_mat
        return env

    @property
    def data(self):
        data = {
            'opaque_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'window_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'external_insulation'       : self.external_insulation,
            'insulation_thickness'      : self.insulation_thickness,
            'facade_cladding'           : self.facade_cladding,
            'glazing_system'            : self.glazing_system,
            'height'                    : self.height,
            'shade_depth_h'             : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'shade_depth_v1'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'shade_depth_v2'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'wwr'                       : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'wall_embodied'             : self.wall_embodied,
            'window_embodied'           : self.window_embodied,
            'shading_embodied'          : self.shading_embodied,
            'int_finish'                : self.int_finish,
            'ewall_framing'             : self.ewall_framing,
            'interior_insul_mat'        : self.interior_insul_mat,
        }

        for okey in self.shade_depth_h:
            data['shade_depth_h'][repr(okey)] = self.shade_depth_h[okey]

        for okey in self.shade_depth_v1:
            data['shade_depth_v1'][repr(okey)] = self.shade_depth_v1[okey]
        
        for okey in self.shade_depth_v2:
            data['shade_depth_v2'][repr(okey)] = self.shade_depth_v2[okey]

        for okey in self.wwr:
            data['wwr'][repr(okey)] = self.wwr[okey]

        for okey in self.opaque_areas:
            for zkey in self.opaque_areas[okey]:
                data['opaque_areas'][repr(okey)][repr(zkey)] = self.opaque_areas[okey][zkey]

        for okey in self.window_areas:
            for zkey in self.window_areas[okey]:
                data['window_areas'][repr(okey)][repr(zkey)] = self.window_areas[okey][zkey]

        return data

    @data.setter
    def data(self, data):
        opaque_areas                = data.get('opaque_areas') or {}
        window_areas                = data.get('window_areas') or {}
        self.external_insulation    = data.get('external_insulation') or {}
        self.insulation_thickness   = data.get('insulation_thickness') or {}
        self.facade_cladding        = data.get('facade_cladding') or {}
        self.glazing_system         = data.get('glazing_system') or {}
        self.height                 = data.get('height') or {}
        shade_depth_h               = data.get('shade_depth_h') or {}
        shade_depth_v1              = data.get('shade_depth_v1') or {}
        shade_depth_v2              = data.get('shade_depth_v2') or {}
        wwr                         = data.get('wwr') or {} 
        self.wall_embodied          = data.get('wall_embodied') or {}
        self.window_embodied        = data.get('window_embodied') or {}
        self.shading_embodied       = data.get('shading_embodied') or {}
        self.int_finish             = data.get('int_finish') or {}
        self.ewall_framing          = data.get('ewall_framing') or {}
        self.interior_insul_mat     = data.get('interior_insul_mat') or {}

        for okey in opaque_areas:
            for zkey in opaque_areas[okey]:
                self.opaque_areas[literal_eval(okey)][literal_eval(zkey)] = opaque_areas[okey][zkey]

        for okey in window_areas:
            for zkey in window_areas[okey]:
                self.window_areas[literal_eval(okey)][literal_eval(zkey)] = window_areas[okey][zkey]

        for okey in wwr:
            self.wwr[literal_eval(okey)] = wwr[okey]

        for okey in shade_depth_h:
            self.shade_depth_h[literal_eval(okey)] = shade_depth_h[okey]

        for okey in shade_depth_v1:
            self.shade_depth_v1[literal_eval(okey)] = shade_depth_v1[okey]

        for okey in shade_depth_v2:
            self.shade_depth_v2[literal_eval(okey)] = shade_depth_v2[okey]

    def compute_embodied(self):
        tot_opaque = 0.  # this should be in feet?
        tot_win = 0.     # this should be in feet?
        sides = {}
        for okey in self.opaque_areas:
            opaque_orient = 0
            win_orient = 0
            for zkey in self.opaque_areas[okey]:
                opaque_orient += self.opaque_areas[okey][zkey]
                win_orient += self.window_areas[okey][zkey]
            sides[okey] = (opaque_orient + win_orient) / self.height
            tot_opaque += opaque_orient
            tot_win += win_orient

        # external insulation - - -
        ins_mat = self.external_insulation
        if ins_mat == 'None':
            ins_thick = 0.
            ins_emb_ = 0
        else:
            ins_thick = float(self.insulation_thickness) / 12. # currently in inches
            ins_emb_ = float(read_materials_city(ins_mat, self.city)) / 27.  # currently (kgCO2/yd3)
        ins_emb = tot_opaque * ins_thick * ins_emb_ 

        # facade cladding - - -
        fac_mat = self.facade_cladding
        fac_thick = float(read_materials(fac_mat)['thickness_in']) / 12. # currently (kgCO2/yd3)
        fac_emb_ = float(read_materials_city(fac_mat, self.city)) / 27. # currently (kgCO2/yd3)
        fac_emb = tot_opaque * fac_thick * fac_emb_ 

        # interior framing - - -
        fram_mat = self.ewall_framing
        fram_thick = float(read_materials(fram_mat)['thickness_in']) / 12. # currently (kgCO2/yd3)
        fram_emb_ = float(read_materials_city(fram_mat, self.city)) / 27. # currently (kgCO2/yd3)
        fram_emb = tot_opaque * fram_thick * fram_emb_ 

        # interior insulation - - -
        int_ins_mat = self.interior_insul_mat
        if fram_mat == '2x4 Wood Studs':
            int_ins_thick = 4. / 12.
            int_ins_emb_ = float(read_materials_city(int_ins_mat, self.city)) / 27. # currently (kgCO2/yd3)
            self.int_finish = 'Gyp'
        elif fram_mat == '2x6 Wood Studs':
            int_ins_thick = 6. / 12.
            int_ins_emb_ = float(read_materials_city(int_ins_mat, self.city)) / 27. # currently (kgCO2/yd3)
            self.int_finish = 'Gyp'
        elif fram_mat == '2x8 Wood Studs':
            int_ins_thick = 8. / 12.
            int_ins_emb_ = float(read_materials_city(int_ins_mat, self.city)) / 27. # currently (kgCO2/yd3)
            self.int_finish = 'Gyp'
        elif fram_mat == '2x10 Wood Studs':
            int_ins_thick = 10. / 12.
            int_ins_emb_ = float(read_materials_city(int_ins_mat, self.city)) / 27. # currently (kgCO2/yd3)
            self.int_finish = 'Gyp'
        elif fram_mat == '2x12 Wood Studs':
            int_ins_thick = 12. / 12. 
            int_ins_emb_ = float(read_materials_city(int_ins_mat, self.city)) / 27. # currently (kgCO2/yd3)
            self.int_finish = 'Gyp'
        else:
            int_ins_thick = 0.
            int_ins_emb_ = 0.       
        
        int_ins_emb = tot_opaque * int_ins_thick * int_ins_emb_ 

        # interior finish - - -
        int_mat = self.int_finish
        if int_mat == 'None':
            int_thick = 0.
            int_emb_ = 0
        else:
            int_thick = float(read_materials(int_mat)['thickness_in']) / 12# currently (kgCO2/yd3)
            int_emb_ = float(read_materials_city(int_mat, self.city)) / 27 # currently (kgCO2/yd3)
        int_emb = tot_opaque * int_thick * int_emb_ 

        win_sys = self.glazing_system
        if win_sys == 'Aluminum Double' or win_sys == 'Wood Double':
            glass_mat = 'Glass Double'
        else:
            glass_mat = 'Glass Triple'
        # win_emb_ = float(read_glazing(win_sys)['embodied_carbon_imperial']) # currently (KgCO2/ft2)
        glass_thick = float(read_materials(glass_mat)['thickness_in']) / 12# currently (kgCO2/yd3)
        win_emb_ = float(read_materials_city(glass_mat, self.city)) / 27. # currently (kgCO2/yd3)
        win_emb = tot_win * win_emb_ * glass_thick

        self.wall_embodied =  ins_emb + fac_emb + int_emb + fram_emb + int_ins_emb
        self.window_embodied = win_emb

        alum_emb = float(read_materials_city('Aluminum', self.city)) / 27. # currently (kgCO2/yd3)
        shd_area = 0
        for okey in sides:
            side = sides[okey]
            numsec = round(side / 10., 0)
            # print(side, numsec)
            secside = side / float(numsec)
            secarea = secside * self.height
            wwr = self.wwr[okey]
            vertical = self.height - 2
            horizontal = (secarea * wwr) / vertical
            shd_area += horizontal * self.shade_depth_h[okey] * numsec
            shd_area += vertical * self.shade_depth_v1[okey] * numsec
            shd_area += vertical * self.shade_depth_v2[okey] * numsec

        self.shading_embodied = shd_area * 0.0164042 * alum_emb # 5 mm aluminimum
        self.window_embodied += self.shading_embodied
        self.env_strings = []
        s = '{0:20}{1:32}{2:22}{3:20}{4:20}'.format('Type', 'Material', 'Thickness (ft)', 'GWP/ft3', 'GWP/ft2')
        self.env_strings.append(s)
        
        names = ['cladding', 'ext.insulation', 'framing', 'int.insulation', 'interior', 'window']
        mat = [fac_mat, ins_mat, fram_mat, int_ins_mat, int_mat, glass_mat]
        thick = [fac_thick, ins_thick, fram_thick, int_ins_thick, int_thick, glass_thick]
        emb = [fac_emb_, ins_emb_, fram_emb_, int_ins_emb_, int_emb_, win_emb_]

        for i in range(6):
            string = '{0:20}{1:20}{2:20}{3:20}{4:20}'.format(names[i],
                                                             mat[i],
                                                             thick[i],
                                                             emb[i],
                                                             thick[i] * emb[i])
            self.env_strings.append(string)


if __name__ == "__main__":
    pass