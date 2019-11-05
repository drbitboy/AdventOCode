import os
import sys
import pprint

do_debug = "DEBUG" in os.environ
do_log24 = "LOG24" in os.environ

class GROUP(object):
  """Class to hold properties and execute behavior of group either of
immune system units, or of infection units.

"""

  ##################################
  ### Class-wide properties
  ##################################

  ### - Atack types
  st_attacks = set('cold slashing bludgeoning radiation fire'.split())

  ##################################
  def __repr__(self):
    if not do_debug: return self.group_name
    return '{7}/{0}/{1}/{2}:{3}/{4}/i:{5}/w:{6}'.format(
      self.units
      ,self.hp
      ,self.unit_attack_damage
      ,self.attack_type
      ,self.initiative
      ,','.join([k for k in GROUP.st_attacks if not self.dt_iw_multiples[k]])
      ,','.join([k for k in GROUP.st_attacks if 2 == self.dt_iw_multiples[k]])
      ,self.group_name
      )

  ##################################
  def __init__(self,toks, group_name='Unknown group'):
    """Constructor for a group of immune system or infection units

========================================================================
Input argument [toks] is an iterator of strings from a line of the input
file e.g. this input line:

  18 units each with 729 hit points (weak to fire; immune to cold, slashing) with an attack that does 8 radiation damage at initiative 10

yields this list of tokens (toks argument):

  ['18', 'units', ..., 'initiative', 10]

"""

    ### Instantiate, and set to None, attribute placeholder for which
    ### attacking group is targeting this group.
    ###
    ### N.B. this attribuite may be set during the target selection
    ###      phase, and cleared at the end of the attacking phase
    self.clear_attacker()

    ### Save original line, assume toks are single-spaced
    ### Save group name
    self.original = ' '.join(toks)
    self.group_name = group_name

    ### Parse toks (tokens) list from back end using .pop() e.g.
    ###   ... with an attack that does 8 cold damage at initiative 10

    self.initiative = int(toks.pop())
    assert 'initiative' == toks.pop()
    assert 'at' == toks.pop()
    assert 'damage' ==toks.pop()
    self.attack_type = toks.pop()
    assert self.attack_type in GROUP.st_attacks
    self.unit_attack_damage = int(toks.pop())
    assert 'does' == toks.pop()
    assert 'that' == toks.pop()
    assert 'attack' == toks.pop()
    assert 'an' == toks.pop()
    assert 'with' == toks.pop()

    ### Reverse tokens to parse from front end using .pop() e.g.
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

    ### Loop over reversed tokens i.e. from end of list, which is also
    ### the start of the tokens originally supplied
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
    """Calculate effective power, (units * damage/unit)"""

    return self.units * self.unit_attack_damage


  ##################################
  def select_target_key(self,target):
    """Key function for max(<target_list>,key=<key>) to select from list
of targets for self as attacker.

Returns a four-tuple with a value representing each of metrics below

Usage:

  selected_target = max(list_targets, attacker.select_target)
  selected_target.set_attacker(attacker)

Metrics:
1) Selection ideally meets the following three criteria*
1a) target must not already be selected as a target by another attacking
     group during the selection process**, AND
1b) target must have a non-zero number of units***, AND
1c) attacker would deal a non-zero amount of damage against target****;
2) select target which will have the most damage done to it by self, out
2) select target which will have the most damage done to it by self
   (attacker), if tied on and meet criteria in (1);
3) select target with largest effective power, if tied on (1) and (2);
4) select target with highest initiative, if tied on (1), (2), and (3).

* N.B. the case where all target groups fail to meet one or more of
       these criteria is an edge case, as the call to method
       max(target_list,key=attacker.select_target_key) will return one
       of those invalid targets.  That case must be handled again in the
       target.set_attacker method.  In retrospect, it might be better to
       remove targets which have dropped to zero units from the lists
       being processed.

** "Defending groups can only be chosen as a target by one attacking
    group."

*** "Groups never have zero or negative units; instead, the group is
     removed from combat."

**** "Deal damage" does "not [account] for whether defender has enough
      units to actually receive all of [the] damage," but "If [attacker]
      cannot deal any defending groups damage, it does not choose a
      target."

"""
    return (((target.attacker is None)                ### (1a)
             and (target.units > 0)                   ### (1b)
             and (target.calculate_damage(self) > 0)  ### (1c)
             and 1 or 0
            )
           ,target.calculate_damage(self)             ### (2)
           ,target.effective_power()                  ### (3)
           ,target.initiative                         ### (4)
           )


  ##################################
  def calculate_damage(self, attacker):
    """Calculate attack damage dealt to self by attack from attacker.

Accounts for attacker effective power and self (target) immunities and
weaknesses; does not account for presence or absence of self.units*

* "after accounting for [target] weaknesses and immunities, but not
   accounting for whether the defending group [self] has enough units
   to actually receive all of that damage" i.e do not account for how
   much actual damage would be ***received*** by self, so "damage dealt"
   to self can be non-zero ***even if*** self.units is zero.

"""

    ### If attacker is not a group (i.e. is None), then return zero

    if not isinstance(attacker,GROUP): return 0

    ### Scale effective power of attacker by any immunity or weakness
    ### - Do "not [account] for whether the defending group has enough
    ###   units to actually receive all of that damage."

    return ( attacker.effective_power()
           * self.dt_iw_multiples[attacker.attack_type]
           )


  ##################################
  def run_defense(self,log=False):
    """Run one attack from GROUP self.attacker"""

    damage = self.calculate_damage(self.attacker)

    if damage > 0:

      ### Limit reduction of self.units to no more than what self
      ### currently possesses
      units_lost = min([damage / self.hp, self.units])

      if log:
        print('[{0}] attacks [{1}]:  damage={2}; units lost={3}'.format(
              self.attacker, self, damage, units_lost)
             )

      ### Decrement units
      self.units -= units_lost

    else:

      if log:
        print('[{0}] attacks [{1}]:  damage={2}'.format(
              self.attacker, self, damage)
             )

    ### Reset attacker placeholder
    self.clear_attacker()


  ##################################
  def clear_attacker(self):
    """Clear attacker"""

    self.set_attacker()    ### Defaults to setting self.attacker to None


  ##################################
  def set_attacker(self,attacker=None):
    """Reset attacker for next attacking phase

1) Do not allow overwriting one attacker with another
2) "If [attacker] cannot deal any defending groups damage,
    it does not choose a target."
3) "Groups never have zero or negative units; instead, the group is
    removed from combat."

N.B. The target selection phase will never select a defending group with
     any of these cases true ***except*** if all defending groups match
     one or more of these cases.  So we need to check these cases again
     here to cover that edge case exception.

* Maximum attacker.select_target_key(<defender>) value across all
  defenders

"""
    if attacker is None:
      self.attacker = None

    elif not isinstance(self.attacker,GROUP          ### (1)
         ) and (self.calculate_damage(attacker) > 0  ### (2)
         ) and (self.units > 0                       ### (3)
         ):
      self.attacker = attacker


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

