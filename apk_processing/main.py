from apk_processing import file
import re

monosharedraw = file.load('source/sgm_exports/SharedMonoBehaviour', True)
monoshared = monosharedraw['sharedassets0.assets.split0']
monoglobal = file.load('source/sgm_exports/GlobalMonoBehaviour', True)
corpus = file.load('source/sgm_exports/TextAsset')

character_traits = ['characterAbility', 'englishVoArtist']
variant_traits = ['baseCharacter', 'displayVariantName', 'variantQuote']
catalyst_traits = ['randomCharacter', 'randomElement']

def get_keys(traits):
    'Get keys of objects with certain attributes from the parent object.'
    keys = set()
    for key in monoshared:
        has_all_traits = True
        for trait in traits:
            if trait not in monoshared[key]:
                has_all_traits = False
                break
        if has_all_traits:
            keys.add(key)
    return keys

def follow_id(parent, path):
    'Get an object referenced by an m_PathID object.'
    m = 'm_PathID' if 'm_PathID' in path else '0 SInt64 m_PathID'
    if m in path:
        key = str(path[m])
        if key in parent:
            return parent[key]
    return {}

def follow_resource(path):
    'Get keys referenced by an resourcePath object.'
    if 'resourcePath' in path:
        pathname = path['resourcePath']
        for key in monoglobal:
            for subkey in monoglobal[key]:
                if '0 GameObject Base' in monoglobal[key][subkey]:
                    if '1 string m_Name' in monoglobal[key][subkey]['0 GameObject Base']:
                        if monoglobal[key][subkey]['0 GameObject Base']['1 string m_Name'] == pathname:
                            return key, subkey
    return '', ''

def build_ca(ability): # combine with other build_s?
    data = {}
    if 'title' in ability:
        data['title'] = ability['title']
    if 'description' in ability:
        data['description'] = ability['description']
    return data

def build_ma(ma_key, ma_subkey):
    components = monoglobal[ma_key]
    ma_core = monoglobal[ma_key][ma_subkey]['0 GameObject Base']

    def build_subs(substitutions, tieraw):
        subs = []
        for substitution in substitutions:
            sub0, sub1 = substitution.split('.')
            # sub0 = sub0.upper()
            sub1 = sub1[0].lower() + sub1[1:]
            for ngyy in iter_thing(tieraw):
                if ngyy['id'] == sub0:
                    value = ngyy[sub1]
                    print(value, type(value))
                    if value % 2048 == 0:
                        value = value / 2048
                    subs.append(value)
            # for ngyy in iter_thing(abovewards):
            #     pass
        return subs

    def iter_thing(thing, skip_keys=[]):
        'Iterate through everything nested within an object.'
        if isinstance(thing, dict):
            if 'm_PathID' in thing:
                thing = follow_id(components, thing)
            if 'id' in thing:
                yield thing
            for key in thing:
                if key not in skip_keys:
                    for subthing in iter_thing(thing[key], skip_keys):
                        yield subthing
        elif isinstance(thing, list):
            for item in thing:
                for subthing in iter_thing(item, skip_keys):
                    yield subthing

    def build_tiers(temp, paths, substitutions):
        tiers = []
        for path in paths:
            raw = follow_id(components, path)
            tier = {}
            tier['level'] = raw['unlockAtLevel']
            tier['values'] = build_subs(substitutions, raw)
            tiers.append(tier)
        return tiers

    def build_features(paths):
        features = []
        for path in paths:
            raw = follow_id(components, path)
            feature = {}
            # feature['title'] = raw['title']
            feature['description'] = raw['description']
            feature['tiers'] = build_tiers(raw['description'], raw['tiers']['Array'], raw['substitutions']['Array'])
            features.append(feature)
        return features

    ability = {}
    if '1 string m_Name' in ma_core:
        ability['title'] = ma_core['1 string m_Name']
    if '0 vector m_Component' in ma_core:
        for thing in ma_core['0 vector m_Component']['1 Array Array']:
            component = follow_id(components, thing['0 ComponentPair data']['0 PPtr<Component> component'])
            if 'title' in component and 'features' in component:
                ability['title'] = component['title']
                ability['features'] = build_features(component['features']['Array'])
                break
    return ability

def get_characters(character_keys, variant_keys): # figure out why beowulf is gone
    characters = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        id = character['humanReadableGuid']
        if id == '':
            id = character['guid']
        data = {}
        data['name'] = character['displayName']
        ca = follow_id(monoshared, character['characterAbility'])
        data['ca'] = build_ca(ca)
        for variant_key in variant_keys:
            variant = monoshared[variant_key]
            if variant['superAbility']['resourcePath'] == '': # dummy
                continue
            base = variant['baseCharacter']
            base_key = str(base['m_PathID'])
            if base_key == character_key:
                ma_key, ma_subkey = follow_resource(variant['superAbility'])
                data['ma'] = build_ma(ma_key, ma_subkey)
                break
        characters[id] = data
    return characters

