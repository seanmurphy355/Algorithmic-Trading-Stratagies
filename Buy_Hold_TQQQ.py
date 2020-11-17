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




#Buy and Hold The TQQQ
class QuantumVentralAutosequencers(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2010,1, 1)  #Set Start Date
        self.SetEndDate(2020,10,25)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.Tqqq = self.AddEquity("TQQQ",Resolution.Daily)
        self.Tqqq.SetDataNormalizationMode(DataNormalizationMode.Raw) #set TQQQ

    def OnData(self, data):
        if self.IsWarmingUp:
            return
        
        if not self.Portfolio.Invested:
            self.SetHoldings("TQQQ",1)
        