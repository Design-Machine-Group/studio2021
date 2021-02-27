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

#TODO: Check all nbumbers, sizing, just made these up for now. 

class Structure(object):

    def __init__(self, area, span, col_length, beam_length):
        self.name = 'Structure'
        self.area = area
        self.span = span
        self.col_length = col_length
        self.beam_length = beam_length

        self.glulam_kgco2_ft3 = 10.1 # temporary numbers
        self.clt_kgco2_f3 = 10. # temporary numbers
        self.conc_kgco2_ft3 = 20. # temporary numbers
        self.conc_thick = .166667 # 2 inches in feet

        self.slab_embodied = None
        self.beam_embodied = None
        self.column_embodied = None

    
    def __str__(self):
        return TPL.format(self.name, self.span, self.embodied)

    @property
    def data(self):
        return {}

    def compute_embodied(self):
        self.compute_slab_embodied
        self.compute_column_embodied
        self.compute_beam_embodied
        

    @property
    def compute_slab_embodied(self):
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
        self.slab_embodied = timber + concrete

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
        self.beam_embodied = sec * self.beam_length * self.glulam_kgco2_ft3
    
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
        self.column_embodied = sec * self.col_length * self.glulam_kgco2_ft3

if __name__ == "__main__":
    span = 30
    area = 20000
    num_col = 20
    num_beam = 16 + 15
    col_length = 9 * num_col
    beam_length = span * num_beam
    s = Structure(area, span, col_length, beam_length)
