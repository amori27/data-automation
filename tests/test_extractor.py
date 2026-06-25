from src.core.extractor import from_csv


def test_from_csv(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("col1,col2\n1,2\n3,4")
    df = from_csv(str(csv))
    assert len(df) == 2
    assert list(df.columns) == ["col1", "col2"]
