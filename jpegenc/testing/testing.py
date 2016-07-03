
import sys
import os
import subprocess
import pytest
import myhdl


skip_ref_test = pytest.mark.skipif(reason="skip reference cosimulation")
if hasattr(sys, '_called_from_test'):
    skip_ref_test = pytest.mark.skipif(
        not pytest.config.getoption("--include-reference"),
        reason="reference tests, needs --include-reference option to run"
    )


def sim_available(sim='ghdl'):
    ok = True
    try:
        subprocess.call([sim, '-v'])
    except FileNotFoundError as err:
        ok = False
    return ok


def run_testbench(bench, trace=True, bench_id=None):
    """A small wrapper to set common configuration

    Arguments:
        bench (myhdl.Block): the test


    """
    name = bench.__name__
    inst = bench()
    if trace:
        vcdpath = 'output/vcd'
        if not os.path.isdir(vcdpath):
            os.makdirs(vcdpath)

        if bench_id is None:
            bench_id = str(id(bench))
        name = "{}_{}.vcd".format(name, bench_id)

        myhdl.traceSignals.name = nm
        myhdl.traceSignals.directory = dr
        myhdl.traceSignals.timescale = timescale
        inst.config_sim(trace=True)

    inst.run_sim()
    del inst


def convert_testbench(bench):
    pass