#!/usr/bin/env python3
"""
MobiDB-lite, 3.2.2, March 2018

By Marco Necci, Damiano Piovesan & Silvio C.E. Tosatto
BiocomputingUP lab, Padua, Italy

MobiDB-lite executes 8 different disorder predictors, collects the outputs and
calculates a consensus. The consensus is generated by measuring predictors
agreement. 5 out of 8 predictors must agree to assign disorder state to a
residue. Then a mathematical morphology (MM) dilation/erosion processing is
applied. Finally short regions are filtered out.

For further details on how to call mobidb_lite.py, call::

	mobidb_lite.py --help

For further details on requirements and troubleshooting, **see readme.md**
"""

__version__ = u'3.2.2'

import os
import sys
import gzip
import logging
import warnings
import configparser
from itertools import groupby

# relative imports
import mdblib.cli as cli
import mdblib.logger as logger
import mdblib.setdirs as setdirs
from mdblib.protein import Protein
from mdblib.consensus import MobidbLiteConsensus, SimpleConsensus
from mdblib.outformats import InterProFormat, ExtendedFormat, Mobidb3Format, FullIdPredsFormat


class MobidbLite(object):
    """
    MobiDB-Lite application.

    MobiDB-Lite application launcher. Manages predictors execution,
    consensus computation and output formatting based on parameters.
    """
    def __init__(self, launchdir, _args):
        self.args = _args

        # Parse config file
        self.config_parser = configparser.ConfigParser()
        self.config_parser.optionxform = str
        self.config_parser.read(self.args.conf)

        # Set BINX directories
        self.bin_dirs = setdirs.predictors(
            launchdir, self.config_parser, self.args.outputFormat)
        self.thresholds = {p: float(t) for p, t in dict(
            self.config_parser.items('thresholds')).items()}
        self.outgroup = dict(self.config_parser.items('outfmt_groups'))[str(self.args.outputFormat)]

        logging.debug('outfmt: %i outgroup: %s', self.args.outputFormat, self.outgroup)

        # Set environmental path for IUPred
        os.environ["IUPred_PATH"] = os.path.join(self.bin_dirs['iupred'],
                                                 "bin{}".format(self.args.architecture))

        if self.args.fastaFile == '-':
            self.instream = sys.stdin
        else:
            _, infile_extension = os.path.splitext(self.args.outFile)
            if infile_extension == '.gz':
                self.instream = gzip.open(self.args.fastaFile, "r")
            else:
                self.instream = open(self.args.fastaFile)

    def _fasta_iter(self):
        """
        given a fasta file. yield tuples of header, sequence
        """
        faiter = (x[1] for x in groupby(self.instream, lambda line: line[0] == ">"))
        for header in faiter:
            # drop the ">"
            header = next(header)[1:].strip()
            # join all sequence lines to one.
            seq = "".join(s.strip() for s in next(faiter))
            yield header, seq

    def run(self):
        """
        Run the predictors, combine predictions in a consensus and write output
        """

        # Set Output stream
        if self.args.outFile:
            _, outfile_extension = os.path.splitext(self.args.outFile)

            if outfile_extension == '.gz':
                outstream = gzip.open(self.args.outFile, "w")
            else:
                outstream = open(self.args.outFile, "w")
        else:
            outstream = sys.stdout

        input_count = 0
        output_count = 0

        # Parse input Fasta
        for input_count, (acc, sequence) in enumerate(self._fasta_iter(), 1):
            # run predictors
            logging.debug('Current input %s', acc)

            protein = Protein(acc, sequence)
            protein.generate_repr()
            protein.run_predictors(
                outgroup=self.outgroup,
                bin_dirs=self.bin_dirs,
                thresholds=self.thresholds,
                architecture=self.args.architecture,
                processes=self.args.threads,
            )
            protein.delete_repr()

            multi_acc = None
            if self.args.multiplyOutputBy is not None:
                if self.args.multiplyOutputBy in acc:
                    multi_acc = acc.split('=')[-1].split(self.args.multiplySeparator)

            output = str()

            if protein.predictions:

                pappu = True if self.args.outputFormat == 2 else False
                # calculate consensus
                mobidblite_consensus = MobidbLiteConsensus(
                    protein.predictions, protein.sequence,
                    pappu=pappu, force=self.args.forceConsensus)

                # overwrite acc with a parsed accession if asked to
                if self.args.parseAccession:
                    acc = protein.uniprot_acc if protein.uniprot_acc else acc

                # generate output based on selected output format
                if self.args.outputFormat == 0:
                    output = InterProFormat(acc, mobidblite_consensus,
                                            _features=self.args.skipFeatures)

                elif self.args.outputFormat == 1:
                    output = ExtendedFormat(acc, mobidblite_consensus, _multi_accessions=multi_acc)

                elif self.args.outputFormat == 2:
                    simple_consensus = SimpleConsensus(protein.predictions,
                                                       protein.sequence,
                                                       force=self.args.forceConsensus)

                    output = Mobidb3Format(acc,
                                           len(protein.sequence),
                                           mobidblite_consensus,
                                           simple_consensus,
                                           protein.predictions,
                                           _multi_accessions=multi_acc)

                elif self.args.outputFormat == 3:
                    output = FullIdPredsFormat(acc,
                                               mobidblite_consensus,
                                               protein.predictions,
                                               _multi_accessions=multi_acc)

                # This step is necessary since formatter methods overwrite __repr__
                output = str(output)

                # Write output
                if output:
                    output_count += 1
                    outstream.write('{}\n'.format(output))

        # Close Input and Output stream
        if self.instream != sys.stdin:
            self.instream.close()
        if outstream != sys.stdout:
            outstream.close()
        logging.info('Input seqs: %i Output count: %i', input_count, output_count)


if __name__ == "__main__":

    # Get dir where this piece of code is
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    # Parse command line arguments
    ARGS = cli.arg_parser(SCRIPT_DIR)
    # Suppress warnings
    warnings.filterwarnings('ignore')
    # Set logger
    logger.set_logger(ARGS.log, ARGS.logLevel)
    # Instantiate and run MobiDB-Lite application
    MobidbLite(SCRIPT_DIR, ARGS).run()
