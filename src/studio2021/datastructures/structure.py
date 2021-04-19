from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from studio2021.functions import material_reader
try:
    reload(material_reader)
except:
    pass
from studio2021.functions.material_reader import read_materials

from math import sqrt
from studio2021.functions import distance_point_point
from studio2021.functions import geometric_key
from studio2021.functions import midpoint_point_point
from studio2021.functions import area_polygon

TPL = """
################################################################################
Structure datastructure: {}
################################################################################

span:   {}
embodied: {}

"""

# TODO: Add gypsum to beams and columns

class Structure(object):
    def __init__(self):
        self.conc_thick = 2. / 12. # 2 inches in feet
        self.gypsum_thick = (2 * (5. / 8.)) / 12. # based on min 80 minutes fire rating
        self.gl_allowable = 2400 * 144. * .6 # GL24f in psi to psf .6 safety
        self.liveload = 80  # lbs / ft2 
        self.clt_density = 36  # lbs / ft3
        self.concrete_density = 149.8271  # lbs / ft3

        self.clt_kgco2_yd3 = read_materials('CLT')['embodied_carbon']
        self.glulam_kgco2_yd3 = read_materials('Glulam')['embodied_carbon']
        self.conc_kgco2_yd3 = read_materials('Concrete')['embodied_carbon']
        self.gyp_kgco2_yd3 = read_materials('GypsumX')['embodied_carbon']
        self.steel_kgco2_yd3 = read_materials('Steel')['embodied_carbon']
        self.rebar_kgco2_yd3 = read_materials('Rebar')['embodied_carbon']

        self.area               = None
        self.composite          = None
        self.btype              = None
        self.num_floors_above   = None
        self.core               = None
        self.slab_embodied      = None
        self.beam_embodied      = None
        self.column_embodied    = None
        self.timber_thick       = None
        self.span_x             = None
        self.span_y             = None
        self.column_length      = None
        self.height             = None
        self.columns            = None
        self.n_columns          = None
        self.main_beams         = None
        self.second_beams       = None 
        self.main_span          = None
        self.second_span        = None 
        
    def __str__(self):
        return TPL.format(self.name)

    @property
    def data(self):
        data = {
            'area'              : self.area,
            'composite'         : self.composite,
            'btype'             : self.btype,
            'num_floors_above'  : self.num_floors_above,
            'conc_thick'        : self.conc_thick,
            'timber_thick'      : self.timber_thick,
            'gypsum_thick'      : self.gypsum_thick,
            'slab_embodied'     : self.slab_embodied,
            'beam_embodied'     : self.beam_embodied,
            'column_embodied'   : self.column_embodied,
            'gl_allowable'      : self.gl_allowable,
            'liveload'          : self.liveload,
            'clt_density'       : self.clt_density,
            'concrete_density'  : self.concrete_density,
            'clt_kgco2_yd3'     : self.clt_kgco2_yd3,
            'glulam_kgco2_yd3'  : self.glulam_kgco2_yd3,
            'conc_kgco2_yd3'    : self.conc_kgco2_yd3,
            'gyp_kgco2_yd3'     : self.gyp_kgco2_yd3,
            'steel_kgco2_yd3'   : self.steel_kgco2_yd3,
            'rebar_kgco2_yd3'   : self.rebar_kgco2_yd3,
            'span_x'            : self.span_x,
            'span_y'            : self.span_y,
            'column_length'     : self.column_length,
            'height'            : self.height,
            'n_columns'         : self.n_columns,
            'columns'           : self.columns,
            'core'              : self.core,
            'main_beams'        : self.main_beams,
            'second_beams'      : self.second_beams,
            'main_span'         : self.main_span,
            'second_span'       : self.second_span,
        }
        return data

    @data.setter
    def data(self, data):
        self.conc_thick         = data.get('conc_thick') or {}
        self.gypsum_thick       = data.get('gypsum_thick') or {}
        self.gl_allowable       = data.get('gl_allowable') or {}
        self.liveload           = data.get('liveload') or {} 
        self.clt_density        = data.get('clt_density') or {}
        self.concrete_density   = data.get('concrete_density') or {}
        self.clt_kgco2_yd3      = data.get('clt_kgco2_yd3') or {}
        self.glulam_kgco2_yd3   = data.get('glulam_kgco2_yd3') or {}
        self.conc_kgco2_yd3     = data.get('conc_kgco2_yd3') or {}
        self.gyp_kgco2_yd3      = data.get('gyp_kgco2_yd3') or {}
        self.steel_kgco2_yd3    = data.get('steel_kgco2_yd3') or {}
        self.rebar_kgco2_yd3    = data.get('rebar_kgco2_yd3') or {}
        self.area               = data.get('area') or {}
        self.composite          = data.get('composite') or {}
        self.btype              = data.get('btype') or {}
        self.num_floors_above   = data.get('num_floors_above') or {}
        self.core               = data.get('core') or {}
        self.slab_embodied      = data.get('slab_embodied') or {}
        self.beam_embodied      = data.get('beam_embodied') or {}
        self.column_embodied    = data.get('column_embodied') or {}
        self.timber_thick       = data.get('timber_thick') or {}
        self.span_x             = data.get('span_x') or {}
        self.span_y             = data.get('span_y') or {}
        self.column_length      = data.get('column_length') or {}
        self.height             = data.get('height') or {}
        self.columns            = data.get('columns') or {}
        self.n_columns          = data.get('n_columns') or {}
        self.main_beams         = data.get('main_beams') or {}
        self.second_beams       = data.get('second_beams') or {}
        self.main_span          = data.get('main_span') or {}
        self.second_span        = data.get('second_span') or {}

    @classmethod
    def from_data(cls, data):
        structure = cls()
        structure.data = data
        return structure

    @classmethod
    def from_geometry(cls, data, building):
        structure = cls()
        structure.add_columns_beams(data)
        structure.area = building.floor_area

        structure.composite          = data['composite_slab']
        structure.btype              = data['building_type']
        structure.num_floors_above   = data['num_floors_above']

        structure.column_length = 0
        temp = []
        for a, b in structure.columns:
            d = distance_point_point(a, b)
            structure.column_length += d
            temp.append(d)

        structure.height = max(temp)
        structure.n_columns = len(structure.columns)

        if structure.span_x > structure.span_y:
            structure.main_beams = structure.beams_x
            structure.second_beams = structure.beams_y
            structure.main_span = structure.span_x
            structure.second_span = structure.span_y
        else:
            structure.main_beams = structure.beams_y
            structure.second_beams = structure.beams_x
            structure.main_span = structure.span_y
            structure.second_span = structure.span_x
        return structure

    def add_columns_beams(self, data):
        columns = data['columns']
        beams_x = data['beams_x']
        beams_y = data['beams_y']
        cores    = data['cores']

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

        columns = [[list(a), list(b)] for a, b in columns]
        bx = [[list(a), list(b)] for a, b in bx]
        by = [[list(a), list(b)] for a, b in by]

        cores_ = []
        for core in cores:
            cores_.append([list(p) for p in core])

        self.columns = columns
        self.beams_x = bx
        self.beams_y = by
        self.cores = cores_

        self.span_x = 0
        self.span_y = 0
        for a, b in bx:
            d = distance_point_point(a, b)
            if d > self.span_x:
                self.span_x = d

        for a, b in by:
            d = distance_point_point(a, b)
            if d > self.span_y:
                self.span_y = d  

    def compute_embodied(self):
        self.compute_slab_embodied()
        self.compute_column_embodied()
        self.compute_beam_embodied()
        self.compute_core_embodied()
        
    def compute_slab_embodied(self):
        """These values are taken from Strobel (2016), using composite/non composite 
        values. Two inches of concrete are added for acoustics, and two more when 
        composite action is specified. Spans should be in feet, thicknesses in feet. 
        """
        span = self.second_span
        if self.composite:
            self.conc_thick *= 2.
            if span < 20:
                thick = 3.9 / 12.# feet
            elif span < 25:
                thick = 6.7 / 12.# feet
            elif span < 30:
                thick = 9.4 / 12.
            elif span < 35:
                thick = 12.2 / 12.
            else:
                raise(NameError('Span is too large for composite CLT slab'))
        else:
            if span < 20:
                thick = 6.7 / 12.# feet
            elif span < 25:
                thick = 8.6 / 12.# feet
            elif span < 30:
                thick = 10.4 / 12.
            else:
                raise(NameError('Span is too large for composite CLT slab'))
        
        # timber - - -
        self.timber_thick = thick
        timber =  ((self.area  * thick) / 27.) * self.clt_kgco2_yd3

        # conrete - - -
        concrete = ((self.area * self.conc_thick) / 27.) * self.conc_kgco2_yd3

        # gypsum - - - 
        if self.btype in ['Type 3', 'Type 4C', 'Type 5']:
            gypsum = 0
        elif self.btype == 'Type 4B':
            gypsum = ((self.area * .8 * self.gypsum_thick) / 27.) * self.gyp_kgco2_yd3
        elif self.btype == 'Type 4A':
            gypsum = ((self.area * 1. * self.gypsum_thick) / 27.) * self.gyp_kgco2_yd3
        else:
            raise(NameError('Bulinding type is wrong'))
        
        self.slab_embodied = timber + concrete + gypsum
        
    def compute_column_embodied(self):
        
        trib = self.span_x * self.span_y
        concrete_dl = self.conc_thick * trib * self.concrete_density
        timber_dl = self.timber_thick * trib * self.clt_density 
        ll = trib * self.liveload  # live load in lbs / ft3
        load = (concrete_dl + timber_dl + ll) * self.num_floors_above

        self.col_area = load / self.gl_allowable
        self.col_side = sqrt(self.col_area)

        if self.col_side < 1:
            self.col_side = 1.

        if self.btype in ['Type 3', 'Type 5']:
            self.col_side += 1.8 / 12.
        elif self.btype in ['Type 4B', 'Type 4C']:
            self.col_side += 3.6 / 12.
        elif self.btype == 'Type 4A':
            self.col_side += 5.4 / 12.
        else:
            raise(NameError('Bulinding type is wrong'))

        self.col_area = self.col_side**2
        vol = (self.col_area * self.height) / 27.  # vol in cubic yards

        timber = vol * self.glulam_kgco2_yd3 * self.n_columns
        self.column_embodied = timber

        steel_vol = (self.col_side * 4 * (1. / 12.)) / 27. 
        self.connections_embodied = steel_vol * self.steel_kgco2_yd3 * self.n_columns

    def compute_beam_embodied(self):

        concrete_dl = self.conc_thick * self.concrete_density
        timber_dl = self.timber_thick * self.clt_density 
        dl = concrete_dl + timber_dl
        trib_l = self.second_span
        l = self.main_span
        w_load = trib_l * (dl + self.liveload)
        m_max = (w_load * l**2) / 8.
        fb = self.gl_allowable

        self.beam_width = self.col_side * .5
        if self.beam_width < 1:
            self.beam_width = 1.
        self.beam_height = sqrt((6 * m_max) / (fb * self.beam_width))

        tot_len_main = 0
        for a, b in self.main_beams:
            d = distance_point_point(a, b)
            tot_len_main += d

        tot_len_second = 0
        for a, b in self.second_beams:
            d = distance_point_point(a, b)
            tot_len_second += d

        vol = self.beam_width * self.beam_height * tot_len_main
        vol += self.beam_width * (self.beam_height / 2.) * tot_len_second
        vol /= 27.

        timber = vol * self.glulam_kgco2_yd3
        self.beam_embodied = timber

    def compute_core_embodied(self):
        tdist = 0
        for pts in self.cores:
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                tdist += distance_point_point(a, b)
        vol = tdist * self.height * 0.037037
        self.core_embodied = (vol * self.conc_kgco2_yd3) + (vol * .04 * self.rebar_kgco2_yd3)
        

if __name__ == "__main__":
    pass
