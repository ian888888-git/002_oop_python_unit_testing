import pytest 
from src.iot_data.stream_validator import StreamValidator

class TestStreamValidator: 
    """
    Class ini bertugas menguji semua fungsionalitas dari kelas StreamValidator.
    Setiap method di dalamnya merepresentasikan satu skenario pengujian spesifik.
    """

    def test_event_success(self):
         #1. ARRANGE
        """Skenario: Memastikan data sensor yang valid diproses dengan sukses."""
        validator = StreamValidator()
        payload_input = {
            "sensor_id": "SENSOR-IOT-01",
            "temperature": 29.5,
            "humidity": 65
        }
        # 2. ACT
        result = validator.proses_event(payload_input)

        #ASSERT 
        assert result["sensor_id"] == "SENSOR-IOT-01"
        assert result["temperature"] == 29.5
        assert result["humidity"] == 65
        assert "timestamp" in result
    
    def test_event_missing_key(self):
        #1. ARRANGE 
        """Skenario: Memastikan ValueError dilempar saat ada key wajib yang absen."""
        validator = StreamValidator()
        payload_input = {
            "temperature": 29.5,
            "humidity": 65
        }
        # 2. ACT
        with pytest.raises(ValueError) as exc_info:
            validator.proses_event(payload_input)
        # 3. ASSERT 
        # VERIFIKASI PRESISI: Harus cocok dengan output _format_error_message()
        error_message  = "Data tidak valid! Key 'sensor_id' hilang."
        assert str(exc_info.value) == error_message
    
    def test_event_failed_by_wrong_data(self): 
        #1. ARRANGE 
        validator = StreamValidator() 
        payload_input = {
            "sensor_id": "SENSOR-IOT-01",
            "temperature": "TIGA PULUH",
            "humidity": "65"
        }
        # 2. ACT
        with pytest.raises(ValueError) as exc_info:
            validator.proses_event(payload_input)
        # 3. ASSERT
        # VERIFIKASI PRESISI: Harus cocok dengan output _format_error_message()
        error_message = "Tipe data 'temperature' harus berupa angka!"
        assert str(exc_info.value) == error_message