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

    # 2. Penanganan operasi DELETE
    if op_type == "D":
        # Ambil account_id dari 'before' jika 'after' bernilai None
        npwz = cdc.get("before", {}).get("npwz") if payload is None else payload.get("npwz")
        if not npwz:
            raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
        # Hapus data nasabah dari memori
        self.donaturs.pop("npwz", None)
        return {}
    
    # 3. Validasi payload 'after' untuk operasi INSERT ("C") dan UPDATE ("U")
    if not payload:
        raise DataInvalidError(DataInvalidError.ERR_CDC_STRUCT)
    
    # 4. Validasi field wajib (NPWZ: Data Empty)
    npwz = payload.get("npwz")
    if not npwz:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)
    
    # 5. Penanganan Operasi UPDATE ("U")
    if op_type == "U":
        # Jika data nasabah belum ada di memori saat update datang,
        # kita daftarkan data baru dari payload 'after'
        if npwz not in self.donaturs:
            self.donaturs[npwz] = {
                "npwz": npwz,
                "nama_lengkap": payload.get("nama_lengkap"),
                "status": payload.get("status"),
                "jenis": payload.get("jenis"),
                "gender": payload.get("gender"),
                "no_hp": payload.get("no_hp")
            }
        else:
            # Perbarui data nasabah di memori dengan nilai baru dari payload 'after'
            self.donaturs[npwz].update({
                "nama_lengkap": payload.get("nama_lengkap", self.donaturs[npwz].get("nama_lengkap")),
                "status": payload.get("status", self.donaturs[npwz].get("status")),
                "jenis": payload.get("jenis", self.donaturs[npwz].get("jenis")),
                "gender": payload.get("gender", self.donaturs[npwz].get("gender")),
                "no_hp": payload.get("no_hp", self.donaturs[npwz].get("no_hp"))
            })
        return self.donaturs[npwz]
    # 5. Penanganan Operasi INSERT / CREATE ("C")
    elif(op_type == "C"):
        self.donaturs[npwz] = {
            "npwz": npwz,
            "nama_lengkap": payload.get("nama_lengkap"),
            "status": payload.get("status"),
            "jenis": payload.get("jenis"),
            "gender": payload.get("gender"),
            "no_hp": payload.get("no_hp")
        }
        return self.donaturs[npwz]
    return {}

def transaction_dns(self, donation_cdc: dict) -> dict:
    """Memproses data transaksi Donasi dari objek CDC."""
    # Ekstrak payload dari struktur CDC
    payload = donation_cdc.get("after") if isinstance(donation_cdc, dict) else None

    if not payload:
        payload = donation_cdc if isinstance(donation_cdc, dict) else {}

    npwz = payload.get("npwz")
    no_trs = payload.get("no_trs")
    jml_donasi = payload.get("jml_donasi")
    tgl_trs = payload.get("tgl_trs")
    program = payload.get("program")
    kategori = payload.get("kategori")
    jenis = payload.get("jenis")

    # 1. Validasi NPWZ Kosong
    if npwz is None:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)

    # 2. Validasi Program Kosong
    if not program:
        raise DataEmptyError(DataEmptyError.ERR_CDC_EMPTY)

    # 3. Validasi Tipe Data Nominal (jml_donasi)
    if not isinstance(jml_donasi, (int, float)) or isinstance(jml_donasi, bool):
        raise DataTypeMismatchError(DataTypeMismatchError.ERR_TYPE)

    # 4. Validasi jml_donasi Nilai Negatif
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