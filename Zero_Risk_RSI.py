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

    
    def Initialize(self):
          # window size
        self.window_size = 14
        self.SetWarmUp(self.window_size)
        
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
        self.rsi = self.RSI("TQQQ", 60,  MovingAverageType.Simple, Resolution.Daily)

  
    def OnData(self,data):
        if self.IsWarmingUp:
            return
        
        
        'Set holdings and base data that is to be used'
        rsiValue = self.rsi.Current.Value
        holdings_TQQQ = self.Portfolio['TQQQ'].Quantity
        holdings_SPY = self.Portfolio['SPY'].Quantity
        holdings_RUT = self.Portfolio['URTY'].Quantity
        holdings_UDOW = self.Portfolio['UDOW'].Quantity
       
            
        'Check to see if this is a good Trade based on the current RSI of the TQQQ in this case we are over sold '
        if rsiValue < 30:
       
            #set up the intial dist of the portfolio as well as starting marketTicket
    
            self.SetHoldings("TQQQ",.70)
            self.SetHoldings("UDOW",.10)
            self.SetHoldings("URTY",.10)
            self.SetHoldings("SPY",.10)
        
        'Check to see if this is a good Trade based on the current RSI of the TQQQ In this case we are over bought'
        if rsiValue > 70:
        
            #set up the intial dist of the portfolio
            #Generate a stop Market ticket and a Stop market order that is to sell all Tqqq holdings if price drops below close
         
            self.SetHoldings("TQQQ",.25)
            self.SetHoldings("URTY",.25)
            self.SetHoldings("UDOW",.25)
            self.SetHoldings("SPY",.25)
           
        else:

            self.SetHoldings("TQQQ",.50)
            self.SetHoldings("SPY",.15)
            self.SetHoldings("URTY",.15)
            self.SetHoldings("UDOW",.20)
            self.Debug("distrib")