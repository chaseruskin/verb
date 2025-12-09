import json

from aquila import env
from aquila import orbit

class Verb:
    """
    A hardware verification library built on top of cocotb.
    """

    def __init__(self):
        '''
        Construct a new Verb instance.
        '''
        pass

    def configure(self, dut: str, ext_generics: dict):
        # convert from string to structured json
        dut_json = orbit.get_unit_json(dut)
        # update generic values with external values
        for key, val in ext_generics.items():
            for dut_gen in dut_json['generics']:
                if dut_gen['name'] == key:
                    dut_gen['default'] = str(val)
                    break
        # convert back to string
        dut_json = json.dumps(dut_json, separators=(',', ':'))
        env.write('VERB_DUT_JSON', dut_json)
