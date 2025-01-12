import pprint
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.style as style
import sys
import os

# --- Why this is needed? ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import bidask as ba

class OrderBook():
    """
    A class that keeps track of all bids and asks.

    Attributes:
        orders (dataframe) : Tracks all bids and asks
    """

    # Dataframe columns: Unit, Price, Type, User_id
    col_names = [
        'Unit',
        'Price',
        'Type',
        'User'
    ]

    def __init__(self):
        # Create an empty orderbook
        self.orders = pd.DataFrame(columns=self.col_names)

    def add_bid(
        self,
        unit,
        price,
        user_id
    ):
        """
        Add one bid to the orderbook.

        Args:
            unit (int): units for this bid 

            price (float): bid price

            user_id (int): corresponding user id
        """
        new_bid = pd.DataFrame([[unit, price, 'bid', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    def add_bid_csv(
        self,
        input_path
    ):
        """
        Add a collection of bids to the orderbook.

        Args:
            input_path (str): path to the .csv file.
            Unit, Price, User
        """
        new_bid = pd.read_csv(input_path, header=None, names=["Unit", "Price", "User"], sep=',')
        new_bid["Type"] = "bid"
        new_bid = new_bid[["Unit", "Price", "Type", "User"]]

        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    def add_ask(
        self,
        unit,
        price,
        user_id
    ):
        """
        Add one ask to the orderbook.

        Args:
            unit (int): units for this ask 

            price (float): ask price

            user_id (int): corresponding user id
        """  
        
        new_ask = pd.DataFrame([[unit, price, 'ask', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_ask], ignore_index=True)

    def add_ask_csv(
        self,
        input_path
    ):
        """
        Add a collection of asks to the orderbook.

        Args:
            input_path (str): path to the .csv file.
            Unit, Price, User
        """
        new_bid = pd.read_csv(input_path, header=None, names=["Unit", "Price", "User"], sep=',')
        new_bid["Type"] = "ask"
        new_bid = new_bid[["Unit", "Price", "Type", "User"]]

        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    def display(self, scale=0):
        """
        Args:
            scale (int, default=0): 
                0: both bids and asks; 
                1: bids; 2: asks

        Returns:
            dataframe: the orderbook
        """

        if scale == 0:
            return self.orders
        elif scale == 1:
            return [self.orders['Type'] == 'bid']
        else:
            return self.orders[self.orders['Type'] == 'ask']

    def get_bids(self):
        """
        Extract all bids, sorted in non-ascending order by prices.
        Bids of the same prices are merged.

        Returns:
            numpy array: [[bid_price, units] ...]
        """
        bids = self.orders[self.orders['Type'] == 'bid']
        bid_curves = bids.groupby('Price')['Unit'].sum().reset_index()

        return bid_curves.sort_values(by=['Price'], ascending=False).to_numpy()
    
    def get_asks(self):
        """
        Extract all asks, sorted in non-descending order by prices.
        Asks of the same prices are merged.

        Returns:
            numpy array: [[ask_price, units] ...]
        """

        asks = self.orders[self.orders['Type'] == 'ask']
        ask_curves = asks.groupby('Price')['Unit'].sum().reset_index()

        return ask_curves.sort_values(by=['Price']).to_numpy()

    def _get_demand_curve(self):
        """
        Extract all bids, sorted in non-ascending order by prices.
        Bids of the same prices are merged.

        Returns:
            numpy array: [[bid_price, units] ...]
        """

        bids = self.orders[self.orders['Type'] == 'bid']
        bid_curves = bids.groupby('Price')['Unit'].sum().reset_index()

        return bid_curves.sort_values(by=['Price'], ascending=False).to_numpy()

    def _get_supply_curve(self):
        """
        Extract all asks, sorted in non-descending order by prices.
        Asks of the same prices are merged.

        Returns:
            numpy array: [[ask_price, units] ...]
        """

        asks = self.orders[self.orders['Type'] == 'ask']
        ask_curves = asks.groupby('Price')['Unit'].sum().reset_index()

        return ask_curves.sort_values(by=['Price']).to_numpy()
        

    def plot_curves(self):
        """
        Plot the supply & demand curve as two step functions.
        """

        demand_curve = self._get_demand_curve().tolist()
        supply_curve = self._get_supply_curve().tolist()

        demand_units = [unit for price, unit in demand_curve]
        demand_prices = [price for price, unit in demand_curve]
        cumulative_demand = [0] + list(ba.cumu_sum(demand_units))
    
        supply_units = [unit for price, unit in supply_curve]
        supply_prices = [price for price, unit in supply_curve]
        cumulative_supply = [0] + list(ba.cumu_sum(supply_units))
    
        demand_prices = demand_prices + [demand_prices[-1]]
        supply_prices = supply_prices + [supply_prices[-1]]

        plt.figure(figsize=(7, 4), dpi=450)
        
        plt.step(cumulative_demand, demand_prices, label='Demand', where='post', 
                 color='#1f77b4', linewidth=2.5, alpha=0.8)
        plt.step(cumulative_supply, supply_prices, label='Supply', where='post', 
                 color='#ff7f0e', linewidth=2.5, alpha=0.8)
    
        plt.title('Demand & Supply Curves', fontsize=14, fontweight='bold')
        plt.xlabel('Quantity', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=True, fontsize=10, ncol=2)
        plt.grid(True, linestyle='--', alpha=0.6)
    
        # Show the plot
        plt.tight_layout()  
        plt.show()