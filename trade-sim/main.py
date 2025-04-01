#!/usr/bin/env python3

import copy
import graphviz
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

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
    def __init__(self, max_depth):
        self.stations = dict()
        self.merchants = dict()
        self.max_depth = max_depth
        
    def add_station(self, name):
        station = Station(name)
        self.stations[name] = station
        print("added station:", name)
        
    def add_merchant(self, name, current_station, money):
        merchant = Merchant(name, self.stations[current_station])
        merchant.money = money
        self.merchants[name] = merchant
        print("added merchant:", name, "to station:", current_station)
        
    def build_trees(self, path='interpolated'):
        print("building trees")
        
        for name, merchant in self.merchants.items():
            merchant.build_tree(self.stations, self.max_depth, path)

        for name, station in self.stations.items():
            station.has_changed = False

    def process(self):
        for name, station in self.stations.items():
            if station.has_changed:
                self.build_trees()

        for name, merchant in self.merchants.items():
            if not merchant.process():
                self.update_stations()
                break

    def update_stations(self):
        for name, station in self.stations.items():
            station.update()

class Station:
    def __init__(self, name):
        self.name = name
        self.stock = dict()
        self.sell_prizes = dict()
        self.buy_prizes = dict()
        self.money_made = dict()
        self.has_changed = False

    def update(self):
        self.has_changed = True

        """for good, value in self.money_made.items():
            if sum(value) < 0.0:
                self.buy_prizes[good] = int(0.99 * self.buy_prizes[good])
                #self.sell_prizes[good] = int(1.1 * self.sell_prizes[good])

            if sum(value) > 0.0:
                #self.buy_prizes[good] = int(1.1 * self.buy_prizes[good])
                self.sell_prizes[good] = int(1.01 * self.sell_prizes[good])"""

        print("updating station")
        
    def add_good(self, good, number, sell_prize, buy_prize):
        self.stock[good] = number
        self.sell_prizes[good] = sell_prize
        self.buy_prizes[good] = buy_prize
        self.money_made[good] = []
        self.has_changed = True
        
        print("added good to station", self.name)
        print("    name:", good, "number:", number, "sell_prize:", sell_prize, "buy_prize:", buy_prize)

    def buy(self, merchant, good, amount):
        merchant.money += self.buy_prizes[good] * amount
        merchant.stock[good] -= amount
        self.money_made[good].append(-self.buy_prizes[good] * amount)

    def sell(self, merchant, good, amount):
        merchant.money -= self.sell_prizes[good] * amount
        merchant.stock[good] += amount
        self.money_made[good].append(self.sell_prizes[good] * amount)
        
