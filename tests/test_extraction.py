from receiptreader.extraction import candidate_fields

def test_simple_fields():
    fields = candidate_fields('ABC STORE\nDATE 12/10/2026\nTOTAL RM 25.90')
    assert fields.company == 'ABC STORE'
    assert fields.date == '12/10/2026'
    assert fields.total == '25.90'
    assert fields.address == ''

def test_empty_input():
    fields = candidate_fields('')
    assert all(v == '' for v in fields.to_dict().values())
