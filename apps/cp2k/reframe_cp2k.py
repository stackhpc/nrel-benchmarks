""" Performance test using CP2K quantum chemistry and solid state physics software package for atomistic simulations.

    See README.md for details.

    NB:
    - The executable is either cp2k.popt (for MPI only) or cp2k.psmp (for MPI + OpenMP).
    - Only the former is currently implemented here.
"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os
from collections import namedtuple
from reframe.core.logging import getlogger
sys.path.append('.')
from reframe_extras import sequence, Scheduler_Info, CachedRunTest
from modules.utils import parse_time_cmd
# CSCS include a CP2k test which provides the input file we need, so find that test:
RFM_CP2K_PATH = os.path.join(os.path.dirname(rfm.__path__[0]), 'cscs-checks', 'apps', 'cp2k')

node_seq = sequence(1, Scheduler_Info().num_nodes + 1, 2)

@rfm.parameterized_test(*[[n_nodes] for n_nodes in node_seq])
class Cp2k_H2O_256(rfm.RunOnlyRegressionTest):

    def __init__(self, num_nodes):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.modules = ['cp2k']
        self.extra_resources = {}
        self.prerun_cmds = ['time \\']
        self.executable = 'cp2k.popt'
        self.executable_opts = ['H2O-256.inp']
        self.sourcesdir = os.path.join(os.path.abspath(RFM_CP2K_PATH), 'src')

        self.num_nodes = num_nodes
        
        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.tags = {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}
        
        self.exclusive_access = True
        self.time_limit = None
        
        # 'Sanity checks' based on included CSCS CP2K test, but format seems to have changed slightly for step count & energy
        energy = sn.extractsingle(r'\s+ENERGY\| Total FORCE_EVAL \( QS \) '
                                  r'energy \[a\.u\.\]:\s+(?P<energy>\S+)', # note change to [a.u.] rather than (a.u.)
                                  self.stdout, 'energy', float, item=-1)
        energy_reference = -4404.2323
        energy_diff = sn.abs(energy-energy_reference)
        self.sanity_patterns = sn.all([
            sn.assert_found(r'PROGRAM STOPPED IN', self.stdout),
            sn.assert_eq(sn.count(sn.extractall(
                r'Step number',
                self.stdout)), 10),
            sn.assert_lt(energy_diff, 1e-4)
        ])

        self.perf_patterns = {
            # from cp2k output:
            'cp2k_time': sn.extractsingle(r'^ CP2K\s+\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)',
                                     self.stdout, 1, float), # "Total Max" time for CP2K subroutine
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'cp2k_time': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
            }
        }