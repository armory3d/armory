import cProfile
import os
import pstats

import arm
from arm import log, utils

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    utils = arm.reload_module(utils)
else:
    arm.enable_reload(__name__)


class Profile:
    """Context manager for profiling the enclosed code when the given condition is true.
    The output file is stored in the SDK directory and can be opened by tools such as SnakeViz.
    """
    def __init__(self, filename_out: str, condition: bool):
        self.filename_out = filename_out
        self.condition = condition
        self.pr = cProfile.Profile()

    def __enter__(self):
        if self.condition:
            self.pr.enable()
            log.debug("Profiling started")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.condition:
            self.pr.disable()
            log.debug("Profiling finished")

            profile_path = os.path.join(utils.get_sdk_path(), self.filename_out)
            with open(profile_path, 'w', encoding="utf-8") as profile_file:
                stats = pstats.Stats(self.pr, stream=profile_file)
                stats.dump_stats(profile_path)

        return False
