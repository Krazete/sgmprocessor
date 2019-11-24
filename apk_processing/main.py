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

def build_ability(ability_key, ability_subkey):
    components = monoglobal[ability_key]
    ma_core = monoglobal[ability_key][ability_subkey]['0 GameObject Base']

    def getsubval(value):
        if isinstance(value, str):
            return float(value)
        if isinstance(value, dict):
            return value['value'] / 2048
        return value

    def build_subs(ft, substitutions, tieraw):
        subs = []
        for substitution in substitutions:
            sub0, sub1 = substitution.split('.')
            sub1 = sub1[0].lower() + sub1[1:]
            keepsearching = True
            for ngyy in iter_thing(tieraw):
                if ngyy['id'] == sub0:
                    value = getsubval(ngyy[sub1])
                    subs.append(value)
                    keepsearching = False
                    break
            if keepsearching:
                for ngyy in iter_thing(ft, ['tiers']):
                    if ngyy['id'] == sub0:
                        value = getsubval(ngyy[sub1])
                        subs.append(value)
                        break
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

    def build_tiers(ft, paths, substitutions):
        tiers = []
        for path in paths:
            raw = follow_id(components, path)
            tier = {}
            tier['level'] = raw['unlockAtLevel']
            tier['values'] = build_subs(ft, substitutions, raw)
            tiers.append(tier)
        return tiers

    def build_features(paths):
        features = []
        for path in paths:
            raw = follow_id(components, path)
            feature = {}
            if raw['title'] != '': # find a better way to detect if ability is a marquee
                feature['title'] = raw['title']
            feature['description'] = raw['description']
            feature['tiers'] = build_tiers(raw, raw['tiers']['Array'], raw['substitutions']['Array'])
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

def is_dummy(variant):
    return variant['superAbility']['resourcePath'] == ''

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
            if is_dummy(variant):
                continue
            base = variant['baseCharacter']
            base_key = str(base['m_PathID'])
            if base_key == character_key:
                ability_key, ability_subkey = follow_resource(variant['superAbility'])
                data['ma'] = build_ability(ability_key, ability_subkey)
                break
        characters[id] = data
    return characters

def get_variants(variant_keys):
    variants = {}
    for variant_key in variant_keys:
        variant = monoshared[variant_key]
        if is_dummy(variant):
            continue
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
        sa_key, sa_subkey = follow_resource(variant['signatureAbility'])
        # print(id, variant['signatureAbility'])
        data['sa'] = build_ability(sa_key, sa_subkey)
        data['fandom'] = corpus['en'][variant['displayVariantName']]
        variants[id] = data
    return variants

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        for sm_ref in character['specialMoves']['Array']:
            sm = follow_id(monoshared, sm_ref)
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
            if sm['signatureAbility']['resourcePath'] != '':
                ability_key, ability_subkey = follow_resource(sm['signatureAbility'])
                data['ability'] = build_ability(ability_key, ability_subkey)
            sms[id] = data
    return sms

def get_bbs(character_keys):
    bbs = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        for bb_ref in character['blockbusters']['Array']:
            bb = follow_id(monoshared, bb_ref)
            id = bb['humanReadableGuid']
            if id == '':
                id = bb['guid']
            data = {}
            data['base'] = character['humanReadableGuid']
            data['icon'] = follow_id(monoshared, bb['palettizedIcon'])['dynamicSprite']['resourcePath'].split('/')[-1]
            data['title'] = bb['title']
            data['type'] = 1
            data['tier'] = bb['tier']
            data['gear'] = bb['gearDamageTier']
            data['cost'] = bb['gearPointsCost']
            data['attack'] = bb['attackDamageMultipliers']
            data['damage'] = bb['damageIndicatorLevels']
            data['cooldown'] = bb['strengthLevel']
            if bb['signatureAbility']['resourcePath'] != '':
                ability_key, ability_subkey = follow_resource(bb['signatureAbility'])
                data['ability'] = build_ability(ability_key, ability_subkey)
            bbs[id] = data
    return bbs

def get_catalysts(catalyst_keys):
    catalysts = {}
    for catalyst_key in catalyst_keys:
        catalyst = monoshared[catalyst_key]
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
        # if catalyst['signatureAbility']['resourcePath'] != '':
        #     skasdasd, skasdasdasdk = follow_resource(catalyst['signatureAbility'])
        #     print(id, follow_resource(catalyst['signatureAbility']))
        #     data['ability'] = build_ability(skasdasd, skasdasdasdk)
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

    # for key in character_keys:
    #     if monoshared[key]['humanReadableGuid'] == 'va':
    #         charkey = key
    #         break
    # for key in variant_keys:
    #     if str(monoshared[key]['baseCharacter']['m_PathID']) == charkey:
    #         varkey = key
    #         break
    # ability_key, ability_subkey = follow_resource(monoshared[varkey]['superAbility'])
    # monoglobal[ability_key]

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
