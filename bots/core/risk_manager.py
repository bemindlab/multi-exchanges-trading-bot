import logging
from datetime import datetime, timedelta
from typing import Dict, List

class RiskManager:
    def __init__(self, max_daily_loss: float = 100, max_position_size: float = 1000):
        self.max_daily_loss = max_daily_loss  # USDT
        self.max_position_size = max_position_size  # USDT
        self.daily_trades: List[Dict] = []
        self.logger = logging.getLogger(__name__)

    def can_open_position(self, pair: str, amount: float, price: float) -> bool:
        """
        ตรวจสอบว่าสามารถเปิด position ใหม่ได้หรือไม่
        """
        # ตรวจสอบขนาด position
        position_value = amount * price
        if position_value > self.max_position_size:
            self.logger.warning(f"Position size {position_value} USDT exceeds maximum {self.max_position_size} USDT")
            return False

        # ตรวจสอบการขาดทุนรายวัน
        daily_pnl = self.calculate_daily_pnl()
        if daily_pnl < -self.max_daily_loss:
            self.logger.warning(f"Daily loss {daily_pnl} USDT exceeds maximum {self.max_daily_loss} USDT")
            return False

        return True

    def add_trade(self, pair: str, amount: float, price: float, side: str):
        """
        เพิ่มการเทรดใหม่เข้าไปในประวัติ
        """
        trade = {
            'timestamp': datetime.now(),
            'pair': pair,
            'amount': amount,
            'price': price,
            'side': side,
            'value': amount * price
        }
        self.daily_trades.append(trade)
        self.logger.info(f"Added trade: {trade}")

    def calculate_daily_pnl(self) -> float:
        """
        คำนวณกำไร/ขาดทุนรายวัน
        """
        today = datetime.now().date()
        daily_trades = [t for t in self.daily_trades if t['timestamp'].date() == today]
        
        pnl = 0
        for trade in daily_trades:
            if trade['side'] == 'buy':
                pnl -= trade['value']
            else:
                pnl += trade['value']
        
        return pnl

    def cleanup_old_trades(self):
        """
        ลบประวัติการเทรดที่เก่ากว่า 24 ชั่วโมง
        """
        cutoff_time = datetime.now() - timedelta(days=1)
        self.daily_trades = [t for t in self.daily_trades if t['timestamp'] > cutoff_time]
        self.logger.info(f"Cleaned up old trades. Remaining trades: {len(self.daily_trades)}")

    def get_risk_metrics(self) -> Dict:
        """
        ดึงข้อมูลเมตริกความเสี่ยง
        """
        return {
            'daily_pnl': self.calculate_daily_pnl(),
            'max_daily_loss': self.max_daily_loss,
            'max_position_size': self.max_position_size,
            'total_trades_today': len([t for t in self.daily_trades if t['timestamp'].date() == datetime.now().date()])
        } 