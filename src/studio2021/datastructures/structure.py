from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from studio2021.functions import material_reader
reload(material_reader)
from studio2021.functions.material_reader import read_materials

from math import sqrt
from studio2021.functions import distance_point_point

TPL = """
################################################################################
Structure datastructure: {}
################################################################################

span:   {}
embodied: {}

"""

# TODO: Add gypsum to beams and columns

class Structure(object):

    def __init__(self, area, columns, bx, by, composite, btype, numf):
        self.name = 'Structure'
        self.area = area
        self.composite = composite
        self.btype = btype
        self.num_floors_above = numf

        self.conc_thick = 2. / 12. # 2 inches in feet
        self.timber_thick = None
        self.gypsum_thick = (2 * (5. / 8.)) / 12. # based on min 80 minutes fire rating

        self.slab_embodied = None
        self.beam_embodied = None
        self.column_embodied = None

        self.gl_allowable = 2400 * 144. * .6 # GL24f in psi to psf .6 safety
        self.liveload = 80  # lbs / ft2 
        self.clt_density = 36  # lbs / ft3
        self.concrete_density = 149.8271  # lbs / ft3

        self.clt_kgco2_yd3 = read_materials('CLT')['embodied_carbon']
        self.glulam_kgco2_yd3 = read_materials('Glulam')['embodied_carbon']
        self.conc_kgco2_yd3 = read_materials('Concrete')['embodied_carbon']
        self.gyp_kgco2_yd3 = read_materials('GypsumX')['embodied_carbon']

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

        self.column_length = 0
        temp = []
        for a, b in columns:
            d = distance_point_point(a, b)
            self.column_length += d
            temp.append(d)

        self.height = max(temp)
        self.columns = columns
        self.n_columns = len(columns)

        if self.span_x > self.span_y:
            self.main_beams = bx
            self.second_beams = by
            self.main_span = self.span_x
            self.second_span = self.span_y
        else:
            self.main_beams = by
            self.second_beams = bx
            self.main_span = self.span_y
            self.second_span = self.span_x
        

    def __str__(self):
        return TPL.format(self.name)

    @property
    def data(self):
        return {}

    def compute_embodied(self):
        self.compute_slab_embodied()
        self.compute_column_embodied()
        self.compute_beam_embodied()
        
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

if __name__ == "__main__":
    pass
