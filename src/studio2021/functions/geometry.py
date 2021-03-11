from __future__ import print_function

from math import fabs
from math import sqrt

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"


def midpoint_point_point(a, b):
    return [0.5 * (a[0] + b[0]),
            0.5 * (a[1] + b[1]),
            0.5 * (a[2] + b[2])]


def geometric_key(xyz, precision=None, sanitize=True):
    x, y, z = xyz
    if not precision:
        precision = '3f'
    if precision == 'd':
        return '{0},{1},{2}'.format(int(x), int(y), int(z))
    if sanitize:
        minzero = "-{0:.{1}}".format(0.0, precision)
        if "{0:.{1}}".format(x, precision) == minzero:
            x = 0.0
        if "{0:.{1}}".format(y, precision) == minzero:
            y = 0.0
        if "{0:.{1}}".format(z, precision) == minzero:
            z = 0.0
    return '{0:.{3}},{1:.{3}},{2:.{3}}'.format(x, y, z, precision)


def distance_point_point(a, b):
    """Compute the distance bewteen a and b.

    Parameters
    ----------
    a : sequence of float
        XYZ coordinates of point a.
    b : sequence of float
        XYZ coordinates of point b.

    Returns
    -------
    float
        Distance bewteen a and b.

    Examples
    --------
    >>> distance_point_point([0.0, 0.0, 0.0], [2.0, 0.0, 0.0])
    2.0

    See Also
    --------
    distance_point_point_xy

    """
    ab = subtract_vectors(b, a)
    return length_vector(ab)


def centroid_points(points):
    """Compute the centroid of a set of points.

    Warnings
    --------
    Duplicate points are **NOT** removed. If there are duplicates in the
    sequence, they should be there intentionally.

    Parameters
    ----------
    points : sequence
        A sequence of XYZ coordinates.

    Returns
    -------
    list
        XYZ coordinates of the centroid.

    Examples
    --------
    >>>
    """
    p = len(points)
    x, y, z = zip(*points)
    return [sum(x) / p, sum(y) / p, sum(z) / p]


def subtract_vectors(u, v):
    """Subtract one vector from another.

    Parameters
    ----------
    u : list
        XYZ components of the first vector.
    v : list
        XYZ components of the second vector.

    Returns
    -------
    list
        The resulting vector.

    Examples
    --------
    >>>

    """
    return [a - b for (a, b) in zip(u, v)]


def cross_vectors(u, v):
    r"""Compute the cross product of two vectors.

    Parameters
    ----------
    u : tuple, list, Vector
        XYZ components of the first vector.
    v : tuple, list, Vector
        XYZ components of the second vector.

    Returns
    -------
    cross : list
        The cross product of the two vectors.

    Notes
    -----
    The xyz components of the cross product of two vectors :math:`\mathbf{u}`
    and :math:`\mathbf{v}` can be computed as the *minors* of the following matrix:

    .. math::
       :nowrap:

        \begin{bmatrix}
        x & y & z \\
        u_{x} & u_{y} & u_{z} \\
        v_{x} & v_{y} & v_{z}
        \end{bmatrix}

    Therefore, the cross product can be written as:

    .. math::
       :nowrap:

        \mathbf{u} \times \mathbf{v}
        =
        \begin{bmatrix}
        u_{y} * v_{z} - u_{z} * v_{y} \\
        u_{z} * v_{x} - u_{x} * v_{z} \\
        u_{x} * v_{y} - u_{y} * v_{x}
        \end{bmatrix}


    Examples
    --------
    >>> cross_vectors([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
    [0.0, 0.0, 1.0]

    """
    return [u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]]


def length_vector(vector):
    """Calculate the length of the vector.

    Parameters
    ----------
    vector : list
        XYZ components of the vector.

    Returns
    -------
    float
        The length of the vector.

    Examples
    --------
    >>> length_vector([2.0, 0.0, 0.0])
    2.0

    >>> length_vector([1.0, 1.0, 0.0]) == sqrt(2.0)
    True

    """
    return sqrt(length_vector_sqrd(vector))


def length_vector_sqrd(vector):
    """Compute the squared length of a vector.

    Parameters
    ----------
    vector : list
        XYZ components of the vector.

    Returns
    -------
    float
        The squared length.

    Examples
    --------
    >>> length_vector_sqrd([1.0, 1.0, 0.0])
    2.0

    """
    return vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2


def dot_vectors(u, v):
    """Compute the dot product of two vectors.

    Parameters
    ----------
    u : tuple, list, Vector
        XYZ components of the first vector.
    v : tuple, list, Vector
        XYZ components of the second vector.

    Returns
    -------
    dot : float
        The dot product of the two vectors.

    Examples
    --------
    >>> dot_vectors([1.0, 0, 0], [2.0, 0, 0])
    2.0

    """
    return sum(a * b for a, b in zip(u, v))


