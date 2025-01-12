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

# --- Bids and asks can also be added individually ---
# Ask: unit, price, user_id
# M.ask(10, 1, user_id=0)
# M.ask(5, 1.5, user_id=1)
# M.ask(3, 2, user_id=2)

# # Bid: unit, price, user_id
# M.bid(10, 1, user_id=3)
# M.bid(5, 2, user_id=4)
# M.bid(10, 2.5, user_id=5)

# Compute the clearing price, volumn, and gap
price, vol, gap = M.clearing()

print(f"Price: {price}")
print(f"Volumn: {vol}")
print(f"Transction amount: {price * vol}")
print(f"gap: {gap}")