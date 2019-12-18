import os
import sys
import math

do_debug = 'DEBUG' in os.environ

class XY(object):
  def __init__(self,col,row): self.x,self.y,self.rsq = col,row,(col*col)+(row*row)
  def __eq__(self,other): return self.x==other.x and self.y==other.y
  def __hash__(self): return (self.x,self.y,).__hash__()
  def __repr__(self): return 'XY({0},{1})'.format(self.x,self.y)

  def subtract(self,subtrahend):
    return XY(self.x-subtrahend.x,self.y-subtrahend.y)

  def scale(self,factor):
    return XY(self.x*factor,self.y*factor)

  def add(self,addend):
    return XY(self.x+addend.x
             ,self.y+addend.y
             )

  def divide(self,divisor):
    assert not (abs(self.x) % divisor)
    assert not (abs(self.y) % divisor)
    return XY(self.x/divisor,self.y/divisor)

  def reduce(self):
    ahi,alo = abs(self.x),abs(self.y)
    if ahi<alo: alo,ahi = ahi,alo
    while alo > 0:
      oldalo = alo
      alo = ahi % alo
      ahi = oldalo
    if ahi: return self.divide(ahi)
    return XY(self.x,self.y)

  def arctan(self): return math.atan2(self.x,self.y)
    

class ASTEROIDMAP(object):

  def __init__(self,fn):
    self.width = None
    self.xys = set()
    with open(fn,'r') as fin:
      row = 0
      for rawline in fin:
        line = rawline.rstrip()
        width = len(line)
        if self.width is None: self.width = width
        assert self.width==width
        assert not line.replace('.','').replace('#','')
        self.xys.update([XY(col,row)
                         for col in range(width)
                         if '#'==line[col]
                        ]
                       )
        row += 1
      self.height = row
    self.count = len(self.xys)

  def invisibles(self,xybase,full_set=None):
    if do_debug: print(dict(xybase=xybase))
    if isinstance(full_set,set): xys = full_set
    else                       : xys = self.xys
    assert xybase in xys
    invisibles = set([xybase])
    for xy in xys:
      dxy = xy.subtract(xybase)
      if dxy.rsq < 1:
        if do_debug: print(dict(xybase=xybase,xy=xy,continuing=dxy))
        continue
      gcdxy = dxy.reduce()
      if do_debug: print(dict(xybase=xybase,xy=xy,dxy=dxy,gcdxy=gcdxy))
      factor = 1
      while True:
        fdxy = gcdxy.scale(factor)
        if do_debug: print(dict(factor=factor,fdxy=fdxy,fdrsq=fdxy.rsq,drsq=dxy.rsq,))
        if fdxy.rsq > dxy.rsq:
          checkxy = xybase.add(fdxy)
          if do_debug: print(dict(checkxy=checkxy,inxys=checkxy in xys))
          if checkxy.x > -1 and checkxy.y > -1 and checkxy.x < self.width and checkxy.y < self.height:
            if checkxy in xys:
              invisibles.add(checkxy)
              if do_debug: print(dict(invisibles=invisibles))
          else:
            if do_debug: print(dict(breaking=checkxy))
            break
        factor += 1

    return invisibles

  def visible_from(self,xybase):
    return self.count - len(self.invisibles(xybase)),xybase

  def optimal_removals(self):
    first_count,xybase = max(map(self.visible_from,am.xys))
    lt_ordered_removals = list()
    current_set = self.xys
    while len(current_set) > 1:
      invisibles = self.invisibles(xybase,full_set=current_set)
      vaporized = list(current_set - invisibles)
      vaporized.sort(key=lambda xy:xy.subtract(xybase).arctan(),reverse=True)
      lt_ordered_removals.extend(vaporized)
      current_set = invisibles
    return first_count,xybase,current_set,lt_ordered_removals

  def __repr__(self):
    return '{0}...;len={1};{2}x{3}'.format(list(self.xys)[:10],len(self.xys),self.width,self.height)

########################################################################
if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)
  am = ASTEROIDMAP(fn)

  if not bn.startswith('sample_input_part2_'):
    print(dict(part1=max(map(am.visible_from,am.xys))))

  if not bn.startswith('sample_input_part1_'):
    optimal_removals = am.optimal_removals()
    N = min([200,len(optimal_removals[-1])])-1
    try:
      Nth_removed = optimal_removals[-1][N]
      part2 = (Nth_removed.x*100) + Nth_removed.y
    except:
      Nth_removed = 'Failed'
      part2 = 'Failed'
    print(dict(part2=part2
              ,N=N
              ,Nth_removed=Nth_removed
              ,extra=optimal_removals[:-1]
              )
         )
