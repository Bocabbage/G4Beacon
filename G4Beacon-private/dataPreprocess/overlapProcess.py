import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str)
parser.add_argument('-o', type=str)
args = parser.parse_args()

lastChrom = 'invalid'
lastEnd = 0
with open(args.i, 'r') as ifile:
    with open(args.o, 'w+') as ofile:
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
