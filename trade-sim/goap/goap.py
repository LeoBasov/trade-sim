class Action:
    def __init__(self):
        self.prerequisites = []
        self.results = []
        self.desired_state = dict()
        self.cost = 1.0

        self.set_up()

    def set_up(self):
        pass

    def procedural_requirement(self):
        pass

class Agent:
    def __init__(self):
        self.state = dict()
        self.object = None
        self.world = None

    def set_up(self, object, world):
        pass

    def _grow_tree(self, action, actions):
        pass

    def plan(self, goal_plan, actions):
        for goal in goal_plan:
            for action in actions:
                if goal in action.results:
                    self._grow_tree(action, actions)