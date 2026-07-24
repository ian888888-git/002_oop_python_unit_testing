from datetime import datetime
# Impor kategori error dari library internal kita
from lib.errors import (
    DataInvalidError,
    DataEmptyError,
    DataTypeMismatchError,
    BusinessRuleValidationError
)

class BankProcessor:
    """Processor transaksi ATM (IoT) dan sinkronisasi data nasabah (CDC)."""
    def __init__(self):
        # State store lokal di memori
        self.customers = {}
    
    def sync_customer(self, cdc: dict) -> dict:
        """Menangkap dan menyinkronkan data nasabah dari PostgreSQL CDC (Insert, Update, Delete)."""
        # 1. Validasi struktur utama (Kategori: Data Invalid)
        if "op" not in cdc: 
            raise DataInvalidError(DataInvalidError.ERR_CDC_STRUCT)
        
        op_type = cdc["op"]
        payload = cdc.get("after")

        # 2. Penanganan Operasi DELETE ("D")
        if op_type == "D":
            # Ambil account_id dari 'before' jika 'after' bernilai None
            account_id = cdc.get("before", {}).get("account_id") if payload is None else payload.get("account_id")
            if not account_id:
                raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
            
            # Hapus data nasabah dari memori
            self.customers.pop(account_id, None)
            return {}

        # 3. Validasi payload 'after' untuk operasi INSERT ("C") dan UPDATE ("U")
        if not payload:
            raise DataInvalidError(DataInvalidError.ERR_CDC_STRUCT)

        acc_id = payload.get("account_id")
        if not acc_id:
            raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)

        # 4. Penanganan Operasi UPDATE ("U")
        if op_type == "U":
            # Jika data nasabah belum ada di memori saat update datang,
            # kita daftarkan data baru dari payload 'after'
            if acc_id not in self.customers:
                self.customers[acc_id] = {
                    "account_id": acc_id,
                    "full_name": payload.get("full_name"),
                    "account_status": payload.get("account_status"),
                    "daily_limit": payload.get("daily_limit", 0)
                }
            else:
                # Perbarui data nasabah di memori dengan nilai baru dari payload 'after'
                self.customers[acc_id].update({
                    "full_name": payload.get("full_name", self.customers[acc_id]["full_name"]),
                    "account_status": payload.get("account_status", self.customers[acc_id]["account_status"]),
                    "daily_limit": payload.get("daily_limit", self.customers[acc_id]["daily_limit"])
                })
            return self.customers[acc_id]

        # 5. Penanganan Operasi INSERT / CREATE ("C")
        elif op_type == "C":
            self.customers[acc_id] = {
                "account_id": acc_id,
                "full_name": payload.get("full_name"),
                "account_status": payload.get("account_status"),
                "daily_limit": payload.get("daily_limit", 0)
            }
            return self.customers[acc_id]

        return {}
    
    def validate_tx(self, iot: dict) -> dict:
        """Memproses data transaksi IoT dan cek anomali berdasar batasan bisnis."""
        acc_id = iot.get("account_id")
        amount = iot.get("amount", 0)

        # 1. Validasi Tipe Data Nominal (Kategori: Type Mismatch)
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise DataTypeMismatchError(DataTypeMismatchError.ERR_TYPE)
        
        # 2. Validasi Keberadaan Rekening (Kategori: Business Rule)
        if acc_id not in self.customers:
            raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_NOT_FOUND)
        nasabah = self.customers[acc_id]

        # 3. Validasi Status Rekening (Kategori: Business Rule)
        if nasabah["account_status"] != "ACTIVE":
            raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_ACCOUNT_FROZEN)

        # 4. Validasi Limit Transaksi (Kategori: Business Rule)
        if amount > nasabah["daily_limit"]: 
            raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_LIMIT)
        
        return {
            "account_id": acc_id,
            "full_name": nasabah["full_name"],
            "transaction_id": iot.get("transaction_id"),
            "account_status": nasabah["account_status"],
            "transaction_status": "CLEAN",
            "amount": amount,
            "timestamp": iot.get("timestamp"),   
            "processed_at": datetime.now().isoformat()
        }