class GeneralTests(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'


class LinearityConfig(GeneralTests):
    def __init__(self):
        self.bastidor_list = [1041182345, 1041182347]
        self.individual_module_list = [[1, 2, 3, 4], [5, 6, 7, 8]]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.warmup_time = 10800


class ResolutionConfig(GeneralTests):
    def __init__(self):
        self.bastidor_list = [1041182345, 1041182347]
        self.individual_module_list = [[1, 2, 3, 4], [5, 6, 7, 8]]
        self.idc_list = [5, 0, -5]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.warmup_time = 10800
        self.nbits = 18


class EficiencyConfig(GeneralTests):
    def __init__(self):
        self.bastidor = 1041182345
        self.individual_module_list = [1, 2, 3, 4]
        self.slot_address = 1
        self.ps_iout = [0, 1, -1, 5, -5, 10, -10]
        self.input_current_channel = 101
        self.output_current_channel = 102
        self.input_voltage_channel = 107
        self.output_voltage_channel = 108
        self.warmup_time = 600


class CrossTalkConfig(GeneralTests):
    def __init__(self):
        self.bastidor_list = [1041182345, 1041182347]
        self.individual_module_list = [[1, 2, 3, 4], [5, 6, 7, 8]]
        self.idc_set_test_list = [10, 0, -10]
        self.idc_set_current_list = [0, 10, 0, -10, 0]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.step_time = 60
        self.warmup_time = 2*3600


class FrequencyResponseConfig(GeneralTests):
    def __init__(self):
        self.bastidor = [1041182345]
        self.individual_module_list = [1, 2, 3, 4, 5]
        self.idc_list = [5, 0, -5]
        self.ctrl_loop = ['open', 'closed']
        self.channel_freq = 101
        self.channel_rms = 102


class RippleConfig(GeneralTests):
    def __init__(self):
        self.dso_addr = ''
        self.dso_file = 'ripple_fbp.scp'
        self.bastidor = [1041182345]
        self.individual_module_list = [1, 2, 3, 4]
        self.group_module_list = [1, 2, 3, 4]
        self.ps_iout = [0, 2, 4, 6, 8, 10, -10, -8, -6, -4, -2]
        self.warmup_time = 120
        self.measurements = 10