from src.bank.bank_processor import BankProcessor

class BankPipeline:
    def __init__(self):
        self.processor = BankProcessor()
    
    def run_process(self) -> dict:
        """Menjalankan instansiasi data dan memproses output dari BankProcessor."""
        mock_cdc = {
            "op": "C",
            "after": {
                "account_id": "USR-TX-001",
                "full_name": "John Doe",
                "account_status": "ACTIVE",
                "daily_limit": 50000000
            }
        }
        mock_iot = {
            "transaction_id": "TX-001",
            "account_id": "USR-TX-001",
            "amount": 1000000,
            "timestamp": "2022-01-01 00:00:00"
        }

        self.processor.sync_customer(mock_cdc)
        return self.processor.validate_tx(mock_iot)