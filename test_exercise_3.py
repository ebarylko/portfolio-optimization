import exercise_3 as ex3


def test_generate_unique_covar_matrix_entries():
    assert ex3.generate_unique_covar_matrix_entries(3) == [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]