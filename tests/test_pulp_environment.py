import pulp
import pytest

from notebook_support import assert_saved_notebook


def test_cbc_solves_integer_problem():
    problem = pulp.LpProblem('cbc_smoke', pulp.LpMinimize)
    x = problem.add_variable('x', lowBound=0, cat='Integer')
    problem += x >= 2.5
    problem += x
    stats = problem.solve(pulp.COIN_CMD(msg=False))
    assert stats.status == pulp.LpSolveStatus.Optimal
    assert stats.has_solution
    assert x.value() == 3


@pytest.mark.parametrize('path', [
    '7.recommendation/recommendation.ipynb',
    '7.recommendation/recommendation_cvxpy.ipynb',
    '7.recommendation/recommendation_ver2.ipynb',
])
def test_unchanged_notebooks_are_valid(path):
    assert_saved_notebook(path)
