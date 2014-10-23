(define (domain ghost)
  (:requirements :typing :conditional-effects)
  (:types pos)				;; x-y positions are treated as a single variable
  (:predicates  (At ?p - pos) 		;; Position of Ghost
                (PacmanAt ?p - pos)	;; Position of Pacman
                (Adjacent ?pos1 ?pos2 - pos)	;; Whether two positions are connected
                (Scared)		;; Whether Ghost is scared of Pacman
  )
  ;; Ghost is only able to move to the next position when its current position
  ;; is posCurr, and its next position is connected to its current position
  ;; When Ghost moves, its position changes, and if he is not scared, eats a Pacman
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Adjacent ?posCurr ?posNext)
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )
                       (when (not (Scared)) (not  (PacmanAt ?posNext) ))
                   )
   )
)