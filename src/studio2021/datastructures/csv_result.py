

class CSV_Result(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.read_csv()

    def read_csv(self):
        fh = open(self.filepath, 'r')
        lines = fh.readlines()
        fh.close()

        # data - - - 
        self.name = lines[0].split(',')[0].rstrip('\n')
        self.city = lines[2].split(',')[1].rstrip('\n')
        self.program = lines[1].split(',')[1].rstrip('\n')
        self.height = float(lines[4].split(',')[1])
        self.floor_area = float(lines[33].split(',')[6])
        try:
            self.wall_r = float(lines[5].split(',')[1])
            self.win_u = float(lines[6].split(',')[1])
        except:
            self.wall_r = None
            self.win_u = None
        self.wwr_n = float(lines[8].split(',')[1])
        self.wwr_s = float(lines[13].split(',')[1])
        self.wwr_e = float(lines[18].split(',')[1])
        self.wwr_w = float(lines[23].split(',')[1])

        # embodied - - - -

        emb = lines[30].split(',')
        slab, beam, col, win, wall, tot = emb[1:7]
        self.slab = float(slab)
        self.beam = float(beam)
        self.col = float(col)
        self.win = float(win)
        self.wall = float(wall)
        self.emb_tot = float(tot)

        # operational - - - -

        self.cool = float(lines[66].split(',')[6])
        self.heat = float(lines[67].split(',')[6])
        self.li = float(lines[68].split(',')[6])
        self.eq = float(lines[69].split(',')[6])
        self.wat = float(lines[70].split(',')[6])
        self.op_tot = float(lines[71].split(',')[6])

    
if __name__ == '__main__':
    import os
    import studio2021
    for i in range(50): print('')

    filepath = os.path.join(studio2021.TEMP, 'Milwaukee_example_202105081627.csv')
    csv = CSV_Result(filepath)