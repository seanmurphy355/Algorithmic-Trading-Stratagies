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
          # window size
        self.window_size = 14
        self.SetWarmUp(self.window_size)
        
        # Symbols to Trade
        self.equity_symbols = ['TQQQ', 'DJI', '^RUT', 'DUSL', "NDAQ"]
        
        self.SetStartDate(2010,1, 1)  #Set Start Date
        self.SetEndDate(2020,10,25)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.Tqqq = self.AddEquity("TQQQ",Resolution.Daily)
        self.Tqqq.SetDataNormalizationMode(DataNormalizationMode.Raw) #set TQQQ
        self.spy = self.AddEquity("SPY", Resolution.Daily)
        self.spy.SetDataNormalizationMode(DataNormalizationMode.Raw) #set SPY
        self.dji = self.AddEquity("DJI",Resolution.Daily)
        self.dji.SetDataNormalizationMode(DataNormalizationMode.Raw) #DJI set
        self.rut= self.AddEquity("^RUT", Resolution.Daily)
        self.rut.SetDataNormalizationMode(DataNormalizationMode.Raw) #RUT set
        self.Debug("Starting Params taken")
        self.NUM = 0
        self.HIGH = 0
        self.NUM_Med = 0
        self.Rebalance = 0
        self.Check = 1
        self.rsi = self.RSI("TQQQ", 45,  MovingAverageType.Simple, Resolution.Daily)
        '''std = self.STD("TQQQ", 365, Resolution.Minute)'''
        '''history = self.History("TQQQ", 365,Resolution.Minute)'''
 
  
    def OnData(self,data):
        if self.IsWarmingUp:
            return
        
        #Not working at the moment
        if self.Rebalance > 0:
            if self.Rebalance >= 7:
                self.Rebalance = 0
            self.Rebalance += 1
            return
        
        'Set holdings and base data that is to be used'
        rsiValue = self.rsi.Current.Value
        holdings_TQQQ = self.Portfolio['TQQQ'].Quantity
        holdings_SPY = self.Portfolio['SPY'].Quantity
        holdings_RUT = self.Portfolio['^RUT'].Quantity
        holdings_DJI = self.Portfolio['DJI'].Quantity
       
            
        'Check to see if this is a good Trade based on the current RSI of the TQQQ'
        if rsiValue < 30:
            value = self.NUM
            Check = self.Check
            
            #Current daily price        
            Current_TQQQ_Price = self.Securities['TQQQ'].Price
            Current_Rut_Price = self.Securities['^RUT'].Price
            Current_DJI_Price = self.Securities['DJI'].Price
            Current_SPY_Price = self.Securities['SPY'].Price
            
            #set up the intial dist of the portfolio
            if value == 0:
                self.SetHoldings("TQQQ",.70)
                self.SetHoldings("DJI",.10)
                self.SetHoldings("^RUT",.10)
                self.SetHoldings("SPY",.10)
        
            #set up the sell and buy targets for the portfolio
            if value == 0:
                Tqqq_liq_Price = self.Securities['TQQQ'].Price*.40 + self.Securities['TQQQ'].Price
         
                #Stop loss vars
                Tqqq_Limit_price = self.Securities['TQQQ'].Price *.92
                Tqqq_Market_price = self.Securities['TQQQ'].Price *.86
                Tqqq_First_Sell_Target = self.Securities['TQQQ'].Price *.25 + self.Securities['TQQQ'].Price 
                Tqqq_Sec_Sell_Target = self.Securities['TQQQ'].Price *.50 + self.Securities['TQQQ'].Price
                Starting_Hold = self.Portfolio['TQQQ'].Quantity
                cash_out = 1
    

            
                
            #Liquidate if we are up 50% on a traded
            if Tqqq_liq_Price <= Current_TQQQ_Price:
                self.Liquidate("DJI")
                self.Liquidate("^RUT")
                self.Liquidate("SPY")
                self.Liquidate("TQQQ")
            
            
            'Stop loss cases'
            self.StopMarketOrder("TQQQ", -(holdings_TQQQ*.40), Tqqq_Limit_price)
            self.StopMarketOrder("TQQQ",-(holdings_TQQQ), Tqqq_Market_price)
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("^DJI")
                self.Liquidate("^RUT")
                self.Liquidate("SPY")
            
            #Set flags to starting values
            self.NUM = 1
            self.HIGH = 0
            self.NUM_Med = 0
            cash_out = 0
            
    
    
      

        if rsiValue > 70:
            
            value = self.HIGH
            Check = self.Check
            
            #Current daily price        
            Current_TQQQ_Price = self.Securities['TQQQ'].Price
            Current_Rut_Price = self.Securities['^RUT'].Price
            Current_DJI_Price = self.Securities['DJI'].Price
            Current_SPY_Price = self.Securities['SPY'].Price
            
            
            #set up the intial dist of the portfolio
            if value == 0:
                self.SetHoldings("TQQQ",.40)
                self.SetHoldings("^RUT",.20)
                self.SetHoldings("DJI",.20)
                self.SetHoldings("SPY",.20)
                self.Debug("Starting Params taken")
                self.Debug("enter1")
                
            
            #set up the sell and buy targets for the portfolio
            if value == 0:
                Tqqq_liq_Price = self.Securities['TQQQ'].Price*.35 + self.Securities['TQQQ'].Price
                #Stop loss vars
                Tqqq_Limit_price = self.Securities['TQQQ'].Price *.94
                Tqqq_Market_price = self.Securities['TQQQ'].Price *.87
                Tqqq_First_Sell_Target = self.Securities['TQQQ'].Price *.25 + self.Securities['TQQQ'].Price 
                Tqqq_Sec_Sell_Target = self.Securities['TQQQ'].Price *.50 + self.Securities['TQQQ'].Price
                Starting_Hold = self.Portfolio['TQQQ'].Quantity
                self.Debug("enter2")
                cash_out = 1
                
                
            #Liquidate if we are up 35% on a traded
            if Tqqq_liq_Price <= Current_TQQQ_Price:
                self.Liquidate("DJI")
                self.Liquidate("^RUT")
                self.Liquidate("SPY")
                self.Liquidate("TQQQ")
           
           
            self.StopMarketOrder("TQQQ", -(holdings_TQQQ*.40), Tqqq_Limit_price)
            self.StopMarketOrder("TQQQ",-holdings_TQQQ, Tqqq_Market_price)
            
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("^DJI")
                self.Liquidate("^RUT")
                self.Liquidate("SPY")
                
            #Set flags to starting values
            self.NUM = 0
            self.NUM_Med = 0
            self.High = 1
            cash_out = 0
        
            
        else:
            value = self.NUM_Med
            #set up the intial dist of the portfolio
            self.SetHoldings("TQQQ",.50)
            self.SetHoldings("SPY",.15)
            self.SetHoldings("^RUT",.15)
            self.SetHoldings("DJI",.20)
            self.Debug("distrib")
            
            if value == 0:
                #Stop loss vars
                Tqqq_Limit_price = self.Securities['TQQQ'].Price *.90
                Tqqq_Market_price = self.Securities['TQQQ'].Price *.84
          
     
            #after we do our stopMarket order to sell all holdings we now need to liquidate everything
            if holdings_TQQQ == 0:
                self.Liquidate("^DJI")
                self.Liquidate("^RUT")
                self.Liquidate("SPY")
            
            #Set flags to starting values
            self.NUM = 0
            self.High = 0
            self.NUM_Med = 1