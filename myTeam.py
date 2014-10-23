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
import random, time, util, operator
from util import nearestPoint
from game import Directions
import game

POWERCAPSULETIME = 120

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'TopAgent', second = 'BottomAgent'):
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

class MainAgent(CaptureAgent):

  # Give each agent a most likely position and a power timer
  def __init__(self, gameState):
    CaptureAgent.__init__(self, gameState)
    self.mostlikely = [None]*4
    self.powerTimer = 0
  
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
    # Sets if agent is on red team or not
    if self.red:
      CaptureAgent.registerTeam(self, gameState.getRedTeamIndices())
    else:
      CaptureAgent.registerTeam(self, gameState.getBlueTeamIndices())

    # Get how large the game space is
    self.x, self.y = gameState.getWalls().asList()[-1] 
    # Legal positions are positions without walls
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
    self.walls = list(gameState.getWalls())
    # Chokes contains choke points on our side of game space
    self.chokes = [] 
    
    # Offsets for how far away from middle our ghosts should sit if an invader is detected
    # but cannot be seen for some reason
    if self.red:
        xAdd = -3
    else:
        xAdd = 4
    
    # Find all choke points of interest
    for i in range(self.y): 
        if not self.walls[self.x/2+xAdd][i]:
            self.chokes.append(((self.x/2+xAdd), i))	
    if self.index == max(gameState.getRedTeamIndices()) or self.index == max(gameState.getBlueTeamIndices()):
        x, y = self.chokes[3*len(self.chokes)/4]
    else:
        x, y = self.chokes[1*len(self.chokes)/4]
    self.goalTile = (x, y) 

    # beliefs is used to infere the position of enemy agents using noisey data
    global beliefs
    beliefs = [util.Counter()] * gameState.getNumAgents() 
    
    # All beliefs begin with the agent at its inital position
    for i, val in enumerate(beliefs):
        if i in self.getOpponents(gameState): 
            beliefs[i][gameState.getInitialAgentPosition(i)] = 1.0  
      
    #Agents inital move towards the centre with a bias for either the top or the bottom
    self.goToCenter(gameState)
    
  # Detect position of enemies that are visible
  def getEnemyPos(self, gameState):
    enemyPos = []
    for enemy in self.getOpponents(gameState):
      pos = gameState.getAgentPosition(enemy)
      #Will need inference if None
      if pos != None:
        enemyPos.append((enemy, pos))
    return enemyPos

  # Find which enemy is the closest
  def enemyDist(self, gameState):
    pos = self.getEnemyPos(gameState)
    minDist = None
    if len(pos) > 0:
      minDist = float('inf')
      myPos = gameState.getAgentPosition(self.index)
      for i, p in pos:
        dist = self.getMazeDistance(p, myPos)
        if dist < minDist:
          minDist = dist
    return minDist

  #Is agent a pacman or a ghost?
  def inEnemyTerritory(self, gameState):
    return gameState.getAgentState(self.index).isPacman
  
  # Return the position of the agent currently being processed  
  def getMyPos(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  # Calculates the distance to the partner of the current agent
  def getDistToPartner(self, gameState):
    distanceToAgent = None
    agentsList = self.agentsOnTeam
    if self.index == self.agentsOnTeam[0]:
      otherAgentIndex = self.agentsOnTeam[1]
      distanceToAgent = None
    else:
      otherAgentIndex = self.agentsOnTeam[0]
    # The below code is under 'else' so that only
    # one of the pacmen cares how close it is to the other
    # so that they don't become confused
      myPos = self.getMyPos(gameState)
      otherPos = gameState.getAgentState(otherAgentIndex).getPosition()
      distanceToAgent = self.getMazeDistance(myPos, otherPos)
      if distanceToAgent == 0:
        distanceToAgent = 0.5
    return distanceToAgent
    
  # Which side of the board is the agent?  
  def side(self,gameState):
    width, height = gameState.data.layout.width, gameState.data.layout.height
    pos = gameState.getAgentPosition(self.index)
    if self.index%2==1:
      # red
      if pos[0]<width/(2):
        return 1.0
      else:
        return 0.0
    else:
      # blue
      if pos[0]>width/2-1:
        return 1.0
      else:
        return 0.0

  # Is pacman powered?
  def isPowered(self):
    return self.powerTimer > 0
  
  # How much longer is the ghost scared?
  def ScaredTimer(self, gameState):
    return gameState.getAgentState(self.index).scaredTimer

  # Gets the distribution for where a ghost could be, all weight equally
  def getDist(self, p):
    posActions = [(p[0] - 1, p[1]), (p[0] + 1, p[1]), (p[0], p[1] - 1), (p[0], p[1] + 1), (p[0], p[1])]
    actions = []
    for act in posActions:
        if act in self.legalPositions:
            actions.append(act)
        
    dist = util.Counter()
    for act in actions:
        dist[act] = 1
    return dist
        
  # Looks at how an agent could move from where they currently are
  def elapseTime(self, gameState): 
    for agent, belief in enumerate(beliefs):
        if agent in self.getOpponents(gameState):
            newBeliefs = util.Counter()
            # Checks to see what we can actually see
            pos = gameState.getAgentPosition(agent) 
            if pos != None:
                newBeliefs[pos] = 1.0
            else:
                # Look at all current beliefs
                for p in belief:
                    if p in self.legalPositions and belief[p] > 0: 
                        # Check that all these values are legal positions
                        newPosDist = self.getDist(p)
                        for x, y in newPosDist:# iterate over these probabilities
                            newBeliefs[x, y] += belief[p] * newPosDist[x, y] 
                            # The new chance is old chance * prob of this location from p
                if len(newBeliefs) == 0:
                    oldState = self.getPreviousObservation()
                    if oldState != None and oldState.getAgentPosition(agent) != None: # just ate an enemy
                        newBeliefs[oldState.getInitialAgentPosition(agent)] = 1.0
                    else:
                        for p in self.legalPositions: newBeliefs[p] = 1.0
            beliefs[agent] = newBeliefs

    #self.displayDistributionsOverPositions(beliefs)
  
  # Looks for where the enemies currently are
  def observe(self, agent, noisyDistance, gameState):
		myPos = gameState.getAgentPosition(self.index)
        # Current state probabilities
		allPossible = util.Counter()
		for p in self.legalPositions:   # check each legal position
			trueDistance = util.manhattanDistance(p, myPos) # distance between this point and Pacman
			allPossible[p] += gameState.getDistanceProb(trueDistance, noisyDistance) 
        # The new values are product of prior probability and new probability  
		for p in self.legalPositions:
			beliefs[agent][p] *= allPossible[p]  
    
  # Choose which action will result in the best move
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    # You can profile your evaluation time by uncommenting these lines
    #start = time.time()

    # Get all legal actions of current state
    actions = gameState.getLegalActions(self.index)
    # Get list of opponents
    opponents = self.getOpponents(gameState)
    # Get noisey distance data
    noisyD = gameState.getAgentDistances() 
    # Get this agent's current position
    myPos = gameState.getAgentPosition(self.index)
    
    # Observe each opponent to get noisey distance measurement and process
    for agent in opponents:
        self.observe(agent, noisyD[agent], gameState) 
   
    # Set default move location to the hover position from above
    self.locations = [self.chokes[len(self.chokes)/2]] * gameState.getNumAgents() 
    for i, belief in enumerate(beliefs):
        maxLoc = 0
        checkForAllEq = 0
        for val in beliefs[i]:
            # Checks if there are many possible locations for the enemy with equal probability 
            if belief[val] == maxLoc and maxLoc > 0: 
                # If many locations are equally likely, ignore this inference itteration as it is inaccurate
                checkForAllEq += 1 
            elif belief[val] > maxLoc:
                maxLoc = belief[val]
                self.locations[i] = val
                # Set target location as the highest probability location
        if checkForAllEq > 5:
            self.locations[i] = self.goalTile
   
    # Normalise new probabilities and pick most likely location for enemy agent
    for agent in opponents:
        beliefs[agent].normalize()   
        self.mostlikely[agent] = max(beliefs[agent].iteritems(), key=operator.itemgetter(1))[0]
    
    # Do next time step
    self.elapseTime(gameState)
    # Get agent position
    agentPos = gameState.getAgentPosition(self.index)
    
    ##################
    # Choose Tactics #
    ##################
    
    # Default to attack mode
    evaluateType = 'attack' 
    
    #Start in the start state, move to the centre then switch to attack
    if self.atCenter == False:
      evaluateType = 'start'

    # If at centre, switch to attack
    if agentPos == self.center and self.atCenter == False:
      self.atCenter = True
      evaluateType = 'attack'

    # If an enemy is attacking our food, hunt that enemy down
    for agent in opponents:
        if(gameState.getAgentState(agent).isPacman):
            evaluateType = 'hunt'    
    
    #If we directly see an enemy on our side, swich to defence
    enemyPos = self.getEnemyPos(gameState)
    if len(enemyPos) > 0:
      for enemy, pos in enemyPos:
        if self.getMazeDistance(agentPos, pos) < 5 and not self.inEnemyTerritory(gameState):
          evaluateType = 'defend'
          break
    
    # Get all legal actions this agent can make in this state
    actions = gameState.getLegalActions(self.index)
    # Calcualte heuristic score of each action
    values = [self.evaluate(gameState, a, evaluateType) for a in actions]
    #print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    # Pick the action with the highest heuristic score as the best next move
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
  
    # If multiple best moves exist (unlikely), pick one at random
    return random.choice(bestActions)


  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  # Calculate the heurisic score of each action depending on what tactic is being used
  def evaluate(self, gameState, action, evaluateType):
    """
    Computes a linear combination of features and feature weights
    """
    if evaluateType == 'attack':
      #print "ATTACKING!!!"
      features = self.getFeaturesAttack(gameState, action)
      weights = self.getWeightsAttack(gameState, action)
    elif evaluateType == 'defend':
      #print "DEFENDING!!!"
      features = self.getFeaturesDefend(gameState, action)
      weights = self.getWeightsDefend(gameState, action)
    elif evaluateType == 'start':
      #print "STARTING!!!"
      features = self.getFeaturesStart(gameState, action)
      weights = self.getWeightsStart(gameState, action)
    elif evaluateType == 'hunt':
      #print "HUNTING!!!"
      features = self.getFeaturesHunt(gameState, action)
      weights = self.getWeightHunt(gameState, action)

    return features * weights

  # Returns all the heuristic features for the HUNT tactic  
  def getFeaturesHunt(self, gameState, action):
    
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    
    # Get own position
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    
    # Get opponents and invaders
    opponents = self.getOpponents(gameState)
    invaders = [agent for agent in opponents if successor.getAgentState(agent).isPacman]

    # Find number of invaders
    features['numInvaders'] = len(invaders)
    
    # For each invader, calulate its most likely poisiton and distance
    for agent in invaders:
        enemyPos = self.mostlikely[agent]
        enemyDist = self.getMazeDistance(myPos, enemyPos)
    features['invaderDistance'] = enemyDist

    # Compute distance to partner
    if self.inEnemyTerritory(successor):
      distanceToAlly = self.getDistToPartner(successor)
      # distanceToAgent is always None for one of the agents (so they don't get stuck)
      if distanceToAlly != None:
        features['distanceToAlly'] = 1.0/distanceToAlly

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features
  
  # Returns all the heuristic features for the ATTACK tactic  
  def getFeaturesAttack(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    # Get own position, size of game state and locations of all food to eat
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    agentsList = self.agentsOnTeam
    width, height = gameState.data.layout.width, gameState.data.layout.height
    foodList = self.getFood(successor).asList()

    # Get score for successor state
    features['successorScore'] = self.getScore(successor)

    # Dist to nearest food heuristic 
    if len(foodList) > 0:
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Pickup food heuristic
    if(len(foodList)>0):
      features['pickupFood'] = -len(foodList) + 100*self.getScore(successor)
      
    # Compute distance to enemy 
    distEnemy = self.enemyDist(successor)
    if(distEnemy != None):
      if(distEnemy <= 2):
         features['danger'] = 4/distEnemy
      elif(distEnemy <= 4):
          features['danger'] = 1
      else:
        features['danger'] = 0  

    # Compute distance to capsule
    capsules = self.getCapsules(successor)
    if(len(capsules) > 0):
      minCapsuleDist = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
      features['pickupCapsule'] = -len(capsules)
    else:
      minCapsuleDist = .1
    features['capsuleDist'] =  1.0/minCapsuleDist

    # Holding food heuristic
    if myPos in self.getFood(gameState).asList():
      self.foodNum += 1.0
    if self.side(gameState) == 0.0:
      self.foodNum = 0.0
    features['holdFood'] = self.foodNum*(min([self.distancer.getDistance(myPos,p) for p in [(width/2,i) for i in range(1,height) if not gameState.hasWall(width/2,i)]]))*self.side(gameState)          
    
    # Dropping off food heuristic
    features['dropFood'] = self.foodNum*(self.side(gameState))
    
    # If picked up a capsule, set power timer
    if myPos in self.getCapsules(gameState):
        self.powerTimer = POWERCAPSULETIME
    
    # If powered, reduce power timer each itteration
    if self.powerTimer>0:
        self.powerTimer -= 1

    # Is powered heuristic
    if(self.isPowered()):
      features['isPowered'] = self.powerTimer/POWERCAPSULETIME
      features['holdFood'] = 0.0
      features['pickupFood'] = 100*features['pickupFood']
    else:
      features['isPowered'] = 0.0
    
    # Compute distance to partner
    if self.inEnemyTerritory(successor):
      distanceToAlly = self.getDistToPartner(successor)
      # distanceToAgent is always None for one of the agents (so they don't get stuck)
      if distanceToAlly != None:
        features['distanceToAlly'] = 1.0/distanceToAlly
    
    # Dead end heuristic
    actions = gameState.getLegalActions(self.index)
    if(len(actions) <= 2):
       features['deadEnd'] = 1.0
    else:
       features['deadEnd'] = 0.0

    # Stop heuristic
    if(action == Directions.STOP):
       features['stop'] = 1.0
    else:
       features['stop'] = 0.0

    return features

  # Returns all the heuristic features for the DEFEND tactic  
  def getFeaturesDefend(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    
    # Get own position
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # List invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]

    # Get number of invaders
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      enemyDist = [self.getMazeDistance(myPos, enemy.getPosition()) for enemy in invaders]
      #Find closest invader
      features['invaderDistance'] = min(enemyDist)

    # Compute distance to enemy
    distEnemy = self.enemyDist(successor)
    if(distEnemy <= 5):
      features['danger'] = 1
      if(distEnemy <= 1 and self.ScaredTimer(successor) > 0):
        features['danger'] = -1
    else:
      features['danger'] = 0  

    # Compute distance to partner
    if self.inEnemyTerritory(successor):
      distanceToAlly = self.getDistToPartner(successor)
      # distanceToAgent is always None for one of the agents (so they don't get stuck)
      if distanceToAlly != None:
        features['distanceToAlly'] = 1.0/distanceToAlly

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  # Returns all the heuristic features for the START tactic  
  def getFeaturesStart(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    # Get own position
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Compute distance to board centre
    dist = self.getMazeDistance(myPos, self.center)
    features['distToCenter'] = dist
    if myPos == self.center:
      features['atCenter'] = 1
    return features

  # Returns heuristic weightings for the ATTACK tactic
  def getWeightsAttack(self, gameState, action): 
    return {'successorScore': 800, 'distanceToFood': -10, 'danger': -1000,
            'pickupFood': 4000, 'capsuleDist': 700, 'stop': -1000, 'deadEnd': -200,
            'isPowered': 5000000, 'dropFood': 100, 'holdFood': -20,
            'distToAlly': -6000, 'pickupCapsule': 5000}
 
  # Returns heuristic weightings for the HUNT tactic
  def getWeightHunt(self, gameState, action):
  
    return {'numInvaders': -100, 'invaderDistance': -10, 'stop': -5000,
            'reverse': -5000, 'distanceToAlly': -2500} 
            
  # Returns heuristic weightings for the DEFEND tactic
  def getWeightsDefend(self, gameState, action):
    return {'numInvaders': -10000, 'invaderDistance': -500, 'stop': -5000,
            'reverse': -200, 'danger': 3000, 'distanceToAlly': -4000}

  # Returns heuristic weightings for the START tactic
  def getWeightsStart(self, gameState, action):
    return {'distToCenter': -1, 'atCenter': 1000}
  
# Agent that has a bias to moving around the top of the board
class TopAgent(MainAgent):

  def goToCenter(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    #0 to x-1 and x to width
    if self.red:
      x = x - 1
    # Set where the centre is
    self.center = (x, y)
    maxHeight = gameState.getWalls().height

    # Look for locations to move to that are not walls (favor top positions)
    for i in xrange(maxHeight - y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y + 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None

    # Find shortest distance to centre
    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos
    
# Agent that has a bias to moving around the bottom of the board
class BottomAgent(MainAgent):

  def goToCenter(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    #0 to x-1 and x to width
    if self.red:
      x = x - 1
    # Set where the centre is
    self.center = (x, y)
    
    # Look for locations to move to that are not walls (favor bot positions)
    for i in xrange(y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y - 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None

    # Find shortest distance to centre
    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos
