import sys

sys.path.append('./trade-sim/')

import goap as gp

class ActionSell(gp.Action):
    def set_up(self):
        self.results.append("make_money")

class World:
    def __init__(self):
        pass

class Object:
    def __init__(self):
        pass

if __name__ == '__main__':
    goal_set = ["make_money"]
    actions = [ActionSell()]
    world = World()
    object = Object()
    agent = gp.Agent()

    agent.set_up(object, world)
    agent.plan(goal_set, actions)

    print("done")