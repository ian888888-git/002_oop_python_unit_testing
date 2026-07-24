class Exception(Exception):
    """Base Exception untuk semua error di sistem perbankan ini."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)
    

# 1. Kategori: Error Data Tidak Valid
class DataInvalidError(Exception):
    """Dilemparkan jika struktur data rusak atau tidak sesuai skema."""
    ERR_CDC_STRUCT = "FORMAT_CDC_RUSAK"
    
    def __init__(self, code: str, message: str = None):
        # Jika kode produksi memanggil dengan satu argumen, jadikan argumen tersebut sebagai 'code'
        msg = message or f"Error Code: {code}"
        super().__init__(code, msg)


# 2. Kategori: Error Data Kosong
class DataEmptyError(Exception):
    """Dilemparkan jika ada parameter wajib yang bernilai kosong/null."""
    ERR_ACC_EMPTY = "ACCOUNT_ID_KOSONG"
    
    # Jembatan penyelamat jika kode produksi menggunakan nama ERR_CDC_EMPTY
    ERR_CDC_EMPTY = "ACCOUNT_ID_KOSONG"

    def __init__(self, code: str, message: str = None):
        super().__init__(code, message or f"Error Code: {code}")


# 3. Kategori: Error karena Terfilter Validasi / Ketentuan Aturan Bisnis
class BusinessRuleValidationError(Exception):
    """Dilemparkan jika melanggar kepatuhan atau aturan transaksi perbankan."""
    ERR_NOT_FOUND = "DATA_TIDAK_DITEMUKAN"
    ERR_FROZEN = "REKENING_DIBEKUKAN"
    ERR_LIMIT = "TRANSAKSI_MELEBIHI_LIMIT"
    ERR_AMOUNT_NEGATIVE = "NOMINAL_NEGATIF"
    
    # Ditambahkan berdasarkan baris ke-128 pada kode unit testing Anda
    ERR_ACCOUNT_FROZEN = "REKENING_DIBEKUKAN" 

    def __init__(self, code: str, message: str = None):
        super().__init__(code, message or f"Error Code: {code}")


# 4. Kategori: Error Jenis TypeErrors
class DataTypeMismatchError(Exception):
    """Dilemparkan jika tipe data parameter salah (misal: nominal berupa teks)."""
    ERR_TYPE = "TIPE_DATA_TIDAK_SESUAI"

    def __init__(self, code: str, message: str = None):
        super().__init__(code, message or f"Error Code: {code}")