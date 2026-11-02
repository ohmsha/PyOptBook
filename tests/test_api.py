import ast
import io
import json
from types import SimpleNamespace

import pandas as pd
import pulp
import pytest
from fastapi.testclient import TestClient

import api
import api_fastapi
import application
from problem import CarGroupProblem
from api_support import BASELINE, RESOURCE, ROOT, assert_assignment, sample_data


@pytest.fixture
def data():
    return sample_data()


@pytest.fixture
def baseline():
    return {
        'solution': pd.read_csv(BASELINE).to_dict(orient='records'),
        'single_car_solution': [{'student_id': s, 'car_id': 0} for s in range(4)],
    }


def uploads(students, cars):
    return {
        'students': (io.BytesIO(students.to_csv(index=False).encode()), 'students.csv'),
        'cars': (io.BytesIO(cars.to_csv(index=False).encode()), 'cars.csv'),
    }


def test_formulation_dimensions_and_binary_variables(data):
    problem = CarGroupProblem(*data)
    model = problem.prob['prob'].toDict()
    variables = [v for v in model['variables'] if v['name'] != '__dummy']
    assert len(variables) == 144
    assert len(model['constraints']) == 72
    assert all(v['cat'] == 'Integer' and v['lowBound'] == 0 and v['upBound'] == 1
               for v in variables)


def test_sample_solution_and_alternate_optimum(data, baseline):
    students, cars = data
    original = pd.DataFrame(baseline['solution'])
    assert_assignment(original, students, cars)
    actual = CarGroupProblem(*data).solve()
    assert_assignment(actual, students, cars)
    alternative = original.copy()
    alternative['car_id'] = (alternative.car_id + 1) % len(cars)
    assert not alternative.equals(original)
    assert_assignment(alternative, students, cars)


def test_unique_solution_matches_pulp3_exactly(data, baseline):
    students, cars = data
    actual = CarGroupProblem(students.iloc[:4], cars.iloc[:1]).solve()
    pd.testing.assert_frame_equal(actual, pd.DataFrame(baseline['single_car_solution']))


def test_repeat_solve_and_independent_models(data):
    first, second = CarGroupProblem(*data), CarGroupProblem(*data)
    for problem in (first, second, first):
        assert_assignment(problem.solve(), *data)


@pytest.mark.parametrize('missing', ['capacity', 'license', 'male', 'female', 'grade'])
def test_infeasible_constraints(data, missing):
    students, cars = data
    if missing == 'capacity':
        cars['capacity'] = 3
    elif missing == 'license':
        students['license'] = 0
    elif missing in ('male', 'female'):
        students['gender'] = 1 if missing == 'male' else 0
    else:
        students.loc[students.grade == 4, 'grade'] = 3
    problem = CarGroupProblem(students, cars)
    if hasattr(pulp, 'LpSolveStatus'):
        with pytest.raises(ValueError, match='Infeasible'):
            problem.solve()
    else:
        assert problem.prob['prob'].solve() == pulp.LpStatusInfeasible


@pytest.mark.skipif(not hasattr(pulp, 'LpSolveStatus'), reason='PuLP 4 status API')
@pytest.mark.parametrize('has_solution', [False, True])
def test_time_limit_uses_solution_flag(data, monkeypatch, has_solution):
    problem = CarGroupProblem(*data)
    expected = problem.solve()
    stats = SimpleNamespace(status=pulp.LpSolveStatus.TimeLimit,
                            status_str='TimeLimit', has_solution=has_solution)
    monkeypatch.setattr(problem.prob['prob'], 'solve', lambda *args: stats)
    if has_solution:
        pd.testing.assert_frame_equal(problem.solve(), expected)
    else:
        with pytest.raises(ValueError, match='TimeLimit'):
            problem.solve()


@pytest.mark.parametrize('unique', [False, True])
def test_flask_csv_contract(data, baseline, unique):
    students, cars = data
    if unique:
        students, cars = students.iloc[:4], cars.iloc[:1]
    response = api.app.test_client().post('/api', data=uploads(students, cars))
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    actual = pd.read_csv(io.StringIO(response.get_data(as_text=True)))
    assert_assignment(actual, students, cars)
    if unique:
        assert response.data == pd.DataFrame(baseline['single_car_solution']).to_csv(index=False).encode()


@pytest.mark.parametrize('unique', [False, True])
def test_fastapi_json_contract(baseline, unique):
    payload = json.loads((RESOURCE / 'request_fastapi.json').read_text(encoding='utf-8'))
    if unique:
        payload['students'] = payload['students'][:4]
        payload['cars'] = payload['cars'][:1]
    with TestClient(api_fastapi.app) as client:
        response = client.post('/api', json=payload)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert all(set(row) == {'student_id', 'car_id'} for row in response.json())
    assert all(type(value) is int for row in response.json() for value in row.values())
    assert_assignment(pd.DataFrame(response.json()), pd.DataFrame(payload['students']),
                      pd.DataFrame(payload['cars']))
    if unique:
        assert response.json() == baseline['single_car_solution']


def test_fastapi_invalid_request():
    payload = json.loads((RESOURCE / 'wrong_request_fastapi.json').read_text(encoding='utf-8'))
    with TestClient(api_fastapi.app) as client:
        assert client.post('/api', json=payload).status_code == 422


def test_web_form_and_csv_download(data):
    client = application.app.test_client()
    assert client.get('/').status_code == 200
    response = client.post('/', data=uploads(*data))
    assert response.status_code == 200
    table = pd.read_html(io.StringIO(response.get_data(as_text=True)))[0]
    assert_assignment(table, *data)
    download = client.post('/download', data={'solution_html': table.to_html(index=False)})
    assert download.status_code == 200
    assert download.headers['Content-Type'] == 'text/csv'
    assert download.headers['Content-Disposition'] == 'attachment; filename=solution.csv'
    assert download.data == table.to_csv(index=False).encode()


def test_web_empty_upload_redirects(data):
    files = uploads(*data)
    files['students'] = (io.BytesIO(b''), '')
    assert application.app.test_client().post('/', data=files).status_code == 302


def test_streamlit_csv_helpers(data, baseline):
    source = ast.parse((ROOT / '6.api' / 'application_streamlit.py').read_text(encoding='utf-8'))
    functions = ast.Module(body=[node for node in source.body if isinstance(node, ast.FunctionDef)],
                           type_ignores=[])
    namespace = {'pd': pd}
    exec(compile(functions, 'application_streamlit.py', 'exec'), namespace)
    students, cars = data
    actual = namespace['preprocess'](io.StringIO(students.to_csv(index=False)),
                                     io.StringIO(cars.to_csv(index=False)))
    for frame, expected in zip(actual, data):
        pd.testing.assert_frame_equal(frame, expected)
    solution = CarGroupProblem(students.iloc[:4], cars.iloc[:1]).solve()
    expected = pd.DataFrame(baseline['single_car_solution']).to_csv().encode('utf-8')
    assert namespace['convert_to_csv'](solution) == expected
