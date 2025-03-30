#!/usr/bin/env python3

import copy
import graphviz
import math

station1 = "station 1"
station2 = "station 2"

merchant1 = "merchant 1"
merchant2 = "merchant 2"

good_a = "good_a"

action_move = "move"
action_buy = "buy"
action_sell = "sell"
action_none = "none"

travel_cost = 2
do_nothing_cost = 1

class World:
    def __init__(self):
        self.stations = dict()
        self.merchants = dict()
        self.max_depth = 7
        
    def add_station(self, name):
        station = Station(name)
        self.stations[name] = station
        print("added station:", name)
        
    def add_merchant(self, name, current_station):
        merchant = Merchant(name, self.stations[current_station])
        self.merchants[name] = merchant
        print("added merchant:", name, "to station:", current_station)
        
    def build_trees(self):
        print("building trees")
        
        for name, merchant in self.merchants.items():
            merchant.build_tree(self.stations, self.max_depth)

        for name, station in self.stations.items():
            station.has_changed = False

    def process(self):
        for name, station in self.stations.items():
            if station.has_changed:
                self.build_trees()

        for name, merchant in self.merchants.items():
            merchant.process()

class Station:
    def __init__(self, name):
        self.name = name
        self.stock = dict()
        self.sell_prizes = dict()
        self.buy_prizes = dict()
        self.has_changed = False
        
    def add_good(self, good, number, sell_prize, buy_prize):
        self.stock[good] = number
        self.sell_prizes[good] = sell_prize
        self.buy_prizes[good] = buy_prize
        self.has_changed = True
        
        print("added good to station", self.name)
        print("    name:", good, "number:", number, "sell_prize:", sell_prize, "buy_prize:", buy_prize)
        
class Merchant:
    def __init__(self, name, current_station):
        self.name = name
        self.current_station = current_station
        self.money = 0
        self.stock = dict()
        self.tree = Tree()
        
    def build_tree(self, stations, max_depth):
        self.tree.build(self, stations, max_depth)

    def process(self):
        next_step = self.tree.get_next_step()
        
        if next_step == None:
            raise Exception("next_step is None")
        elif next_step.action == action_move:
            print(self.name + " processsing action " + action_move + " form " + self.current_station.name + " to " + next_step.current_station.name)
            self.current_station = next_step.current_station
        elif next_step.action == action_buy:
            for good, value in self.stock.items():
                if value != next_step.stock[good]:
                    amount = next_step.stock[good] - value
                    print(self.name + " processsing action " + action_buy + " of " + good + " amout " + str(amount))

        elif next_step.action == action_sell:
            print(self.name + " processsing action " + action_sell)
        elif next_step.action == action_none:
            print(self.name + " processsing action " + action_none)

