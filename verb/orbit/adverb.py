import json

from aquila import env
from aquila.env import KvPair

class Verb:
    '''
    A hardware verification library built on top of cocotb.
    '''

    def __init__(self, generics: list):
        '''
        Construct a new Verb instance.
        '''
        # convert from string to structured json
        dut_json = json.loads(env.read('ORBIT_DUT_JSON'))
        # update generic values with command-line values
        cli_gen: KvPair
        for cli_gen in generics:
            for dut_gen in dut_json['generics']:
                if dut_gen['identifier'] == cli_gen.key:
                    dut_gen['default'] = str(cli_gen.val)
                    break
        # convert back to string
        dut_json = json.dumps(dut_json, separators=(',', ':'))
        env.write('VERB_DUT_JSON', dut_json)
