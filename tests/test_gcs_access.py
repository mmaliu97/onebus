# tests/test_data_loader.py
from app.utils.data_loader import read_gcs_csv

def test_data_loading():
    df = read_gcs_csv("stops.csv")
    assert not df.empty
    assert 'stop_id' in df.columns