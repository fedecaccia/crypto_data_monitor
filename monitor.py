import settings
from threading import Lock, Barrier
from workers import ExchangeWorker
import os
import sys

if len(sys.argv) != 2:
    raise ValueError("Invalid amount of arguments. Provide 'orderbook/candles'.")

data_type = sys.argv[1].lower()    

if data_type=="orderbook":
    orderbook_dir = "./orderbook"
    table_name = "orderbook"
    db_name = "sqlite:///"+orderbook_dir+"/data.db"
    if not os.path.exists(orderbook_dir):
        os.makedirs(orderbook_dir)
elif data_type=="orderbook":
    candles_dir = "./candles"
    table_name = "candles"
    if not os.path.exists(candles_dir):
        os.makedirs(candles_dir)
    db_name = "sqlite:///"+candles_dir+"/data.db"
else:
    raise ValueError("Invalid argument: '"+data_type+"'.")

n_exchanges = len(settings.exchanges)
workers = []
mutex = Lock()
barrier = Barrier(n_exchanges)

for exchange in settings.exchanges:
    worker = ExchangeWorker(exchange,
                            settings.symbols,
                            settings.symbol_freq,
                            settings.req_freq,
                            data_type,
                            mutex,
                            barrier,
                            db_name,
                            table_name)
    workers.append(worker)
    worker.start()