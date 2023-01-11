import re
import json
import UnityPy
from functools import lru_cache
from data_processing import file

# DATA INITIALIZATION

apk = UnityPy.load('data_processing/input/base.apk')
for sa0 in apk.assets:
    if 'sharedassets0' in sa0.name:
        break
assert sa0.name == 'sharedassets0.assets', 'Variable sa0 is misassigned.'
# asset.objects == {k: v for k, v in zip(asset.keys(), asset.values())}

loc = UnityPy.load('data_processing/input/localization') # apk contains localization data too, but it is outdated
corpus = {}
for key in loc.container:
    val = loc.container[key].read()
    language = val.name
    translations = json.loads(bytes(val.script))
    corpus[language] = translations

sig = UnityPy.load('data_processing/input/signatureabilities')

with open('data_processing/input/typetrees.json', 'r') as fp:
    typetrees = json.load(fp)

# MAIN FUNCTIONS

def read_obj(obj):
    typetree = typetrees[obj.read().m_Script.read().m_Name]
    return obj.read_typetree(typetree)

@lru_cache
def get_monos(datatype):
    'Get MonoBehaviour of specified type name.'
    monos = []
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            if monotype == datatype: # todo: this is similar to read_obj, see if it can be merged
                typetree = typetrees[monotype]
                monotree = mono.read_typetree(typetree)
                monos.append(monotree)
    return monos

def sa0_get_id(ptr):
    return read_obj(sa0[ptr['m_PathID']])

def sig_get_id(ptr):
    id = ptr['m_PathID']
    if id in sig.assets[0].keys():
        return sig.assets[0][id].read_typetree() # doesn't use read_obj because typetrees wasn't built with sig
    return {}

def sig_get_rp(ptr):
    rp = ptr['resourcePath']
    if rp in sig.container:
        return sig.container[rp].read_typetree()
    return {}

def create_id(parent, data):
    'Retrieve ID from data and alter it to be unique if necessary.'
    id = data['humanReadableGuid']
    if id == '':
        id = data['guid']
        print(id)

    dupe = False
    while id in parent:
        dupe = True
        id += '_'
    if dupe: # warn about a possible ID inconsistency which may need manual fixing
        print('WARNING: A non-unique ID has been detected and renamed:', id)

    return id

def is_collectible(variant):
    'True if Variant has Marquee Ability (e.g. no Sparring Partners or Competitive Fighters).'
    return variant['superAbility']['resourcePath'] != ''

def build_character_ablity(abilityptr):
    ability = sa0_get_id(abilityptr)
    return {
        'title': ability['title'],
        'description': ability['description']
    }

def get_characters():
    characters = {}
    for character in get_monos('BaseCharacterData'):
        id = create_id(characters, character)
        variant = None # prevent assigning ma from variant in previous loop
        for variant in get_monos('VariantCharacterData'):
            if is_collectible(variant):
                base = sa0_get_id(variant['baseCharacter'])
                if base == character:
                    break
        characters[id] = {
            'name': character['displayName'],
            'ca': build_character_ablity(character['characterAbility']),
            'ma': build_ability(variant['superAbility']), # todo: account for extra subtitle property
            'pa': build_ability(character['prestigeAbility'])
        }
    return characters

def build_ability(abilityptr):
    ability = sig_get_rp(abilityptr)

    def get_true_value(value):
        if isinstance(value, str):
            return float(value)
        if isinstance(value, dict):
            return value['value'] / 2048
        return value

    visited = set()
    def iter_effects(data, skip_keys=['randomModifierList'], root=True):
        if root:
            visited.clear()
        if isinstance(data, dict):
            if 'm_PathID' in data:
                id = data['m_PathID']
                if id not in visited:
                    data = sig_get_id(data)
                visited.add(id)
            if 'id' in data and data['id'] != '':
                yield data
            for key in data:
                if key not in skip_keys:
                    for subdata in iter_effects(data[key], skip_keys, False):
                        yield subdata
        elif isinstance(data, list):
            for item in data:
                for subdata in iter_effects(item, skip_keys, False):
                    yield subdata

    def build_value(subx, suby, tier):
        for x in iter_effects(tier['modifierSets']):
            if x['id'] == subx and suby in x:
                return get_true_value(x[suby])
        print(subx, suby, tier)
        # for modifierset in tier['modifierSets']:
        #     for modifierptr in modifierset['modifiers']:
        #         print(sig_get_id(modifierptr)['id'], tier, substitution)

    def build_tier(tierptr, substitutions):
        tier = sig_get_id(tierptr)
        return {
            "level": tier['unlockAtLevel'],
            "values": [build_value(subx, suby, tier) for subx, suby in substitutions]
        }

    def build_feature(featureptr):
        feature = sig_get_id(featureptr)
        substitutions = []
        for sub in feature['substitutions']: # todo: rename these sub variables
            subx, suby = sub.split('.')
            substitutions.append([subx.upper(), suby[0].lower() + suby[1:]])
        blah = { # todo: refine the addition of the title attribute for marquee abilities
            'description': feature['description'],
            'tiers': [build_tier(tierptr, substitutions) for tierptr in feature['tiers']]
        }
        if 'title' in feature and feature['title'] != '':
            blah['title'] = feature['title']
        return blah

    componentptrs = ability['m_Component']
    for componentptr in componentptrs:
        component = sig_get_id(componentptr['component'])
        if 'title' in component and 'features' in component:
            return {
                'title': component['title'],
                'features': [build_feature(featureptr) for featureptr in component['features']]
            }
    return {}

