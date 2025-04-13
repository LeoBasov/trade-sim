import sys

sys.path.append('./trade-sim/')

import goap as gp
from enum import Enum

States = Enum('States', [('MONEY', 1), ('GOODS', 2)])

class Goal:
    def __init__(self):
        pass

    def check(self, state_begin, state_end):
        return state_end[States.MONEY] > state_begin[States.MONEY]
    
class ActionBuy(gp.Action):
    def __init__(self):
        self.name = "buy"
        self.value = 9

    def check_preconditions(self, state):
        return state[States.MONEY] > self.value

    def apply_results(self, state):
        state[States.MONEY] -= self.value
        state[States.GOODS] += 1

class ActionSell(gp.Action):
    def __init__(self):
        self.name = "buy"
        self.value = 14

    def check_preconditions(self, state):
        return state[States.GOODS] > 0

    def apply_results(self, state):
        state[States.MONEY] += self.value
        state[States.GOODS] -= 1
    
class GoapAgent:
    def __init__(self):
        self.goal = Goal()
        self.state = {States.MONEY : 100, States.GOODS : 0}
        self.actions = [ActionBuy(), ActionSell()]
        self.tree = gp.Tree()


    def build_tree(self):
        self.tree.build(self.actions, self.state)

if __name__ == '__main__':
    agent = GoapAgent()

    agent.build_tree()

    print("done")