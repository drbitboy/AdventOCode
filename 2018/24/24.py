import os
import sys

do_debug = "DEBUG" in os.environ

class GROUP(object):

  ### Atack types
  st_attacks = 'cold slashing bludgeoning radiation fire'.split()
  ###dt_attacks = dict([(s,i) for i,s in enumerate(st_attacks)])

  def __repr__(self):
    return '{0}/{1}/{2}:{3}/{4}/i:{5}/w:{6}'.format(
      self.units
      ,self.hp
      ,self.attack_damage
      ,self.attack_type
      ,self.initiative
      ,','.join([k for k in GROUP.st_attacks if not self.dt_iw[k]])
      ,','.join([k for k in GROUP.st_attacks if 2 == self.dt_iw[k]])
      )

  def __init__(self,toks):
    """Constructor for a group of units, immune system or infection"""

    ### Placeholder for which opposing group is targeting this group
    ### N.B. this will be set during the target selection phase, and
    ###      cleared at the end of the attacking phase
    self.clear_attacker()

    ### Save original string, assume single-spaced
    self.original = ' '.join(toks)

    ### Parse from back end
    ###   ... with an attack that does 8 cold damage at initiative 10

    self.initiative = int(toks.pop())
    assert 'initiative' == toks.pop()
    assert 'at' == toks.pop()
    assert 'damage' ==toks.pop()
    self.attack_type = toks.pop()
    assert self.attack_type in GROUP.st_attacks
    self.attack_damage = int(toks.pop())
    assert 'does' == toks.pop()
    assert 'that' == toks.pop()
    assert 'attack' == toks.pop()
    assert 'an' == toks.pop()
    assert 'with' == toks.pop()

    ### Reverse tokens to parse from front end
    ###   18 units each with 729 hit points ...

    toks.reverse()

    self.units = int(toks.pop())
    assert 'units' == toks.pop()
    assert 'each' == toks.pop()
    assert 'with' == toks.pop()
    self.hp = int(toks.pop())
    assert 'hit' == toks.pop()
    assert 'points' == toks.pop()

    ### Initialize all damage multipliers to 1
    self.dt_iw = dict([(s,1,) for s in GROUP.st_attacks])

    ### Parse middle section immunities and/or weaknesses
    ###   .. (weak to fire; immune to cold, slashing) ...

    ### Set immunity/weakness multiple to None to ensure parsed data are
    ### correct
    iw = None

    ### Loop over tokens
    while toks:
      tok = toks.pop()

      if tok.endswith('weak'):

        ### - Weaknesses double the damage of the given attack types

        assert iw is None
        iw = 2
        assert 'to' == toks.pop()
        continue

      if tok.endswith('immune'):

        ### - Immunities avoid all damage of the given attack types

        assert iw is None
        iw = 0
        assert 'to' == toks.pop()
        continue

      ### - Attack types (st_attacks); set multiple per last [immune to]
      ###   or [weak to] tokens parsed

      assert tok[:-1] in GROUP.st_attacks
      assert not (iw is None)
      self.dt_iw[tok[:-1]] = iw

      ### - Clear iw multiple if a semi-colon is encountered
      if tok.endswith(';'): iw = None

      ### End of [while toks:] loop


  def effective_power(self):
    """Calculate effective power"""
    return self.units * self.attack_damage

  def select_target(self,target):
    """Select target by 1) which target has not already been selected
as a target by another group; 2) to which target the most damage will be
done; 3) target with largest effective power; 3) target with highest
initiative

Return a tuple with a value representing each metric

"""

    return (target.targeted_by is None ? 1 : 0
           ,target.calculate_damage(self)
           ,target.effective_power()
           ,target.initiative
           )

  def calculate_damage(self, targeted_by):
    """Calculate attack damage based on attack type"""

    if not isinstance(targeted_by,GROUP): return 0

    return ( targeted_by.units
           * targeted_by.attack_damage
           * dt_iw[targeted_by.attack_type]
           )

  def run_attack(self):
    """Run an attack from GROUP self.targeted_by"""
    damage = self.calculate_damage(self.targeted_by)

    if damage > 0:
      units_lost = damage / self.hp
      if units_lost >= self.units:
        self.units = 0
      else
        self.units -= units_lost

    self.clear_attacker()

  def clear_attacker(self):
    """Clear attacker"""

    self.set_attacker(None)

  def set_attacker(self,attacker):
    """Set attacker for next attacking phase"""

    self.targeted_by = attacker

### End of class GROUP
########################################################################
### Ordering keys

def doselection_key(group):
  """Selection order is by decreasing effective power, then
decreasing initiative (higher initiative chooses first)

Return a tuple with a value representing each metric

"""

  return (group.effective_power(),group.initiative,)

def doattack_key(group):
  """Attack order is by decreasing initiative (higher initiative attacks
first)

"""

  return group.initiative


########################################################################
class OHDEER(object):
  """Class to hold a deer's immunities and infections"""

  def __init__(self,iter):

    self.lt_immune = list()
    self.lt_infection = list()

    team = None

    for rawline in iter:

      toks = rawline.strip().split()

      L = len(toks)

      if 2 == L:
        assert 'System:' == toks.pop()
        assert 'Immune' == toks.pop()
        team = self.lt_immune

      elif 1 == L:
        assert 'Infection:' == toks.pop()
        team = self.lt_infection

      elif 17 < L:
        team.append(GROUP(toks))

      assert not len(toks)


if "__main__" == __name__ and sys.argv[1:]:


  with open(sys.argv[1],'r') as fin: ohdeer = OHDEER(fin)

  print(vars(ohdeer))
