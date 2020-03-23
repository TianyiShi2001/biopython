# Copyright 2009-2013 by Peter Cock.  All rights reserved.
# Parts copyright 1999 by Jeffrey Chang.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
"""Tests for Bio.SeqIO.FastaIO module."""
import unittest
from io import StringIO
from Bio import SeqIO
from Bio.SeqIO.FastaIO import FastaIterator
from Bio.Alphabet import generic_nucleotide, generic_dna
from Bio.SeqIO.FastaIO import SimpleFastaParser, FastaTwoLineParser
from Bio.SeqIO.FastaIO import fasta_title_parser_auto, FastaNcbiIterator


def title_to_ids(title):
    """Convert a FASTA title line into the id, name, and description.
    This is just a quick-n-dirty implementation, and is definetely not meant
    to handle every FASTA title line case.
    """
    # first split the id information from the description
    # the first item is the id info block, the rest is the description
    all_info = title.split(" ")
    id_info = all_info[0]
    rest = all_info[1:]
    descr = " ".join(rest)
    # now extract the ids from the id block
    # gi|5690369|gb|AF158246.1|AF158246
    id_info_items = id_info.split("|")
    if len(id_info_items) >= 4:
        assert id_info_items[2] in ["gb", "emb", "dbj", "pdb"], title
        id = id_info_items[3]  # the id with version info
        name = id_info_items[4]  # the id without version info
    else:
        # Fallback:
        id = id_info_items[0]
        name = id_info_items[0]
    return id, name, descr


def read_title_and_seq(filename):
    """Crude parser that gets the first record from a FASTA file."""
    with open(filename) as handle:
        title = handle.readline().rstrip()
        assert title.startswith(">")
        seq = ""
        for line in handle:
            if line.startswith(">"):
                break
            seq += line.strip()
    return title[1:], seq


class Wrapping(unittest.TestCase):
    """Tests for two-line-per-record FASTA variant."""

    def test_fails(self):
        """Test case which should fail."""
        self.assertRaises(ValueError, SeqIO.read, "Fasta/aster.pro", "fasta-2line")

    def test_passes(self):
        """Test case which should pass."""
        expected = SeqIO.read("Fasta/aster.pro", "fasta")
        record = SeqIO.read("Fasta/aster_no_wrap.pro", "fasta")
        self.assertEqual(expected.id, record.id)
        self.assertEqual(expected.name, record.name)
        self.assertEqual(expected.description, record.description)
        self.assertEqual(expected.seq, record.seq)
        record = SeqIO.read("Fasta/aster_no_wrap.pro", "fasta-2line")
        self.assertEqual(expected.id, record.id)
        self.assertEqual(expected.name, record.name)
        self.assertEqual(expected.description, record.description)
        self.assertEqual(expected.seq, record.seq)


class TitleFunctions(unittest.TestCase):
    """Test using title functions."""

    def simple_check(self, filename, alphabet):
        """Test parsing single record FASTA files."""
        msg = "Test failure parsing file %s" % filename
        title, seq = read_title_and_seq(filename)  # crude parser
        idn, name, descr = title_to_ids(title)
        # First check using Bio.SeqIO.FastaIO directly with title function.
        records = FastaIterator(filename, alphabet, title_to_ids)
        record = next(records)
        with self.assertRaises(StopIteration):
            next(records)
        self.assertEqual(record.id, idn, msg=msg)
        self.assertEqual(record.name, name, msg=msg)
        self.assertEqual(record.description, descr, msg=msg)
        self.assertEqual(str(record.seq), seq, msg=msg)
        self.assertEqual(record.seq.alphabet, alphabet, msg=msg)
        # Now check using Bio.SeqIO (default settings)
        record = SeqIO.read(filename, "fasta", alphabet)
        self.assertEqual(record.id, title.split()[0], msg=msg)
        self.assertEqual(record.name, title.split()[0], msg=msg)
        self.assertEqual(record.description, title, msg=msg)
        self.assertEqual(str(record.seq), seq, msg=msg)
        self.assertEqual(record.seq.alphabet, alphabet, msg=msg)
        # Uncomment this for testing the methods are calling the right files:
        # print("{%s done}" % filename)

    def multi_check(self, filename, alphabet):
        """Test parsing multi-record FASTA files."""
        msg = "Test failure parsing file %s" % filename
        re_titled = list(FastaIterator(filename, alphabet, title_to_ids))
        default = list(SeqIO.parse(filename, "fasta", alphabet))
        self.assertEqual(len(re_titled), len(default), msg=msg)
        for old, new in zip(default, re_titled):
            idn, name, descr = title_to_ids(old.description)
            self.assertEqual(new.id, idn, msg=msg)
            self.assertEqual(new.name, name, msg=msg)
            self.assertEqual(new.description, descr, msg=msg)
            self.assertEqual(str(new.seq), str(old.seq), msg=msg)
            self.assertEqual(new.seq.alphabet, old.seq.alphabet, msg=msg)
        # Uncomment this for testing the methods are calling the right files:
        # print("{%s done}" % filename)

    def test_no_name(self):
        """Test FASTA record with no identifier."""
        handle = StringIO(">\nACGT")
        record = SeqIO.read(handle, "fasta")
        handle.close()
        self.assertEqual(str(record.seq), "ACGT")
        self.assertEqual("", record.id)
        self.assertEqual("", record.name)
        self.assertEqual("", record.description)

    def test_single_nucleic_files(self):
        """Test Fasta files containing a single nucleotide sequence."""
        paths = (
            "Fasta/lupine.nu",
            "Fasta/elderberry.nu",
            "Fasta/phlox.nu",
            "Fasta/centaurea.nu",
            "Fasta/wisteria.nu",
            "Fasta/sweetpea.nu",
            "Fasta/lavender.nu",
            "Fasta/f001",
        )
        for path in paths:
            self.simple_check(path, generic_nucleotide)

    def test_multi_dna_files(self):
        """Test Fasta files containing multiple nucleotide sequences."""
        paths = ("Quality/example.fasta",)
        for path in paths:
            self.multi_check(path, generic_dna)

    def test_single_proteino_files(self):
        """Test Fasta files containing a single protein sequence."""
        paths = (
            "Fasta/aster.pro",
            "Fasta/rosemary.pro",
            "Fasta/rose.pro",
            "Fasta/loveliesbleeding.pro",
        )
        for path in paths:
            self.simple_check(path, generic_nucleotide)

    def test_multi_protein_files(self):
        """Test Fasta files containing multiple protein sequences."""
        paths = ("Fasta/f002", "Fasta/fa01")
        for path in paths:
            self.multi_check(path, generic_dna)


