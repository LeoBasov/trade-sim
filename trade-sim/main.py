#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

class Product:
    def __init__(self, name, demand, availibility, production, capacity):
        self.name = name
        self.demand = demand # per  person elem [0, 1]
        self.availibility = availibility
        self.production = production # per  person elem [0, 1]
        self.capacity = capacity
        self.price = 0.0

        self.calc_price()

    def produce(self, number_workers):
        self.availibility = min(self.availibility + number_workers*self.production, self.capacity)

    def calc_price(self):
        if self.demand <= self.availibility:
            self.price = 0.0
        else:
            self.price = self.demand - self.availibility

    def buy(self, money, max_amount):
        amount = money/self.price
        amount = min(amount, max_amount, self.availibility)
        spent_money = amount*self.price

        self.availibility = max(0.0, self.availibility - amount)
        self.calc_price()

        return (amount, spent_money)

    def sell(self, amount):
        earned_money = amount*self.price

        self.availibility = min(self.capacity, self.availibility + amount)
        self.calc_price()

        return earned_money

class Planet:
    def __init__(self, popuplation, products = {}):
        self.popuplation = popuplation
        self.products = products

    def produce(self):
        for key, product in self.products.items():
            product.produce(self.popuplation)

def set_up_planet_A():
    silver = Product('silver', 0.8, 11.0, 1.1, 1e+6)
    gold = Product('gold', 0.9, 0.0, 0.0, 1e+6)
    products = {silver.name : silver, gold.name : gold}

    return Planet(10000, products)

def set_up_planet_B():
    silver = Product('silver', 0.8, 0.0, 0.1, 1e+6)
    gold = Product('gold', 0.9, 11.0, 1.5, 1e+6)
    products = {silver.name : silver, gold.name : gold}

    return Planet(10000, products)

if __name__ == '__main__':
    max_iter = 100
    planet_A = set_up_planet_A()
    planet_B = set_up_planet_B()

    print(80*'=')
    print("TRADE SIMULATION")
    print(80*'-')

    print("NUMBER ITERATIIONS:", max_iter)
    print(80*'-')

    for i in range(max_iter):
        planet_A.produce()
        planet_B.produce()

        print(i, "/", max_iter, "price_sell_in_A", planet_A.products['silver'].availibility, "price_sell_in_B", planet_B.products['silver'].availibility)

    print(80*'=')
