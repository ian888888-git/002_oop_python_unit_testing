import pytest 
from src.bank.bank_processor import BankProcessor
from lib.errors import(
    DataInvalidError,
    DataEmptyError,
    DataTypeMismatchError,
    BusinessRuleValidationError
)

# =====================================================================
# FIXTURES: Penyedia Data Tiruan Lengkap Berbagai Skenario Event
# =====================================================================
@pytest.fixture
def mock_cdc_insert():
    """Mock data CDC saat ada nasabah baru terdaftar dengan status ACTIVE."""
    return {
        "op":"C",
        "after":{
            "account_id":"USR-TX-001",
            "full_name":"John Doe",
            "account_status":"ACTIVE",
            "daily_limit":50000000
        }
    }
@pytest.fixture
def mock_cdc_delete():
    """Mock data CDC saat nasabah dihapus dari database pusat."""
    return {
        "op":"D",
        "before":{
            "account_id":"USR-TX-001"
        },
        "after": None
    }
@pytest.fixture
def mock_cdc_frozen():
    """Mock data CDC untuk nasabah yang status rekeningnya FROZEN."""
    return {
        "op":"U",
        "after":{
            "account_id":"USR-TX-001",
            "full_name":"John Doe",
            "account_status":"FROZEN",
            "daily_limit":50000000
        }
    }
@pytest.fixture
def mock_iot_transactions():
    """Mock data transaksi normal dari mesin ATM (IoT)."""
    return {
        "account_id":"USR-TX-001",
        "transaction_id":"TX-001",
        "transaction_status":"CLEAN",
        "amount":1000000,
        "timestamp":"2022-01-01T10:00:00Z"
    }
