import pytest
import numpy as np

import libertem.analysis.gridmatching as grm


@pytest.fixture
def points():
    return np.array([
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (0, -1),
        (-1, 0),
        (-1, -1)
    ])


@pytest.fixture
def indices():
    return np.array([
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (-1, 0),
        (0, -1),
        (-1, -1)
    ])


@pytest.fixture
def zero():
    return np.array([0, 0])


@pytest.fixture
def a():
    return np.array([0, 1])


@pytest.fixture
def b():
    return np.array([1, 0])


def _fullgrid(zero, a, b, index, skip_zero=False):
    i, j = np.mgrid[-index:index, -index:index]
    indices = np.concatenate(np.array((i, j)).T)
    if skip_zero:
        select = (np.not_equal(indices[:, 0], 0) + np.not_equal(indices[:, 1], 0))
        indices = indices[select]
    return grm.calc_coords(zero, a, b, indices)


def test_consistency(zero, a, b, points, indices):
    coefficients = np.array((a, b))
    result = zero + np.dot(indices, coefficients)
    assert(np.allclose(result, points))


def test_calc_coords(zero, a, b, points, indices):
    result = grm.calc_coords(zero, a, b, indices)
    assert(np.allclose(result, points))


def test_polar():
    data = np.array([
        (0, 1),
        (1, 0),
        (-2, 0)
    ])
    expected = np.array([
        (1, 0),
        (1, np.pi/2),
        (2, -np.pi/2)
    ])

    result = grm.make_polar(data)
    assert(np.allclose(expected, result))


def test_conversion(points):
    assert(np.allclose(points, grm.make_cartesian(grm.make_polar(points))))


def test_sizefilter():
    polars = np.array([
        (0.1, 2),
        (1, 0.3),
        (2, 0.5)
    ])

    assert(np.allclose(grm.size_filter(polars, 0, np.float('inf')), polars))
    assert(len(grm.size_filter(polars, 3, np.float('inf'))) == 0)
    assert(np.allclose(grm.size_filter(polars, 0.9, 1.1), polars[1]))


def test_angle_ckeck():
    polar_1 = np.array([
        (1, 0),
        (17, np.pi/10),
        (8, np.pi*9/10),
        (1, np.pi),
        (0.1, 2*np.pi),
        (1, 2*np.pi*19/20),
        (1, -np.pi/10),
        (1, -np.pi*9/10),
        (1, np.pi*11/10),
        (1, np.pi/2)
    ])
    polar_2 = np.repeat(np.array([(1, 0)]), len(polar_1), axis=0)
    check = grm.angle_check(polar_1, polar_2, np.pi/5)
    assert(not check[:-1].any())
    assert(check[-1])
    check_2 = grm.angle_check(polar_2, polar_1, np.pi/5)
    assert(not check_2[:-1].any())
    assert(check_2[-1])


def test_fastmatch(zero, a, b):
    grid = _fullgrid(zero, a, b, 5)
    correlation_result = grm.CorrelationResult(
        centers=grid,
        refineds=grid,
        peak_values=np.ones(len(grid)),
        peak_elevations=np.ones(len(grid))
    )
    match = grm.Match.fastmatch(
        correlation_result=correlation_result, zero=zero, a=a, b=b)
    assert(np.allclose(zero, match.zero))
    assert(np.allclose(a, match.a))
    assert(np.allclose(b, match.b))
    assert(len(match) == len(grid))
    assert(np.allclose(match.calculated_refineds, grid))
