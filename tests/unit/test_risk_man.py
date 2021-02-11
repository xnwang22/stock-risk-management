from risk_manager import RiskManager
class TestRiskManager:
    def test_symbols(self):
        rm = RiskManager({'sym':['qqq']})
        rm.to_csv()