class TestSimpleFastaParsers(unittest.TestCase):
    """Test SimpleFastaParser and FastaTwoLineParser directly."""

    # Regular cases input strings and outputs
    ins_two_line = [">1\nACGT", ">1\nACGT", ">1\nACGT\n>2\nACGT"]
    outs_two_line = [[("1", "ACGT")], [("1", "ACGT")], [("1", "ACGT"), ("2", "ACGT")]]
    ins_multiline = [">1\nACGT\nACGT", ">1\nACGT\nACGT\n>2\nACGT\nACGT"]
    outs_multiline = [[("1", "ACGTACGT")], [("1", "ACGTACGT"), ("2", "ACGTACGT")]]
    # Edge case input strings and outputs
    ins_two_line_edges = [">\nACGT", ">1\n\n", ">1>1\n\n>1\n\n", ""]
    outs_two_line_edges = [[("", "ACGT")], [("1", "")], [("1>1", ""), ("1", "")], []]
    ins_simple_edges = [">1", ">1\n\n\n", ">\n>1\n>2"]
    outs_simple_edges = [[("1", "")], [("1", "")], [("", ""), ("1", ""), ("2", "")]]

    def test_regular_SimpleFastaParser(self):
        """Test regular SimpleFastaParser cases."""
        for inp, out in zip(self.ins_two_line, self.outs_two_line):
            handle1 = StringIO(inp)
            handle2 = StringIO(inp + "\n")
            self.assertEqual(list(SimpleFastaParser(handle1)), out)
            self.assertEqual(list(SimpleFastaParser(handle2)), out)
        for inp, out in zip(self.ins_multiline, self.outs_multiline):
            handle1 = StringIO(inp)
            handle2 = StringIO(inp + "\n")
            self.assertEqual(list(SimpleFastaParser(handle1)), out)
            self.assertEqual(list(SimpleFastaParser(handle2)), out)

    def test_regular_FastaTwoLineParser(self):
        """Test regular FastaTwoLineParser cases."""
        for inp, out in zip(self.ins_two_line, self.outs_two_line):
            handle1 = StringIO(inp)
            handle2 = StringIO(inp + "\n")
            self.assertEqual(list(FastaTwoLineParser(handle1)), out)
            self.assertEqual(list(FastaTwoLineParser(handle2)), out)

    def test_edgecases_SimpleFastaParser(self):
        """Test SimpleFastaParser edge-cases."""
        for inp, out in zip(self.ins_two_line_edges, self.outs_two_line_edges):
            handle = StringIO(inp)
            self.assertEqual(list(SimpleFastaParser(handle)), out)
        for inp, out in zip(self.ins_simple_edges, self.outs_simple_edges):
            handle = StringIO(inp)
            self.assertEqual(list(SimpleFastaParser(handle)), out)

    def test_edgecases_FastaTwoLineParser(self):
        """Test FastaTwoLineParser edge-cases."""
        for inp, out in zip(self.ins_two_line_edges, self.outs_two_line_edges):
            handle = StringIO(inp)
            self.assertEqual(list(FastaTwoLineParser(handle)), out)

    def test_exceptions_FastaTwoLineParser(self):
        """Test FastaTwoLineParser exceptions."""
        for inp in self.ins_multiline + self.ins_simple_edges:
            handle = StringIO(inp)
            with self.assertRaises(ValueError):
                list(FastaTwoLineParser(handle))


class TestNCBIFastaTitleParser(unittest.TestCase):
    """Test NCBI title parsers
    according to the NCBI standard:
    https://ncbi.github.io/cxx-toolkit/pages/ch_demo#ch_demo.id1_fetch.html_ref_fasta
    Test SimpleFastaParser and FastaTwoLineParser directly."""

    def test_fasta_title_parser_auto(self):
        filename = "Fasta/ncbi_standard.pro"
        dbxrefs_expected = [["EMBL:CAA12345.6", "GI:78"], ["GI:10", "PDB:1A2B"], [], []]
        simple = FastaIterator(filename)
        ncbi = FastaNcbiIterator(filename)
        for rec_simple, rec_ncbi, dbxrefs in zip(simple, ncbi, dbxrefs_expected):
            self.assertEqual(rec_simple.id, rec_ncbi.id)
            self.assertEqual(rec_simple.description, rec_ncbi.descriptioin)
            self.assertEqual(rec_ncbi.description, dbxrefs)


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
