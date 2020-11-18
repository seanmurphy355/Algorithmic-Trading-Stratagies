class UncoupledNadionCoreWave(QCAlgorithm):
    
    currentBar = None
    
    def Initialize(self):
        self.SetStartDate(2010, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        self.AddEquity("URTY", Resolution.Daily)


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''

        if not self.Portfolio.Invested:
            self.SetHoldings("URTY", 1)