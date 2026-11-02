import pytest

from notebook_support import assert_case_matches_baseline, assert_saved_notebook


@pytest.mark.parametrize('case', ['coupon'])
def test_results_match_pulp3(case):
    assert_case_matches_baseline(case)


@pytest.mark.parametrize('path', ['4.coupon/coupon.ipynb'])
def test_saved_notebooks(path):
    assert_saved_notebook(path)