Metric is that higher initiative attacks first.  "Groups attack in
decreasing order of initiative, ..."

N.B. Each attacker will be in the .attacker member of the group it is
     attacking, so it is the ***targeted*** entities that will be sorted

"""

  ### GROUPs that are not targeted will have None as their .attacker
  ### member; sort them last:
  if not isinstance(group.attacker,GROUP): return -1

  return group.attacker.initiative


########################################################################
class OHDEER(object):
  """Class to hold the states of a deer's immunities and infections"""

  ##################################
  def __init__(self,iter):
    """Parse iterable of strings that contain descriptions of groups"""

    self.lt_immune = list()     ### Create lists, of immune system ...
    self.lt_infection = list()  ### ... and infection groups

    team = None  ### Set team (immune or infection list) as invalid

    for rawline in iter:        ### Loop over lines in iterable argument

      toks = rawline.strip().split()  ### Break into tokens @ whitespace
      L = len(toks)                   ### Count of tokens

      if 2 == L:                        ### Immune System:
        assert 'System:' == toks.pop()
        side = toks.pop()
        assert 'Immune' == side
        team = self.lt_immune      ### Set team to reference immune list

      elif 1 == L:                      ### Infection:
        side = toks.pop()
        assert 'Infection:' == side
        team = self.lt_infection    ### Set team to reference infections

      elif 17 < L:                  ### A group descriptions

        ### Build default name e.g. "Immune group 1"
        ### Instantiate group from tokens and append to team list

        group_name = '{0} group {1}'.format(side.rstrip(':')
                                           , len(team) + 1
                                           )
        team.append(GROUP(toks, group_name=group_name))

      assert not len(toks)  ### Only other line should be empty

    ### End of .__init__ constructor
    ####################################################################

  ##################################
  def run_fight(self,log=False):
    """Run one round of target_selection and attacking"""

    ### Separate lists for target selection phase, one common list for 
    ### attacking phase

    lt_two = [self.lt_immune, self.lt_infection]
    lt_both = sum(lt_two,[])

    ################################
    ### Selection phase
    ################################

    lt_target = lt_two[-1]  ### Initialize target list to infections

    ### Loop over teams, immune group list as attackers first

    for lt in lt_two:

      ### Sort attacker list per selection order key

      lt_selection_ordered = sorted(lt,key=selection_order_key)

      ### Make selections

      while lt_selection_ordered:
        attacker = lt_selection_ordered.pop()

        ### Skip attackers which have no more units

        if not attacker.units: continue

        ### Select group to attack in target list, and target that list

        target = max(lt_target,key=attacker.select_target_key)
        target.set_attacker(attacker)

        ### Debugging, to log when attackers are not attached to
        ### selected targets (edge case)

        if not (target.attacker is attacker):
          if log:
            print('[{0}] could not select [{1}] to attack; current attacker is [{2}]'.format(
                  attacker, target, target.attacker)
                 )

      ### End of [while lt_selection_ordered] loop
      ##############################

      lt_target = lt_two[0]  ### Switch target list to immunities for
                             ### second pass through list wih infections
                             ### as attackers

    ### End of [for lt in lt_two] loop
    ################################


    ################################
    ### Attacking phase:  buld attacker-sorted list of defenders;
    ###                   run attacks
    ################################

    ### Sort all groups by initiative

    lt_defenders = sorted(lt_both,key=attack_order_key)

    ### Run attackers against defenders

    while lt_defenders:
      lt_defenders.pop().run_defense(log=log)

    ### Bookkeeping check

    assert not [group.attacker
                for group in lt_both
                if not (group.attacker is None)
               ]

  ### End of [run_fight(self,...)] method
  ##################################


  ##################################
  def run_war(self):
    """Execute fights until one of the teams has no more units

Return numbers of units
"""

    while 0 < min(self.sums_units()):

      log = do_log24 or (do_debug and (10 > min(self.sums_units())))

      self.run_fight(log=log)

      if log and do_debug: pprint.pprint(self.__dict__)

    return self.sums_units()


  ##################################
  def sums_units(self):
    """Sum numbers of units in the arrays of groups"""

    return ( sum([group.units for group in self.lt_immune])
           , sum([group.units for group in self.lt_infection])
           )

### End of [OHDEER] class
####################################


####################################
if "__main__" == __name__ and sys.argv[1:]:

  ### Open input file, pass to OHDEER constructor at iterable of strings

  with open(sys.argv[1],'r') as fin: ohdeer = OHDEER(fin)

  if do_debug or do_log24: pprint.pprint(ohdeer.__dict__)

  print(ohdeer.run_war())             ### Run the war, print the results
