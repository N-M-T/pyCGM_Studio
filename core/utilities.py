import numpy as np
from scipy.interpolate import interp1d


def nan_helper(array_in):

    """
    Helper function used in linear and cubic spline

    :param array_in: 1darray
        marker coordinates with nans representing gaps

    """
    return np.isnan(array_in), lambda z: z.nonzero()[0]


def linear_spline(data_in):

    """
    Perform a linear spline operation on ndarray. Used to highlight gaps between
    markers.

    :param data_in: ndarray
        marker coordinates with gap

    :return: ndarray
        marker coordinates with gap filled
    """

    splined = np.empty([len(data_in), np.shape(data_in)[1]])

    for i in range(np.shape(data_in)[1]):
        y = data_in[:, i]
        nans, x = nan_helper(y)
        y[nans] = np.interp(x(nans), x(~nans), y[~nans])
        splined[:, i] = y

    return splined


def spliner(data_in):

    """
    Perform a linear and cubic spline operation on ndarray. Used to fill gaps between
    markers.

    :param data_in: ndarray
        marker coordinates with gap

    :return: ndarray
        marker coordinates with gap filled
    """

    v_size = len(data_in)
    h_size = np.shape(data_in)[1]
    linear_splined = np.empty([v_size, h_size])
    cubic_splined = np.empty([v_size, h_size])

    for i in range(h_size):
        y = data_in[:, i]
        nans, x = nan_helper(y)
        xnew = np.arange(0, v_size, 1)
        linear = interp1d(x(~nans), y[~nans])
        cubic = interp1d(x(~nans), y[~nans], kind='cubic')

        linear_splined[:, i] = linear(xnew)
        cubic_splined[:, i] = cubic(xnew)

    return linear_splined, cubic_splined


def length(v):
    x, y, z = v
    return np.sqrt(x * x + y * y + z * z)


def vector(b, e):
    x1, y1, z1 = b
    x2, y2, z2 = e
    return x2 - x1, y2 - y1, z2 - z1


def unit(v):
    x, y, z = v
    mag = length(v)
    return [x / mag, y / mag, z / mag]


def normalize(v):

    """
    This is for modifed camera movements
    """

    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def zero_to_nan(in_array):

    """
    Converts all zeros in array to NaNs.

    :param in_array: ndarray
        Data to convert.

    :return: ndarray
        Data with all zeros converted to NaNs.
    """

    # empty array to populate
    nan_empty = np.empty([len(in_array), np.shape(in_array)[1]])

    for i in range(np.shape(in_array)[1]):
        nan_empty[:, i] = [np.nan if x == 0 else x for x in in_array[:, i]]

    return nan_empty




