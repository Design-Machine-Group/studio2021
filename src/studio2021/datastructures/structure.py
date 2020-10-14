from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"


TPL = """
################################################################################
Structure datastructure: {}
################################################################################

span:   {}
embodied: {}

"""

class Structure(object):
    def __init__(self, area, span, col_length, beam_length):
        self.name = 'Structure testing'
        self.area = area
        self.span = span
        self.col_length = col_length
        self.beam_length = beam_length

        self.glulam_kgco2_ft3 = 1.1 # temporary numbers
        self.clt_kgco2_f3 = 1. # temporary numbers
        self.conc_kgco2_ft3 = 2. # temporary numbers
        self.conc_thick = .166667 # 2 inches in feet
    
    def __str__(self):
        return TPL.format(self.name, self.span, self.embodied)

    @property
    def embodied(self):
        slab = self.slab_embodied
        col = self.column_embodied
        beam = self.beam_embodied
        return slab + col + beam

    @property
    def slab_embodied(self):
        """These values are taken from Strobel (2016), using composte values
        and 2.0" concrete section. Spans should be in feet, thicknesses in inches. 
        """
        if self.span < 20:
            thick = 5.9 # inches
        elif self.span < 25:
            thick = 8.7 # inches
        elif self.span < 30:
            thick = 11.4
        elif self.span < 32:
            thick = 14.2
        else:
            raise(NameError('Span is too large for CLT slab'))
        
        timber =  self.area * self.clt_kgco2_f3 * thick
        concrete = self.area * self.conc_kgco2_ft3 * self.conc_thick
        return timber + concrete

    @property
    def beam_embodied(self):
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
        return sec * self.beam_length * self.glulam_kgco2_ft3
    
    @property
    def column_embodied(self):
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
        return sec * self.col_length * self.glulam_kgco2_ft3

if __name__ == "__main__":
    span = 30
    area = 20000
    num_col = 20
    num_beam = 16 + 15
    col_length = 9 * num_col
    beam_length = span * num_beam
    s = Structure(area, span, col_length, beam_length)
    print(s)