import pytest

from notebook_support import assert_case_matches_baseline, assert_saved_notebook


@pytest.mark.parametrize('case', ['tutorial', 'scipy_comparison'])
def test_results_match_pulp3(case):
    assert_case_matches_baseline(case)


@pytest.mark.parametrize('path', ['2.tutorial/tutorial.ipynb', '2.tutorial/tutorial_python-mip.ipynb', '2.tutorial/tutorial_scipy_optimize_milp.ipynb'])
def test_saved_notebooks(path):
    assert_saved_notebook(path)
