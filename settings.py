exchanges = ["Bitfinex", "Bittrex", "Binance"]
symbols = ["ADA/BTC", "ETH/BTC", "BTC/USD", "BTC/USDT"]
symbol_freq = 20 # seg
req_freq = 5 # seg
data_type = "orderbook" # candles / orderbook
db_name = "sqlite:///orderbook/data.db"
table_name = "orderbook"
