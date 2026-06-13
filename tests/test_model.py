from model import DiacriticsModel, MODEL_ID


def test_model_id_from_config():
    assert MODEL_ID == "iliemihai/mt5-base-romanian-diacritics"


def test_diacritics_restoration():
    model = DiacriticsModel()
    input_text = "A inceput sa ii taie un fir de par."
    result = model.restore(input_text)
    assert "început" in result
    assert "să" in result
    assert "păr" in result


def test_batch_restoration():
    model = DiacriticsModel()
    texts = [
        "A inceput sa ii taie un fir de par.",
        "Fata sta in fata si tine camasa de in in mana.",
    ]
    results = model.restore_batch(texts)
    assert len(results) == 2


def test_long_text_restoration():
    model = DiacriticsModel()
    long_text = " ".join(["A inceput sa ii taie un fir de par."] * 50)
    result = model.restore_long(long_text)
    assert "început" in result
