'''
Reports package configurations.
'''

import argparse
import sys
import os


def get_config_path() -> str:
    '''
    Returns the absolute path to the Orbit configuration file packaged with Aquila.
    '''
    abs_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.toml')).replace('\\', '/')
    return abs_cfg_path


class _VerbConfig:

    def __init__(self, cfg_dir):
        self.cfg_dir = cfg_dir

    def run(self):
        if self.cfg_dir:
            print(get_config_path())

    @staticmethod
    def from_args(args: list):
        parser = argparse.ArgumentParser('verb-config')
        parser.add_argument('--config-path', action='store_true', help='Print the absolute path to the config.toml file')
        args = parser.parse_args(args)

        return _VerbConfig(
            cfg_dir=args.config_path
        )
    

def main():
    ac = _VerbConfig.from_args(sys.argv[1:])
    ac.run()


if __name__ == "__main__":
    main()