class Tree:
    def __init__(self):
        self.levels = []
        self.best_path = []
        self.current_step = 1

    def get_next_step(self):
        if self.current_step < len(self.best_path):
            self.current_step += 1
            return self.best_path[self.current_step - 1]
        else:
            return None
        
    def clear(self):
        self.levels = []
        self.best_path = []
        self.current_step = 1
        
    def build(self, merchant, stations, max_depth):
        last_level = 0
        
        self.clear()
        self._add_root(merchant)
        
        while max_depth > len(self.levels) and last_level != len(self.levels):
            print("build new level")
            last_level = len(self.levels)
            self._add_level(stations)

        self.best_path = self.get_best_path_full()
            
    def get_best_path(self):
        max_gain = 0
        best_node = self.levels[0][0]
        
        for level in self.levels:
            for node in level:
                if node.total_gain > max_gain:
                    max_gain = node.total_gain 
                    best_node = node
                    
        if best_node.parent == None:
            return [best_node]
        else:
            nodes = [best_node]
            
            while nodes[-1].parent != None:
                nodes.append(nodes[-1].parent)
                
        return list(reversed(nodes))
    
    def get_best_path_full(self):
        max_gain = -10000
        best_node = self.levels[0][0]
        
        for node in self.levels[-1]:
            if node.total_gain > max_gain:
                max_gain = node.total_gain 
                best_node = node
                    
        if best_node.parent == None:
            return [best_node]
        else:
            nodes = [best_node]
            
            while nodes[-1].parent != None:
                nodes.append(nodes[-1].parent)
                
        return list(reversed(nodes))
        
    def _add_root(self, merchant):
        root = Node()
        
        root.money = merchant.money
        root.stock = merchant.stock
        root.current_station = merchant.current_station
        
        self.levels.append([root])
        
    def _add_level(self, stations):
        new_level = []
        
        for node in self.levels[-1]:
            station = node.current_station
            
            # sell
            for good, value in node.stock.items():
                if value > 0:
                    new_level.append(self._add_sell_node(node, good, station))
            
            # buy
            for good, prize in station.sell_prizes.items():
                if prize <= node.money:
                    new_level.append(self._add_buy_node(node, good, station))
            
            # travel
            for other_station_name, other_station in stations.items():
                if other_station_name != node.current_station and node.money >= travel_cost:
                    new_level.append(self._add_travel_node(node, other_station))
                    
            # do nothing
            if node.money >= do_nothing_cost:
                new_level.append(self._add_do_nothing_node(node))
        
        if len(new_level):
            self.levels.append(new_level)
            
    def _add_sell_node(self, node, good, station):    
        _node = Node()
        _node.action = action_sell
        _node.money = node.money + node.stock[good] * station.buy_prizes[good]
        _node.stock = copy.deepcopy(node.stock)
        
        _node.stock[good] = 0
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain + node.stock[good] * station.buy_prizes[good]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + 1
        
        node.children.append(_node)
        
        return _node
        
    def _add_buy_node(self, node, good, station):   
        _node = Node()
        n_bought = math.floor(node.money / station.sell_prizes[good])
        _node.action = action_buy
        _node.money = node.money - n_bought * station.sell_prizes[good]
        _node.stock = copy.deepcopy(node.stock)
        
        _node.stock[good] += n_bought
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain - n_bought * station.sell_prizes[good]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + 1
        
        node.children.append(_node)
        
        return _node
    
    def _add_travel_node(self, node, new_station):   
        _node = Node()
        _node.action = action_move
        _node.money = node.money - travel_cost
        _node.stock = copy.deepcopy(node.stock)
        _node.current_station = new_station
        _node.total_gain = node.total_gain - travel_cost
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + 1
        
        node.children.append(_node)
        
        return _node
    
    def _add_do_nothing_node(self, node):   
        _node = Node()
        _node.action = action_none
        _node.money = node.money - do_nothing_cost
        _node.stock = copy.deepcopy(node.stock)
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain - do_nothing_cost
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + 1
        
        node.children.append(_node)
        
        return _node
        
class Node:
    def __init__(self):
        self.action = action_none
        self.money = 0
        self.stock = dict()
        self.current_station = ""
        self.total_gain = 0
        self.parent = None
        self.children = []
        self.depth = 0
        
def set_up_station(world):
    print("setting up stations")
    
    world.add_station(station1)
    world.add_station(station2)
    
    world.stations[station1].add_good("good_a", 0, 9, 9)
    world.stations[station2].add_good("good_a", 0, 14, 14)
    

def set_up_merchants(world):
    print("setting up merchants")
    
    world.add_merchant(merchant1, station1)
    world.add_merchant(merchant2, station2)
    
    world.merchants[merchant1].money = 11
    world.merchants[merchant1].stock[good_a] = 0

    world.merchants[merchant2].money = 11
    world.merchants[merchant2].stock[good_a] = 0
    
def visualize_tree_graphviz(merchant):    
    dot = graphviz.Digraph('tree_graph', comment='tree graph')
    
    for level in merchant.tree.levels:
        for node in level:
            if node.parent == None:
                dot.node(str(node), "root money: " + str(node.money) + " gain: " + str(node.total_gain))
            else:
                dot.node(str(node), node.action + " money: " + str(node.money) + " gain: " + str(node.total_gain))
                dot.edge(str(node.parent), str(node))
    
    dot.render(directory='doctest-output', view=True) 
    
def visualize_best_path(merchant):  
    best_path = merchant.tree.get_best_path_full()
    dot = graphviz.Digraph('tree_graph', comment='tree graph')
    
    for node in best_path:
        if node.parent == None:
            dot.node(str(node), "root money: " + str(node.money) + " gain: " + str(node.total_gain))
        else:
            dot.node(str(node), node.action + " money: " + str(node.money) + " gain: " + str(node.total_gain))
            dot.edge(str(node.parent), str(node))
    
    dot.render(directory='doctest-output', view=True)

if __name__ == '__main__':
    world = World()
    
    set_up_station(world)
    set_up_merchants(world)

    for _ in range(6):
        world.process()
    
    #visualize_tree_graphviz(world.merchants[merchant1])
    visualize_best_path(world.merchants[merchant1])
    #visualize_best_path(world.merchants[merchant2])
    
    print("done")

