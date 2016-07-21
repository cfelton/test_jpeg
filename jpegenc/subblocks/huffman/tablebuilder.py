import csv

def build_huffman_rom_tables(csvfile):
    """build huffman tables"""
    code = []
    size = []
    with open(csvfile, 'r') as csvfp:
        csvreader = csv.reader(csvfp, delimiter=',')
        for row in csvreader:
            code.append(row[0])
            size.append(row[1])

    code = tuple(code)
    size = tuple(size)
    return code, size
