mongo orderbook --eval "db.dropDatabase()"
mongo candles --eval "db.dropDatabase()"
sudo service mongodb restart
sudo service mongodb status
