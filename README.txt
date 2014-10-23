To run the planner:
-------------------

Our planner is implimented in python and is located in the file 'myTeam.py'.
To run this planner, use the team select planner flag to select the team colour then the file name, so either:
	-r myTeam
	-b myTeam



Code documentation:
-------------------
Our planner creates two Pacman agents. One moves with a bias to the top of the game space and the other with a bias to the bottom. 

The planner uses four tactics - START, ATTACK, HUNT and DEFEND. Which tactic is implimented is dependent on the state of the game. These tactics will be further outlined and explained below.

To pick the best next move to make, all legal moves are considered. For each legal, a set of tactic dependent heuristics are used to caluclate an overall desireability score for that move. The heuristics consists of a number of features that are relivant to the tactic and their associated weightings of importance. Favourable features are given a positive weighting, while non-favourable features are given a negative rating. All feature/weighting products for a tactic are summed together and the result is that move's desirability score. The move with the highest desiability score is chosen as the best move to make, with draws decided at random.  

Due to the limited sight range of the game space, the enemy location is infered through iteratively filtering noisy distance data to infer the mostly likely position of the enemy. 



Planning approach:
------------------

The tactics that each Pacman agent can impliment are as follows:

1. START:
At the start of the game, each agent moves to the centre along the shortest path possible. Taking the shortest path improves the chance that our agents reach the centre first, where they can begin to attack and score quickly.
 
2. ATTACK:
Once reaching the centre of the game space, the agents diverge to attack, with one moving towards the top of the board and the other to the bottom. Having the agents diverge means that more area can be covered so more food can be eaten quicker. Each agent begins by moving towards the closest food in their respective work areas. 

One a food piece is eaten, the agent makes a decision to either return and deposit the food or to continue to the next closest food and eat that. As the agent eats more food and moves further away from its homeside, it becomes increasingly 'nervous' and is more likely to go back and deposit food rather than continue to venture further into enemy terriroty. 

If the attacking agent sees a ghost, it begins moving away from it, but still searches for more food. When the ghost begins to close in, the Pacman will begin to move directly away from the ghost, circling back to its own side for safety and to deposit food. If a power capsule is close by, the Pacman will each the capsule for defence. 

3. HUNT:
Each agent will continue to attack and eat the enemy's food until an enemy agent crosses over into our home territory. Once an enemy reaches our side, both agents immediately move back to the home side and move in the intercept the enemy agent.If multiple enemies are invading, the closest one is targeted fist. As the enemy position is noisey and inexact, it is infered from all previous data and the now defensive agents move in the general direction of the invading enemy. 

4. DEFEND:
Once the invading enemy is within line of sight, the defensive ghost agents swich to a defensive tactic, where they corner and kill the enemy Pacman. If the invading Pacman eats a power capsule, the ghosts still converge on the invader, but stay one space away for safety. Once the invader powers down, it can be killed instantly. 

Once all invading Pacman are killed, the defensive agents switch back to the START tactic and move back to the centre, repeating the entire process. 

5. Generic tactic considerations:
The ATTACK, HUNT and DEFEND tactics also share some common heuristic features. Each tactic penalises the two team mate agents from moving too close together. This means that they cover more area both when attacking - allowing more food to be eaten, and when defending - cornering the enemy more easily. This is also advantagous when hunting, as there is a greater chance the one of the agents will directly spot the invader. 

These tactics also penalise the STOP and REVERSE moves. There are very few (if any) situations where stopping is the best option, and reversing is only acceptable when reaching a dead end. 


Analysis of the planner:
------------------------
This planner is able to consistantly beat the baselineAgent on all maps. 

The main strengths of this planner is that it is extremely situationally aware due to the different tactics and heuristics implemented, and that it uses dynamic agents that can chance tactics when required. This allows the planner to make best use of both attack and defence, thus the planner being neamed an ALLROUNDER agent. 

However, this planner only ever looks one step ahead when planning. This is both a strength and a weakness. The advantage of only ever looking one step ahead is that more complex heuristics can be used to decide the best action. This allows for more nuance with decision making and makes the agent more situationally aware. The main downside to only planning one step ahead is that when attacking, agents can be corned more easily in dead ends, as it does not predict where an enemy agent will more next. However, as dead ends are highly penalised, this does not happen very often. 

While there is no direct communication between the agents on one team, the penalty for moving too close together allows for indirect communication. If further inter-agent communication was implimented, only one agent would be required to hunt down and kill and invader, allowing the other agent to continute to eat food. However, having both agents converging on the enemy builds in a redundency to kill the enemy, which is preferable in this case, as this planner is very good at initially scoring quickly and taking an early lead. 

When an invader is detected, both agents immediately begin to move back to the gome side to intersept it. While is seems wasteful for both agents to track down the invader as it means no food is collected in that time, is means that there is forced deposition of carried food. This will aid against enemies that make a last ditch effort to grab food at the end of the game, as it means that any hold food is deposited when it might otherwise not be. 

Finally, this planner does not deal with the likelihood that an enemy invader will eat a power capsule. As such defensive agents can not block access to the capsules and are purely reactive if one is eaten. This is partially compensated for by hovering around an invader even while it is powered up. 








