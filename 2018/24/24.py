import os
import sys

do_debug = "DEBUG" in os.environ

class GROUP(object):
  """Class to hold properties and execute behavior of group of either
immunity system units or infection units

"""

  ##################################
  ### Class-wide properties
  ##################################

  ### - Atack types
  st_attacks = 'cold slashing bludgeoning radiation fire'.split()

  ##################################
  def __repr__(self):
    if not do_debug: return self.group_name
    return '{0}/{1}/{2}:{3}/{4}/i:{5}/w:{6}'.format(
      self.units
      ,self.hp
      ,self.attack_damage
      ,self.attack_type
      ,self.initiative
      ,','.join([k for k in GROUP.st_attacks if not self.dt_iw_multiples[k]])
      ,','.join([k for k in GROUP.st_attacks if 2 == self.dt_iw_multiples[k]])
      )

  ##################################
  def __init__(self,toks, group_name='Unknown group'):
    """Constructor for a group of immune system or infection units

Argument [toks] is an iterator of strings from a line of the input file
e.g. this input line:

  18 units each with 729 hit points (weak to fire; immune to cold,
  slashing) with an attack that does 8 radiation damage at initiative 10

yields this list of tokens (toks argument):

  ['18', 'units', ..., 'initiative', 10]
"""

    ### Placeholder for which opposing group is targeting this group
    ### N.B. this will be set during the target selection phase, and
    ###      cleared at the end of the attacking phase
    self.clear_attacker()

    ### Save original line, assume toks are single-spaced
    ### Save group name
    self.original = ' '.join(toks)
    self.group_name = group_name

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
    self.dt_iw_multiples = dict([(s,1,) for s in GROUP.st_attacks])

    ### Parse middle section immunities and/or weaknesses
    ###   .. (weak to fire; immune to cold, slashing) ...
    ###
    ###   N.B. immunity and weakness keywords tokens are always trailed
    ###        by a single character that is not part of the keyword e.g
    ###        "fire;" or "cold," or "slashing)"

    ### Set immunity/weakness multiple to None to ensure parsed data
    ### syntax and grammar is correct
    iw_multiple = None

    ### Loop over reversed tokens i.e. from end of list
    while toks:

      tok = toks.pop()

      if tok.endswith('weak'):

        ### - Weaknesses double the damage of the given attack types

        assert iw_multiple is None
        iw_multiple = 2
        assert 'to' == toks.pop()
        continue

      if tok.endswith('immune'):

        ### - Immunities avoid all damage of the given attack types

        assert iw_multiple is None
        iw_multiple = 0
        assert 'to' == toks.pop()
        continue

      ### - Attack types (st_attacks); set multiple per last [immune to]
      ###   or [weak to] tokens parsed

      assert tok[:-1] in GROUP.st_attacks
      assert not (iw_multiple is None)
      self.dt_iw_multiples[tok[:-1]] = iw_multiple

      ### - Clear iw multiple if a semi-colon is encountered
      if tok.endswith(';'): iw_multiple = None

      ### End of [while toks:] loop


  ##################################
  def effective_power(self):
    """Calculate effective power"""

    return self.units * self.attack_damage


  ##################################
  def select_target_key(self,target):
    """max(<list>,key=<key>) key function to select target for self

Metrics:
1) which target has not already been selected as a target by another
   group;
2) to which target the most damage will be done by self;
3) target with largest effective power;
3) target with highest initiative

Return a four-tuple with a value representing each of those metrics

Usage:

  selected_target = max(list_targets, attacker.select_target)
  selected_target.set_attacker(attacker)

"""
    return ((target.targeted_by is None) and 1 or 0
           ,target.calculate_damage(self)
           ,target.effective_power()
           ,target.initiative
           )


  ##################################
  def calculate_damage(self, targeted_by):
    """Calculate attack damage to self by attack from targeted_by"""

    ### If targeted_by is not a group (i.e. is None), then return zero

    if not isinstance(targeted_by,GROUP): return 0

    ### Scale effective power of targeted_by by any immunity or weakness

    return ( targeted_by.effective_power()
           * self.dt_iw_multiples[targeted_by.attack_type]
           )


  ##################################
  def run_attack(self):
    """Run an attack from GROUP self.targeted_by"""

    damage = self.calculate_damage(self.targeted_by)

    if damage > 0:
      units_lost = min([damage / self.hp, self.units])
      self.units -= units_lost

    self.clear_attacker()


  ##################################
  def clear_attacker(self):
    """Clear attacker"""

    self.set_attacker(None)


  ##################################
  def set_attacker(self,attacker):
    """Set attacker for next attacking phase

- Do not allow overwriting one attacker with another
- Allow neither attacker nor defender to have no units

"""
    if attacker is None:
      self.targeted_by = attacker
      return

    if not isinstance(self.targeted_by,GROUP):

      if (self.units > 1 and attacker.units > 1):

        self.targeted_by = attacker


