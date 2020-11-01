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

    def Initialize(self):
        self.SetStartDate(2010,1, 1)  #Set Start Date
        self.SetEndDate(2020,12,25)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.AddEquity("TQQQ",Resolution.Daily)
        self.AddEquity("SPY", Resolution.Daily)
        self.Debug("Starting Params taken")
        
        self.rsi = self.RSI("TQQQ", 10,  MovingAverageType.Simple, Resolution.Daily)
        '''std = self.STD("TQQQ", 365, Resolution.Minute)'''
        '''history = self.History("TQQQ", 365,Resolution.Minute)'''
 
  
    def OnData(self,data):
        
        rsiValue = self.rsi.Current.Value
        holdings_TQQQ = self.Portfolio['TQQQ'].Quantity
        holdings_SPY = self.Portfolio['SPY'].Quantity

        if rsiValue < 30:
            self.SetWarmUp(200)
            self.SetHoldings("TQQQ",1.0)
            self.SetHoldings("SPY",0)
            self.Debug("in TQQQ")
            if holdings_SPY >= 0:
                self.Liquidate("SPY")
                

        if rsiValue > 70:
            self.SetWarmUp(200)
            self.SetHoldings("TQQQ",0)
            self.SetHoldings("SPY",1.0)
            self.Debug("Starting Params taken")
            self.Debug("in SPY")
            if holdings_TQQQ:
                self.Liquidate("TQQQ")
            
        else:
            self.SetHoldings("TQQQ",1.0)
            self.SetHoldings("SPY",0)
            

        '''if (self.std < 1.2):
            self.SetHoldings("TQQQ",1.0)
            self.SetHoldings("SQQQ",0)
        else:
            self.SetHoldings("TQQQ",0)
            self.SetHoldings("SQQQ",1.0)'''