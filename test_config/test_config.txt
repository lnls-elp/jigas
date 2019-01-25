class LinearityConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor_list = [1043481585, 1043481586]
        self.individual_module_list = [[17, 18, 19, 20], [21, 22, 23, 24]]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.warmup_time = 3*3600
        self.stb_time = 120


class ResolutionConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor_list = [1043481585, 1043481586]
        self.individual_module_list = [[17, 18, 19, 20], [21, 22, 23, 24]]
        self.idc_list = [5, 0, -5]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.warmup_time = 3*3600
        self.nbits = 18


class EficiencyConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor = [1041182350]
        self.individual_module_list = [9, 10, 11, 12]
        self.slot_address = 9
        self.ps_iout = [0, 1, -1, 5, -5, 10, -10]
        self.input_current_channel = 101
        self.output_current_channel = 102
        self.input_voltage_channel = 107
        self.output_voltage_channel = 108
        self.warmup_time = 600


class CrossTalkConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor_list = [1043481585, 1043481586]
        self.individual_module_list = [[17, 18, 19, 20], [21, 22, 23, 24]]
        self.idc_set_test_list = [10, 0, -10]
        self.idc_set_current_list = [0, 10, 0, -10, 0]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.step_time = 60
        self.warmup_time = 2*3600


class FrequencyResponseConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor = [1041182350]
        self.individual_module_list = [9, 10, 11, 12]
        self.idc_list = [5, 0, -5]
        self.ctrl_loop = ['open', 'closed']
        self.channel_freq = 101
        self.channel_rms = 102


class RippleConfig(object):
    def __init__(self):
        self.com_port = '/dev/virtualcom'
        self.inst_addr = 'GPIB::8::INSTR'
        self.dso_addr = 'USB0::2391::6054::MY52492161::INSTR'
        self.dso_file = '../ripple_fbp/ripple_fbp.scp'
        self.bastidor = [1043949057]
        self.individual_module_list = [1, 2, 3, 4]
        self.group_module_list = [1, 2, 3, 4]
        self.ps_iout = [0, 2, 4, 6, 8, 10, -10, -8, -6, -4, -2]
        self.warmup_time = 5
        self.measurements = 10
        self.switching_mode = True
        self.bw3k_coeff = 100
        self.bw500k_coeff = 1
        self.bw1meg_coeff = 1


class StabilityConfig(object):
    def __init__(self):
        self.com_port = 'COM12'
        self.inst_addr = 'GPIB::8::INSTR'
        self.bastidor_list = [1043481585, 1043481586]
        self.individual_module_list = [[17, 18, 19, 20], [21, 22, 23, 24]]
        self.channel_list = [[101, 102, 103, 104], [201, 202, 203, 204]]
        self.ambient_temperature_channel = 105
        self.idc_list = [10, 0, -10]
        self.cooling_time = 3*3600
        self.sampling_period = 60
        self.test_time = 15*3600
