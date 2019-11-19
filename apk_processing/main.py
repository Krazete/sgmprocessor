from apk_processing import file
import re

monolith = file.load('source/sgm_exports/MonoBehaviour', True)
monocore = monolith['sharedassets0.assets.split0']
corpus = file.load('source/sgm_exports/TextAsset')

character_traits = ['characterAbility', 'englishVoArtist']
variant_traits = ['baseCharacter', 'displayVariantName', 'variantQuote']
catalyst_traits = ['randomCharacter', 'randomElement']

def get_keys(parent, traits): # todo: remove parent if monocore is the only object used here
    'Get keys of objects with certain attributes from the parent object.'
    keys = set()
    for key in parent:
        has_all_traits = True
        for trait in traits:
            if trait not in parent[key]:
                has_all_traits = False
                break
        if has_all_traits:
            keys.add(key)
    return keys

def get_possible_referenceicneindeindiend(key_fragment):
    'Get monolith objects whose keys have the specified key fragment.'
    refs = []
    for key in monolith:
        if key_fragment in key:
            refs.append(monolith[key])
    return refs

def follow_path(path):
    'Get an object referenced by a pathID object.'
    if 'm_PathID' in path:
        key = str(path['m_PathID'])
        if key in monocore:
            return monocore[key]
    print(path)
    return {}

def follow_resource(resource):
    'Get an object referenced by a referencePath object.'
    

def extract_ca(ability): # combine into ability_core
    data = {}
    if 'title' in ability:
        data['title'] = ability['title']
    if 'description' in ability:
        data['description'] = ability['description']
    return data

def ability_core(ability): # needs to be fleshed out more
    data = {}
    if 'title' in ability:
        data['title'] = ability['title']
    if 'description' in ability:
        data['description'] = ability['description']
    if 'substitutions' in ability:
        data['substitutions'] = ability['substitutions']
    return data

def get_characters(character_keys, variant_keys): # todo: figure out why beowulf is gone
    characters = {}
    for character_key in character_keys:
        character = monocore[character_key]
        id = character['humanReadableGuid']
        if id == '':
            id = character['guid']
        data = {}
        data['name'] = character['displayName']
        ca = follow_path(character['characterAbility'])
        data['ca'] = extract_ca(ca)
        for variant_key in variant_keys:
            variant = monocore[variant_key]
            base = variant['baseCharacter']
            base_key = str(base['m_PathID'])
            if base_key == character_key:
                ma = follow_path(variant['superAbility'])
                data['ma'] = ability_core(ma)
                break
        characters.setdefault(id, data)
    return characters

def get_variants(variant_keys):
    variants = {}
    for variant_key in variant_keys:
        variant = monolith[variant_key]
        id = variant['humanReadableGuid']
        if id == '':
            id = variant['guid']
        character_key = str(variant['baseCharacter']['m_PathID'])
        if character_key not in monolith:
            print('Character', character_key, 'for Variant', id, 'not found in monolith.')
            continue
        character = monolith[character_key]
        data = {}
        data['base'] = character['humanReadableGuid']
        data['name'] = variant['displayVariantName']
        data['quote'] = variant['variantQuote']
        data['tier'] = variant['initialTier']
        data['element'] = variant['elementAffiliation']
        data['stats'] = variant['baseScaledValuesByTier']['Array']
        sa = follow_path(variant['signatureAbility'])
        data['sa'] = ability_core(sa),
        data['fandom'] = corpus['en'][variant['displayVariantName']]
        variants[id] = data
    return variants

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = monolith[character_key]
        for sm_ref in character['specialMoves']['Array']:
            sm_key = str(sm_ref['m_PathID'])
            sm = monolith[sm_key]
            id = sm['humanReadableGuid']
            if id == '':
                id = sm['guid']
            data = {}
            data['base'] = character['humanReadableGuid']
            data['icon'] = follow_path(sm['palettizedIcon'])['dynamicSprite']['resourcePath'].split('/')[-1]
            data['title'] = sm['title']
            data['type'] = 0
            data['tier'] = sm['tier']
            data['gear'] = sm['gearDamageTier']
            data['cost'] = sm['gearPointsCost']
            data['attack'] = sm['attackDamageMultipliers']
            data['damage'] = sm['damageIndicatorLevels']
            data['cooldown'] = sm['cooldownTimes']
            ability = follow_path(sm['signatureAbility'])
            data['ability'] = ability_core(ability)
            sms[id] = data
    return sms

