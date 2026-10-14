from indicators import sma, rsi

def test_sma_requires_full_window():
    assert sma([1,2,3,4],3) == [None,None,2,3]

def test_rsi_edge_cases():
    assert rsi(list(range(20))) == 100
    assert rsi(list(range(20,0,-1))) == 0
    assert rsi([5]*20) == 50
    assert rsi([1,2]) is None

def test_wilder_known_sequence():
    values=[44.34,44.09,44.15,43.61,44.33,44.83,45.10,45.42,45.84,46.08,45.89,46.03,45.61,46.28,46.28]
    assert abs(rsi(values)-70.4641350211)<1e-6