class Merchant:
    def __init__(self, name, current_station):
        self.name = name
        self.current_station = current_station
        self.money = 0
        self.stock = dict()
        self.capacity = dict()
        self.tree = Tree()

    def add_good(self, good, amount, capacity):
        self.stock[good] = amount
        self.capacity[good] = capacity
        
    def build_tree(self, stations, max_depth, path):
        self.tree.build(self, stations, max_depth, path)

    def process(self):
        next_step = self.tree.get_next_step()

        if next_step == None:
            return False
        
        print(self.name, "money at start:", self.money)
        
        if next_step == None:
            raise Exception("next_step is None")
        elif next_step.action == action_move:
            print(self.name + " processsing action " + action_move + " form " + self.current_station.name + " to " + next_step.current_station.name)
            self.current_station = next_step.current_station
            self.money -= travel_cost
        elif next_step.action == action_buy:
            for good, value in self.stock.items():
                if value != next_step.stock[good]:
                    amount = next_step.stock[good] - value
                    self.current_station.sell(self, good, amount)
                    print(self.name + " processsing action " + action_buy + " of " + good + " amout " + str(amount))

        elif next_step.action == action_sell:
            for good, value in self.stock.items():
                if value != next_step.stock[good]:
                    amount = value - next_step.stock[good]
                    self.current_station.buy(self, good, amount)
                    print(self.name + " processsing action " + action_sell + " of " + good + " amout " + str(amount))

        elif next_step.action == action_none:
            self.money -= do_nothing_cost
            print(self.name + " processsing action " + action_none)

        print(self.name, "money at end:", self.money)

        return True

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
        
    def build(self, merchant, stations, max_depth, path):
        last_level = 0
        
        self.clear()
        self._add_root(merchant)
        
        while max_depth > len(self.levels) and last_level != len(self.levels):
            last_level = len(self.levels)
            self._add_level(stations)

        print("getting best path")
        
        if path == 'best':
            self.best_path = self.get_best_path()
        elif path == 'full':
            self.best_path = self.get_best_path_full()
        elif path == 'interpolated':
            self.best_path = self.get_best_path_interpolated()
            
    def get_best_path(self):
        max_gain = 0
        best_node = self.levels[0][0]
        
        for level in self.levels:
            for node in level:
                if node.total_gain[-1] > max_gain:
                    max_gain = node.total_gain[-1] 
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
            if node.total_gain[-1] > max_gain:
                max_gain = node.total_gain[-1] 
                best_node = node
                    
        if best_node.parent == None:
            return [best_node]
        else:
            nodes = [best_node]
            
            while nodes[-1].parent != None:
                nodes.append(nodes[-1].parent)
                
        return list(reversed(nodes))
    
    def get_best_path_interpolated(self):
        max_slope = -1e-16
        best_node = None

        for node in self.levels[-1]:
            res = stats.linregress(node.depth, node.total_gain)

            if res.slope > max_slope:
                max_slope = res.slope
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
        root.capacity = copy.deepcopy(merchant.capacity)
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
                if prize <= node.money and (node.capacity[good] - node.stock[good]) > 0:
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
        _node.capacity = copy.deepcopy(node.capacity)
        
        _node.stock[good] = 0
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain + [node.total_gain[-1] + node.stock[good] * station.buy_prizes[good]]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + [node.depth[-1] + 1]
        
        node.children.append(_node)
        
        return _node
        
    def _add_buy_node(self, node, good, station):   
        _node = Node()
        n_bought = min(math.floor(node.money / station.sell_prizes[good]), node.capacity[good] - node.stock[good])
        _node.action = action_buy
        _node.money = node.money - n_bought * station.sell_prizes[good]
        _node.capacity = copy.deepcopy(node.capacity)
        _node.stock = copy.deepcopy(node.stock)
        
        _node.stock[good] += n_bought
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain + [node.total_gain[-1] - n_bought * station.sell_prizes[good]]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + [node.depth[-1] + 1]
        
        node.children.append(_node)
        
        return _node
    
    def _add_travel_node(self, node, new_station):   
        _node = Node()
        _node.action = action_move
        _node.money = node.money - travel_cost
        _node.stock = copy.deepcopy(node.stock)
        _node.capacity = copy.deepcopy(node.capacity)
        _node.current_station = new_station
        _node.total_gain = node.total_gain + [node.total_gain[-1] - travel_cost]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + [node.depth[-1] + 1]
        
        node.children.append(_node)
        
        return _node
    
    def _add_do_nothing_node(self, node):   
        _node = Node()
        _node.action = action_none
        _node.money = node.money - do_nothing_cost
        _node.stock = copy.deepcopy(node.stock)
        _node.capacity = copy.deepcopy(node.capacity)
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain + [node.total_gain[-1] - do_nothing_cost]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + [node.depth[-1] + 1]
        
        node.children.append(_node)
        
        return _node
        
class Node:
    def __init__(self):
        self.action = action_none
        self.money = 0
        self.stock = dict()
        self.capacity = dict()
        self.current_station = ""
        self.total_gain = [0]
        self.parent = None
        self.children = []
        self.depth = [0]
        
def set_up_station(world):
    print("setting up stations")
    
    world.add_station(station1)
    world.add_station(station2)
    
    world.stations[station1].add_good("good_a", 0, 9, 9)
    world.stations[station2].add_good("good_a", 0, 14, 14)
    

def set_up_merchants(world):
    print("setting up merchants")
    
    world.add_merchant(merchant1, station1, 100)
    #world.add_merchant(merchant2, station2, 100)

    world.merchants[merchant1].add_good(good_a, 0, 10)
    #world.merchants[merchant2].add_good(good_a, 0, 10)
    
def visualize_tree_graphviz(merchant):    
    dot = graphviz.Digraph('tree_graph', comment=merchant.name)
    
    for level in merchant.tree.levels:
        for node in level:
            if node.parent == None:
                dot.node(str(node), "root money: " + str(node.money) + " gain: " + str(node.total_gain))
            else:
                dot.node(str(node), node.action + " money: " + str(node.money) + " gain: " + str(node.total_gain))
                dot.edge(str(node.parent), str(node))
    
    dot.render(directory='doctest-output', view=True) 
    
def visualize_best_path(merchant):  
    dot = graphviz.Digraph(merchant.name, comment=merchant.name)
    
    for node in merchant.tree.best_path:
        if node.parent == None:
            dot.node(str(node), "root money: " + str(node.money) + " gain: " + str(node.total_gain[-1]))
        else:
            dot.node(str(node), node.action + " money: " + str(node.money) + " gain: " + str(node.total_gain[-1]))
            dot.edge(str(node.parent), str(node))
    
    dot.render(directory="output_" + merchant.name, view=True)

def visualize_stations(world):
    legend = []

    for name, station in world.stations.items():
        for good, money in station.money_made.items():
            legend.append(name + " " + good)
            money_full = [money[0]]

            for i in range(1, len(money)):
                money_full.append(money_full[i - 1] + money[i])

            plt.plot(money_full)

    plt.legend(legend)
    plt.show()

if __name__ == '__main__':
    max_depth = 5
    world = World(max_depth)
    
    set_up_station(world)
    set_up_merchants(world)

    for i in range(19):
        world.process()

    visualize_best_path(world.merchants[merchant1])
    #visualize_best_path(world.merchants[merchant2])
    #visualize_stations(world)
    
    print("done")

