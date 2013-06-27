import os
import grp
import signal
import daemon
import lockfile

from deslicerd import (
    initial_program_setup,
    do_main_program,
    program_cleanup,
    reload_program_config,
    )

context = daemon.DaemonContext(
    working_directory='/var/lib/deslicer',
    umask=0o002,
    pidfile=lockfile.FileLock('/var/run/deslicer.pid'),
    )

context.signal_map = {
    signal.SIGTERM: program_cleanup,
    signal.SIGHUP: 'terminate',
    signal.SIGUSR1: reload_program_config,
    }

slicer_gid = grp.getgrnam('hacxman').gr_gid
context.gid = slicer_gid

important_file = open('spam.data', 'w')
interesting_file = open('eggs.data', 'w')
context.files_preserve = [important_file, interesting_file]

initial_program_setup()

with context:
    do_main_program()
