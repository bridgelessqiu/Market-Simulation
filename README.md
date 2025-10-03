# An overview of the market simulator

## `data`

**Overview:** Contains `.csv` data files for bids and asks of the form:

| Unit  | Price |  User |
| ------------- | ------------- |  ------------- |

- `User` entry consists of the `id` of a user
- `Price` entry consists of a per-unit-price for a user
- `Unit` entry is the number of units a user wants to buy (in the case of a bidder) or sell

**Example data:**

1. ``example_ask.csv``

2. ``example_bids.csv``


## `marketlib`
**Overview:** Contains subpackages for various markets and clearing mechanisms.

#### 1. ``markets``

  1. ``market`` module

       The base market class. It supports the following methods:

       a. `bid`: Add one bid to the orderbook

       b. `bid_csv`: Add a collections of bids to the orderbook

       c. `ask`: Add one ask to the orderbook

       d. `ask_csv`: Add a collections of asks to the orderbook

       e. `display`: Return the entire orderbook

       f. `clearing`: Perform market clearning. This is an abstract method.

       g. `plot`: Plot the supply and demand curve

  2.  ``orderbook`` module

      The class for all bids and asks orders. It communicates with a market to add bids/asks, display the dataframe, and plots.

  3. `pool` module

      The class for the **pool-based market**, inherited from the `market` base class.

     The clearing is performed as follows:

     1. Sort the union of ask and bid prices in non-descending order.

     2. Iterative over each price, compute the corresponding volume.

     3. Return the price with the highest volume.
            Note: the resulting volume should be non-decreasing as 
            price increases to the volume-maximizing price. Therefore, 
            once we see the volume start to decrease, the previous price 
            is then the target price to return.

4.  `one_side` module

    The class for a one sided market which supports the following **auctions**: (i) first-price; (ii) second-price; (iii) double and (iv) reverse.

5. `bilateral` module

    The class of bilateral markets, which supports various matching mechanisms and bargaining mechanisms.

#### 2. ``utils``

Contains the utility functions that are used by various types of markets.

1. `bidask` module: contains utility functions for clearing in pooled markets.
2. `allocation` module: contains various resource allocation mechanism for clearing pooled markets.
3. `auction` module: contains different auction mechanisms for one-sided markets.
4. `matching` and `bargain` modules: contains different matching and bargaining mechanisms for bilateral markets.

## An example:

```python
python3 -m marketlib.markets.pool
```

Output:
```
---- Clearing Info ----
Clearing price: 2.0
Total volume: 19
Gap: 6

---- Buyer Allocation ----
  User Units Bought  Price
0    3            9    2.0
1    5           10    2.0

---- Seller Allocation ----
  User Units Sold  Price
0    0         11    2.0
1    1          5    2.0
2    2          3    2.0
```