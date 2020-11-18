import numpy as np
from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Brokerages import *
from QuantConnect.Orders import *
from QuantConnect.Data import *
from QuantConnect.Data.UniverseSelection import *
from QuantConnect.Algorithm.Framework.Execution import ExecutionModel
import statistics



class BasicRSItrading(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''
    highestTQQQPrice = 0
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    
    def Initialize(self):
          # window size
        self.window_size = 14
        self.SetWarmUp(self.window_size)
        
        # Symbols to Trade
        self.equity_symbols = ['TQQQ', 'UDOW', 'URTY', 'DUSL', "NDAQ"]
        
        self.SetStartDate(2010,10, 25)  #Set Start Date
        self.SetEndDate(2020,10,25)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.Tqqq = self.AddEquity("TQQQ",Resolution.Daily)
        self.Tqqq.SetDataNormalizationMode(DataNormalizationMode.Raw) #set TQQQ
        self.spy = self.AddEquity("SPY", Resolution.Daily)
        self.spy.SetDataNormalizationMode(DataNormalizationMode.Raw) #set SPY
        self.UDOW = self.AddEquity("UDOW",Resolution.Daily)
        self.UDOW.SetDataNormalizationMode(DataNormalizationMode.Raw) #UDOW set
        self.rut= self.AddEquity("URTY", Resolution.Daily)
        self.rut.SetDataNormalizationMode(DataNormalizationMode.Raw) #RUT set
        self.NUM = 0
        self.HIGH = 0
        self.NUM_Med = 0
        self.Rebalance = 0
        self.Check = 1
        self.rsi = self.RSI("TQQQ", 60,  MovingAverageType.Simple, Resolution.Daily)
        '''std = self.STD("TQQQ", 365, Resolution.Minute)'''
        '''history = self.History("TQQQ", 365,Resolution.Minute)'''
 
  
    def OnData(self,data):
        if self.IsWarmingUp:
            return
        
        if (self.Time - self.stopMarketOrderFillTime).days <= 0:
            return
        
        'Set holdings and base data that is to be used'
        rsiValue = self.rsi.Current.Value
        holdings_TQQQ = self.Portfolio['TQQQ'].Quantity
        holdings_SPY = self.Portfolio['SPY'].Quantity
        holdings_RUT = self.Portfolio['URTY'].Quantity
        holdings_UDOW = self.Portfolio['UDOW'].Quantity
       
            
        'Check to see if this is a good Trade based on the current RSI of the TQQQ in this case we are over sold '
        if rsiValue < 30:
            #Check Flags as well as starting marketTicket
            value = self.NUM
            Check = self.Check
        
            #set up the intial dist of the portfolio as well as starting marketTicket
            if value == 0:
                self.SetHoldings("TQQQ",.70)
                self.SetHoldings("UDOW",.10)
                self.SetHoldings("URTY",.10)
                self.SetHoldings("SPY",.10)
                #Generate a stop Market ticket and a Stop market order that is to sell all Tqqq holdings if price drops below close
                self.stopMarketTicket = self.StopMarketOrder("TQQQ", -holdings_TQQQ, 0.85 * self.highestTQQQPrice)
                self.Debug("enter0")
        
            #Adaptivee Stop Loss Strat
            if self.Securities["TQQQ"].Close > self.highestTQQQPrice:
                self.highestTQQQPrice = self.Securities["TQQQ"].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestTQQQPrice * 0.85
                self.stopMarketTicket.Update(updateFields)
                self.Debug("TQQQ: " + str(self.highestTQQQPrice) + " Stop: " + str(updateFields.StopPrice))
                
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("^UDOW")
                self.Liquidate("URTY")
                self.Liquidate("SPY")
                
            #Set flags to starting values
            self.NUM = 1
            self.HIGH = 0
            self.NUM_Med = 0
        
        
        'Check to see if this is a good Trade based on the current RSI of the TQQQ In this case we are over bought'
        if rsiValue > 70:
            #Check Flags as well as starting marketTicket
            value = self.HIGH
            Check = self.Check
            
            #set up the intial dist of the portfolio
            #Generate a stop Market ticket and a Stop market order that is to sell all Tqqq holdings if price drops below close
            if value == 0:
                self.SetHoldings("TQQQ",.25)
                self.SetHoldings("URTY",.25)
                self.SetHoldings("UDOW",.25)
                self.SetHoldings("SPY",.25)
                self.stopMarketTicket = self.StopMarketOrder("TQQQ", -holdings_TQQQ, 0.90 * self.highestTQQQPrice)
                self.Debug("enter1")
            
            #make sure that the stop ticket was set before updating the adaptive stop fields.
            if value == 1:
                if self.Securities["TQQQ"].Close > self.highestTQQQPrice:
                    self.highestTQQQPrice = self.Securities["TQQQ"].Close
                    updateFields = UpdateOrderFields()
                    updateFields.StopPrice = self.highestTQQQPrice * 0.90
                    self.stopMarketTicket.Update(updateFields)
                    self.Debug("TQQQ: " + str(self.highestTQQQPrice) + " Stop: " + str(updateFields.StopPrice))
           
                
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("UDOW")
                self.Liquidate("URTY")
                self.Liquidate("SPY")
                
                
            #Set flags to starting values
            self.NUM = 0
            self.NUM_Med = 0
            self.High = 1
            
            
        
        #limbo
        else:
            value = self.NUM_Med
            #set up the intial dist of the portfolio
            self.SetHoldings("TQQQ",.50)
            self.SetHoldings("SPY",.15)
            self.SetHoldings("URTY",.15)
            self.SetHoldings("UDOW",.20)
            self.Debug("distrib")
            
    
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("^UDOW")
                self.Liquidate("URTY")
                self.Liquidate("SPY")
            
            #Set flags to starting values
            self.NUM = 0
            self.High = 0
            self.NUM_Med = 1
            
            
    #order
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time