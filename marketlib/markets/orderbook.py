"""Orderbook tracks all active bids and asks, used by the Market class.

    How to run:
    1. You are not suppose to run this module explicitly. 
    2. For testing: python3 -m marketlib.markets.orderbook
"""

import pandas as pd
import matplotlib.pyplot as plt  # type: ignore
from marketlib.utils import bidask as ba

class _OrderBook():
    """ Track of all active bids and asks.

    Attributes:
        orders (dataframe):
            Columns are "Unit" | "Price" | "Type" | "User". 
            "Price" is per-unit, "Type" is either bid or ask, 
            "User" is user id.
    """

    col_names = [
        'Unit',
        'Price',
        'Type',
        'User'
    ] 

    def __init__(self):
        # Initially an empty order book
        self.orders = pd.DataFrame(columns=self.col_names)

    # ----------------------
    #   Add a single bid   -
    # ----------------------
    def _add_bid(
        self,
        unit,
        price,
        user_id
    ):
        """ Add a single bid to the orderbook.

        Args:
            unit (int): 
                Number of buying units for this bid 
            price (float): 
                Per-unit bid price
            user_id (int):
                The id of the buyer who placed this bid.
                (Buyers and sellers ids don't overlap)
        """

        new_bid = pd.DataFrame([[unit, price, 'bid', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    # --------------------------
    #   Add a bundle of bids   -
    # --------------------------
    def add_bid_csv(
        self,
        input_path
    ):
        """ Add a collection of bids to the orderbook.

        Args:
            input_path (str):
                Path to the .csv file which contains a collection of bids.
                Columns of csv: Unit, Price, User.
                Note: The "Type" column will be added automatically to the orderbook. No need to specify it in the csv file.
        """

        new_bid = pd.read_csv(input_path, sep=',')
        new_bid["Type"] = "bid"
        new_bid = new_bid[self.col_names]
        self.orders = pd.concat([self.orders, new_bid], ignore_index=True)

    # ----------------------
    #   Add a single ask   -
    # ----------------------
    def _add_ask(
        self,
        unit,
        price,
        user_id
    ):
        """ Add a single ask to the orderbook.

        Args:
            unit (int): 
                Number of buying units for this ask 
            price (float): 
                Per-unit ask price
            user_id (int):
                The id of the seller who placed this bid.
                (Buyers and sellers ids don't overlap)
        """  
        
        new_ask = pd.DataFrame([[unit, price, 'ask', user_id]], columns=self.col_names)
        self.orders = pd.concat([self.orders, new_ask], ignore_index=True)
    
    # --------------------------
    #   Add a bundle of asks   -
    # --------------------------
    def add_ask_csv(
        self,
        input_path
    ):
        """ Add a collection of asks to the orderbook.

        Args:
            input_path (str): 
                Path to the .csv file which contains a collection of asks.
                Columns of csv: Unit, Price, User.
                Note: The "Type" column will be added automatically to the orderbook. No need to specify it in the csv file.
        """

        new_ask = pd.read_csv(input_path, sep=',')  # <- no header=None
        new_ask["Type"] = "ask"
        new_ask = new_ask[self.col_names]
        self.orders = pd.concat([self.orders, new_ask], ignore_index=True)

    # -----------------------------------
    #   Display the current orderbook   -
    # -----------------------------------
    def display(self, scale=0):
        """ Print the orderbook.

        Args:
            scale (int, default=0): 
                0: both bids and asks; 
                1: bids; 
                2: asks
        """

        if scale == 0:
            print(self.orders)
        elif scale == 1:
            print([self.orders['Type'] == 'bid'])
        else:
            print(self.orders[self.orders['Type'] == 'ask'])

        print('\n')


    # ------------------
    #   Get all bids   -
    # ------------------
    def _get_bids(self):
        """ Extract all bids, sorted in non-ascending order by prices. Bids of the same prices are merged where their units accumulate.

        This function gives the demand curve, which is used to compute the market clearing price.

        Returns:
            A numpy array of the form [[bid_price_1, units_1], [bid_price_2, units_2], ...]
        """

        bids = self.orders[self.orders['Type'] == 'bid']
        bid_curves = bids.groupby('Price')['Unit'].sum().reset_index()

        return bid_curves.sort_values(by=['Price'], ascending=False).to_numpy()
 
    # ------------------
    #   Get all asks   -
    # ------------------   
    def _get_asks(self):
        """ Extract all asks, sorted in non-descending order by prices. Asks of the same prices are merged where their units accumulate.

        This function gives the supply curve, which is used to compute the market clearing price.

        Returns:
            A numpy array of the form [[ask_price_1, units_1] ...]
        """

        asks = self.orders[self.orders['Type'] == 'ask']
        ask_curves = asks.groupby('Price')['Unit'].sum().reset_index()

        return ask_curves.sort_values(by=['Price']).to_numpy()

    # ---------------------------------
    #   Plot supply & demand curves   -
    # ---------------------------------
    def plot_curves(self):
        """ Plot the supply & demand curve as two separate step functions.

            *This code is generated by ChatGPT*
        """

        demand_curve = self.get_bids().tolist()
        supply_curve = self.get_asks().tolist()

        demand_units = [unit for price, unit in demand_curve]
        demand_prices = [price for price, unit in demand_curve]
        cumulative_demand = [0] + list(ba.cumu_sum(demand_units))
    
        supply_units = [unit for price, unit in supply_curve]
        supply_prices = [price for price, unit in supply_curve]
        cumulative_supply = [0] + list(ba.cumu_sum(supply_units))
    
        demand_prices = demand_prices + [demand_prices[-1]]
        supply_prices = supply_prices + [supply_prices[-1]]

        plt.figure(figsize=(7, 4), dpi=450)
        
        plt.step(cumulative_demand, demand_prices, label='Demand', where='post', color='#1f77b4', linewidth=2.5, alpha=0.8)
        plt.step(cumulative_supply, supply_prices, label='Supply', where='post', color='#ff7f0e', linewidth=2.5, alpha=0.8)
    
        plt.title('Demand & Supply Curves', fontsize=14, fontweight='bold')
        plt.xlabel('Quantity', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=True, fontsize=10, ncol=2)
        plt.grid(True, linestyle='--', alpha=0.6)
    
        # Show the plot
        plt.tight_layout()  
        plt.show()
    

if __name__ == "__main__":
    B_1 = _OrderBook()
    B_2 = _OrderBook()

    # Add single bids and asks
    B_1._add_bid(5, 1, 0)
    B_1._add_bid(10, 1.5, 1)
    B_1._add_bid(20, 0.5, 2)
    B_1._add_ask(7, 0.85, 3)
    B_1._add_ask(12, 1.15, 4)

    # Add bundles
    B_2.add_ask_csv('data/example_asks.csv')
    B_2.add_bid_csv('data/example_bids.csv')

    print("--- Order Book 1 ---")
    B_1.display()

    print("--- Order Book 2 ---")
    B_2.display()

    """ 
    OUTPUTS:

    --- Order Book 1 ---
    Unit Price Type User
    0    5     1  bid    0
    1   10   1.5  bid    1
    2   20   0.5  bid    2
    3    7  0.85  ask    3
    4   12  1.15  ask    4

    --- Order Book 2 ---
    Unit  Price Type User
    0   10    1.0  ask    0
    1    5    1.5  ask    1
    2    3    2.0  ask    2
    3    1    1.2  ask    0
    4   10    1.0  bid    3
    5   10    2.0  bid    3
    6    5    2.0  bid    4
    7   10    2.5  bid    5
    """