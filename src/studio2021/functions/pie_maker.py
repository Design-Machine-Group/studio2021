import os
import studio2021

def make_pies(filename, num_years):
    path = studio2021.TEMP

    filepath = os.path.join(path, filename)
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()

    # embodied - - - -

    labels = lines[29].split(',')


    emb = lines[30].split(',')
    slab, beam, col, win, wall, tot = emb[1:7]

    slab = float(slab)
    beam = float(beam)
    col = float(col)
    win = float(win)
    wall = float(wall)
    tot = float(tot)

    slab = round(100*(slab / tot), 1)
    beam = round(100*(beam / tot), 1)
    col = round(100*(col / tot), 1)
    win = round(100*(win / tot), 1)
    wall = round(100*(wall / tot), 1)

    s = ['{} {}%'.format(labels[1], slab)] * int(slab)
    b = ['{} {}%'.format(labels[2], beam)] * int(beam)
    c = ['{} {}%'.format(labels[3], col)] * int(col)
    wi = ['{} {}%'.format(labels[4], win)] * int(win)
    wa = ['{} {}%'.format(labels[5], wall)] * int(wall)

    embodied = s + b + c + wi + wa

    # operational - - - -

    cool = float(lines[66].split(',')[6])
    heat = float(lines[67].split(',')[6])
    li = float(lines[68].split(',')[6])
    eq = float(lines[69].split(',')[6])
    wat = float(lines[70].split(',')[6])
    tot_ = float(lines[71].split(',')[6])

    cool = round(100*(cool / tot_), 1)
    heat = round(100*(heat / tot_), 1)
    li = round(100*(li / tot_), 1)
    eq = round(100*(eq / tot_), 1)
    wat = round(100*(wat / tot_), 1)

    s = ['cooling {}%'.format(cool)] * int(cool)
    b = ['heating {}%'.format(heat)] * int(heat)
    c = ['lighting {}%'.format(li)] * int(li)
    wi = ['equipment {}%'.format(eq)] * int(eq)
    wa = ['hot water {}%'.format(wat)] * int(wat)

    operational = s + b + c + wi + wa

    # operational vs embodied  - - - 

    tot_ *= num_years

    t = tot + tot_
    e = round(100*(tot / t), 1)
    o = round(100*(tot_ / t), 1)

    e = ['embodied {}%'.format(e)] * int(e)
    o = ['operational {}%'.format(o)] * int(o)

    emb_v_op = e + o

    # per ft^2 - - - - - - - -
    tot_ = float(lines[71].split(',')[6])
    
    ft2 = float(lines[33].split(',')[6])
    embft = tot / ft2
    opft = tot_ / ft2

    return embodied, operational, emb_v_op, embft, opft

def make_emb_pie(building):
    slab = building.structure.slab_embodied
    beam = building.structure.beam_embodied
    col = building.structure.column_embodied
    conn = building.structure.connections_embodied
    core = building.structure.core_embodied
    win = building.envelope.window_embodied
    wall = building.envelope.wall_embodied
    tot = sum([slab, beam, col, core, conn, win, wall])

    slab = round(100*(slab / tot), 1)
    beam_col = round(100*((beam + col + conn) / tot), 1)
    core = round(100*(core / tot), 1)
    win = round(100*(win / tot), 1)
    wall = round(100*(wall / tot), 1)

    s = ['{} {}%'.format('slab', slab)] * int(slab)
    b = ['{} {}%'.format('beams & columns', beam_col)] * int(beam_col)
    c = ['{} {}%'.format('core', core)] * int(core)
    wi = ['{} {}%'.format('windows', win)] * int(win)
    wa = ['{} {}%'.format('walls', wall)] * int(wall)

    tot_ft2 = tot / building.floor_area

    return s + b + c + wi + wa, tot, tot_ft2

