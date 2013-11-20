#!/usr/bin/env python

"""
This module implements a EnergyModel abstract class and some basic
implementations. Basically, an EnergyModel is any model that returns an
"energy" for any given structure.
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "11/19/13"

import abc

from pymatgen.serializers.json_coders import MSONable
from pymatgen.analysis.ewald import EwaldSummation
from pymatgen.symmetry.finder import SymmetryFinder


class EnergyModel(MSONable):
    """
    Abstract structure filter class.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_energy(self, structure):
        """
        Returns a boolean for any structure. Structures that return true are
        kept in the Transmuter object during filtering.
        """
        return

    @classmethod
    def from_dict(cls, d):
        for m in ['energy_models']:
            mod = __import__('pymatgen.analysis.' + m,
                             globals(), locals(), [d['@class']], -1)
            if hasattr(mod, d['@class']):
                model = getattr(mod, d['@class'])
                return model(**d['init_args'])
        raise ValueError("Invalid filter dict")


class EwaldElectrostaticModel(EnergyModel):
    """
    Wrapper around EwaldSum to calculate the electrostatic energy.
    """

    def __init__(self, real_space_cut=None, recip_space_cut=None,
                 eta=None, acc_factor=8.0):
        """
        Initializes the model. Args have the same definitions as in the
        EwaldSummatation class.

        Args:
            real_space_cut:
                Real space cutoff radius dictating how many terms are used in
                the real space sum. Defaults to None, which means determine
                automagically using the formula given in gulp 3.1
                documentation.
            recip_space_cut:
                Reciprocal space cutoff radius. Defaults to None, which means
                determine automagically using the formula given in gulp 3.1
                documentation.
            eta:
                The screening parameter. Defaults to None, which means
                determine automatically.
            acc_factor:
                No. of significant figures each sum is converged to.
        """
        self.real_space_cut = real_space_cut
        self.recip_space_cut = recip_space_cut
        self.eta = eta
        self.acc_factor = acc_factor

    def get_energy(self, structure):
        e = EwaldSummation(structure, real_space_cut=self.real_space_cut,
                           recip_space_cut=self.recip_space_cut,
                           eta=self.eta,
                           acc_factor=self.acc_factor)
        return e.total_energy

    @property
    def to_dict(self):
        return {"version": __version__,
                "@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "init_args": {"real_space_cut": self.real_space_cut,
                              "recip_space_cut": self.recip_space_cut,
                              "eta": self.eta,
                              "acc_factor": self.acc_factor}}


class SymmetryModel(EnergyModel):
    """
    Sets the energy to the -ve of the spacegroup number. Higher symmetry =>
    higher "energy"
    """

    def __init__(self, symprec=0.1, angle_tolerance=5):
        """
        Args have same meaning as in
        :class:pymatgen.symmetry.finder.SymmetryFinder.

        Args:
            symprec:
                Symmetry tolerance. Defaults to 0.1/
            angle_tolerance:
                Tolerance for angles. Defaults to 5 degrees.
        """
        self.symprec = symprec
        self.angle_tolerance = angle_tolerance

    def get_energy(self, structure):
        f = SymmetryFinder(structure, symprec=self.symprec,
                           angle_tolerance=self.angle_tolerance)
        return -f.get_spacegroup_number()

    @property
    def to_dict(self):
        return {"version": __version__,
                "@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "init_args": {"symprec": self.symprec,
                              "angle_tolerance": self.angle_tolerance}}