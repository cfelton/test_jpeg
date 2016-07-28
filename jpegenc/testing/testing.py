import py
import sys
import os
import subprocess
import pytest
import myhdl

sim_is_ok = False
skip_ref_test = pytest.mark.skipif(reason="skip reference cosimulation")
if hasattr(sys, '_called_from_test'):
    skip_ref_test = pytest.mark.skipif(
        not pytest.config.getoption("--include-reference"),
        reason="reference tests, needs --include-reference option to run"
    )

skipif_no_sim = pytest.mark.skipif(False, reason="simulator is not available")
if hasattr(sys, '_called_from_test'):
    skip_if_no_sim = pytest.mark.skipif(
        True,
        reason="simulator is not ok "
    )

def sim_available(sim='ghdl'):
    ok = True
    if not py.path.local.sysfind(sim):
        ok = False
    return ok


def run_testbench(bench, trace=True, bench_id=None):
    """A small wrapper to set common configuration

    Arguments:
        bench (myhdl.Block): the test
        trace (bool): enable tracing
        bench_id (str): extra string to append to filenames
    """
    name = bench.__name__
    inst = bench()
    if trace:
        vcdpath = 'output/vcd'
        if not os.path.isdir(vcdpath):
            os.makedirs(vcdpath)

        if bench_id is None:
            bench_id = str(id(bench))
        name = "{}_{}.vcd".format(name, bench_id)

        # remove the existing VCD file if it exists
        path = os.path.join(vcdpath, name)
        if os.path.isfile(path):
            os.remove(path)
        nm = name[:-4]

        myhdl.traceSignals.name = nm
        myhdl.traceSignals.directory = vcdpath
        myhdl.traceSignals.timescale = '1ns'
        inst.config_sim(trace=True)

    inst.run_sim()
    del inst


def convert_testbench(bench):
    pass