# =====================================================================
# CLASS TESTING (OOP): Cakupan Pengujian Lengkap Berbasis Custom Lib
# =====================================================================
class TestBankProcessor:
    # -----------------------------------------------------------------
    # BLOK UJI 1: Validasi & Filter Fungsi sync_customer (CDC)
    # -----------------------------------------------------------------
    def test_sync_customer_success(self, mock_cdc_insert):
        """Memastikan data CDC bertipe INSERT berhasil masuk ke database memori."""
        db = BankProcessor()
        db.sync_customer(mock_cdc_insert)

        assert "USR-TX-001" in db.customers
        assert db.customers["USR-TX-001"]["full_name"] == "John Doe"
        assert db.customers["USR-TX-001"]["account_status"] == "ACTIVE"
        assert db.customers["USR-TX-001"]["daily_limit"] == 50000000
    
    def test_sync_customer_format_rusak(self):
        """Memastikan DataInvalidError jika skema data CDC tidak memiliki key 'op' atau 'after'."""
        db = BankProcessor() 
        cdc_sampah = {"data_acak": "tidak_valid"}

        with pytest.raises(DataInvalidError) as exc_info:
            db.sync_customer(cdc_sampah)
        assert str(exc_info.value.code) == DataInvalidError.ERR_CDC_STRUCT
    
    def test_sync_customer_account_id_kosong(self):
        """Memastikan DataEmptyError jika key 'account_id' absen di dalam payload CDC."""
        db = BankProcessor()
        cdc_tanpa_acc_id = {
            "op":"C",
            "after":{
                "full_name":"John Doe",
                "account_status":"ACTIVE",
                "daily_limit":50000000
            }
        }
        with pytest.raises(DataEmptyError) as exc_info:
            db.sync_customer(cdc_tanpa_acc_id)
        assert str(exc_info.value.code) == DataEmptyError.ERR_CDC_EMPTY
    
    def test_sync_customer_delete_success(self, mock_cdc_insert, mock_cdc_delete):
        """Memastikan data nasabah di memori langsung terhapus jika menerima event CDC DELETE."""
        db = BankProcessor()
        # Ambil ID target secara transparan dari data mock agar alurnya jelas
        target_account_id = mock_cdc_insert["after"]["account_id"]
        # LANGKAH 1: Masukkan data nasabah baru (INSERT)
        db.sync_customer(mock_cdc_insert)
        # Pengecekan Informatif: Pastikan datanya BENAR-BENAR MASUK dulu sebelum kita tes hapus
        assert target_account_id in db.customers, f"Gagal mempersiapkan data: Akun {target_account_id} tidak terdaftar di memori."
        # LANGKAH 2: Jalankan aksi penghapusan (DELETE)
        db.sync_customer(mock_cdc_delete)
        # Pengecekan Informatif: Pastikan datanya BENAR-BENAR HAPUS
        assert target_account_id not in db.customers, f"Gagal mempersiapkan data: Akun {target_account_id} masih ada di memori."

    # -----------------------------------------------------------------
    # BLOK UJI 2: Validasi & Filter Fungsi validate_tx (IoT)
    # -----------------------------------------------------------------
    def test_error_not_syncronized(self, mock_iot_transactions):
        """Skenario: Transaksi ditolak karena rekening belum terdaftar di memori."""
        iot_db = BankProcessor()
        with pytest.raises(BusinessRuleValidationError) as exc_info:
            iot_db.validate_tx(mock_iot_transactions)
        assert str(exc_info.value.code) == BusinessRuleValidationError.ERR_NOT_FOUND
    
    def test_error_account_frozen(self, mock_cdc_frozen, mock_iot_trsansactions):
        """Skenario: Transaksi ditolak jika status_rekening nasabah bernilai 'FROZEN'."""
        iot_db = BankProcessor()
        iot_db.sync_customer(mock_cdc_frozen)
        with pytest.raises(BusinessRuleValidationError) as exc_info:
            iot_db.validate_tx(mock_iot_trsansactions)
        assert str(exc_info.value.code) == BusinessRuleValidationError.ERR_ACCOUNT_FROZEN
    
    def test_error_over_limit(self, mock_cdc_insert, mock_iot_transactions):
        """Skenario: Transaksi ditolak jika nominal IoT melewati batasan limit nasabah."""
        iot_db = BankProcessor()
        iot_db.sync_customer(mock_cdc_insert)
        iot_limit = mock_iot_transactions.copy()
        iot_limit["amount"] = 60000000
        with pytest.raises(BusinessRuleValidationError) as exc_info:
            iot_db.validate_tx(iot_limit)
        assert str(exc_info.value.code) == BusinessRuleValidationError.ERR_LIMIT
    
    def test_error_missmatch_type(self, mock_cdc_insert, mock_iot_transactions):
        """Skenario: Menolak transaksi jika tipe data amount berupa string (Type Mismatch)."""
        db = BankProcessor()
        db.sync_customer(mock_cdc_insert)

        iot_amount_string = mock_iot_transactions.copy()
        iot_amount_string["amount"] = "1000000"

        with pytest.raises(DataTypeMismatchError) as exc_info:
            db.validate_tx(iot_amount_string)
        assert str(exc_info.value.code) == DataTypeMismatchError.ERR_TYPE
    
    # -----------------------------------------------------------------
    # BLOK UJI 3: Skenario Transaksi Sukses (Happy Path)
    # -----------------------------------------------------------------
    def test_success_validate_tx(self, mock_cdc_insert, mock_iot_transactions):
        """Memastikan transaksi IoT yang memenuhi semua kriteria bisnis berhasil diproses."""
        db = BankProcessor()
        # 1. Daftarkan nasabah ke memori terlebih dahulu via CDC
        db.sync_customer(mock_cdc_insert)
        # 2. Proses transaksi ATM (IoT) yang valid
        result = db.validate_tx(mock_iot_transactions)
        # 3. Verifikasi output data dan ketegasan status akhir
        assert result["account_id"] == "TRS-IOT-001"
        assert result["customer_id"] == "USR-TX-001"
        assert result["full_name"] == "John Doe"
        assert result["transaction_id"] == "TX-001"
        assert result["transaction_status"] == "CLEAN"
        assert result["account_status"] == "ACTIVE"
        assert result["amount"] == 1000000
        assert "processed_at" in result