def get_bbs(character_keys):
    bbs = {}
    for character_key in character_keys:
        character = monolith[character_key]
        for bb_ref in character['blockbusters']['Array']:
            bb_key = str(bb_ref['m_PathID'])
            bb = monolith[bb_key]
            id = bb['humanReadableGuid']
            if id == '':
                id = bb['guid']
            data = {}
            data['base'] = character['humanReadableGuid']
            data['icon'] = follow_path(bb['palettizedIcon'])['dynamicSprite']['resourcePath'].split('/')[-1]
            data['title'] = bb['title']
            data['type'] = 0
            data['tier'] = bb['tier']
            data['gear'] = bb['gearDamageTier']
            data['cost'] = bb['gearPointsCost']
            data['attack'] = bb['attackDamageMultipliers']
            data['damage'] = bb['damageIndicatorLevels']
            data['cooldown'] = bb['strengthLevel']
            ability = follow_path(bb['signatureAbility'])
            data['ability'] = ability_core(ability)
            bbs[id] = data
    return bbs

def get_catalysts(catalyst_keys):
    catalysts = {}
    for catalyst_key in catalyst_keys:
        catalyst = monolith[catalyst_key]
        id = catalyst['humanReadableGuid']
        if id == '':
            id = catalyst['guid']
        data = {}
        data['title'] = catalyst['title']
        data['tier'] = catalyst['tier']
        data['icon'] = catalyst['icon']['resourcePath']
        data['characterLock'] = catalyst['randomCharacter']
        data['elementLock'] = catalyst['randomElement']
        constraint = follow_path(catalyst['abilityConstraint'])
        data['constraint'] = {}
        if 'charactersNeeded' in constraint:
            character_ref = constraint['charactersNeeded']['Array'][0]
            character = follow_path(character_ref)
            if 'humanReadableGuid' in character:
                data['constraint']['base'] = character['humanReadableGuid']
            else:
                data['constraint']['base'] = 'be' # WHY IS BEOWULF'S FILE MISSING???
        if 'elementsNeeded' in constraint:
            data['constraint']['element'] = constraint['elementsNeeded']['Array'][0]
        ability = follow_path(catalyst['signatureAbility'])
        data['ability'] = ability_core(ability)
        catalysts[id] = data
    return catalysts

def get_corpus_keys(object):
    keys = set()
    if isinstance(object, str) and object in corpus['en']:
        keys.add(object)
    elif isinstance(object, list):
        for item in object:
            keys |= get_corpus_keys(item)
    elif isinstance(object, dict):
        for key in object:
            value = object[key]
            keys |= get_corpus_keys(value)
    return keys

if __name__ =='__main__':
    character_keys = get_keys(monocore, character_traits)
    variant_keys = get_keys(monocore, variant_traits)
    catalyst_keys = get_keys(monocore, catalyst_traits)

    get_possible_referenceicneindeindiend('18062')
    get_possible_referenceicneindeindiend('17996')

    characters = get_characters(character_keys, variant_keys)
    variants = get_variants(variant_keys)
    sms = get_sms(character_keys)
    bbs = get_bbs(character_keys)
    catalysts = get_catalysts(catalyst_keys)

    file.resetdir('data')

    file.save(characters, 'data/characters.json')
    file.save(variants, 'data/variants.json')
    file.save(sms, 'data/sms.json')
    file.save(bbs, 'data/bbs.json')
    file.save(catalysts, 'data/catalysts.json')

    corpus_keys = set()
    corpus_keys |= get_corpus_keys(characters)
    corpus_keys |= get_corpus_keys(variants)
    corpus_keys |= get_corpus_keys(sms)
    corpus_keys |= get_corpus_keys(bbs)
    corpus_keys |= get_corpus_keys(catalysts)

    for language in corpus:
        corpus_core = {key: corpus[language][key] for key in corpus_keys if key in corpus[language]}
        corpus_core[''] = 'UNDEFINED'
        file.save(corpus_core, 'data/{}.json'.format(language))
