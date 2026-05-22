import backtrader as bt

class DeTimeSignalData(bt.feeds.PandasData):
    lines = ('detime_signal',)
    params = (('detime_signal', -1),)

class DeTimeSignalStrategy(bt.Strategy):
    params = dict(stake=10)

    def next(self):
        sig = self.data.detime_signal[0]
        if sig > 0 and not self.position:
            self.buy(size=self.params.stake)
        elif sig <= 0 and self.position:
            self.sell(size=self.params.stake)
