import ast
import contextlib
import csv
import io
import json
import os
from pathlib import Path
import re
import tempfile
from unittest.mock import patch

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat
import pandas as pd
import pulp
import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / 'fixtures' / 'notebook_results.csv'
INITIAL_SOLUTION = Path(__file__).parent / 'fixtures' / 'routing_initial_solution.csv'
CASES = {
    'tutorial': ('2.tutorial/tutorial.ipynb', None),
    'scipy_comparison': ('2.tutorial/tutorial_scipy_optimize_milp.ipynb', None),
    'school': ('3.school/school.ipynb', None),
    'coupon': ('4.coupon/coupon.ipynb', None),
    'routing': ('5.routing/routing.ipynb', [1, 3, 4, 9, 11, 12, 15, 17, 18, 19, 20]),
    'routing_v2_small': ('5.routing_ver2/routing_ver2.ipynb',
                         [4, 6, 7, 9, 10, 12, 14, 32, 35, 38, 39, 41, 44, 45]),
    'routing_v2_tsp': ('5.routing_ver2/routing_ver2.ipynb', [31, 32, 33, 34]),
    'routing_v2_large': ('5.routing_ver2/routing_ver2.ipynb', [4, 16, 18, 19, 20, 21, 22, 25]),
}


def read_notebook(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def check_solution(prob):
    data = prob.toDict()
    values = {v['name']: v['varValue'] for v in data['variables']}
    for v in data['variables']:
        if v['name'] == '__dummy':
            continue
        value = v['varValue']
        assert value is not None, v['name']
        assert v['lowBound'] is None or value >= v['lowBound'] - 1e-5, v
        assert v['upBound'] is None or value <= v['upBound'] + 1e-5, v
        if v['cat'] == 'Integer':
            assert abs(value - round(value)) <= 1e-5, v
    for constraint in data['constraints']:
        products = [c['value'] * (values[c['name']] or 0)
                    for c in constraint['coefficients']]
        residual = constraint['constant'] + sum(products)
        tolerance = 1e-7 * max(1, abs(constraint['constant']), sum(map(abs, products)))
        if constraint['sense'] == 0:
            assert abs(residual) <= tolerance, (constraint['name'], residual, tolerance)
        else:
            assert constraint['sense'] * residual >= -tolerance, (constraint['name'], residual)


def run_case(case):
    path, selected = CASES[case]
    notebook = read_notebook(path)
    records = []
    solve = pulp.LpProblem.solve
    namespace = {'__name__': '__main__'}

    def checked_solve(prob, solver=None, **kwargs):
        model = prob.toDict()
        num_variables = sum(v['name'] != '__dummy' for v in model['variables'])
        num_constraints = len(model['constraints'])
        constant = float(prob.objective.constant) if prob.objective is not None else 0.0
        if solver is None:
            solver = pulp.COIN_CMD(msg=False)
        solver.msg = False
        solver.timeLimit = 600 if case == 'routing_v2_large' else 120
        if os.environ.get('PYOPTBOOK_CBC_PATH'):
            solver.path = os.environ['PYOPTBOOK_CBC_PATH']
        if case == 'routing_v2_large':
            with INITIAL_SOLUTION.open() as f:
                initial = {row['variable']: float(row['value']) for row in csv.DictReader(f)}
            for variable in prob.variables():
                variable.setInitialValue(initial.get(variable.name, 0))
            solver.optionsDict['warmStart'] = True
            solver.keepFiles = True
            solver.options.append('preprocess off')
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / 'cbc.log'
            solver.optionsDict['logPath'] = str(log_path)
            with contextlib.chdir(tmp):
                result = solve(prob, solver, **kwargs)
            log = log_path.read_text()
        has_solution = result.has_solution
        optimal = result.status == pulp.LpSolveStatus.Optimal
        status = result.status_str
        gap_limited = 'within gap tolerance' in log
        objective = None
        if has_solution:
            check_solution(prob)
            objective = float(pulp.value(prob.objective) or 0)
        lower = re.search(r'Lower bound:\s+([-+\d.eE]+)', log)
        best_bound = float(lower.group(1)) + constant if lower else None
        records.append({'variables': num_variables, 'constraints': num_constraints,
                        'status': status, 'has_solution': has_solution, 'objective': objective})
        if case == 'routing_v2_large':
            assert has_solution
            assert optimal or gap_limited, (status, objective, best_bound, log[-2500:])
            if gap_limited:
                assert best_bound is not None
                assert abs(objective - best_bound) <= 0.101 * abs(objective - constant)
        return result

    with contextlib.chdir(ROOT / Path(path).parent), contextlib.redirect_stdout(io.StringIO()), \
            patch.object(pulp.LpProblem, 'solve', checked_solve):
        try:
            for index, cell in enumerate(notebook['cells']):
                if cell['cell_type'] != 'code' or (selected is not None and index not in selected):
                    continue
                source = ''.join(cell['source'])
                exec(compile(source, f'{path}:cell_{index}', 'exec'), namespace)
                if case == 'routing' and index == 1:
                    from joblib import Parallel
                    namespace['Parallel'] = lambda **kwargs: Parallel(n_jobs=1)
                if case == 'routing' and index == 3:
                    namespace.update(num_places=4, num_days=5, num_requests=12)
        finally:
            plt.close('all')
    assert records, case
    return records


def assert_case_matches_baseline(case):
    results = pd.read_csv(BASELINE)
    expected = results[results.case == case].to_dict(orient='records')
    actual = run_case(case)
    assert len(actual) == len(expected)
    for new, old in zip(actual, expected):
        assert new['variables'] == old['variables']
        assert new['constraints'] == old['constraints']
        assert new['has_solution'] == (old['result'] != 'infeasible')
        if old['result'] == 'optimal':
            assert new['status'] in ('Optimal', 'GapLimit'), new
            assert new['objective'] == pytest.approx(old['objective'], rel=1e-8, abs=1e-5)
        elif old['result'] == 'infeasible':
            assert new['status'] == 'Infeasible'


def assert_saved_notebook(path):
    path = ROOT / path
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    executed = path.relative_to(ROOT).as_posix() in {p for p, _ in CASES.values()}
    if executed:
        assert any(cell.get('outputs') for cell in notebook.cells)
    for cell in notebook.cells:
        if cell.cell_type != 'code':
            continue
        ast.parse(cell.source)
        assert not re.search(r'pulp\.(LpVariable\s*[.(]|LpStatus\b|PULP_CBC_CMD\b|LpAffineExpression\(\))',
                             cell.source)
        if executed and cell.source.strip():
            assert cell.execution_count is not None
            assert all(output.output_type != 'error' for output in cell.outputs)