### End of class GROUP
########################################################################

########################################################################
### Ordering key functions
###
### N.B. Lists will be created with sorted(<list>,key=<key>), and then
###      processed from the **end** of the list via .pop(), so the
###      ordering of the list is that the first GROUP to be processed,
###      that is the group with the highest-sorted metrics, will be last
###      on the sorted list, and the last GROUP to be processed will be
###      first on the list
########################################################################


####################################
def selection_order_key(group):
  """Selection order key for sorted list with 1st selector last in list

Metrics:
1) by decreasing effective power,
2) decreasing initiative (higher initiative chooses first)

Return a two-tuple with a value representing each metric

"""

  return (group.effective_power(),group.initiative,)


####################################
def attack_order_key(group):
  """Attack order key for sorted list with 1st attacker last in list

Metric is that higher initiative attacks first.

N.B. Each attacker will be in the .targeted_by member of the group it is
     attacking, so it is the ***targeted*** entities that will be sorted

"""

  ### GROUPs that are not targeted will have None as their .targeted_by
  ### member; sort them last:
  if not isinstance(group.targeted_by,GROUP): return -1

  return group.targeted_by.initiative


########################################################################
class OHDEER(object):
  """Class to hold the states of a deer's immunities and infections"""

  def __init__(self,iter):
    """Parse iterable of strings that contain descriptions of groups"""

    self.lt_immune = list()
    self.lt_infection = list()

    team = None

    for rawline in iter:

      toks = rawline.strip().split()

      L = len(toks)

      if 2 == L:
        side = toks.pop()
        assert 'System:' == side
        assert 'Immune' == toks.pop()
        team = self.lt_immune

      elif 1 == L:
        side = toks.pop()
        assert 'Infection:' == side
        team = self.lt_infection

      elif 17 < L:
        group_name = '{0} group {1}'.format(side[:-1], len(team) + 1)
        team.append(GROUP(toks, group_name=group_name))

      assert not len(toks)

    ### End of .__init__ constructor
    ####################################################################

  ##################################
  def run_fight(self):
    """Run one round of target_selection and attacking"""

    lt_two = [self.lt_immune, self.lt_infection]

    ### Selection phase

    lt_target = lt_two[-1]

    for lt in lt_two:

      ### Sort attacker list per selection order key
      lt_selection_ordered = sorted(lt,key=selection_order_key)

      while lt_selection_ordered:
        lt_group = lt_selection_ordered.pop()

        ### Find group to attack in target list
        target_group = max(lt_target,key=lt_group.select_target_key)

        ### And target that list
        target_group.set_targeted_by(lt_group)

      ### Switch target list
      lt_target = lt_two[0]

    ### Attacking phase:  buld attack-sorted list; run attacks

    lt_attack = sorted(sum(lt_two,[]),key=attack_order_key)

    while lt_attack: lt_attack.pop().run_attack()


  ##################################
  def sums_units(self,lt):
    """Sum numbers of units in the arrays of groups"""

    return ( sum([group.units for group in self.lt_immune])
           , sum([group.units for group in self.lt_infection])
           )


if "__main__" == __name__ and sys.argv[1:]:


  with open(sys.argv[1],'r') as fin: ohdeer = OHDEER(fin)

  print(vars(ohdeer))
