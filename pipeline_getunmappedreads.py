##############################################################################
#
#   MRC FGU CGAT
#
#   $Id$
#
#   Copyright (C) 2009 Andreas Heger
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
"""===========================
Pipeline template
===========================

:Author: Jacob Parker
:Release: $Id$
:Date: |today|
:Tags: Python

This pipeline calculates the number of mismatches per base for a given set of genes for mapped RNA-seq data using pysam.
The data are merged into one final table.

Overview
========

files :file:``pipeline.ini` and :file:`conf.py`.

Usage
=====

See :ref:`PipelineSettingUp` and :ref:`PipelineRunning` on general
information how to use CGAT pipelines.

Configuration
-------------

The pipeline requires a configured :file:`pipeline.ini` file.
CGATReport report requires a :file:`conf.py` and optionally a
:file:`cgatreport.ini` file (see :ref:`PipelineReporting`).

Default configuration files can be generated by executing:

   python <srcdir>/pipeline_mismatch.py config

Input files
-----------

Set of genes, as specified in the `pipeline.ini` file (job:gene_list).

Requirements
------------

The pipeline requires the results from
:doc:`pipeline_annotations`. Set the configuration variable
:py:data:`annotations_database` and :py:data:`annotations_dir`.

On top of the default CGAT setup, the pipeline requires the following
software to be in the path:

.. Add any additional external requirements such as 3rd party software
   or R modules below:

Requirements:

* samtools >= 1.1

Pipeline output
===============

.. Describe output files of the pipeline here

Glossary
========

.. glossary::


Code
====

"""
from ruffus import *

import sys
import os
import sqlite3
import CGAT.Experiment as E
import CGATPipelines.Pipeline as P
import re
from CGAT import GTF
from CGAT import IOTools
# load options from the config file
PARAMS = P.getParameters(
    ["%s/pipeline.ini" % os.path.splitext(__file__)[0],
     "../pipeline.ini",
     "pipeline.ini"])

PARAMS["pipelinedir"] = os.path.dirname(__file__)


# ---------------------------------------------------
# Specific pipeline tasks
#Files must be in the format: variable1(e.g.Tissue)-ChiporControl-variable2
#(e.g.Experimentalcondition)-Furthercondition(if needed e.g. protein)
#and/orreplicate.bam
#Example: Cerebellum-Chip-minusCPT-Top1_2.bam
#Controls must have 1 as the value in the final position

#filters out reads that are unmapped, not a primary alignment or chimeric



@follows(mkdir("deduplicated_unmapped_reads.dir"))
@transform("*.bam",
           regex(r"(.+).bam"),
           r"deduplicated_unmapped_reads.dir/\1.deduplicated_unmapped.bam")
def getunmappeddeduplicatedreads(infile, outfile):
    temp_file1=P.snip(outfile, ".deduplicated_unmapped.bam") + ".temp.bam"
    temp_file2=P.snip(outfile, ".deduplicated_unmapped.bam") + ".deduplicated_unmapped.temp.bam"
    metrics_file=P.snip(outfile, ".bam") + ".metrics"
    statement='''MarkDuplicates I=%(infile)s  
                                O=%(temp_file1)s 
                                M=%(metrics_file)s > %(temp_file1)s.log;
                                checkpoint;
                                samtools view
                                -q 30
                                -F 1280
                                -b
                                %(temp_file1)s
                                > %(temp_file2)s;
                                checkpoint;
                                samtools view
                                -f 4
                                -b
                                %(temp_file2)s
                                > %(outfile)s;
                                checkpoint;
                                rm -r %(temp_file1)s;
                                checkpoint;
                                rm -r %(temp_file2)s;
                                samtools index %(outfile)s'''
    job_memory="6G"
    P.run()

# ---------------------------------------------------
# Generic pipeline tasks
@follows(getunmappeddeduplicatedreads)
def full():
    pass


if __name__ == "__main__":
    sys.exit(P.main(sys.argv))
