from marketlib.markets import bilateral as mk

bid_file_path = "./data/example_bids.csv"
ask_file_path = "./data/example_asks.csv"

M = mk.BilateralMarket()

M.bid_csv(bid_file_path)
M.ask_csv(ask_file_path)

print(M.clearing())