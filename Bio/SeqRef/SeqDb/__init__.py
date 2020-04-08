# Copyright 2020 by Tianyi Shi.  All rights reserved.
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.

r"""Classes of sequence databases.

These classes know how to construct urls from given accession codes.
"""

from .NcbiDb import NcbiNucleotideDb, NcbiProteinDb
from .EbiDb import EbiEnaDB
from .RcsbDb import RcsbDb
