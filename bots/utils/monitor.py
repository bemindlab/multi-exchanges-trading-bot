from flask import Flask, render_template, jsonify
import threading
import logging
from datetime import datetime
from typing import Dict, List
import json

app = Flask(__name__)
logger = logging.getLogger(__name__)

class Monitor:
    def __init__(self):
        self.trades: List[Dict] = []
        self.risk_metrics: Dict = {}
        self.bot_status: Dict = {
            'is_running': False,
            'last_update': None,
            'mode': None,
            'pairs': []
        }
        self._start_monitor()

    def _start_monitor(self):
        """เริ่มต้น Flask server ในเธรดแยก"""
        threading.Thread(target=self._run_flask, daemon=True).start()

    def _run_flask(self):
        """รัน Flask server"""
        app.run(host='0.0.0.0', port=5001)

    def update_trade(self, trade_data: Dict):
        """อัพเดทข้อมูลการเทรด"""
        trade_data['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade_data)
        logger.info(f"Updated trade: {trade_data}")

    def update_risk_metrics(self, metrics: Dict):
        """อัพเดทเมตริกความเสี่ยง"""
        self.risk_metrics = metrics
        logger.info(f"Updated risk metrics: {metrics}")

    def update_bot_status(self, status: Dict):
        """อัพเดทสถานะบอท"""
        self.bot_status = status
        self.bot_status['last_update'] = datetime.now().isoformat()
        logger.info(f"Updated bot status: {status}")

# Flask routes
@app.route('/')
def dashboard():
    """แสดงหน้า dashboard"""
    return render_template('dashboard.html')

@app.route('/api/trades')
def get_trades():
    """API สำหรับดึงข้อมูลการเทรด"""
    return jsonify(monitor.trades)

@app.route('/api/risk-metrics')
def get_risk_metrics():
    """API สำหรับดึงเมตริกความเสี่ยง"""
    return jsonify(monitor.risk_metrics)

@app.route('/api/bot-status')
def get_bot_status():
    """API สำหรับดึงสถานะบอท"""
    return jsonify(monitor.bot_status)

# สร้าง instance ของ Monitor
monitor = Monitor() 