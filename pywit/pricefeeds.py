import requests
import time

from .config import Configuration
from .interface import SteemExplorer
from .logger import Logger


class PriceFeed():
    def __init__(self, stm: SteemExplorer):
        self.stm = stm
        self.conf = stm.conf
        self.log = stm.log
        self.min_spread = 2.0

    def get_pair(self, pair):
        self.log.add_func("PriceFeed:get_pair")
        if pair == "SU":
            # steem/usd- full price
            sb = self.get_prices(1)
            bu = self.get_pair("BU")
            btu = self.get_pair("BTU")

            #multiply and average and voila
            su = []
            for i in sb:
                p = float(i) * bu
                su.append(p)
                p = float(i) * btu
                su.append(p)

            #print prices in su
            for i in su:
                logstr = "STEEM to USD Price: {:.4f} USD per STEEM".format(i)
                self.log.log(logstr, 2)

            avg = self.get_avg(su)
            logstr = "Final STEEM to USD Price: {:.3f} USD per STEEM".format(
                avg)
            self.log.log(logstr, 1)

            self.log.pop_func()
            return avg

        elif pair == "BTU":
            # btc/tether/usd price: gets bt and tu and returns b/u
            bt = self.get_pair("BT")
            tu = self.get_pair("TU")

            # multiply and return
            btu = bt * tu
            logstr = "Bitcoin to USD Price (Proxied through USDT): \
                {:.4f} USD per BTC".format(
                btu)
            self.log.log(logstr, 2)

            self.log.pop_func()
            return btu

        elif pair == "BU":
            # btc/usd
            p = self.get_prices(2)[0]
            logstr = "Bitcoin to USD Price: {:.4f} USD per BTC".format(p)
            self.log.log(logstr, 2)

            self.log.pop_func()
            return p

        elif pair == "BT":
            # btc/usdt
            p = self.get_prices(3)

            for i in p:
                logstr = "Bitcoin to USDT Price: {:.4f} USDT per BTC".format(i)
                self.log.log(logstr, 2)

            # list prices off
            avg = self.get_avg(p)
            logstr = "Average Bitcoin to USDT Price: {:.4f} USDT per BTC".format(
                avg)
            self.log.log(logstr, 2)

            self.log.pop_func()
            return avg

        elif pair == "TU":
            # usdt/usd
            p = self.get_prices(4)

            for i in p:
                logstr = "USDT to USD Price: {:.4f} USD per USDT".format(i)
                self.log.log(logstr, 2)

            avg = self.get_avg(p)
            logstr = "Average USDT to USD Price: {:.4f} USD per USDT".format(
                avg)
            self.log.log(logstr, 2)

            self.log.pop_func()
            return avg

        else:
            # error
            self.log.log('Error: Invalid Pair Type', 1)
            self.log.pop_func()

    # same order as get_pair
    def get_prices(self, pair):
        self.log.add_func("PriceFeed:get_prices")
        if pair == 1:
            # steem/btc prices
            prices = []

            try:
                self.log.log("Querying Bittrex", 2)
                r = requests.get(
                    'https://bittrex.com/api/v1.1/public/getmarketsummary?market=BTC-STEEM',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['result'][0]
                    prices.append(float(d['Last']))
                    logstr = "Bittrex: {:.8f} BTC/STEEM".format(prices[-1])
                    self.log.log(logstr, 2)

                self.log.log("Querying Binance", 2)
                r = requests.get(
                    'https://api.binance.com/api/v1/ticker/24hr', timeout=30)
                if r.status_code == 200:
                    d = [x for x in r.json() if x['symbol'] == 'STEEMBTC'][0]
                    prices.append(float(d['lastPrice']))
                    logstr = "Binance: {:.8f} BTC/STEEM".format(prices[-1])
                    self.log.log(logstr, 2)

                self.log.log("Querying Poloniex", 2)
                r = requests.get(
                    'https://poloniex.com/public?command=returnTicker',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['BTC_STEEM']
                    prices.append(float(d['last']))
                    logstr = "Poloniex: {:.8f} BTC/STEEM".format(prices[-1])
                    self.log.log(logstr, 2)

                if len(prices) == 3:
                    diff = self.get_percent_difference(prices[0], prices[2])
                    difftwo = self.get_percent_difference(prices[1], prices[2])
                    diffavg = (diff + difftwo) / 2

                    if diffavg > self.min_spread:
                        prices.pop()
                        self.log.log("Removed Poloniex for high variance.", 2)
            except KeyError:
                self.log.log("Key Error Occured.", 1)
                self.log.pop_func()
                return
            self.log.pop_func()
            return prices
        elif pair == 2:
            # btc/usd straight prices
            prices = []
            # only bittrex to query

            try:
                self.log.log("Querying Bittrex", 2)
                r = requests.get(
                    'https://bittrex.com/api/v1.1/public/getmarketsummary?market=USD-BTC',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['result'][0]
                    prices.append(float(d['Last']))
                    logstr = "Bittrex: {:.4f} BTC/USD".format(prices[-1])
                    self.log.log(logstr, 2)
            except KeyError:
                self.log.log("Key Error Occured.", 1)
                self.log.pop_func()
                return
            self.log.pop_func()
            return prices
        elif pair == 3:
            # btc/usdt price
            prices = []

            try:
                self.log.log("Querying Poloniex", 2)
                r = requests.get(
                    'https://poloniex.com/public?command=returnTicker',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['USDT_BTC']
                    prices.append(float(d['last']))
                    logstr = "Poloniex: {:.4f} USDT/BTC".format(prices[-1])
                    self.log.log(logstr, 2)

                self.log.log("Querying Bittrex", 2)
                r = requests.get(
                    'https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-BTC',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['result'][0]
                    prices.append(float(d['Last']))
                    logstr = "Bittrex: {:.4f} USDT/BTC".format(prices[-1])
                    self.log.log(logstr, 2)

                self.log.log("Querying Binance", 2)
                r = requests.get(
                    'https://api.binance.com/api/v1/ticker/24hr', timeout=30)
                if r.status_code == 200:
                    d = [x for x in r.json() if x['symbol'] == 'BTCUSDT'][0]
                    prices.append(float(d['lastPrice']))
                    logstr = "Binance: {:.4f} USDT/BTC".format(prices[-1])
                    self.log.log(logstr, 2)
            except KeyError:
                self.log.log("Key Error Occured.", 1)
                self.log.pop_func()
                return
            self.log.pop_func()
            return prices
        elif pair == 4:
            # usdt/usd price
            # btc/usdt price
            prices = []

            try:
                self.log.log("Querying Bittrex", 2)
                r = requests.get(
                    'https://bittrex.com/api/v1.1/public/getmarketsummary?market=USD-USDT',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['result'][0]
                    prices.append(float(d['Last']))
                    logstr = "Bittrex: {:.4f} USD/USDT".format(prices[-1])
                    self.log.log(logstr, 2)

                self.log.log("Querying Kraken", 2)
                r = requests.get(
                    'https://api.kraken.com/0/public/Ticker?pair=USDTZUSD',
                    timeout=30)
                if r.status_code == 200:
                    d = r.json()['result']['USDTZUSD']
                    prices.append(float(d['c'][0]))
                    logstr = "Kraken: {:.4f} USD/USDT".format(prices[-1])
                    self.log.log(logstr, 2)
            except KeyError:
                self.log.log("Key Error Occured.", 1)
                self.log.pop_func()
                return
            self.log.pop_func()
            return prices
        else:
            # error
            print("Error: Invalid Pair Type Passed.")
            self.log.pop_func()

    def get_avg(self, d):
        self.log.add_func("PriceFeed:get_avg")
        avg = 0
        for i in d:
            avg += i
        self.log.pop_func()
        return avg / len(d)

    def get_percent_difference(self, num, numTwo):
        self.log.add_func("PriceFeed:get_percent_difference")
        diff = num - numTwo
        if diff < 0:
            diff = -diff
        perc = (diff)/((num + numTwo)/2) * 100
        self.log.pop_func()
        return perc

    def do_feed(self, pnow):
        self.log.add_func("PriceFeed:do_feed")
        p = self.get_pair("SU")
        per = self.get_percent_difference(self.last_price, p)
        if per > self.min_spread or self.pub_today == 24 or pnow:
            if per < 25 and self.last_price != 0:
                self.stm.pubfeed(p)
                self.last_price = p
                logstr = "Published feed %.3f USD/Steem." % p
                self.log.log(logstr, 1)
                self.pub_today = 0
            else:
                logstr = "Percent difference {:.2f}% greater than 25%, \
                    not publishing.".format(
                    per)
                self.log.log(logstr, 1)
        else:
            logstr = "Percent difference {:.2f}% lower than minimum spread \
                {:.2f}%, not publishing.".format(
                per, self.min_spread)
            self.log.log(logstr, 1)
            self.pub_today += 1
        self.log.pop_func()

    def run_feeds(self, slptime=6000, spread=2.0, pnow=False):
        self.log.add_func("PriceFeed:run_feeds")
        if self.stm.locked():
            if not self.stm.unlock_wallet():
                print("You must unlock your wallet to run price feed.")
                return
        self.pub_today = 0
        self.min_spread = spread
        self.last_price = self.stm.get_price_feed()
        logstr = "Running price feeds with minimum spread {:.2f}\
                and sleep time {:.2f} minutes.".format(
            self.min_spread, (slptime / 60))
        self.log.log(logstr, 1)
        while True:
            try:
                self.do_feed(pnow)
                if pnow:
                    pnow = False
                time.sleep(slptime)
            except KeyboardInterrupt:
                self.log.pop_func()
                print(" ")
                return
