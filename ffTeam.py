# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ffAgent', second = 'ffAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ffAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  # Add any necessary instance variables here
  def __init__(self, gameState):
    CaptureAgent.__init__(self, gameState)

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.generatePDDLDomain()
    # gameState.data.layout

  def createPDDLobjects(self, gameState):
    objects = ''

    # First we deal with the valid spaces for movement
    obs = self.getCurrentObservation()
    
    if gameState.isOnRedTeam(self.index):
      food = gameState.getRedFood()
    else:
      food = gameState.getBlueFood()

    #for 
    return ""

  def createPDDLfluents(self, gameState):
    return ""

  def createPDDLgoal(self, gameState):
    return ""

  def generatePDDLproblem(self, gameState): 
	"""
        outputs a file called problem.pddl describing the initial and
        the goal state
        """

	f = open("problem%d.pddl"%(self.index + 1),"w");
	lines = list();
	lines.append("(define (problem pacman-problem)\n");
   	lines.append("   (:domain pacman)\n");
   	lines.append("   (:objects \n");
	lines.append( self.createPDDLobjects(gameState) + "\n");
	lines.append("    )\n");
	lines.append("   (:init \n");\
	lines.append( self.createPDDLfluents(gameState) + "\n");
        lines.append("    )\n");
        lines.append("   (:goal \n");          
        lines.append("	( and  \n");
        lines.append( self.createPDDLgoal(gameState) + "\n");
        lines.append("	)\n");
        lines.append("   )\n");
        lines.append(")\n");

	f.writelines(lines);
	f.close();

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    #actions = gameState.getLegalActions(self.index)

    self.generatePDDLproblem(gameState)

    '''
    You should change this in your own agent.
    '''

    #return random.choice(actions)
    return 'Stop'
  
  # Generates the PDDL Domain file (should only ever need to be done once, offline)
  def generatePDDLDomain(self):

    f = open("pacman-domain.pddl","w")
    lines = list()

    lines.append("(define (domain pacman)\n")

    lines.append("  (:requirements :typing)\n")
    lines.append("  (:types pos)\n")

    lines.append("  ;; Define the problem facts\n")
    lines.append("  ;; \"?\" denotes a variable\, \"-\" denotes a type\n")
    lines.append("  (:predicates  (At ?p - pos)\n")
    lines.append("                (FoodAt ?p - pos)\n")
    lines.append("                (Adjacent ?pos1 ?pos2 - pos)\n")
    lines.append("  )\n")

    lines.append("  ;; Define the actions\n")
    lines.append("  (:action move\n")
    lines.append("        :parameters (?posCurr ?posNext - pos)\n")
    lines.append("        :precondition (and (At ?posCurr)\n")
    lines.append("                           (Adjacent ?posCurr ?posNext)\n")
    lines.append("                       )\n")
    lines.append("        :effect   (and (At ?posNext)\n")
    lines.append("                       (not  (At ?posCurr) )\n")
    lines.append("                       (not  (FoodAt ?posNext) )\n")
    lines.append("                   )\n")
    lines.append("   )\n")

    lines.append(")")
    
    
    f.writelines(lines)
    f.close()
