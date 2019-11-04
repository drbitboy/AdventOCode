import os
import sys
import math

do_debug = "DEBUG" in os.environ

V = type(None)

class PT(object):
  """point"""
  def __init__(self,rawtextline='',xy=None):

    self.name = rawtextline.strip().replace(' ','').replace('+','')

    if xy is None        : xypair = self.name.split(',')
    elif isinstance(xy,V): xypair = (xy.vec.x, xy.vec.y,)
    else                 : xypair = xy

    self.x,self.y = map(int,xypair)

  def moveup(self,dist=1): self.y += 1
  def moveleft(self,dist=1): self.x -= 1
  def movedown(self,dist=1): self.y -= 1
  def moveright(self,dist=1): self.x += 1


gbl_vzero = PT(xy=(0,0))

class V(object):
  """vector between two points"""


  def __init__(self,tip,root=gbl_vzero):
    self.rootpt = root
    self.tippt = tip
    self.vec = PT(xy=(tip.x - root.x, tip.y - root.y,))
    self.magsq = self.vdot(self)

  def vscale(self,scale_factor):
    return V(PT(xy=(self.vec.x*scale_factor,self.vec.y*scale_factor,)))

  def vminus(self): return self.vscale(-1.0)

  def vadd(self,other):
    return V(PT(xy=(self.vec.x+other.vec.x, self.vec.y+other.vec.y,)))

  def vsub(self): return self.vadd(other.vminus())

  def vdot(self,other):
    return (self.vec.x*other.vec.x) + (self.vec.y*other.vec.y)

  def uvdot(self,other):
    return self.vdot(other) / math.sqrt(self.magsq * other.magsq)


class BOUNDARY(object):

  """Model boundary line halfway from point pin to pout"""

  def __init__(self,pin,pout):
    """pin is on "in" side, pout is on "out" side, of boundary line"""
    self.pout_name = pout.name
    self.pin = pin
    self.pintopout = V(pout,pin)
    self.magsqdiv2 = (self.pintopout.magsq / 2.0) - (0./1024.)

  def closer_to_pin(self,pt):
    """Return True if pt is on pin side of boundary line"""
    if do_debug:
      print('closer_to_pin'
           ,self.pout_name
           ,('[pintopout]',self.pintopout.vec.x,self.pintopout.vec.y,)
           ,('[pt]',pt.x,pt.y,)
           ,('[pin]->[{0}]'.format(pt.name),V(pt,self.pin).vec.x,V(pt,self.pin).vec.y,)
           ,('[pin]',self.pin.x,self.pin.y,)
           ,self.magsqdiv2
           ,self.pintopout.vdot(V(pt,self.pin))
           )
    return self.pintopout.vdot(V(pt,self.pin)) < self.magsqdiv2

  def __cmp__(this,that):
    if this.magsqdiv2 < that.magsqdiv2: return -1
    if this.magsqdiv2 > that.magsqdiv2: return 1
    return 0


