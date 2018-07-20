import settings
from threading import Lock
from workers import ExchangeWorker

workers = []
mutex = Lock()

for exchange in settings.exchanges:
    worker = ExchangeWorker(exchange,
                            settings.symbols,
                            settings.symbol_freq,
                            settings.req_freq,
                            settings.data_type,
                            mutex,
                            settings.db_name,
                            settings.table_name)
    workers.append(worker)
    worker.start()