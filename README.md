# Design

## `data`

**Overview:** Contains .csv data for bids and asks of the form:

| Unit  | Price |  User |
| ------------- | ------------- |  ------------- |

**Example data:**

1. ``example_ask.csv``

2. ``example_bids.csv``


## `marketlib`
**Overview:** Contains subpackages for markets, ordres and clearnings.

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

      This class for the **pool-based market**, inherited from the `market` base class.

     The clearing is performed as follows:

     1. Sort the union of ask and bid prices in non-descending order.

     2. Iterative over each price, compute the corresponding volume.

     3. Return the price with the highest volume.
            Note: the resulting volume should be non-decreasing as 
            price increases to the volume-maximizing price. Therefore, 
            once we see the volume start to decrease, the previous price 
            is then the target price to return.

#### 2. ``utils``

Continas all utility functions.

1. `bidask` module: contains utility functions for market clearning. 

## `tests`
**Overview**: Contains testing moduels

#### 1. ``simple_market``

Performs testing for the simple pool-based market. 

An example:

```python
from marketlib import markets as mk

bid_file_path = "../data/example_bids.csv"
ask_file_path = "../data/example_asks.csv"

# Create a simple pool market and add bids/asks
M = mk.PoolMarket()
M.bid_csv(bid_file_path)
M.ask_csv(ask_file_path)

# Do the clearing
price, vol, gap = M.clearing()

# Report the clearing outcome
print(f"Price: {price}")
print(f"Volumn: {vol}")
print(f"Transction amount: {price * vol}")
print(f"gap: {gap}")
```
