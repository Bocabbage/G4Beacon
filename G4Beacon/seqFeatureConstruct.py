#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2023/03/30
import os
import re
import random
import argparse
from Bio import SeqIO
from .commonUtils import runShellCmd

_transformDict = {'A': 't', 'T': 'a', 'C': 'g', 'G': 'c'}
_transTab = str.maketrans('ACGT', '0123')


def seqSaveNums(seqFile: str,
                oseqFile: str,
                obedFile: str,
                extend: int,
                reverse: bool) -> None:
    r'''
        Save the extracted sequences of [mid-extend, mid+extend] to seqFile
        and save the corresponding origin entries to the obedFile.
        Noted that the seq-file is saved in One-Hot torch-tensor format.
        Noted that the obedFile may be different from the original input bed file
        because some entries may meet problems during sequence-extract.
    '''
    getPositionRe = re.compile(r'[:-]+')
    # onehotMat = []
    onehotFeatures = []
    with open(obedFile, 'w+') as oBEDFile:
        with open(seqFile, 'r') as ifile:
            if reverse:
                for record in SeqIO.parse(ifile, 'fasta'):
                    seqId, seq = str(record.id), str(record.seq).upper()
                    chrom, start, end = getPositionRe.split(seqId)
                    originStart, originEnd = int(start) + extend, int(end) - extend  # Get origin g4-seq entry

                    seq = seq[len(seq) // 2 - extend:len(seq) // 2 + extend]
                    if 'N' in seq:
                        continue

                    # Reverse strand
                    seq = seq[::-1]
                    for k, v in _transformDict.items():
                        seq = seq.replace(k, v)
                    seq = seq.upper()

                    oBEDFile.write("{}\t{}\t{}\n".format(chrom, originStart, originEnd))
                    # data = list(seq.translate(_transTab))
                    # data = torch.tensor([int(x) for x in data], device=_device)
                    # data = one_hot(data, 4)
                    data = [int(x) for x in list(seq.translate(_transTab))]
                    onehotFeatures.append(data)
                    # onehotMat.append(data)
            else:
                for record in SeqIO.parse(ifile, 'fasta'):
                    seqId, seq = str(record.id), str(record.seq).upper()
                    chrom, start, end = getPositionRe.split(seqId)
                    originStart, originEnd = int(start) + extend, int(end) - extend  # Get origin g4-seq entry

                    seq = seq[len(seq) // 2 - extend:len(seq) // 2 + extend]
                    if 'N' in seq:
                        continue

                    oBEDFile.write("{}\t{}\t{}\n".format(chrom, originStart, originEnd))
                    # data = list(seq.translate(_transTab))
                    # data = torch.tensor([int(x) for x in data], device=_device)
                    # data = one_hot(data, 4)
                    data = [int(x) for x in list(seq.translate(_transTab))]
                    onehotFeatures.append(data)
                    # onehotMat.append(data)

    # onehotMat = torch.stack(onehotMat, dim=0)
    # torch.save(onehotMat, oseqFile)
    with open(oseqFile, 'w+') as ofile:
        # write into CSV file
        for feature in onehotFeatures:
            writeline = (len(feature) * "{},").format(*feature)
            writeline = writeline[:-1] + "\n"
            ofile.write(writeline)


def bedFiltOutliner(filePath: str, minSize: int, maxSize: int) -> None:
    r'''
        Wash out the entries in bed-file whose length
        is lower than minSize or higher than maxSize.
    '''
    filePrename, fileSuffix = os.path.splitext(filePath)
    ofilePath = filePrename + ".clean_min{}max{}.".format(minSize, maxSize) + fileSuffix
    cmd = (("awk 'BEGIN{{ min={min};max={max} }}"
            "{{ len=$3-$2; if(len > min && len < max){{print $0;}} }}' "
            "{ifile} > {ofile}").format(
                min=minSize,
                max=maxSize,
                ifile=filePath,
                ofile=ofilePath))
    runShellCmd(cmd)


def g4SeqExtract(bedFile: str,
                 oseqFile: str,
                 obedFile: str,
                 extend: str,
                 refGenomeFile: str,
                 reverse: bool) -> None:
    r'''
        Take raw g4-seq file(name) in BED format as input,
        extract the sequence from the location
        [chr, mid-extend, mid+extend] and save them in file
        with encoding by ONE-HOT.
    '''
    randId = random.randint(0, 4000)
    basename = os.path.basename(bedFile)
    tmpBedFile = f"{randId}tmp.{basename}.extendG4Rigion1.bed"

    # Extend and rm 'chrM'
    runShellCmd((
        "grep -v 'chrM' {bedFile} | "
        "awk 'BEGIN{{ extend={extend};OFS=\"\t\" }}"
        "{{ if($2 > extend){{print $1, $2-extend, $3+extend;}} }}' "
        "> {tmpBedFile}").format(extend=extend, bedFile=bedFile, tmpBedFile=tmpBedFile)
    )

    # Extract sequence
    tmpFaFile = f"{randId}tmp.{basename}.extendG4Rigion2.fa"
    runShellCmd("bedtools getfasta -fi {} -bed {} > {}".format(refGenomeFile, tmpBedFile, tmpFaFile))
    seqSaveNums(tmpFaFile, oseqFile, obedFile, extend, reverse)

    runShellCmd("rm {} {}".format(tmpBedFile, tmpFaFile))


def seqFeatureConstruct_main(args):
    r"""seqFeatureConstruct-module main function for g4beacon user interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, help="Input g4 raw bed file.")
    parser.add_argument('-oseq', type=str, help="Output g4-extend sequence file (One-Hot encoded).")
    parser.add_argument('-obi', type=str, help="Bed file of sequence extract valid entries.")
    parser.add_argument('-fi', type=str, help="Reference sequence file.")
    parser.add_argument('--extend', type=int, default=1000, help="Get [start - extend, end + extend] entries.")
    parser.add_argument('--reverse', action="store_true", default=False, dest="reverse")
    args = parser.parse_args(args)

    g4SeqExtract(args.i, args.oseq, args.obi, args.extend, args.fi, args.reverse)
