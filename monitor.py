import settings
from threading import Lock, Barrier
from workers import ExchangeWorker
import os
import sys

if len(sys.argv) != 2:
    raise ValueError("Invalid amount of arguments. Provide 'orderbook/candles'.")

data_type = sys.argv[1].lower()

directory = "./"+data_type
if not os.path.exists(directory):
    os.makedirs(directory)

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
                            settings.database_type,
                            mutex,
                            barrier)
    workers.append(worker)
    worker.start()