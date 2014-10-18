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
from util import nearestPoint

      
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent'):
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

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

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

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    ''' 
    You should change this in your own agent.
    '''

    return random.choice(actions)


class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  powerTimer = 0
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)


    if self.red:
      self.agentsOnTeam = gameState.getRedTeamIndices()
    else:
      self.agentsOnTeam = gameState.getBlueTeamIndices()


    self.foodNum = 0
    powerTimer = 0
    
  # Defect enemies
  def getEnemyPos(self, gameState):
    enemyPos = []
    for enemy in self.getOpponents(gameState):
      pos = gameState.getAgentPosition(enemy)
      if pos != None:
        enemyPos.append((enemy, pos))
    return enemyPos

  # Find closest enemy
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

  # Which side of the map are we on?
  def inEnemyTerritory(self, gameState):
    return gameState.getAgentState(self.index).isPacman

  # Is pacman powered?
  def isPowered(self):
    return self.powerTimer > 0

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


  def sideEval(self,gameState,otherPos):
    width, height = gameState.data.layout.width, gameState.data.layout.height
    if self.index%2==1:
      # red
      if otherPos[0]<width/(2):
        return -1.0
      else:
        return 1.0
    else:
      # blue
      if otherPos[0]>width/2:
        return -1.0
      else:
        return 1.0

  def getMyPos(self, gameState):
    return gameState.getAgentState(self.index).getPosition()
  
  def getDistToPartner(self, gameState):
    distanceToAgent = None
    agentsList = self.agentsOnTeam
    if self.index == self.agentsOnTeam[0]:
      otherAgentIndex = self.agentsOnTeam[1]
    else:
      otherAgentIndex = self.agentsOnTeam[0]
    # The below code is indented under 'else'
    # so that only 1 of the agents cares how close it is to the other
      myPos = self.getMyPos(gameState)
      otherPos = gameState.getAgentState(otherAgentIndex).getPosition()
      distanceToAgent = self.getMazeDistance(myPos, otherPos)
      if distanceToAgent == 0: distanceToAgent = 0.5
    return distanceToAgent
  
  
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    actions = gameState.getLegalActions(self.index)

    myPos = gameState.getAgentPosition(self.index)
    enemyPos = self.getEnemyPos(gameState)

    evaluateType = 'attack'

    if len(enemyPos) > 0:
      for enemy, pos in enemyPos:
        #If we detect an enemy and are on home turf we go after them and defend home
        if self.getMazeDistance(myPos, pos) < 10 and not self.inEnemyTerritory(gameState):
          evaluateType = 'defend'
          break

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a, evaluateType) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    

    
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

  def evaluate(self, gameState, action, evaluateType):
    """
    Computes a linear combination of features and feature weights
    """
    if evaluateType == 'attack':
      features = self.getFeaturesAttack(gameState, action)
      weights = self.getWeightsAttack(gameState, action)
    elif evaluateType == 'defend':
      features = self.getFeaturesDefend(gameState, action)
      weights = self.getWeightsDefend(gameState, action)

    return features * weights

##### Get Features Attacks
  def getFeaturesAttack(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    agentsList = self.agentsOnTeam
    width, height = gameState.data.layout.width, gameState.data.layout.height
    foodList = self.getFood(successor).asList()
    enemyFoodList = self.getFoodYouAreDefending(successor).asList()

    # Score
    features['successorScore'] = self.getScore(successor)

    # Dist to nearest food    
    if len(foodList) > 0:
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    #features['pickupFood'] = -len(foodList)
    if(len(foodList)>0):
      features['pickupFood'] = -len(foodList) + 100*self.getScore(successor)

    # Compute distance to enemy - need to add inference *****
    distEnemy = self.enemyDist(successor)
    if(distEnemy <= 4):
      if(not self.inEnemyTerritory):
        features['danger'] = -1
      else:
        features['danger'] = 1
    else:
      features['danger'] = 0  

    # Compute distance to capsule
    capsules = self.getCapsules(successor)
    if(len(capsules) > 0):
      minCapsuleDist = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
    else:
      minCapsuleDist = .1
    features['capsuleDist'] =  1.0/minCapsuleDist

    # Holding food
    if myPos in self.getFood(gameState).asList():
      self.foodNum += 1.0

    if self.side(gameState) == 0.0:
      self.foodNum = 0.0

    #features['holdFood'] = self.foodNum   
    features['holdFood'] = self.foodNum*(min([self.distancer.getDistance(myPos,p) for p in [(width/2,i) for i in range(1,height) if not gameState.hasWall(width/2,i)]]))*self.side(gameState)          

    # Dropping off food
    features['dropFood'] = self.foodNum*(self.side(gameState))

    # Is powered
    if(self.isPowered()):
      features['isPowered'] = powerTimer/POWERCAPSULETIME
    else:
      features['isPowered'] = 0.0
    
    # Compute distance to partner
    if self.inEnemyTerritory(successor):
      distanceToAlly = self.getDistToPartner(successor)
      # distanceToAgent is always None for one of the agents (so they don't get stuck)
      if distanceToAlly != None:
        features['distanceToAlly'] = 1.0/distanceToAlly

    # Dead End
    actions = gameState.getLegalActions(self.index)
    if(len(actions) <= 2):
       features['deadEnd'] = 1.0
    else:
       features['deadEnd'] = 0.0

    # Stop
    if(action == Directions.STOP):
       features['stop'] = 1.0
    else:
       features['stop'] = 0.0

    
    return features



##### Get Weights Attack
  def getWeightsAttack(self, gameState, action):
    return {'successorScore': 800, 'distanceToFood': -1, 'danger': -1000,
            'pickupFood': 4000, 'capsuleDist': 5000, 'stop': -100, 'deadEnd': -100,
            'isPowered': 5000000, 'dropFood': 100, 'holdFood': -100,
            'distToAlly': -4000}



##### Get Features Defend
  def getFeaturesDefend(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]

    # Find number of invaders
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      enemyDist = [self.getMazeDistance(myPos, enemy.getPosition()) for enemy in invaders]
      #Find closest invader
      features['invaderDistance'] = min(enemyDist)

    # Compute distance to enemy - need to add inference *****
    distEnemy = self.enemyDist(successor)
    if(distEnemy <= 10):
      features['danger'] = 1
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


##### Get Weights Defend
  def getWeightsDefend(self, gameState, action):
    return {'numInvaders': -10000, 'invaderDistance': -500, 'stop': -5000,
            'reverse': -200, 'danger': 3000, 'distanceToAlly': -4000}









    #return {'successorScore': 100, 'danger': -400, 'distanceToFood': -1,
    #        'stop': -2000, 'reverse': -20, 'capsuleDist': 3}


  

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Dead end
    if(len(action) <= 2):
      features['deadEnd'] = 1
    else:
      features['deadEnd'] = 0

    # Compute distance to enemy, if within 4 spaces, trigger 'danger' warning
    distEnemy = self.enemyDist(successor)
    if(distEnemy <= 4):
      features['danger'] = 1 * self.side(gameState)
    else:
      features['danger'] = 0    
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'deadEnd': -10, 'danger': -100}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}



    



    
      
