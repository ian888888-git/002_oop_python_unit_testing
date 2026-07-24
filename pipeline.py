from src.bank.bank_pipeline import BankPipeline
from src.donation.donation_pipeline import DonationPipeline

class PipelineRunner:
    def __init__(self):
        # Mendaftarkan seluruh module pipeline yang aktif ke dalam list internal
        self.registry = [
            BankPipeline(),
            DonationPipeline()
            # KEDEPAN: Jika ada modul baru bertambah, tinggal masukkan ke list ini:
            # AnotherPipeline(),
        ]
    
    def run_all_pipelines(self):
        """Satu fungsi utama untuk mengeksekusi semua module pipeline yang terdaftar."""
        combines_output = {}

        for pipeline_module in self.registry:
            # Mendapatkan nama kelas sebagai key identifikasi output (misal: 'BankPipeline')
            module_name = pipeline_module.__class__.__name__
            # Setiap module wajib memiliki standard method yang sama (misal: run_process)
            combines_output[module_name] = pipeline_module.run_process()
        return combines_output