#! usr/bin python
# -*- coding: utf-8 -*-
# Description: preprocess for atac raw-data
# Author: Zhuofan Zhang
# Update date: 2021/07/26
import os
import random
import argparse
from commonUtils import run_shell_cmd, running_log


@running_log("atac_preprocess.log")
def atac_raw_process(iFile: str,
                     oFile: str,
                     obedFile: str,
                     chrSizeFile: str,
                     bed2BigWigTool: str,
                     hg38Tohg19Chain: str,
                     bedExtend: bool,
                     isHg38: bool) -> None:
    r'''
        Take raw ATAC-seq file(name) in BED format as input,
        deduplicate the entry-locations, sort the entries
        and save it into BIGWIG FORMAT at the same dir,
        which can be take as into by computeMatrix(deeptools)
    '''
    randId = random.randint(0, 4000)
    tmpSortDedupFile = "{}tmp.dedup.bed".format(randId)

    # Dedup and sort
    if not bedExtend:
        run_shell_cmd("sort -k1,1 -k2,3n -u {} > {}".format(iFile, tmpSortDedupFile))
    else:
        # the extend format
        # Select the highest pValue entry in duplication groups
        run_shell_cmd(("sort -k1,1 -k2,2n -k8,8rn {} | "
                       "sort -k1,1 -k2,2n -u | "
                       "awk '{{ print $1, $2, $3, $7 }}' > {}").format(iFile, tmpSortDedupFile))

    if isHg38:
        tmpLiftoverFile = "{}tmp.dedup.hg19.bed".format(randId)
        tmpLiftUnmapFile = "{}tmp.dedup.hg19.unmap.bed".format(randId)
        run_shell_cmd("liftOver {} {} {} {}".format(tmpSortDedupFile, hg38Tohg19Chain, tmpLiftoverFile, tmpLiftUnmapFile))
        run_shell_cmd("sort -k1,1 -k2,2n {} > {}".format(tmpLiftoverFile, tmpSortDedupFile))
        run_shell_cmd("rm {} {}".format(tmpLiftoverFile, tmpLiftUnmapFile))

    # Handle the entry-overlap problems
    preparedBedFile = "{}tmp.dedup.hg19.sort.merge.bed".format(randId)
    lastChrom = 'invalid'
    lastEnd = 0
    with open(tmpSortDedupFile, 'r') as ifile:
        with open(preparedBedFile, 'w+') as ofile:
            for line in ifile.readlines():
                nChrom, nStart, nEnd, nScore = line.strip().split('\t')
                nStart, nEnd = int(nStart), int(nEnd)

                if (nChrom == lastChrom) and nEnd < lastEnd:
                    continue
                elif (nChrom == lastChrom) and (nStart < lastEnd):
                    ofile.write("{}\t{}\t{}\t{}\n".format(nChrom, lastEnd, nEnd, nScore))
                else:
                    ofile.write(line)
                lastChrom, lastEnd = nChrom, nEnd

    # Convert the BED file to BIGWIG file
    run_shell_cmd("{tool} {ifile} {chrSize} {ofile}".format(
        tool=bed2BigWigTool,
        ifile=preparedBedFile,
        chrSize=chrSizeFile,
        ofile=oFile
    ))

    run_shell_cmd("mv {} {}".format(preparedBedFile, obedFile))
    run_shell_cmd("rm {} {}".format(tmpSortDedupFile, preparedBedFile))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, help="Input atac raw bed file.")
    parser.add_argument('-obw', type=str, help="Output atac bw file.")
    parser.add_argument('-obed', type=str, help="Output atac bed file.")
    parser.add_argument('--extendBed', action="store_true",
                        dest="extendBed", default=False)
    parser.add_argument('--hg38', action="store_true",
                        dest="isHg38", default=False)
    args = parser.parse_args()

    # Get the utils dir
    utilDir = os.path.dirname(os.path.realpath(__file__))
    chrSizeFile = os.path.join(utilDir, "hg19.chrom.sizes")
    bed2bwTool = os.path.join(utilDir, "bedGraphToBigWig")
    hg38Tohg19Chain = os.path.join(utilDir, "hg38ToHg19.over.chain.gz")

    atac_raw_process(args.i,
                     args.obw,
                     args.obed,
                     chrSizeFile,
                     bed2bwTool,
                     hg38Tohg19Chain,
                     args.extendBed,
                     args.isHg38)
