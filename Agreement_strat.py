import pandas as pd
import numpy as np
from QuantConnect.Python import PythonQuandl
from QuantConnect.Data.Custom.CBOE import *

class BasicRSItrading(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        self.SetStartDate(2010,1, 1)  #Set Start Date
        self.SetEndDate(2020,12,25)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        
        # Symbols to Trade
        self.equity_symbols = ['TQQQ', 'DJI', '^RUT', 'DUSL', "NDAQ"]
        
        
        # Store SymbolData objects with symbols as key
        self.Data = {}
        
        # window size
        self.window_size = 14
        
        # warm up period of size window_size before we start analysis
        self.SetWarmUp(self.window_size)
        
        # for each symbol create a new SymbolData object and add symbol to portfolio
        for symbol in self.equity_symbols:
            self.AddEquity(symbol, Resolution.Daily)
            self.Data[symbol] = SymbolData(symbol, self)
        
        # Keep track of symbol we are currently invested in and the number of max symbols it had (Need to revisit probs should not be max)
        self.current_invested_symbol = None
        self.max_num_signals = float('-inf')
        
        # define number of indicators in order to buy
        self.NUM_INDICATORS = 1
        
        # trailing stop
        self.trailing_stop = 0
        
        # buy price
        self.buy_price = 0


    def OnData(self, data):
        
        # dont do anything if were in the warming up period
        if self.IsWarmingUp:
            return
        
        # update indicator data for symbol we are invested in
        if self.current_invested_symbol:
            self.max_num_signals = self.Data[self.current_invested_symbol].Update()
        
        # go through the equities and try to buy it if it beats the current num signals seen
        temp_symbol = self.current_invested_symbol
        temp_num_signal = self.max_num_signals
        
        for symbol in self.equity_symbols:
            
            # dont need to update current invested symbol
            if symbol == self.current_invested_symbol:
                continue
            
            # get current symbol indicator count
            indicator_count = self.Data[symbol].Update()
            
            # if its bigger then we want to buy that symbol and sell our current symbol
            if indicator_count >= self.NUM_INDICATORS and indicator_count > self.max_num_signals:
                temp_symbol = symbol
                temp_num_signal =  indicator_count
        
        # if we found a different symbol to buy
      
        if not temp_symbol or not data.ContainsKey(temp_symbol):
            return
        
        if temp_symbol != self.current_invested_symbol and temp_num_signal >= self.NUM_INDICATORS:
            # sell previous symbol if we have one
            if temp_symbol:
                # self.Log(f"Sold {temp_symbol} {self.Portfolio[temp_symbol].Quantity}, Indicators {temp_num_signal}")
                self.Liquidate(temp_symbol)
                
            # buy current one if we aren't already invested
            if self.Portfolio.Invested  == False:
                self.SetHoldings(temp_symbol, 1.0)
                self.buy_price = self.Securities[temp_symbol].Price
                # self.Log(f"Bought {temp_symbol} {self.Portfolio[temp_symbol].Quantity}, Indicators {temp_num_signal}")
                self.current_invested_symbol = temp_symbol
                self.max_num_signals = temp_num_signal
                
                self.highestPrice = self.Securities[temp_symbol].Close
                
        elif self.max_num_signals < self.NUM_INDICATORS and self.Portfolio[self.current_invested_symbol].Quantity > 0 and self.Securities[self.current_invested_symbol].Price < self.trailing_stop and self.Data[self.current_invested_symbol].StopBB() :
            self.Liquidate(self.current_invested_symbol)
            self.trailing_stop = 0
        
        if self.current_invested_symbol:
                stop_loss = self.Data[self.current_invested_symbol].StopATR()
                if stop_loss > self.trailing_stop:
                    # self.Log(f"New Stop Loss... Old: {self.highestPrice}, New: {stop_loss}")
                    self.trailing_stop = stop_loss
                    
                    # %15 hard stop loss 
                if self.buy_price < self.Securities[self.current_invested_symbol].Close:
                    self.buy_price = self.Securities[self.current_invested_symbol].Close
                    
                if self.buy_price > 0 and self.Securities[self.current_invested_symbol].Close <= self.buy_price * .85:
                    self.Liquidate(self.current_invested_symbol)
                    self.trailing_stop = 0
                    self.buy_price = 0
                
                # if self.Portfolio[self.current_invested_symbol].Quantity > 0 and self.Securities[self.current_invested_symbol].Price < self.trailing_stop:
                #     self.Log(f"Selling {self.current_invested_symbol}, {self.Securities[self.current_invested_symbol].Price}")
                #     self.Liquidate(self.current_invested_symbol)
                
                        

    
            
class SymbolData:
    
    # initialize SymbolData class
    def __init__(self, symbol, algorithm):
        # save symbol name and reference to 
        self.Symbol = symbol
        self.algorithm = algorithm
        
        # future implimentation 
        self.stop_loss = None
        self.window_size = 14
        
        # initialize Momentum indicators and data trackers
        self.close = algorithm.Identity(symbol)
        self.RSI_ind  = algorithm.RSI(symbol, self.window_size)
        self.ROC_ind  = algorithm.ROC(symbol, self.window_size)
        self.ADX_ind  = algorithm.ADX(symbol, self.window_size)
        self.AROON_ind = algorithm.AROON(symbol, self.window_size)
        self.ATR_ind = algorithm.ATR(symbol, self.window_size)
        self.bollinger = algorithm.BB(symbol, self.window_size, 2)
        
        #initialize volitility indicators
        self.SAR_Ind = algorithm.PSAR(symbol, afStart=0.02, afIncrement=0.02, afMax=0.02)
        
        
        # flag for when all indicators are ready to be read from
        self.isReady = self.RSI_ind.IsReady and self.ROC_ind.IsReady and self.ADX_ind.IsReady and self.AROON_ind.IsReady and self.close.IsReady and self.SAR_Ind.IsReady
        
        # track stop loss value
        self.stop_loss = 0
        
    # function to update isReady flag and return number of indicators
    def Update(self):
        self.isReady = self.RSI_ind.IsReady and self.ROC_ind.IsReady and self.ADX_ind.IsReady and self.AROON_ind.IsReady and self.close.IsReady and self.SAR_Ind.IsReady
        return self.TryEnter()
        
    # function to calculate number of indicators and return them
    def TryEnter(self):
        if self.algorithm.Portfolio[self.Symbol].Quantity > 0:
            return False
            
        # self.algorithm.Log(f"Calculating Indicators....")
        num_buy_singals = 0
        
        if self.RSI_ind.Current.Value > 30:
            num_buy_singals += 1
        
        if self.ROC_ind.Current.Value > .10:
            num_buy_singals += 1
            
        if self.ADX_ind.Current.Value > 25 and self.ADX_ind.PositiveDirectionalIndex > self.ADX_ind.NegativeDirectionalIndex:
            num_buy_singals += 1
            
        if self.AROON_ind.Current.Value > 10:
            num_buy_singals += 1
        
        # self.algorithm.Log(f"Calculated Indicators -> {num_buy_singals}\n")
        
        return num_buy_singals
    
    def StopATR(self):
        
        return self.algorithm.Securities[self.Symbol].Close - (self.ATR_ind.Current.Value * 2 )
    
    def StopBB(self):
        return self.algorithm.Securities[self.Symbol].Close < self.bollinger.Current.Price