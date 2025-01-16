import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from marketlib import markets as mk


bid_file_path = "../data/example_bids.csv"
ask_file_path = "../data/example_asks.csv"

M = mk.PoolMarket()

M.bid_csv(bid_file_path)
M.ask_csv(ask_file_path)

# Print orderbook
print(M.show())

M.clearing()

# Compute the clearing price, volumn, and gap
# price, vol, gap = M.clearing()

# print(f"Price: {price}")
# print(f"Volumn: {vol}")
# print(f"Transction amount: {price * vol}")
# print(f"gap: {gap}")