class WeeklySMAAlgorithm(QCAlgorithm):
    def Initialize(self):
        #
        self.SetStartDate(2009, 6, 1)
        #self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)
        
        # Add equity
        self.symbol = self.AddEquity("QLD", Resolution.Daily).Symbol
        
        # Weekly consolidator
        self.weekly_consolidator = TradeBarConsolidator(timedelta(days=7))
        self.SubscriptionManager.AddConsolidator(self.symbol, self.weekly_consolidator)
        
        # Weekly SMA (using 4 weeks)
        self.sma_period = 20
        self.weekly_sma = SimpleMovingAverage(self.sma_period)
        
        # Update SMA with consolidated weekly bars
        self.weekly_consolidator.DataConsolidated += self.OnWeeklyData

        self.all_time_high = 0


    def OnWeeklyData(self, sender, bar):
        """Updates the SMA with the latest weekly close price."""
        self.weekly_sma.Update(bar.EndTime, bar.Close)
        self.Debug(f"New Weekly SMA: {self.weekly_sma.Current.Value}")

    def OnData(self, data):
        """Trading logic - optional"""
        if not data.Bars.ContainsKey(self.symbol):
            return
        
        close_price = data.Bars[self.symbol].Close
        
        # Update all-time high
        if close_price > self.all_time_high:
            self.all_time_high = close_price
            self.Debug(f"New All-Time High: {self.all_time_high}")

        if not self.weekly_sma.IsReady:
            self.Debug(f"Weekly SMA: {self.weekly_sma.Current.Value}")
            return 

        # Buy Condition: Daily close < Weekly SMA
        if close_price < 0.98*self.weekly_sma.Current.Value and not self.Portfolio[self.symbol].Invested:
            self.SetHoldings(self.symbol, 1)  # Invest 100%
            self.Debug(f"BUY: {self.symbol} at {close_price}, Weekly SMA: {self.weekly_sma.Current.Value}")
            self.frozen_all_time_high = self.all_time_high
            self.bought_price = close_price
        if self.Portfolio[self.symbol].Invested and close_price > 1.1*self.frozen_all_time_high:
        # if self.Portfolio[self.symbol].Invested and close_price > 1.2*self.bought_price:
            self.Liquidate(self.symbol)
            self.Debug(f"SELL: {self.symbol} at {close_price}, Previous All-Time High: {self.all_time_high}")

