import os
import sys
import math

do_debug = "DEBUG" in os.environ

class PT(object):
  """point"""

  fxp = 1     ### self.fences bit for +X direction
  fyp = 2     ### self.fences bit for +Y direction
  fym = 4     ### self.fences bit for -X direction
  fxm = 8     ### self.fences bit for -Y direction
  fall = fxp|fyp|fym|fxm

  def __init__(self,rawtextline='',xy=None,dxy=None,branch=False):

    
    self.name = rawtextline.strip().replace(' ','').replace('+','')
    self.dxy = dxy
    self.branch = branch

    if xy is None         : xypair = self.name.split(',')
    elif isinstance(xy,PT): xypair = (xy.x, xy.y,)
    else                  : xypair = xy

    self.x,self.y = map(int,xypair)

    self.fences = 0
    self.fencexp = None
    self.fenceyp = None
    self.fencexm = None
    self.fenceym = None

  def spawn(self):

    lt_rtn = list()

    if not (self.dxy is None):

      ### Spawn another one in the same direction with the same branch
      lt_rtn.append(PT(xy=(self.x + self.dxy[0]
                          ,self.y + self.dxy[1]
                          ,)
                      ,dxy=self.dxy
                      ,branch=self.branch
                      )
                   )

      if self.branch:

        ### If self.branch is True, then spawn another one after that at
        ### a direction 90deg CCW from the first one

        lt_rtn.append(PT(xy=(self.x - self.dxy[1]
                            ,self.y + self.dxy[0]
                            ,)
                        ,dxy=(-self.dxy[1],self.dxy[0],)
                        )
                     )

    return lt_rtn


  def calc_area(self,other_pairs):
    if self.fences < PT.fall:
      self.area = 0
      return

    self.area = 1

    for x in range(self.fencexm+1,self.fencexp):
      for y in range(self.fenceym+1,self.fenceyp):
        if x==self.x and y==self.y: continue
        ptest = PT(xy=(x,y,))
        md = self.md(ptest)
        md2 = md << 1
        is_in = True
        for othermd,otherpt in other_pairs:
          if md2 < othermd: continue
          is_in = otherpt.md(ptest) > md
          if not is_in: break
        if is_in: self.area += 1

  def moveup(self,dist=1): self.y += 1
  def moveleft(self,dist=1): self.x -= 1
  def movedown(self,dist=1): self.y -= 1
  def moveright(self,dist=1): self.x += 1

  def __repr__(self):
    if self.name: return 'PT(xy=({0})'.format(self.name)
    return 'PT(xy=({0},{1}))'.format(self.x,self.y)

  def md(self, otherpt):
    return abs(otherpt.x-self.x) + abs(otherpt.y-self.y)

  def set_fences(self, otherpt):

    if otherpt is self: return

    dx,dy = otherpt.x-self.x, otherpt.y-self.y
    adx,ady = abs(dx), abs(dy)
    fencexp,fenceyp,fencexm,fenceym = None,None,None,None

    dfence = (self.md(otherpt)+1) >> 1

    if adx>=ady:
      if dx < 0:
        if 0 == (self.fences & PT.fxm
           ) or (self.x - self.fencexm) > dfence:
          self.fences |= PT.fxm
          self.fencexm = self.x - dfence
      else:
        if 0 == (self.fences & PT.fxp
           ) or (self.fencexp - self.x) > dfence:
          self.fences |= PT.fxp
          self.fencexp = self.x + dfence

    if adx<=ady:
      if dy < 0:
        if 0 == (self.fences & PT.fym
           ) or (self.y - self.fenceym) > dfence:
          self.fences |= PT.fym
          self.fenceym = self.y - dfence
      else:
        if 0 == (self.fences & PT.fyp
           ) or (self.fenceyp - self.y) > dfence:
          self.fences |= PT.fyp
          self.fenceyp = self.y + dfence


if "__main__" == __name__ and sys.argv[1:]:
  with open(sys.argv[1],'r') as fin:
    lt_pts = list(map(PT,fin))

  n_pts = len(lt_pts)
  lt_mds = [(pt,sorted([(pt.set_fences(other),pt.md(other),other,)[-2:] for other in lt_pts])[1:],) for pt in lt_pts]

  st_inf = set([pt.name for pt in lt_pts if pt.fences < PT.fall])

  #print(lt_mds)
  #print(st_inf)

  for pt,ptlt_mds in lt_mds: pt.calc_area(ptlt_mds)
  
  print(dict(partI_area=max([pt.area for pt in lt_pts])))


  if "SKIP_PART_II" in os.environ: sys.exit(0)


  xmean = sum([p.x for p in lt_pts]) / n_pts
  ymean = sum([p.x for p in lt_pts]) / n_pts

  pt0 = PT(xy=(xmean,ymean))

  
  sumall = lambda pt:sum(map(pt.md,lt_pts))
  
  sumall0 = sumall(pt0)

  print(dict(pt0=pt0,sumall0=sumall0))

  upper_limit = int(os.environ.get("UPPER_LIMIT",10000))

  assert sumall0 < upper_limit

  partII_size = 1
  lt_pt2s = list()
  lt_pt2s.append(PT(xy=(pt0.x+1,pt0.y,),dxy=(1,0,),branch=True))
  lt_pt2s.append(PT(xy=(pt0.x,pt0.y+1,),dxy=(0,1,),branch=True))
  lt_pt2s.append(PT(xy=(pt0.x-1,pt0.y,),dxy=(-1,0,),branch=True))
  lt_pt2s.append(PT(xy=(pt0.x,pt0.y-1,),dxy=(0,-1,),branch=True))

  extras = 10000

  while lt_pt2s:

    ptnext = lt_pt2s.pop(0)

    if sumall(ptnext) < upper_limit:
      partII_size += 1
      lt_pt2s.extend(ptnext.spawn())

    elif extras > 0:
      extras -= 1
      lt_pt2s.extend(ptnext.spawn())
    
  print(dict(partII_size=partII_size,extras=extras))
