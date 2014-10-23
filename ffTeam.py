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
import subprocess
import platform
import sys
import os

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ffAgentCollector', second = 'ffAgentCollector'):
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

########## ffAgentCollector ##########
# Creates a Collector type Agent which attempts to eat all the opponent's food

class ffAgentCollector(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  # Add any necessary instance variables here
  def __init__(self, gameState):
    CaptureAgent.__init__(self, gameState)
    self.distanceThreshold = 5
    self.carryThreshold = 5

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

  def findClosestHomePosition(self, gameState, state):
    layout = gameState.data.layout
    myPos = state.getPosition()

    boundary = list()

    # Find the boundary position for your team
    if self.red:
      xBoundary = layout.width/2 - 1
    else:
      xBoundary = layout.width/2

    # Find the positions along the boundary that aren't walls      
    walls = gameState.getWalls().asList()
    for i in range(0,layout.height):
      if (xBoundary,i) not in walls:
        boundary.append((xBoundary,i))

    minDist = 9999
    closestPoint = None
    for point in boundary:
      dist = self.getMazeDistance(myPos, point)
      if dist < minDist:
        minDist = dist
        closestPoint = point

    return closestPoint    

  def createPDDLobjects(self, gameState):
    objects = ""

    # First we build the PDDL objects; the positions
    # layout is of type Layout, in layout.py
    layout = gameState.data.layout

    for i in range(0,layout.width):
      for j in range(0,layout.height):
        objects = objects + " p_" + str(i) + "_" + str(j)

    objects = objects + " - pos"
      
    return objects

  def createPDDLfluents(self, gameState):
    fluents = ""

    # obs is of type GameState, found in capture.py
    obs = self.getCurrentObservation()

    # First we add the current position
    pos = gameState.getAgentPosition(self.index)
    fluents = fluents + "\t\t(At " + "p_" + str(pos[0]) + "_" + str(pos[1]) + ")\n"

    # Now we deal with the walls
    # walls is of type Grid, found in game.py
    walls = gameState.getWalls()
    wallsList = walls.asList()
    
    # For every grid position
    for i in range(0,walls.width):
      for j in range(0,walls.height):
        # Check the position is a wall
        currPos = "p_" + str(i) + "_" + str(j)
        if (i,j) not in wallsList:
          # If it is not a wall, check each of its neightbours,
          # and add them to the adjacency list if they are free
          # Check left
          if (i - 1 >= 0) and ((i - 1,j) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i-1) + "_" + str(j) + ")\n"
          # Check right
          if (i + 1 < walls.width) and ((i + 1,j) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i+1) + "_" + str(j) + ")\n"
          # Check up
          if (j + 1 >= 0) and ((i,j+1) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i) + "_" + str(j+1) + ")\n"
          # Check down
          if (j - 1 >= 0) and ((i,j-1) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i) + "_" + str(j-1) + ")\n"    

    # This is a collector type Agent, so we add the food to find on the opposing side
    # food is of type Grid, found in game.py
    food = self.getFood(gameState).asList()

    for x,y in food:
      fluents = fluents + "\t\t(FoodAt p_" + str(x) + "_" + str(y) + ")\n"
      
    return fluents

  def createPDDLgoal(self, gameState):

    state = gameState.getAgentState(self.index)
    
    goals = ""

    # This is a hunter type Agent, so its main objective is to eat food
    food = self.getFood(gameState).asList()

    # No food, so run home
    if len(food) == 0 or state.numCarrying >= self.carryThreshold:
      pos = self.findClosestHomePosition(gameState,state)
      
      goals = goals + "\t\t(At p_" + str(pos[0]) + "_" + str(pos[1]) + ")\n"      
    else:
      for x,y in food:
        goals = goals + "\t\t(not (FoodAt p_" + str(x) + "_" + str(y) + "))\n"

    enemies = [gameState.getAgentState(i).getPosition() for i in self.getOpponents(gameState)]

    for enemy in enemies:
      if not enemy == None:
        goals = goals + "\t\t(not (At p_" + str(int(enemy[0])) + "_" + str(int(enemy[1])) + "))\n"
    
    return goals

  def generatePDDLproblem(self, gameState): 
	"""
        outputs a file called problem.pddl describing the initial and
        the goal state
        """

	f = open("problem%d.pddl"%(self.index + 1),"w");
	lines = list();
	lines.append("(define (problem pacman-problem)\n");
   	lines.append("   (:domain pacman)\n");
   	lines.append("   (:objects " + self.createPDDLobjects(gameState) + ")\n");
	lines.append("   (:init \n");\
	lines.append( self.createPDDLfluents(gameState));
        lines.append("    )\n");
        lines.append("   (:goal \n");          
        lines.append("	( and  \n");
        lines.append( self.createPDDLgoal(gameState));
        lines.append("	)\n");
        lines.append("   )\n");
        lines.append(")\n");

	f.writelines(lines);
	f.close();

  def callFF(self):

    action = 'Stop'
    
    #actions = gameState.getLegalActions(self.index)

    # If we're not on Windows, assume a Unix system (the servers)
    if not platform.system() == "Windows":
      # Call the ff planner
      out = os.popen("/home/subjects/482/local/project/ff -o pacman-domain.pddl -f problem"\
                   + str(self.index + 1) + ".pddl").read()
      # Split the output into lines
      ffPlan = out.split("\n")
      # Find the first MOVE action
      for s in ffPlan:
        pos = s.find("MOVE")
        if pos > 0:
          # We only care about the to and from positions
          fromPos,toPos = s[pos+5:].split()
          _,xCurr,yCurr = fromPos.split("_")
          _,xNext,yNext = toPos.split("_")

          xCurr = int(xCurr)
          yCurr = int(yCurr)
          xNext = int(xNext)
          yNext = int(yNext)

          # Moving right
          if (xNext - xCurr == 1):
            action = 'East'
          # Moving left
          elif (xNext - xCurr == -1):
            action = 'West'
          # Moving up
          elif (yNext - yCurr == 1):
            action = 'North'
          # Moving down
          elif (yNext - yCurr == -1):
            action = 'South'
          # Not moving
          else:
            action = 'Stop'

          break
        
    return action

  def chooseAction(self, gameState):

    self.generatePDDLproblem(gameState)

    action = self.callFF()
      
    return action
  
  # Generates the PDDL Domain file for Pacman (should only ever need to be done once, offline)
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
    lines.append("                (CapsuleAt ?p - pos)\n")
    lines.append("                (GhostAt ?p - pos)\n")
    lines.append("                (Adjacent ?pos1 ?pos2 - pos)\n")
    lines.append("                (Powered)\n")
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
    lines.append("                       (not  (CapsuleAt ?posNext) )\n")
    lines.append("                       (when (Powered) (not (GhostAt ?posNext)))\n")
    lines.append("                   )\n")
    lines.append("   )\n")

    lines.append(")")
    
    
    f.writelines(lines)
    f.close()

########## ffAgentHunter ##########
# Creates a Hunter type Agent which attempts to hunt 

class ffAgentHunter(CaptureAgent):
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

  def createPDDLobjects(self, gameState):
    objects = ""

    # First we build the PDDL objects; the positions
    # layout is of type Layout, in layout.py
    layout = gameState.data.layout

    for i in range(0,layout.width):
      for j in range(0,layout.height):
        objects = objects + " p_" + str(i) + "_" + str(j)

    objects = objects + " - pos"
      
    return objects

  def createPDDLfluents(self, gameState):
    fluents = ""

    # obs is of type GameState, found in capture.py
    obs = self.getCurrentObservation()

    # First we add the current position
    pos = gameState.getAgentPosition(self.index)
    fluents = fluents + "\t\t(At " + "p_" + str(pos[0]) + "_" + str(pos[1]) + ")\n"

    # Now we deal with the walls
    # walls is of type Grid, found in game.py
    walls = gameState.getWalls()
    wallsList = walls.asList()
    
    # For every grid position
    for i in range(0,walls.width):
      for j in range(0,walls.height):
        # Check the position is a wall
        currPos = "p_" + str(i) + "_" + str(j)
        if (i,j) not in wallsList:
          # If it is not a wall, check each of its neightbours,
          # and add them to the adjacency list if they are free
          # Check left
          if (i - 1 >= 0) and ((i - 1,j) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i-1) + "_" + str(j) + ")\n"
          # Check right
          if (i + 1 < walls.width) and ((i + 1,j) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i+1) + "_" + str(j) + ")\n"
          # Check up
          if (j + 1 >= 0) and ((i,j+1) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i) + "_" + str(j+1) + ")\n"
          # Check down
          if (j - 1 >= 0) and ((i,j-1) not in wallsList):
            fluents = fluents + "\t\t(Adjacent " + currPos + " " + "p_" + str(i) + "_" + str(j-1) + ")\n"    

    # This is a hunter type Agent, so we add the opponents to hunt on our side
    if gameState.isOnRedTeam(self.index):
      blue = gameState.getBlueTeamIndices()
      enemies = list()
      enemies.append(gameState.getAgentPosition(blue[0]))
      enemies.append(gameState.getAgentPosition(blue[1]))
      states = list()
      states.append(gameState.getAgentState(blue[0]).isPacman)
      states.append(gameState.getAgentState(blue[1]).isPacman)
    else:
      red = gameState.getRedTeamIndices()
      enemies = list()
      enemies.append(gameState.getAgentPosition(red[0]))
      enemies.append(gameState.getAgentPosition(red[1]))
      states = list()
      states.append(gameState.getAgentState(red[0]).isPacman)
      states.append(gameState.getAgentState(red[1]).isPacman)

    # For every observable enemy, if there is a Pacman, we hunt him down...
    for pos,state in zip(enemies,states):
      if (not pos == None) and (state == True):
        fluents = fluents + "\t\t(PacmanAt p_" + str(pos[0]) + "_" + str(pos[1]) + ")\n"
        
    return fluents

  def createPDDLgoal(self, gameState):
    goals = ""

    # This is a hunter type Agent, so its main objective is to kill Pacman
    if gameState.isOnRedTeam(self.index):
      blue = gameState.getBlueTeamIndices()
      enemies = list()
      enemies.append(gameState.getAgentPosition(blue[0]))
      enemies.append(gameState.getAgentPosition(blue[1]))
      states = list()
      states.append(gameState.getAgentState(blue[0]).isPacman)
      states.append(gameState.getAgentState(blue[1]).isPacman)
    else:
      red = gameState.getRedTeamIndices()
      enemies = list()
      enemies.append(gameState.getAgentPosition(red[0]))
      enemies.append(gameState.getAgentPosition(red[1]))
      states = list()
      states.append(gameState.getAgentState(red[0]).isPacman)
      states.append(gameState.getAgentState(red[1]).isPacman)
      
    for pos,state in zip(enemies,states):
      if (not pos == None) and (state == True):
        goals = goals + "\t\t(not (PacmanAt p_" + str(pos[0]) + "_" + str(pos[1]) + "))\n"
    
    return goals

  def generatePDDLproblem(self, gameState): 
	"""
        outputs a file called problem.pddl describing the initial and
        the goal state
        """

	f = open("problem%d.pddl"%(self.index + 1),"w");
	lines = list();
	lines.append("(define (problem ghost-problem)\n");
   	lines.append("   (:domain ghost)\n");
   	lines.append("   (:objects " + self.createPDDLobjects(gameState) + ")\n");
	lines.append("   (:init \n");\
	lines.append( self.createPDDLfluents(gameState));
        lines.append("    )\n");
        lines.append("   (:goal \n");          
        lines.append("	( and  \n");
        lines.append( self.createPDDLgoal(gameState));
        lines.append("	)\n");
        lines.append("   )\n");
        lines.append(")\n");

	f.writelines(lines);
	f.close();

  def callFF(self):

    action = 'Stop'
    
    #actions = gameState.getLegalActions(self.index)

    # If we're not on Windows, assume a Unix system (the servers)
    if not platform.system() == "Windows":
      # Call the ff planner
      out = os.popen("/home/subjects/482/local/project/ff -o ghost-domain.pddl -f problem"\
                   + str(self.index + 1) + ".pddl").read()
      # Split the output into lines
      ffPlan = out.split("\n")
      # Find the first MOVE action
      for s in ffPlan:
        pos = s.find("MOVE")
        if pos > 0:
          # We only care about the to and from positions
          fromPos,toPos = s[pos+5:].split()
          _,xCurr,yCurr = fromPos.split("_")
          _,xNext,yNext = toPos.split("_")

          xCurr = int(xCurr)
          yCurr = int(yCurr)
          xNext = int(xNext)
          yNext = int(yNext)

          # Moving right
          if (xNext - xCurr == 1):
            action = 'East'
          # Moving left
          elif (xNext - xCurr == -1):
            action = 'West'
          # Moving up
          elif (yNext - yCurr == 1):
            action = 'North'
          # Moving down
          elif (yNext - yCurr == -1):
            action = 'South'
          # Not moving
          else:
            action = 'Stop'

          break
        
    return action

  def chooseAction(self, gameState):

    self.generatePDDLproblem(gameState)

    action = self.callFF()
      
    return action
  
  # Generates the PDDL Domain file for Pacman (should only ever need to be done once, offline)
  def generatePDDLDomain(self):

    f = open("ghost-domain.pddl","w")
    lines = list()

    lines.append("(define (domain ghost)\n")

    lines.append("  (:requirements :typing :conditional-effects)\n")
    lines.append("  (:types pos)\n")

    lines.append("  ;; Define the problem facts\n")
    lines.append("  ;; \"?\" denotes a variable\, \"-\" denotes a type\n")
    lines.append("  (:predicates  (At ?p - pos)\n")
    lines.append("                (PacmanAt ?p - pos)\n")
    lines.append("                (Adjacent ?pos1 ?pos2 - pos)\n")
    lines.append("                (Scared)		;; Whether Ghost is scared of Pacman\n")
    lines.append("  )\n")

    lines.append("  ;; Define the actions\n")
    lines.append("  (:action move\n")
    lines.append("        :parameters (?posCurr ?posNext - pos)\n")
    lines.append("        :precondition (and (At ?posCurr)\n")
    lines.append("                           (Adjacent ?posCurr ?posNext)\n")
    lines.append("                       )\n")
    lines.append("        :effect   (and (At ?posNext)\n")
    lines.append("                       (not  (At ?posCurr) )\n")
    lines.append("                       (when (not (Scared)) (not  (PacmanAt ?posNext) ) )\n")
    lines.append("                   )\n")
    lines.append("   )\n")

    lines.append(")")
    
    
    f.writelines(lines)
    f.close()
