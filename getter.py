from abc import ABCMeta, abstractmethod
from datetime import datetime
import numpy as np
import time
from ccxt.base.errors import DDoSProtection

class Getter(object):

    """Getter: Generic class to request data from exchanges.
    """

    __metaclass__ = ABCMeta

    def __init__(self, exchange, client, mutex, barrier, db):
        self.exchange = exchange
        self.client = client
        self.mutex = mutex
        self.barrier = barrier
        self.db = db
        self.last_request_time = 0

    @abstractmethod
    def request(self, symbol):
        pass
    
    def store(self, symbol, data):
        self.mutex.acquire()
        self.db.insert(self.exchange, symbol, data)
        self.mutex.release()

    def synchronize(self):
        while (time.time() - self.last_request_time)<self.client.rateLimit/1000:
            pass
        self.barrier.wait()


class Candles(Getter):

    """Candles: A class to request candles data from exchange.
    Runs all time because different exchanges returns more or less candles.
    This way, we standarize the request.
    """

    def __init__(self, exchange, client, mutex, barrier, db, symbols):
        super(Candles, self).__init__(exchange, client, mutex, barrier, db)
        self.last_datetime = {symbol:0 for symbol in symbols}

    def request(self, symbol):

        self.synchronize()
        n_candles = 1000
        
        try:            
            candles = self.client.fetch_ohlcv(symbol=symbol, 
                                              timeframe="1m",
                                              since=self.client.milliseconds()-n_candles*60*1000, 
                                              limit=n_candles)
            self.last_request_time = time.time()
            candles = np.array(candles)
            
            # discard last candle: yet incomplete
            candles = np.delete(candles, -1, 0)
        except DDoSProtection:
            self.last_request_time = time.time()
            candles = None
            print("WARNING: DDOS Protection. ERROR rate limit.")
        except Exception as e:
            print(e)
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            candles = None
            pass
        else:
            # remove old values
            for t in candles.transpose()[0]:
                if t <= self.last_datetime[symbol]:
                    candles = np.delete(candles, 0, 0)
                       
            # if new values
            if len(candles)>0:

                # update last datetime
                self.last_datetime[symbol] = candles[-1][0]
                
                for candle in candles:
                    data = {"datetime": datetime.fromtimestamp(candle[0]/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            "open":candle[1],
                            "high":candle[2],
                            "low":candle[3],
                            "close":candle[4],
                            "volume":candle[5]}
                    # store                
                    self.store(symbol, data)

class OrderBook(Getter):

    """OrderBook: A class to request orderbook data from exchange"""

    def __init__(self, exchange, client, mutex, barrier, db):
        super(OrderBook, self).__init__(exchange, client, mutex, barrier, db)

    def request(self, symbol):
        
        self.synchronize()
        
        try:
            book = self.client.fetch_order_book(symbol)
            self.last_request_time = time.time()
        except DDoSProtection:
            book = None
            self.last_request_time = time.time()
            print("WARNING: DDOS Protection. ERROR rate limit.")
        except:
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            book = None
        if self.book_is_valid(book):
            bid_weight_val_1, bid_weight_count_1 = self.weighted_orders(book['bids'], limit=5)
            bid_weight_val_2, bid_weight_count_2 = self.weighted_orders(book['bids'], limit=10)
            ask_weight_val_1, ask_weight_count_1 = self.weighted_orders(book['asks'], limit=5)
            ask_weight_val_2, ask_weight_count_2 = self.weighted_orders(book['asks'], limit=10)
            data = {"datetime": datetime.now(),                    
                    "bid_weight_val_1":bid_weight_val_1,
                    "bid_weight_count_1":bid_weight_count_1,
                    "bid_weight_val_2":bid_weight_val_2,
                    "bid_weight_count_2":bid_weight_count_2,
                    "bid_val_2":book['bids'][2][0],
                    "bid_count_2":book['bids'][2][1],                    
                    "bid_val_1":book['bids'][1][0],
                    "bid_count_1":book['bids'][1][1],
                    "bid_val_0":book['bids'][0][0],
                    "bid_count_0":book['bids'][0][1],
                    "ask_val_0":book['asks'][0][0],
                    "ask_count_0":book['asks'][0][1],
                    "ask_val_1":book['asks'][1][0],
                    "ask_count_1":book['asks'][1][1],
                    "ask_val_2":book['asks'][2][0],
                    "ask_count_2":book['asks'][2][1], 
                    "ask_weight_val_1":ask_weight_val_1, 
                    "ask_weight_count_1":ask_weight_count_1, 
                    "ask_weight_val_2":ask_weight_val_2, 
                    "ask_weight_count_2":ask_weight_count_2}
            self.store(symbol, data)

    def book_is_valid(self, book):
        if book == None:
            return False
        if book == []:
            return False
        if len(book['bids'])<3:
            return False
        if len(book['asks'])<3:
            return False
        return True

    def weighted_orders(self, book, limit):
        
        weighted_value = 0
        count = 0

        for i_order, order in enumerate(book, 0):
            if i_order<limit:              
                weighted_value += order[0]*order[1]
                count += order[1]
            else:
                break

        try:
            weighted_value /= count
        except:
            print(self.exchange, book)

        return weighted_value, count