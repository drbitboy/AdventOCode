import os
import sys


class MOON(object):
  R = range(3)

  def __init__(self,rawline): self.init(rawline)

  def init(self,rawline):
    self.tokens = rawline.strip().replace('<','').replace('>','').replace(' ','').split(',')
    self.xyz = [0]*3
    self.vxyz = [0]*3

    for token in self.tokens[:3]:
      assert '='==token[1]
      idx = 'xyz'.index(token[0])
      self.xyz[idx] = int(token[2:])

    self.s_initial = self.__repr__()

  def reset(self): self.init(self.s_initial[5:-1])

  def pre_step(self,lt_others):
    for idx in MOON.R:
      for other in lt_others:
        if self.xyz[idx] > other.xyz[idx]  : self.vxyz[idx] += -1
        elif self.xyz[idx] < other.xyz[idx]: self.vxyz[idx] += +1

  def post_step(self):
    for idx in MOON.R:
      self.xyz[idx] += self.vxyz[idx]

  def energy(self): return sum(map(abs,self.xyz)) * sum(map(abs,self.vxyz))
  def state6(self): return tuple(self.xyz+self.vxyz)

  def __repr__(self): return 'MOON(<x={0},y={1},z={2},vx={3},vy={4},vz={5}>)'.format(*self.state6())


class SYSTEM(object):
  def __init__(self,fn):
    self.step_count = 0
    self.lt_moons = list()
    with open(fn,'r') as fin:
      for rawline in fin:
        self.lt_moons.append(MOON(rawline))

  def __repr__(self): return '{0}'.format(self.lt_moons).replace(' ','')

  def steps(self,N):
    final_N = self.step_count + N
    while self.step_count < final_N:
      for moon in self.lt_moons: moon.pre_step(self.lt_moons)
      for moon in self.lt_moons: moon.post_step()
      self.step_count += 1
    return self

  def reset(self):
    for moon in self.lt_moons: moon.reset()

  def energy(self):
    return sum([moon.energy() for moon in self.lt_moons])

  def xyzvxyzs(self):
    tups = zip(*[moon.state6() for moon in self.lt_moons])
    return map(lambda tup:sum(tup,()),zip(tups[:3],tups[3:]))

def step6(xyzvxyz):
  t = tuple(xyzvxyz)
  d,ct = dict(),0
  Lhalf = len(t) >> 1
  Rhalf = range(Lhalf)
  while not (t in d):
    d[t] = ct
    lt = list(t)
    for i in Rhalf:
      pos = t[i]
      for j in Rhalf:
        if pos > t[j]  : lt[i+Lhalf] += -1
        elif pos < t[j]: lt[i+Lhalf] += +1
    for i in Rhalf: lt[i] += lt[i+Lhalf]
    t = tuple(lt)
    ct += 1
  assert not d[t]

  return ct

########################################################################

def gcd(a,b):
  while b:
    a,b = b,a%b
  return a

def lcm(a,b): return a * (b / gcd(a,b))

if "__main__" == __name__:

  fn = sys.argv[1:] and sys.argv[1] or 'input.txt'
  bn = os.path.basename(fn)
  sistem = SYSTEM(fn)

  if not bn.startswith('sample_input_part2_'):
    print(dict(part1=sistem.steps(1000).energy()))

  if not bn.startswith('sample_input_part1_'):
    sistem.reset()
    xyzvxyzs = sistem.xyzvxyzs()
    print(xyzvxyzs)
    ct3 = list(map(step6,xyzvxyzs))
    print(ct3)

  l = 1
  while ct3: l = lcm(l,ct3.pop())

  print(l)

