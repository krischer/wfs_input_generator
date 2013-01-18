#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple class hierarchy to abstract different kinds of meshes.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from obspy.core import AttribDict


class Mesh(object):
    """
    Base class of the different kind of meshes. Every mesh is expected to have
    a number of common attributes that are implemented as properties on the
    child classes.

    Furthermore every mesh object has a config attribute which should contain
    additional, potentially solver specific configuration.
    """
    def __init__(self):
        self.config = AttribDict()


class SphericalSectionMesh(Mesh):
    """
    A spherical section mesh. A spherical sections is defined by minimum and
    maximum latitude, longitude, depth, and the number of elements in each
    direction. Depth is given in kilometer and depth 0 is defined to be the
    surface of the Earth.
    """
    def __init__(self):
        self._n_north_south = None
        self._n_west_east = None
        self._n_down_up = None
        self._min_latitude = None
        self._max_latitude = None
        self._min_longitude = None
        self._max_longitude = None
        self._min_depth = None
        self._max_depth = None
        super(SphericalSectionMesh, self).__init__()

    @property
    def n_north_south(self):
        """
        Number of elements in North-South direction. This corresponds to the
        latitude direction.
        """
        return self._n_north_south

    @n_north_south.setter
    def n_north_south(self, value):
        self._n_north_south = int(value)

    @property
    def n_west_east(self):
        """
        Number of elements in West-East direction. This corresponds to the
        longitude direction.
        """
        return self._n_west_east

    @n_west_east.setter
    def n_west_east(self, value):
        self._n_west_east = int(value)

    @property
    def n_down_up(self):
        """
        Number of elements in Down-Up direction. This corresponds to the depth
        direction.
        """
        return self._n_down_up

    @n_down_up.setter
    def n_down_up(self, value):
        self._n_down_up = int(value)

    @property
    def min_latitude(self):
        """
        The minimum latitude of the mesh.
        """
        return self._min_latitude

    @min_latitude.setter
    def min_latitude(self, value):
        self._min_latitude = float(value)

    @property
    def max_latitude(self):
        """
        The maximum latitude of the mesh.
        """
        return self._max_latitude

    @max_latitude.setter
    def max_latitude(self, value):
        self._max_latitude = float(value)

    @property
    def min_longitude(self):
        """
        The minimum longitude of the mesh.
        """
        return self._min_longitude

    @min_longitude.setter
    def min_longitude(self, value):
        self._min_longitude = float(value)

    @property
    def max_longitude(self):
        """
        The maximum longitude of the mesh.
        """
        return self._max_longitude

    @max_longitude.setter
    def max_longitude(self, value):
        self._max_longitude = float(value)

    @property
    def min_depth(self):
        """
        The minimum depth of the mesh in km. Depth zero is defined as the
        surface of the Earth.
        """
        return self._min_depth

    @min_depth.setter
    def min_depth(self, value):
        self._min_depth = float(value)

    @property
    def max_depth(self):
        """
        The maximum depth of the mesh in km. Depth zero is defined as the
        surface of the Earth.
        """
        return self._max_depth

    @max_depth.setter
    def max_depth(self, value):
        self._max_depth = float(value)
