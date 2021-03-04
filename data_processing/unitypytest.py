import UnityPy

env = UnityPy.load(
    'data_processing/input/signatureabilities',
    'data_processing/input/localization'
)

for obj in env.objects:
    data = obj.read()
    if data.title == 'Char_Valentine_SUP_CombatClinic_Title':
        print(data.title)
        break

obj = env.container['assets/characters/valentine/signatureabilities/resources/sa_valentine_sup_combatclinic.prefab']
data = obj.read()
tree = data.read_type_tree()
tree.to_dict()

env.assets['signatureabilities']
env.assets['signatureabilities']['CAB-33795db553e340f803b94491ed8d8bb8'].keys()
env.assets['signatureabilities']['CAB-33795db553e340f803b94491ed8d8bb8'][-4662963343376788019].read().read_type_tree().to_dict()
env.assets['signatureabilities']['CAB-33795db553e340f803b94491ed8d8bb8'][-9170200783047960356].read().read_type_tree().to_dict()
env.assets['signatureabilities'].keys()
env.objects

data = obj.read()
tree = data.read_type_tree()
tree.to_dict()

for obj in env.objects:
    if obj.type == 'MonoBehaviour':
        data = obj.read()
        if data.modifierSets:
            tree = data.read_type_tree()
            print(tree.keys())

for obj in env.objects:
    if obj.type == 'MonoBehaviour':
        data = obj.read()
        tree = data.read_type_tree()
        print(data.title, data.features)


for obj in env.objects:
    data = obj.read()
    if data.m_GameObject:
        print(data.m_GameObject['m_PathID'])

def todict(x):
    return x.read().read_type_tree().to_dict()

todict(env.container['assets/characters/valentine/signatureabilities/resources/sa_valentine_sup_combatclinic.prefab'])

p=env.assets['signatureabilities'].container['assets/characters/valentine/signatureabilities/resources/sa_valentine_sup_combatclinic.prefab'].read().read_type_tree()['m_Component']
