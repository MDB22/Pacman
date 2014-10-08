(define (domain pacman)
  (:requirements :typing)
  (:types pos)
  ;; Define the problem facts
  ;; "?" denotes a variable\, "-" denotes a type
  (:predicates  (At ?p - pos)
                (FoodAt ?p - pos)
                (Adjacent ?pos1 ?pos2 - pos)
  )
  ;; Define the actions
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Adjacent ?posCurr ?posNext)
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )
                       (not  (FoodAt ?posNext) )
                   )
   )
)