def get_variants(variant_keys):
    variants = {}
    for variant_key in variant_keys:
        variant = monoshared[variant_key]
        id = variant['humanReadableGuid']
        if id == '':
            id = variant['guid']
        data = {}
        character = follow_id(monoshared, variant['baseCharacter'])
        if character == {}:
            print('Cannot find', variant['baseCharacter'], 'for', id)
        else:
            data['base'] = character['humanReadableGuid']
        data['name'] = variant['displayVariantName']
        data['quote'] = variant['variantQuote']
        data['tier'] = variant['initialTier']
        data['element'] = variant['elementAffiliation']
        data['stats'] = variant['baseScaledValuesByTier']['Array']
        # sa = follow_id(monoshared, variant['signatureAbility'])
        # data['sa'] = ability_core(sa)
        data['fandom'] = corpus['en'][variant['displayVariantName']]
        variants[id] = data
    return variants

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = monoglobal[character_key]
        for sm_ref in character['specialMoves']['Array']:
            sm_key = str(sm_ref['m_PathID'])
            sm = monoglobal[sm_key]
            id = sm['humanReadableGuid']
            if id == '':
                id = sm['guid']
            data = {}
            data['base'] = character['humanReadableGuid']
            data['icon'] = follow_id(monoshared, sm['palettizedIcon'])['dynamicSprite']['resourcePath'].split('/')[-1]
            data['title'] = sm['title']
            data['type'] = 0
            data['tier'] = sm['tier']
            data['gear'] = sm['gearDamageTier']
            data['cost'] = sm['gearPointsCost']
            data['attack'] = sm['attackDamageMultipliers']
            data['damage'] = sm['damageIndicatorLevels']
            data['cooldown'] = sm['cooldownTimes']
            ability = follow_id(monoshared, sm['signatureAbility'])
            data['ability'] = ability_core(ability)
            sms[id] = data
    return sms

def get_bbs(character_keys):
    bbs = {}
    for character_key in character_keys:
        character = monoglobal[character_key]
        for bb_ref in character['blockbusters']['Array']:
            bb_key = str(bb_ref['m_PathID'])
            bb = monoglobal[bb_key]
            id = bb['humanReadableGuid']
            if id == '':
                id = bb['guid']
            data = {}
            data['base'] = character['humanReadableGuid']
            data['icon'] = follow_id(monoshared, bb['palettizedIcon'])['dynamicSprite']['resourcePath'].split('/')[-1]
            data['title'] = bb['title']
            data['type'] = 0
            data['tier'] = bb['tier']
            data['gear'] = bb['gearDamageTier']
            data['cost'] = bb['gearPointsCost']
            data['attack'] = bb['attackDamageMultipliers']
            data['damage'] = bb['damageIndicatorLevels']
            data['cooldown'] = bb['strengthLevel']
            ability = follow_id(monoshared, bb['signatureAbility'])
            data['ability'] = ability_core(ability)
            bbs[id] = data
    return bbs

def get_catalysts(catalyst_keys):
    catalysts = {}
    for catalyst_key in catalyst_keys:
        catalyst = monoglobal[catalyst_key]
        id = catalyst['humanReadableGuid']
        if id == '':
            id = catalyst['guid']
        data = {}
        data['title'] = catalyst['title']
        data['tier'] = catalyst['tier']
        data['icon'] = catalyst['icon']['resourcePath']
        data['characterLock'] = catalyst['randomCharacter']
        data['elementLock'] = catalyst['randomElement']
        constraint = follow_id(monoshared, catalyst['abilityConstraint'])
        data['constraint'] = {}
        if 'charactersNeeded' in constraint:
            character_ref = constraint['charactersNeeded']['Array'][0]
            character = follow_id(monoshared, character_ref)
            if 'humanReadableGuid' in character:
                data['constraint']['base'] = character['humanReadableGuid']
            else:
                data['constraint']['base'] = 'be' # WHY IS BEOWULF'S FILE MISSING???
        if 'elementsNeeded' in constraint:
            data['constraint']['element'] = constraint['elementsNeeded']['Array'][0]
        ability = follow_id(monoshared, catalyst['signatureAbility'])
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
    character_keys = get_keys(character_traits)
    variant_keys = get_keys(variant_traits)
    catalyst_keys = get_keys(catalyst_traits)

    for key in character_keys:
        if monoshared[key]['humanReadableGuid'] == 'rf':
            charkey = key
            break
    for key in variant_keys:
        if str(monoshared[key]['baseCharacter']['m_PathID']) == charkey:
            varkey = key
            break
    ma_key, ma_subkey = follow_resource(monoshared[varkey]['superAbility'])
    monoglobal[ma_key]

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
