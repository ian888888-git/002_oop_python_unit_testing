from lib.errors import(
    DataInvalidError,
    DataEmptyError,
    DataTypeMismatchError,
    BusinessRuleValidationError
)

class DonationProcessor:
    """ Menangkap dan menyinkronkan data donatur dan transaksi dari PostgreSQL CDC."""
    def __init__(self):
        self.donaturs ={}

def sync_donatur(self, cdc: dict) -> dict:
    """Menangkap Data Dari PostgreSQL"""
     # 1. Validasi struktur utama (Kategori: Data Invalid)
    if "op" not in cdc or "after" not in cdc:
        raise DataInvalidError(DataInvalidError.ERR_CDC_STRUCT)
    op_type = cdc["op"]
    payload = cdc["after"]
    # Penanganan operasi DELETE
    if op_type == "D":
        npwz = cdc.get("before", {}).get("npwz") if payload is None else payload.get("npwz")
        if not npwz:
            raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
        self.donaturs.pop("npwz", None)
        return {}
    # 2. Validasi field wajib (Kategori: Data Empty)
    npwz = payload.get("npwz")
    if not npwz:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
    # Update data
    if op_type == "U":
        if npwz not in self.donaturs:
            raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
        # Perbarui data
        self.donaturs[npwz] = {
            "nama_lengkap": payload.get("nama_lengkap", self.donaturs[npwz].get("nama_lengkap")),
            "status": payload.get("status", self.donaturs[npwz].get("status")),
            "jenis": payload.get("jenis", self.donaturs[npwz].get("jenis")),
            "gender": payload.get("gender", self.donaturs[npwz].get("gender")),
            "no_hp": payload.get("no_hp", self.donaturs[npwz].get("no_hp"))
        }
    # 3. Simpan data ke memori lokal 
    self.donaturs[npwz] = {
        "npwz": payload.get("npwz"),
        "nama_lengkap": payload.get("nama_lengkap"),
        "status": payload.get("status"),
        "jenis": payload.get("jenis"),
        "gender": payload.get("gender"),
        "no_hp": payload.get("no_hp")
    }
    return self.donaturs[npwz]

def transaction_dns(self, donation: dict) -> dict:
    """Memproses data transaksi Donasi."""
    npwz = donation.get("npwz")
    no_trs = donation.get("no_trs")
    jml_donasi = donation.get("jml_donasi", 0)
    tgl_trs = donation.get("tgl_trs")
    program = donation.get("program")
    kategori = donation.get("kategori")
    jenis = donation.get("jenis")

    # 1. Validasi Tipe Data Nominal (jml_donasi)
    if not isinstance(jml_donasi, (int, float)):
        raise DataTypeMismatchError(DataTypeMismatchError.ERR_TYPE)
    # 2. Vaidasi Keberadaan Donatur (npwz)
    if npwz not in self.donaturs: 
        raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_NOT_FOUND)
    # 3. Validasi Npwz Kosong 
    if not npwz:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
    # 4. Validasi Program Kosong
    if not program:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
    # 5. Validasi jml_donasi Negative Value
    if jml_donasi < 0:
        raise BusinessRuleValidationError(BusinessRuleValidationError.ERR_AMOUNT_NEGATIVE)
    return {
        "npwz": npwz,
        "no_trs": no_trs,
        "jml_donasi": jml_donasi,
        "tgl_trs": tgl_trs,
        "program": program,
        "kategori": kategori,
        "jenis": jenis
    } 