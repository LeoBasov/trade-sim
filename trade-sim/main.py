#!/usr/bin/env python3

import treelib as tr

station1 = "station 1"
station2 = "station 2"

merchant1 = "merchant 1"

good_a = "good_a"

action_move = "move"
action_buy = "buy"
action_sell = "sell"
action_none = "none"

class World:
    def __init__(self):
        self.stations = dict()
        self.merchants = dict()
        
    def add_station(self, name):
        station = Station(name)
        self.stations[name] = station
        print("added station:", name)
        
    def add_merchant(self, name, current_station):
        merchant = Merchant(name, current_station)
        self.merchants[name] = merchant
        print("added merchant:", name, "to station:", current_station)
        
    def build_trees(self, max_depth):
        print("building trees")
        
        for name, merchant in self.merchants.items():
            merchant.build_tree(self.stations, max_depth)

class Station:
    def __init__(self, name):
        self.name = name
        self.stock = dict()
        self.sell_prizes = dict()
        self.buy_prizes = dict()
        
    def add_good(self, good, number, sell_prize, buy_prize):
        self.stock[good] = number
        self.sell_prizes[good] = sell_prize
        self.buy_prizes[good] = buy_prize
        
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
        
class Tree:
    def __init__(self):
        self.levels = []
        
    def clear(self):
        self.levels = []
        
    def build(self, merchant, stations, max_depth):
        last_level = 0
        
        self.clear()
        self._add_root(merchant)
        
        while max_depth > len(self.levels) and last_level != len(self.levels):
            print("build new level")
            last_level = len(self.levels)
            self._add_level(stations)
        
    def _add_root(self, merchant):
        root = Node()
        
        root.money = merchant.money
        root.stock = merchant.stock
        root.current_station = merchant.current_station
        
        self.levels.append([root])
        
    def _add_level(self, stations):
        new_level = []
        
        for node in self.levels[-1]:
            station = stations[node.current_station]
            
            # sell
            for good, value in node.stock.items():
                if value > 0:
                    new_level.append(self._add_sell_node(node, good, station))
            
            # buy
            for good, prize in station.sell_prizes.items():
                if prize <= node.money:
                    new_level.append(self._add_buy_node(node, good, station))
            
            # travel
            pass
        
        if len(new_level):
            self.levels.append(new_level)
            
    def _add_sell_node(self, node, good, station):
        print("adding sell node")
        
        _node = Node()
        _node.action = action_sell
        _node.money = node.money + node.stock[good] * station.buy_prizes[good]
        _node.stock = node.stock
        
        _node.stock[good] = 0
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain + node.stock[good] * station.buy_prizes[good]
        _node.parent = node
        _node.children = []
        _node.depth = node.depth + 1
        
        node.children.append(_node)
        
        return _node
        
    def _add_buy_node(self, node, good, station):
        print("adding buy node")
        
        _node = Node()
        n_bought = node.money % station.sell_prizes[good]
        _node.action = action_buy
        _node.money = node.money - n_bought * station.sell_prizes[good]
        _node.stock = node.stock
        
        _node.stock[good] += n_bought
        
        _node.current_station = node.current_station
        _node.total_gain = node.total_gain - n_bought * station.sell_prizes[good]
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
    world.stations[station2].add_good("good_a", 0, 11, 11)
    

def set_up_merchants(world):
    print("setting up merchants")
    
    world.add_merchant(merchant1, station1)
    
    world.merchants[merchant1].money = 10
    world.merchants[merchant1].stock[good_a] = 0
    
def visualize_tree(merchant):
    tree = tr.Tree()
    
    for level in merchant.tree.levels:
        for node in level:
            if node.parent == None:
                tree.create_node("root " + str(node.money), node)
            else:
                tree.create_node(node.action + " " + str(node.money), node, parent=node.parent)

    #tree.create_node("Harry", "harry", parent="1")  # No parent means its the root node
    #tree.create_node("Jane",  "jane"   , parent="harry")
    #tree.create_node("Bill",  "bill"   , parent="harry")
    #tree.create_node("Diane", "diane"  , parent="jane")
    #tree.create_node("Mary",  "mary"   , parent="diane")
    #tree.create_node("Mark",  "mark"   , parent="jane")

    tree.show()

if __name__ == '__main__':
    world = World()
    max_depth = 3
    
    set_up_station(world)
    set_up_merchants(world)
    
    world.build_trees(max_depth)
    
    visualize_tree(world.merchants[merchant1])
    
    print("done")
