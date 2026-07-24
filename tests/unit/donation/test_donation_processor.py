import pytest 
from src.donation.donation_processor import DonationProcessor
from lib.errors import(
    DataInvalidError,
    DataEmptyError,
    DataTypeMismatchError,
    BusinessRuleValidationError
)

@pytest.fixture
def mock_donatur_save():
    return{
        "op":"C",
        "after":{
            "npwz":"3302260001",
            "nama_lengkap":"John Doe",
            "status":"ACTIVE",
            "jenis":"INDIVIDUAL",
            "gender":"L",
            "no_hp":"08123456789"
        }
    }

@pytest.fixture 
def mock_donatur_update():
    return{
        "op":"U",
        "before":{
            "npwz":"3302260001",
            "nama_lengkap":"John Doe",
            "status":"ACTIVE",
            "jenis":"INDIVIDUAL",
            "gender":"L",
            "no_hp":"08123456789"
        },
        "after":{
            "npwz":"3302260001",
            "nama_lengkap":"John Doe",
            "status":"INACTIVE",
            "jenis":"INDIVIDUAL",
            "gender":"L",
            "no_hp":"08123456789"
        }
    }

@pytest.fixture
def mock_donatur_delete():
    return{
        "op":"D",
        "before":{
            "npwz":"3302260001"
        },
        "after": None
    }

@pytest.fixture
def mock_donasi():
    return{
        "op":"C",
        "after":{
            "npwz":"3302260001",
            "no_trs":"TRS-0001",
            "jml_donasi":1000000,
            "tgl_trs":"2022-01-01",
            "program":"Zakat Mal",
            "kategori":"Zakat",
            "jenis":"TUNAI"
        }
    }
class TestDonationProcessor:
    # -----------------------------------------
    # 1.A.Testing Invalid Data Synchronization
    # -----------------------------------------
    def test_sync_donatur_invalid(self): 
        db = DonationProcessor()
        data_invalid = {"xxx":"yyy"}
        # Data doesn't have valid key "op"
        if "op" not in data_invalid or "after" not in data_invalid:
            with pytest.raises(DataInvalidError) as exc_info: 
                db.sync_donatur(data_invalid)
            assert str(exc_info.value.code) == DataInvalidError.ERR_CDC_STRUCT

    # -----------------------------------------
    # 1.B.Testing NPWZ Empty Data Synchronization
    # -----------------------------------------
    def test_sync_donatur_npwz_empty(self):
        db = DonationProcessor()
        data_empty = {
            "op":"C",
            "after":{
                "npwz":None
            }
        }
        with pytest.raises(DataEmptyError) as exc_info:
            db.sync_donatur(data_empty)
        assert str(exc_info.value.code) == DataEmptyError.ERR_CDC_EMPTY

# -----------------------------------------
    # 1.C.Testing Delete Data Synchronization
    # -----------------------------------------
    def test_sync_donatur_delete(self, mock_donatur_save, mock_donatur_delete):
        db = DonationProcessor() 
        # Simpan data donatur terlebih dahulu
        db.sync_donatur(mock_donatur_save)
        
        # Jalankan sinkronisasi delete
        target_delete = db.sync_donatur(mock_donatur_delete)
        assert target_delete is not None

    # -----------------------------------------
    # 1.D.Testing Update Data Synchronization
    # -----------------------------------------
    def test_sync_donatur_update(self, mock_donatur_update):
        db = DonationProcessor()
        data_update = db.sync_donatur(mock_donatur_update)
        assert data_update["status"] == "INACTIVE"

    # -----------------------------------------
    # 1.E.Testing Save Data Synchronization
    # -----------------------------------------
    def test_sync_donatur_save(self, mock_donatur_save):
        db = DonationProcessor()
        data_save = db.sync_donatur(mock_donatur_save)
        assert data_save["npwz"] == "3302260001"
        assert data_save["nama_lengkap"] == "John Doe"
        assert data_save["status"] == "ACTIVE"
        assert data_save["jenis"] == "INDIVIDUAL"
        assert data_save["gender"] == "L"
        assert data_save["no_hp"] == "08123456789"

    # -----------------------------------------
    # 2.A.Testing Mismatch Data Synchronization
    # -----------------------------------------
    def test_sync_missmatch_data(self, mock_donasi):
        db = DonationProcessor()
        data_mismatch = mock_donasi.copy()
        data_mismatch["after"]["jml_donasi"] = "1000000"
        with pytest.raises(DataTypeMismatchError) as exc_info:
            db.transaction_dns(data_mismatch)
        assert str(exc_info.value.code) == DataTypeMismatchError.ERR_TYPE

    # -----------------------------------------
    # 2.B.Testing NPWZ Empty Data Synchronization
    # -----------------------------------------
    def test_sync_donasi_npwz_empty(self, mock_donasi):
        db = DonationProcessor()
        data_empty = mock_donasi.copy()
        data_empty["after"]["npwz"] = None
        with pytest.raises(DataEmptyError) as exc_info:
            db.transaction_dns(data_empty)
        assert str(exc_info.value.code) == DataEmptyError.ERR_CDC_EMPTY

    # ----------------------------------------------------
    # 2.C.Testing Program Empty Data Synchronization
    # ----------------------------------------------------
    def test_sync_donasi_program_empty(self, mock_donasi):
        db = DonationProcessor()
        data_empty = mock_donasi.copy()
        data_empty["after"]["program"] = None
        with pytest.raises(DataEmptyError) as exc_info:
            db.transaction_dns(data_empty)
        assert str(exc_info.value.code) == DataEmptyError.ERR_CDC_EMPTY

    # ----------------------------------------------------
    # 2.D.Testing Jml Donasi Negative Data Synchronization
    # ----------------------------------------------------
    def test_sync_donasi_jml_donasi_negative(self, mock_donasi): 
        db = DonationProcessor()
        data_negative = mock_donasi.copy()
        data_negative["after"]["jml_donasi"] = -1000000
        with pytest.raises(BusinessRuleValidationError) as exc_info:
            db.transaction_dns(data_negative)
        assert str(exc_info.value.code) == BusinessRuleValidationError.ERR_AMOUNT_NEGATIVE

    # ----------------------------------------------------
    # 2.E.Testing Success Data Synchronization
    # ----------------------------------------------------
    def test_sync_succes_donasi(self, mock_donasi):
        db = DonationProcessor()
        data_donasi = db.transaction_dns(mock_donasi)
        assert data_donasi["npwz"] == "3302260001"
        assert data_donasi["no_trs"] == "TRS-0001"
        assert data_donasi["jml_donasi"] == 1000000
        assert data_donasi["tgl_trs"] == "2022-01-01"
        assert data_donasi["program"] == "Zakat Mal"
        assert data_donasi["kategori"] == "Zakat"
        assert data_donasi["jenis"] == "TUNAI"