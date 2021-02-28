from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from studio2021.functions import material_reader
reload(material_reader)
from studio2021.functions.material_reader import read_materials

TPL = """
################################################################################
Structure datastructure: {}
################################################################################

span:   {}
embodied: {}

"""

#TODO: Check all nbumbers, sizing, just made these up for now. 

class Structure(object):

    def __init__(self, area, span, col_length, beam_length, composite, btype):
        self.name = 'Structure'
        self.area = area
        self.span = span
        self.col_length = col_length
        self.beam_length = beam_length
        self.composite = composite
        self.btype = btype

        self.conc_thick = 2. / 12. # 2 inches in feet
        self.timber_thick = None
        self.gypsum_thick = (2 * (5. / 8.)) / 12. # based on min 80 minutes fire rating

        self.slab_embodied = None
        self.beam_embodied = None
        self.column_embodied = None

        self.clt_kgco2_yd3 = read_materials('CLT')['embodied_carbon']
        self.glulam_kgco2_yd3 = read_materials('Glulam')['embodied_carbon']
        self.conc_kgco2_yd3 = read_materials('Concrete')['embodied_carbon']
        self.gyp_kgco2_yd3 = read_materials('GypsumX')['embodied_carbon']
    
    def __str__(self):
        return TPL.format(self.name, self.span)

    @property
    def data(self):
        return {}

    def compute_embodied(self):
        self.compute_slab_embodied
        self.compute_column_embodied
        self.compute_beam_embodied
        
    @property
    def compute_slab_embodied(self):
        """These values are taken from Strobel (2016), using composite/non composite 
        values. Two inches of concrete are added for acoustics, and two more when 
        composite action is specified. Spans should be in feet, thicknesses in feet. 
        """
        if self.composite:
            self.conc_thick *= 2.
            if self.span < 20:
                thick = 3.9 / 12.# feet
            elif self.span < 25:
                thick = 6.7 / 12.# feet
            elif self.span < 30:
                thick = 9.4 / 12.
            elif self.span < 35:
                thick = 12.2 / 12.
            else:
                raise(NameError('Span is too large for composite CLT slab'))
        else:
            if self.span < 20:
                thick = 6.7 / 12.# feet
            elif self.span < 25:
                thick = 8.6 / 12.# feet
            elif self.span < 30:
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
            gypsum = (self.area * .8 * self.gypsum_thick) / 27.
        elif self.btype == 'Type 4A':
            gypsum = (self.area * 1. * self.gypsum_thick) / 27.
        else:
            raise(NameError('Bulinding type is wrong'))
        
        self.slab_embodied = timber + concrete + gypsum
        
    @property
    def compute_beam_embodied(self):
        # these numbers are all incorrect, just temp
        if self.span < 20:
            sec = 5.9 
        elif self.span < 25:
            sec = 8.7 
        elif self.span < 30:
            sec = 11.4
        elif self.span < 32:
            sec = 14.2
        else:
            raise(NameError('Span is too large for Glulam beams'))
        self.beam_embodied = sec * self.beam_length * self.glulam_kgco2_yd3
    
    @property
    def compute_column_embodied(self):
        # these numbers are all incorrect, just temp
        if self.span < 20:
            sec = 5.9 
        elif self.span < 25:
            sec = 8.7 
        elif self.span < 30:
            sec = 11.4
        elif self.span < 32:
            sec = 14.2
        else:
            raise(NameError('Span is too large for Glulam columns'))
        self.column_embodied = sec * self.col_length * self.glulam_kgco2_yd3



if __name__ == "__main__":
    span = 30
    area = 20000
    num_col = 20
    num_beam = 16 + 15
    col_length = 9 * num_col
    beam_length = span * num_beam
    composite = True
    s = Structure(area, span, col_length, beam_length, composite)
