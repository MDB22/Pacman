(define (domain pacman)
  (:requirements :typing :conditional-effects)
  (:types pos)				;; x-y positions are treated as a single variable
  (:predicates  (At ?p - pos) 		;; Position of Pacman
                (FoodAt ?p - pos)	;; Position of food
                (CapsuleAt ?p - pos)	;; Position of capsules
                (GhostAt ?p - pos)	;; Position of Ghosts
                (Adjacent ?pos1 ?pos2 - pos)	;; Whether two positions are connected
                (Powered)		;; Whether Pacman has eaten the capsule
  )
  ;; Pacman is only able to move to the next position when his current position
  ;; is posCurr, and his next position is connected to his current position
  ;; When Pacman moves, his position changes, he eats any food or capsules at
  ;; his new position, and if he is powered, eats a Ghost
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Adjacent ?posCurr ?posNext)
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )
                       (not  (FoodAt ?posNext) )
                       (not  (CapsuleAt ?posNext) )
                       (when (Powered) (not (GhostAt ?posNext)))
                   )
   )
)