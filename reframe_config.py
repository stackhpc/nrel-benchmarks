all_partitions = {
    'scheduler': 'slurm',
    'launcher': 'srun',
    'max_jobs': 20,
}

site_configuration = {
    'systems': [
        {
            'name':'proto',
            'descr': 'Vermilion prototype',
            'hostnames': ['nrel-login-*'],
            'modules_system': 'spack',
            'stagedir': '/scratch/benchmarks',
            'partitions': [
                {
                    'name': 'hpc',
                    'scheduler': 'slurm',
                    'launcher': 'srun',
                    'access': ['--partition=hpc'],
                    'descr': 'hpc partition',
                    'environs': ['spack-gcc@9.3.0-openmpi@4.0.5-ucx'],
                    'variables': [
                        ['SLURM_MPI_TYPE', 'pmix_v3'],
                    ],
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'spack-gcc@9.3.0-openmpi@4.0.5-ucx',
            'target_systems': ['proto'],
        },
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'file',
                    'name': 'reframe.log',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_name)s: %(message)s',   # noqa: E501
                    'append': False
                },
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'name': 'reframe.out',
                    'level': 'info',
                    'format': '%(message)s',
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    # make this the same as output filenames which are ('sysname', 'partition', 'environ', 'testname', 'filename')
                    'prefix': '%(check_system)s/%(check_partition)s/%(check_environ)s/%(check_name)s', # <testname>.log gets appended
                    'level': 'info',
                    # added units here - see Reference: https://reframe-hpc.readthedocs.io/en/latest/config_reference.html?highlight=perflog#logging-.handlers_perflog
                    'format': '%(check_job_completion_time)s|reframe %(version)s|%(check_info)s|jobid=%(check_jobid)s|%(check_perf_var)s=%(check_perf_value)s|%(check_perf_unit)s|ref=%(check_perf_ref)s (l=%(check_perf_lower_thres)s, u=%(check_perf_upper_thres)s)|%(check_tags)s',  # noqa: E501
                    'datefmt': '%FT%T%:z',
                    'append': True
                }
            ]
        }
    ],
    'general': [
        {
            'check_search_path': ['./'],
            'check_search_recursive': True
        }
    ]    
}