if "__main__" == __name__ and sys.argv[1:]:
  with open(sys.argv[1],'r') as fin:
    lt_pts = list(map(PT,fin))

  ### Find lowest-y, lowest-x point

  pnext = lt_pts[0]
  for pother in lt_pts[1:]:
    ### Lowest y
    if pother.y > pnext.y: continue
    ### Equal y, lowest x
    if pother.y == pnext.y and pother.x >= pnext.x: continue
    pnext = pother

  ### Find outermost convex set of points that contains all others

  st_convex_pts = set()
  vnext = V(PT(xy=(0,-1,)))

  while not (pnext.name in st_convex_pts):

    st_convex_pts.add(pnext.name)

    plast = pnext
    vlast = vnext
    uvdotmax = -2.

    for ptest in lt_pts:
      if ptest is plast: continue
      ###if ptest.name in st_convex_pts: continue
      vtest = V(ptest,plast)

      uvdottest = vtest.uvdot(vlast)

      ### Search for greatest uvdot
      if uvdottest < uvdotmax: continue
      if uvdottest == uvdotmax:
        ### If uvdottest is equal, keep closer point
        if vtest.magsq >= vnext.magsq: continue

      pnext,vnext,uvdotmax = ptest,vtest,uvdottest

  max_area = 0;

  ### Calculate area for each point

  for pin in lt_pts:

    ### Skip convex boundary pts

    if pin.name in st_convex_pts: continue

    ### Initialize outer loop parameters
    ### - Create test point ptest, which will move away from pin in a
    ###   spiral pattern
    ### - Initialize area to 1, for the point itself
    ### - Termination criterion [all_out_legs]:  successive passes
    ###   without an increase in area
    ### - Spiral control counter
    ### - Generate boundary lines between pin and all other points

    ptest = PT('test point',xy=(pin.x,pin.y))
    area, all_out_legs, spiral_counter = 1,0,0

    boundaries = [BOUNDARY(pin,pother)
                  for pother in lt_pts
                  if pother.name != pin.name
                 ]
    boundaries.sort()

    if do_debug:
      print([pin.name])
      print([(b.pout_name,b.magsqdiv2,) for b in boundaries])
    
    while all_out_legs < 8:

      ### Terminate loop when eight successive passes through this loop
      ### loop find no points closest to ptest
      ### - Save area at top of loop

      area_at_top_of_loop = area

      ### Increment spiral control spiral_ounter, calculate dependent
      ### spiral parameters

      spiral_counter += 1                ### 1,2,3,4,5,6,7,8,9,...
      steps = (spiral_counter + 1) >> 1  ### 1,1,2,2,3,3,4,4,5,...
      countermod4 = spiral_counter % 4   ### 1,2,3,0,1,2,3,0,1,...

      ### Spiral out in a series of increasing legs from the inital
      ### point ptest as directed by countermod4 and steps
      ###
      ### - spiral_counter==1, countermode4==1, steps==1:  1 up
      ### - spiral_counter==2, countermode4==2, steps==1:  1 left
      ### - spiral_counter==3, countermode4==3, steps==2:  2 down
      ### - spiral_counter==4, countermode4==0, steps==2:  2 right
      ### - spiral_counter==5, countermode4==1, steps==3:  3 up
      ### - spiral_counter==6, countermode4==2, steps==3:  3 left
      ### - spiral_counter==7, countermode4==3, steps==4:  4 down
      ### - ...
      ### 
      ### - Small schematic:
      ###   - ptest initially at [*]
      ###   - [|] is movement up or down
      ###   - [-] is movement left or right
      ### 
      ###   +Y                 ---|
      ###    ^                 |-||
      ###    |                 ||*|
      ###    |                 ||--
      ###    |                 |-...
      ###   -+----->+X
      ###    |
      ### 
      ### - Large schematic with countermod4 embedded:
      ### 
      ###  +<------------2--------+
      ###  |                      ^
      ###  |                      |
      ###  |                      |
      ###  |      +<--2--+        |
      ###  |      |      ^        |
      ###  |      |      |        |
      ###  3      3      1        1
      ###  |      |      |        |
      ###  |      |   [ptest]     |
      ###  |      |               |
      ###  |      |               |
      ###  |      |               |
      ###  |      |               |
      ###  |      v               |
      ###  |      +------0------->+
      ###  |
      ###  |
      ###  v
      ###  +-------------4-------> ...
      ###

      ### Inner loop moves ptest by [steps] steps as directed by
      ### couuntermod4

      if do_debug: print(dict(all_out_legs=all_out_legs
                             ,area=area
                             ,steps=steps
                             ,spiral_counter=spiral_counter
                             ,countermod4=countermod4
                             ,x=ptest.x
                             ,y=ptest.y
                             )
                        )

      while steps:

        ### Move ptest by one step

        steps -= 1

        ### Move ptest in direction per countermod4

        if   countermod4==1: ptest.moveup()
        elif countermod4==2: ptest.moveleft()
        elif countermod4==3: ptest.movedown()
        else               : ptest.moveright()

        ### Test if ptest is closest to pin than to other points

        for boundary in boundaries:
          is_in = boundary.closer_to_pin(ptest)
          if do_debug: print((area,is_in,boundary.pout_name,(ptest.x,ptest.y,),pin.name,))
          if not is_in: break
        if do_debug: print('')

        ### Increment area if ptest is closest to pin

        if is_in:
          area += 1

        ### End of [while steps] loop
        ############################

      ### Termination criterion [all_out_legs]:  increment or reset

      if area == area_at_top_of_loop: all_out_legs += 1
      else                          : all_out_legs = 0

    ### End of [while all_out_legs < 8] loop
    ################################

    ### Save maximum area

    if area > max_area: max_area = area

  print(area)
