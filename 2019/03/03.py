import os
import sys

unitvectors = dict(r=(1,0,),l=(-1,0,),u=(0,1,),d=(0,-1))
hvs = dict(r='h',l='h',u='v',d='v')

def parse_dvector(command):
  direction,distance = command[0],int(command[1:])
  return [hvs[direction]] + [distance*component for component in unitvectors[direction]]
  
class PATH(object):
  def __init__(self,rawline):
    xnew,ynew = 0,0
    self.horizontals,self.verticals,self.all = list(),list(),list()
    modline = rawline.lower().strip()
    for command in modline.split(','):
      hv,dx,dy = parse_dvector(command)
      x,y = xnew,ynew
      xnew,ynew = x+dx,y+dy
      if 'h'==hv:
        last = (min([x,xnew]),max([x,xnew]),y,hv,x,xnew,)
        self.horizontals.append(last)
      else:
        last = (min([y,ynew]),max([y,ynew]),x,hv,y,ynew,)
        self.verticals.append(last)

      self.all.append(last)
      
  def intersections(self,otherpath):
    """Find all intersections; return triples (x,y,manhattandistance)"""
    rtn = set()
    one = self
    two = otherpath
    for ipass in range(2):
      for xlo,xhi,y,h0,h1,h2 in one.horizontals:
        for ylo,yhi,x,v0,v1,v2 in two.verticals[1:]:
          if xlo > x or xhi < x: continue
          if ylo > y or yhi < y: continue
          rtn.add((abs(x)+abs(y),x,y))
      one = otherpath
      two = self
    return rtn

  def part1(self,otherpath):
    return min(self.intersections(otherpath))

  def calc_steps(self,intersection):
    xint,yint = intersection[1:]
    steps = 0

    for (xylo,xyhi,xy,hv,xybeg,xyend,) in self.all:

      if hv is 'h':
        if xy==yint and xylo<=xint and xyhi>=xint:
          return steps + abs(xint-xybeg)
        steps += (xyhi - xylo)

      else:
        if xy==xint and xylo<=yint and xyhi>=yint:
          return steps + abs(yint-xybeg)
        steps += (xyhi - xylo)

    assert False

if "__main__"==__name__:
  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  with open(fn,'r') as fin:
    path1,path2 = map(PATH,fin)
    intersections = path1.intersections(path2)
    ### Part1
    print(min(intersections))
    ### Part2
    print(min([path1.calc_steps(intersection)+path2.calc_steps(intersection)
               for intersection in intersections
              ]))
