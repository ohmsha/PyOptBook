from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / '6.api' / 'resource'
BASELINE = Path(__file__).parent / 'fixtures' / 'api_solution.csv'


def sample_data():
    return pd.read_csv(RESOURCE / 'students.csv'), pd.read_csv(RESOURCE / 'cars.csv')


def assert_assignment(solution, students, cars):
    assert list(solution.columns) == ['student_id', 'car_id']
    assert not solution.isna().any().any()
    assert solution.student_id.is_unique
    assert sorted(solution.student_id) == sorted(students.student_id)
    assert set(solution.car_id) <= set(cars.car_id)
    assigned = students.merge(solution, on='student_id', validate='one_to_one')
    for car in cars.itertuples():
        group = assigned[assigned.car_id == car.car_id]
        assert len(group) <= car.capacity
        assert (group.license == 1).any()
        assert set(group.grade) == {1, 2, 3, 4}
        assert set(group.gender) == {0, 1}
