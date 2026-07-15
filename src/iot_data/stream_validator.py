from datetime import datetime
class StreamValidator:
    def __init__(self):
        # Definisikan key yang wajib ada dalam event sensor IoT
        self.required_keys = ["sensor_id", "temperature", "humidity"]
    
    def proses_event(self, event: dict) -> dict:
        """
        Menerima komponen event (dict/JSON), memvalidasi data,
        dan menambahkan timestamp pemrosesan.
        """
        # 1. Validasi: Pastikan semua key wajib ada
        for key in self.required_keys:
            if key not in event:
                raise ValueError(self._format_error_message(key))
        # 2. Validasi: Pastikan tipe data temperature adalah angka (int/float)
        if not isinstance(event["temperature"], (int, float)):
            raise ValueError("Tipe data 'temperature' harus berupa angka!")
        # 3. Manipulasi Data: Salin data asli dan tambahkan informasi baru (Timestamp)
        processed_event = event.copy()
        processed_event["timestamp"] = datetime.now().isoformat()
        return processed_event
    
    def _format_error_message(self, missing_key: str) -> str:
        """Fungsi internal (helper) untuk membuat pesan error."""
        return f"Data tidak valid! Key '{missing_key}' hilang."
    
