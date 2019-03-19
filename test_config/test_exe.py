import sys
sys.path.insert(0, '../cross-talk_fbp/')
sys.path.insert(0, '../linearidade_fbp/')
sys.path.insert(0, '../rendimento_fbp/')
sys.path.insert(0, '../resolucao_fbp/')
sys.path.insert(0, '../resposta_frequencia_fbp/')
sys.path.insert(0, '../ripple_fbp/')
sys.path.insert(0, '../estabilidade_fbp/')

from CrossTalk import CrossTalk
from Linearidade import Linearity
from Resolucao import Resolution
from Estabilidade import Stability
from Rendimento import Eficiency
from RespostaFrequencia import FrequencyResponse
from Ripple import Ripple

serial = []
serial.append(int(input('Digite o número serial do bastidor: ')))

test1 = CrossTalk()
test2 = Linearity()
test3 = Resolution()
test4 = Stability()
test5 = Eficiency()
test6 = FrequencyResponse(serial)
test7 = Ripple(serial)

# print('\nINICIANDO TESTE DE CROSS TALK...\n')
# test1.cross_talk_test()

# print('\nINICIANDO TESTE DE LINEARIDADE...\n')
# test2.linearity_test()

# print('\nINICIANDO TESTE DE RESOLUCAO\n')
# test3.resolution_test()

# print('\nINICIANDO TESTE DE ESTABILIDADE\n')
# test4.stability_test()

# print('\nINICIANDO TESTE DE EFICIÊNCIA\n')
# test5.eficiency_test()

print('\nINICIANDO TESTE DE RESPOSTA EM FREQUÊNCIA\n')
test6.frequency_response_test()

print('\nINICIANDO TESTE DE RIPPLE\n')
test7.ripple_test()
