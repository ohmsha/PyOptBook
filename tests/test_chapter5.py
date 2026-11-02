import ast
import os

import pulp
import pytest
from joblib import Parallel, delayed

from notebook_support import assert_case_matches_baseline, assert_saved_notebook, read_notebook


@pytest.mark.parametrize('case', ['routing', 'routing_v2_small', 'routing_v2_tsp', 'routing_v2_large'])
def test_results_match_pulp3(case):
    assert_case_matches_baseline(case)


@pytest.mark.parametrize('path', ['5.routing/routing.ipynb', '5.routing_ver2/routing_ver2.ipynb'])
def test_saved_notebooks(path):
    assert_saved_notebook(path)


def configure_worker():
    if os.environ.get('PYOPTBOOK_CBC_PATH'):
        if pulp.LpSolverDefault is not None:
            pulp.LpSolverDefault.path = os.environ['PYOPTBOOK_CBC_PATH']
        pulp.COIN_CMD.defaultPath = lambda self: os.environ['PYOPTBOOK_CBC_PATH']
    if pulp.LpSolverDefault is not None:
        pulp.LpSolverDefault.msg = False


def test_routing_builds_models_inside_parallel_workers():
    notebook = read_notebook('5.routing/routing.ipynb')
    namespace = {'__name__': '__main__'}
    for index in (1, 3, 4):
        exec(''.join(notebook['cells'][index]['source']), namespace)
        if index == 3:
            namespace.update(num_places=4, num_days=5, num_requests=12)
    source = ast.parse(''.join(notebook['cells'][9]['source']))
    functions = ast.Module(body=[node for node in source.body if isinstance(node, ast.FunctionDef)],
                           type_ignores=[])
    exec(compile(functions, 'routing_functions', 'exec'), namespace)
    routes = Parallel(n_jobs=2, initializer=configure_worker)(
        delayed(namespace['simulate_route'])(z) for z in [(0, 1, 0, 0), (1, 1, 0, 0)])
    assert routes[0] is None
    assert routes[1]['optimal']
    assert routes[1]['移動時間'] == pytest.approx(namespace['t'][0, 1] + namespace['t'][1, 0])