def area_polygon(polygon):
    """Compute the area of a polygon.

    Parameters
    ----------
    polygon : sequence
        The XYZ coordinates of the vertices/corners of the polygon.
        The vertices are assumed to be in order.
        The polygon is assumed to be closed:
        the first and last vertex in the sequence should not be the same.

    Returns
    -------
    float
        The area of the polygon.

    Examples
    --------
    >>>
    """
    o = centroid_points(polygon)
    a = polygon[-1]
    b = polygon[0]
    oa = subtract_vectors(a, o)
    ob = subtract_vectors(b, o)
    n0 = cross_vectors(oa, ob)
    area = 0.5 * length_vector(n0)
    for i in range(0, len(polygon) - 1):
        oa = ob
        b = polygon[i + 1]
        ob = subtract_vectors(b, o)
        n = cross_vectors(oa, ob)
        if dot_vectors(n, n0) > 0:
            area += 0.5 * length_vector(n)
        else:
            area -= 0.5 * length_vector(n)
    return area


def add_vectors(u, v):
    """Add two vectors.

    Parameters
    ----------
    u : sequence of float
        XYZ components of the first vector.
    v : sequence of float
        XYZ components of the second vector.

    Returns
    -------
    list
        The resulting vector.

    """
    return [a + b for (a, b) in zip(u, v)]


def scale_vector(vector, factor):
    """Scale a vector by a given factor.

    Parameters
    ----------
    vector : list, tuple
        XYZ components of the vector.
    factor : float
        The scaling factor.

    Returns
    -------
    list
        The scaled vector.

    Examples
    --------
    >>> scale_vector([1.0, 2.0, 3.0], 2.0)
    [2.0, 4.0, 6.0]

    >>> v = [2.0, 0.0, 0.0]
    >>> scale_vector(v, 1 / length_vector(v))
    [1.0, 0.0, 0.0]

    """
    return [axis * factor for axis in vector]


def intersection_line_plane(line, plane, tol=1e-6):
    """Computes the intersection point of a line and a plane

    Parameters
    ----------
    line : tuple
        Two points defining the line.
    plane : tuple
        The base point and normal defining the plane.
    tol : float, optional
        A tolerance for membership verification.
        Default is ``1e-6``.

    Returns
    -------
    point or None

    """
    a, b = line
    o, n = plane

    ab = subtract_vectors(b, a)
    cosa = dot_vectors(n, ab)

    if fabs(cosa) <= tol:
        # if the dot product (cosine of the angle between segment and plane)
        # is close to zero the line and the normal are almost perpendicular
        # hence there is no intersection
        return None

    # based on the ratio = -dot_vectors(n, ab) / dot_vectors(n, oa)
    # there are three scenarios
    # 1) 0.0 < ratio < 1.0: the intersection is between a and b
    # 2) ratio < 0.0: the intersection is on the other side of a
    # 3) ratio > 1.0: the intersection is on the other side of b
    oa = subtract_vectors(a, o)
    ratio = - dot_vectors(n, oa) / cosa
    ab = scale_vector(ab, ratio)
    return add_vectors(a, ab)


def intersection_segment_plane(segment, plane, tol=1e-6):
    """Computes the intersection point of a line segment and a plane

    Parameters
    ----------
    segment : tuple
        Two points defining the line segment.
    plane : tuple
        The base point and normal defining the plane.
    tol : float, optional
        A tolerance for membership verification.
        Default is ``1e-6``.

    Returns
    -------
    point or None

    """
    a, b = segment
    o, n = plane

    ab = subtract_vectors(b, a)
    cosa = dot_vectors(n, ab)

    if fabs(cosa) <= tol:
        # if the dot product (cosine of the angle between segment and plane)
        # is close to zero the line and the normal are almost perpendicular
        # hence there is no intersection
        return None

    # based on the ratio = -dot_vectors(n, ab) / dot_vectors(n, oa)
    # there are three scenarios
    # 1) 0.0 < ratio < 1.0: the intersection is between a and b
    # 2) ratio < 0.0: the intersection is on the other side of a
    # 3) ratio > 1.0: the intersection is on the other side of b
    oa = subtract_vectors(a, o)
    ratio = - dot_vectors(n, oa) / cosa

    if 0.0 <= ratio and ratio <= 1.0:
        ab = scale_vector(ab, ratio)
        return add_vectors(a, ab)

    return None


def normalize_vector(vector):
    """Normalise a given vector.

    Parameters
    ----------
    vector : list, tuple
        XYZ components of the vector.

    Returns
    -------
    list
        The normalized vector.

    Examples
    --------
    >>>

    """
    length = length_vector(vector)
    if not length:
        return vector
    return [vector[0] / length, vector[1] / length, vector[2] / length]
    

def normal_polygon(polygon, unitized=True):
    """Compute the normal of a polygon defined by a sequence of points.

    Parameters
    ----------
    polygon : list of list
        A list of polygon point coordinates.

    Returns
    -------
    list
        The normal vector.

    Raises
    ------
    ValueError
        If less than three points are provided.

    Notes
    -----
    The points in the list should be unique. For example, the first and last
    point in the list should not be the same.

    """
    p = len(polygon)

    assert p > 2, "At least three points required"

    nx = 0
    ny = 0
    nz = 0

    o = centroid_points(polygon)
    a = polygon[-1]
    oa = subtract_vectors(a, o)

    for i in range(p):
        b = polygon[i]
        ob = subtract_vectors(b, o)
        n = cross_vectors(oa, ob)
        oa = ob

        nx += n[0]
        ny += n[1]
        nz += n[2]

    if not unitized:
        return nx, ny, nz

    return normalize_vector([nx, ny, nz])