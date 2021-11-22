#! usr/bin python
# -*- coding: utf-8 -*-
# Author: Zhuofan Zhang
# Update date: 2021/09/25
import re
import random
import argparse
from commonUtils import run_shell_cmd
from Bio import SeqIO

_transformDict = {'A': 't', 'T': 'a', 'C': 'g', 'G': 'c'}
_transTab = str.maketrans('ACGT', '0123')


def _seq_save_onehot(seqFile: str,
                     oseqFile: str,
                     obedFile: str,
                     extend: int,
                     againExtend: int,
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
                    originStart, originEnd = int(start) + againExtend + extend, int(end) - againExtend - extend  # Get origin g4-seq entry

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


parser = argparse.ArgumentParser()
parser.add_argument('--neg', type=str, help="Input negative [origin/extend] bed.")
parser.add_argument('--chip', type=str, help="positive g4 chip-seq bed.")
parser.add_argument('--obed', type=str, help="Output filted negative bed.")
parser.add_argument('--oseq', type=str, help="Output filted negative seqfile.")
parser.add_argument('--extend', type=int, help="original extend of sample.")
parser.add_argument('-F', type=float, help="fraction of overlap threshold. Positive frac or negative int.")
parser.add_argument('--fi', type=str, help="Reference genome fasta file.")
parser.add_argument('--reverse', action="store_true", default=False, dest="reverse")
args = parser.parse_args()

randId = random.randint(0, 4000)
negFile = args.neg
chipFile = args.chip
outBedFile = args.obed
outSeqFile = args.oseq
extend = args.extend
frac = args.F
ref = args.fi
reverse = args.reverse

tmpExtendFile = f"./tmp{randId}.bed"
tmpResultFile = f'./tmp{randId}.result.bed'
tmpSeqFile = f"./tmp{randId}.seq.fa"

if frac > 0:
    run_shell_cmd(f"awk 'BEGIN{{OFS=\"\\t\"}}"
                  f"{{print $1, $2-{extend}, $3+{extend}}}' {negFile} > {tmpExtendFile}")
    run_shell_cmd(f"bedtools intersect -F {frac} -a {tmpExtendFile} -b {chipFile} -v > {tmpResultFile}")
    run_shell_cmd(f"bedtools getfasta -fi {ref} -bed {tmpResultFile} > {tmpSeqFile}")
    _seq_save_onehot(tmpSeqFile, outSeqFile, outBedFile, extend, 0, reverse)

    run_shell_cmd(f"rm ./tmp{randId}*")

elif frac < 0:
    againExtend = abs(int(frac))
    run_shell_cmd((f"awk 'BEGIN{{OFS=\"\\t\"}}"
                   f"{{if($2-{extend}-{againExtend} > 0)"
                   f"{{print $1, $2-{againExtend}-{extend}, $3+{againExtend}+{extend}}}}}'"
                   f" {negFile} > {tmpExtendFile}"))
    run_shell_cmd(f"bedtools intersect -a {tmpExtendFile} -b {chipFile} -v > {tmpResultFile}")
    run_shell_cmd(f"bedtools getfasta -fi {ref} -bed {tmpResultFile} > {tmpSeqFile}")
    _seq_save_onehot(tmpSeqFile, outSeqFile, outBedFile, extend, againExtend, reverse)
    run_shell_cmd(f"rm ./tmp{randId}*")
else:
    print("Frac can't be 0.")
    exit(-1)
