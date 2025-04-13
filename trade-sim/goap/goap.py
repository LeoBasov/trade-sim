from copy import deepcopy

class State:
    pass

class Action:
    def __init__(self, name):
        self.name = name

    def check_preconditions(self, state):
        pass

    def get_cost(self, state):
        pass

    def apply_results(self, state):
        pass

    def __str__(self):
        return self.name
    
    def __eq__(self, value):
        return self.name == value.name

class Goal:
    def __init__(self):
        pass

    def check(self, state_begin, state_end):
        pass

class Leaf:
    def __init__(self, _parent, _action, _state):
        self.parent = _parent
        self.action = _action
        self.state = deepcopy(_state) # state after the action was performed
        self.children = []
        self.path_actions = []
        self.cost = 0

        if _parent != None:
            self.path_actions = deepcopy(_parent.path_actions)
            self.path_actions.append(_action)
            self.cost = _parent.cost
        else:
            self.path_actions = [_action,]

        self.cost += self.action.get_cost(self.state)
        self.action.apply_results(self.state)

    def __str__(self):
        s = "action: " + self.action.name + " state: " + str(self.state)

        return s

class Tree:
    def __init__(self):
        self.roots = []
        self.leafs = []

    def build(self, actions, state):
        self.roots = []

        for action in actions:
            if action.check_preconditions(state):
                print("adding root")
                self.roots.append(Leaf(None, action, state))
                self.leafs.append(Leaf(None, action, state))

        for leaf in self.roots:
            self.add_children(leaf, actions)

    def get_plan(self, goal, state):
        plan = []
        goal_leaf = self.find_goal_leaf(goal, state)

        if goal_leaf != None:
            leaf = goal_leaf

            while(leaf.parent != None):
                plan.append(deepcopy(leaf.action))
                leaf = leaf.parent

            plan.append(deepcopy(leaf.action))

        return [p for p in reversed(plan)]

    def find_goal_leaf(self, goal, state):
        goal_leaf = None
        min_cost = 1e6

        for leaf in self.leafs:
            if goal.check(state, leaf.state) and leaf.cost < min_cost:
                min_cost = leaf.cost
                goal_leaf = leaf

        return goal_leaf

    def add_children(self, leaf, actions):
        for action in actions:
            if action in leaf.path_actions:
                print("dublicate actions, next")
            elif action.check_preconditions(leaf.state):
                print("adding child")
                leaf.children.append(Leaf(leaf, action, leaf.state))
                self.leafs.append(Leaf(leaf, action, leaf.state))
            else:
                print("preconditons dont apply")

        for child in leaf.children:
            self.add_children(child, actions)