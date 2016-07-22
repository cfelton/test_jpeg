
import argparse
from argparse import Namespace

from rhea.build import get_board

from stub_quantizer import stub_quantizer
from stub_mdct import stub_mdct
from board_map import board_map

block_map = {
    'mdct': stub_mdct,
    'quant': stub_quantizer,
}

def run_flow(args):

    brd = get_board(args.brd)
    port = board_map[args.brd]
    blk = block_map[args.blk]
    brd.add_port_name('sdi', port, 0)
    brd.add_port_name('sdo', port, 1)

    flow = brd.get_flow(top=blk)
    flow.run()
    info = flow.get_utilization()

    # @todo: move the converted file to brd_blk.v
    print(dir(flow))

    return info


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('brd', choices=board_map.keys())
    parser.add_argument('blk', choices=block_map.keys())
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = getargs()
    run_flow(args)
        
    