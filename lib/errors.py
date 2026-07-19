class Exception(Exception):
    """Base Exception yang disederhanakan murni menggunakan pesan teks bawaan Python."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# 1. Kategori: Error Data Tidak Valid
class DataInvalidError(Exception):
    """Dilemparkan jika struktur data rusak atau tidak sesuai skema."""
    # Menjaga konstanta agar kode produksi tidak melempar AttributeError
    ERR_CDC_STRUCT = "Format struktur CDC rusak atau tidak memiliki key 'op' / 'after'."

    def __init__(self, message: str = None):
        # Jika dipanggil tanpa argumen, otomatis pakai pesan default sesuai unit testing
        msg = message or self.ERR_CDC_STRUCT
        super().__init__(msg)


# 2. Kategori: Error Data Kosong
class DataEmptyError(Exception):
    """Dilemparkan jika ada parameter wajib yang bernilai kosong/null."""
    ERR_ACC_EMPTY = "Field 'account_id' kosong atau absen di dalam payload CDC."
    ERR_CDC_EMPTY = "Field 'account_id' kosong atau absen di dalam payload CDC."

    def __init__(self, message: str = None):
        msg = message or self.ERR_ACC_EMPTY
        super().__init__(msg)


# 3. Kategori: Error karena Terfilter Validasi / Ketentuan Aturan Bisnis
class BusinessRuleValidationError(Exception):
    """Dilemparkan jika melanggar kepatuhan atau aturan transaksi perbankan."""
    ERR_NOT_FOUND = "Rekening transaksi belum terdaftar di memori lokal."
    ERR_FROZEN = "Transaksi ditolak. Akun nasabah sedang dibekukan (FROZEN)."
    ERR_LIMIT = "Transaksi ditolak. Nominal melewati daily limit nasabah."

    def __init__(self, message: str):
        # Karena di kode produksi Anda memanggil seperti: raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_NOT_FOUND)
        # Maka argumen 'message' yang masuk sebenarnya adalah teks konstanta itu sendiri.
        super().__init__(message)


# 4. Kategori: Error Jenis TypeErrors
class DataTypeMismatchError(Exception):
    """Dilemparkan jika tipe data parameter salah (misal: nominal berupa teks)."""
    ERR_TYPE = "Tipe data nominal 'amount' tidak valid (Harus integer atau float)."

    def __init__(self, message: str = None):
        msg = message or self.ERR_TYPE
        super().__init__(msg)