def get_variants():
    variants = {}
    for variant in get_monos('VariantCharacterData'):
        if is_collectible(variant):
            id = create_id(variants, variant)
            character = sa0_get_id(variant['baseCharacter'])
            variants[id] = {
                'base': character['humanReadableGuid'],
                'name': variant['displayVariantName'],
                'quote': variant['variantQuote'],
                'tier': variant['initialTier'],
                'element': variant['elementAffiliation'],
                'stats': variant['baseScaledValuesByTier'],
                'sa': build_ability(variant['signatureAbility']),
                'fandom': corpus['en'][variant['displayVariantName']]
            }
    return variants

# UTILITY FUNCTIONS

def tally_monotypes():
    monotypes = {}
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            monotypes.setdefault(monotype, 0)
            monotypes[monotype] += 1
    return monotypes

def sign(n):
    return 1 if n > 0 else -1 if n < 0 else 0

def check_sas():
    for key in variants:
        features = variants[key]['sa']['features']
        for i, feature in enumerate(features, 1):
            tiers = [tier['values'] for tier in feature['tiers']]
            constant = True
            for j in range(len(tiers[0])):
                avb = tiers[0][j] - tiers[1][j]
                bvc = tiers[1][j] - tiers[2][j]
                if sign(avb) != sign(bvc):
                    print('Variant {}\'s SA{} is nonmonotonic at index {}: {}'.format(key, i, j, tiers))
                if sign(avb) != 0 or sign(bvc) != 0:
                    constant = False
            if constant:
                print('Variant {}\'s SA{} is constant: {}'.format(key, i, tiers))

##################################
# above is updated, below is old #
##################################    

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = sa0[character_key]
        for pointer in character['specialMoves']['Array']:
            sm = follow_id(sa0, pointer)
            id = create_id(sms, sm)
            if sm['cooldownTimes']['Array'] == [-1]: # competitive pvp burst
                continue
            icon = follow_id(sa0, sm['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
            sma_key = sm['signatureAbility']
            sms[id] = {
                'base': character['humanReadableGuid'],
                'icon': icon_name,
                'title': sm['title'],
                'type': 0,
                'tier': sm['tier'],
                'gear': sm['gearDamageTier'],
                'cost': sm['gearPointsCost'],
                'attack': sm['attackDamageMultipliers'],
                'damage': sm['damageIndicatorLevels'],
                'cooldown': sm['cooldownTimes'],
                'ability': build_ability(sma_key)
            }
    return sms

def get_bbs(character_keys):
    bbs = {}
    for character_key in character_keys:
        character = sa0[character_key]
        for pointer in character['blockbusters']['Array']:
            bb = follow_id(sa0, pointer)
            id = create_id(bbs, bb)
            icon = follow_id(sa0, bb['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
            bba_key = bb['signatureAbility']
            bbs[id] = {
                'base': character['humanReadableGuid'],
                'icon': icon_name,
                'title': bb['title'],
                'type': 1,
                'tier': bb['tier'],
                'gear': bb['gearDamageTier'],
                'cost': bb['gearPointsCost'],
                'attack': bb['attackDamageMultipliers'],
                'damage': bb['damageIndicatorLevels'],
                'strength': bb['strengthLevel'],
                'ability': build_ability(bba_key)
            }
    return bbs

def get_catalysts(catalyst_keys):
    catalysts = {}
    for catalyst_key in catalyst_keys:
        catalyst = sa0[catalyst_key]
        id = create_id(catalysts, catalyst)
        characters = []
        elements = []
        constraint = follow_id(sa0, catalyst['abilityConstraint'])
        if 'charactersNeeded' in constraint:
            for pointer in constraint['charactersNeeded']['Array']:
                character = follow_id(sa0, pointer)
                characters.append(character['humanReadableGuid'])
        if 'elementsNeeded' in constraint:
            for element in constraint['elementsNeeded']['Array']:
                elements.append(element)
        cata_key = catalyst['signatureAbility']
        catalysts[id] = {
            'title': catalyst['title'],
            'tier': catalyst['tier'],
            'icon': catalyst['icon']['resourcePath'],
            'randomCharacter': catalyst['randomCharacter'],
            'randomElement': catalyst['randomElement'],
            'specialCharacter': characters,
            'specialElement': elements,
            'ability': build_ability(cata_key)
        }
    return catalysts

def get_corpus_keys(data):
    keys = set()
    if isinstance(data, str) and data in corpus['en']:
        keys.add(data)
    elif isinstance(data, list):
        for item in data:
            keys |= get_corpus_keys(item)
    elif isinstance(data, dict):
        for key in data:
            keys |= get_corpus_keys(data[key])
    return keys

if __name__ == '__main__':
    characters = get_characters()
    variants = get_variants()
    # sms = get_sms()
    # bbs = get_bbs()
    # catalysts = get_catalysts()

    check_sas() # expected: pShoot

    file.mkdir('data_processing/output')

    file.save(characters, 'data_processing/output/characters.json', True)
    file.save(variants, 'data_processing/output/variants.json', True)
    # file.save(sms, 'data_processing/output/sms.json')
    # file.save(bbs, 'data_processing/output/bbs.json')
    # file.save(catalysts, 'data_processing/output/catalysts.json')

    corpus_keys = set()
    corpus_keys |= get_corpus_keys(characters)
    corpus_keys |= get_corpus_keys(variants)
    # corpus_keys |= get_corpus_keys(sms)
    # corpus_keys |= get_corpus_keys(bbs)
    # corpus_keys |= get_corpus_keys(catalysts)

    for language in corpus:
        corpus_core = {key: corpus[language][key] for key in corpus_keys if key in corpus[language]}
        corpus_core[''] = 'UNDEFINED'
        file.save(corpus_core, 'data_processing/output/{}.json'.format(language), True)

    # with open('data_processing/output/corpus_en.json', 'w') as file:
    #     json.dump(corpus['en'], file, indent=4, separators=(',', ': '))
