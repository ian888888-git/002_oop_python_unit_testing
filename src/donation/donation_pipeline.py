from src.donation.donation_processor import DonationProcessor

class DonationPipeline:
    def __init__(self):
        self.processor = DonationProcessor()

    def run_process(self) -> dict:
        mock_donatur = {
            "op": "C",
            "after": {
                "npwz": "USR-TX-001",
                "nama_lengkap": "John Doe",
                "status": "ACTIVE",
                "jenis": "INDIVIDUAL",
                "gender": "L",
                "no_hp": "08123456789"
            }
        }
        mock_donasi = {
            "op": "C",
            "after": {
                "npwz": "USR-TX-001",
                "no_trs": "TR-001",
                "jml_donasi": 1000000,
                "tgl_trs": "2022-01-01 00:00:00",
                "program": "Zakat Mal",
                "kategori": "Zakat",
                "jenis": "TUNAI"
            }
        }

        self.processor.sync_donatur(mock_donatur)
        return self.processor.transaction_dns(mock_donasi)