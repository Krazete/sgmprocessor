import re
import UnityPy
from data_processing import file
import json

monobehaviour = file.load('data_processing/input/MonoBehaviour', True)
monolith = monobehaviour['sharedassets0.assets.split0']
phone = UnityPy.load(
    'data_processing/input/localization',
    'data_processing/input/signatureabilities'
)

def all_assets(bundle):
    for sf in phone.assets[bundle].values():
        if isinstance(sf, UnityPy.files.SerializedFile):
            for k in sf.keys():
                yield k, sf[k]

def read_obj(obj):
    return obj.read().read_type_tree().to_dict()

def get_corpus():
    corpus = {}
    for pid, obj in all_assets('localization'):
        data = read_obj(obj)
        if 'name' in data and 'm_Script' in data:
            corpus[data['name']] = json.loads(data['m_Script'])
    return corpus

def find_by_pathid(bundle, m_PathID):
    for pid, obj in all_assets(bundle):
        if pid == m_PathID:
            yield read_asset(obj)





placeholder = re.compile('{.*?}') # for build_features in build_ability

def get_keys(attributes):
    'Get monolith keys of objects with certain attributes.'
    keys = set()
    for key in monolith:
        has_all_attributes = True
        for attribute in attributes:
            if attribute not in monolith[key]:
                has_all_attributes = False
                break
        if has_all_attributes:
            keys.add(key)
    return keys

def follow_id(parent, pointer):
    'Get object (from specified parent object) referenced by m_PathID object.'
    m_PathID = 'm_PathID' if 'm_PathID' in pointer else '0 SInt64 m_PathID'
    if m_PathID in pointer:
        key = str(pointer[m_PathID])
        return parent.get(key, {})
    return {}

def follow_resource(pointer): # todo
    'Get monoglobal key and subkey referenced by resourcePath object.'
    path = pointer['resourcePath'].split('/')[-1] # .split for catalysts
    if 'resourcePath' in pointer:
        for key in monoglobal:
            for subkey in monoglobal[key]:
                base = monoglobal[key][subkey].get('0 GameObject Base', {})
                name = base.get('1 string m_Name')
                if name == path:
                    return key, subkey
    return '', ''

def create_id(parent, data):
    'Retrieve ID from data and alter it to be unique if necessary.'
    dupe = False
    id = data['humanReadableGuid']
    if id == '':
        id = data['guid']
    while id in parent:
        dupe = True
        id += '_'
    if dupe: # warn about a possible ID inconsistency which may need manual fixing
        print('WARNING: A non-unique ID has been detected and renamed:', id)
    return id

def is_dummy(variant):
    return variant['superAbility']['resourcePath'] == ''

def build_character_ablity(ability):
    if 'title' in ability and 'description' in ability:
        return {
            'title': ability['title'],
            'description': ability['description']
        }
    return {} # fukua

def build_ability(ability_key, ability_subkey, has_subtitles=False): # todo
    if ability_key not in monoglobal:
        return {}
    components = monoglobal[ability_key]
    base = components[ability_subkey]['0 GameObject Base']

    visited = set()
    def iter_effects(data, skip_keys=[], root=True):
        'Iterate through all effects nested within an object.'
        if root:
            skip_keys.append('randomModifierList') # prevent faulty values e.g. for circular breathing
            visited.clear()
        if isinstance(data, dict):
            if 'm_PathID' in data:
                m_PathID = data.get('m_PathID')
                if m_PathID not in visited:
                    data = follow_id(components, data)
                visited.add(m_PathID)
            if 'id' in data:
                yield data
            for key in data:
                if key not in skip_keys:
                    for subdata in iter_effects(data[key], skip_keys, False):
                        yield subdata
        elif isinstance(data, list):
            for item in data:
                for subdata in iter_effects(item, skip_keys, False):
                    yield subdata

    def get_true_value(value):
        if isinstance(value, str):
            return float(value)
        if isinstance(value, dict):
            return value['value'] / 2048
        return value

    def build_values(feature, tier, substitutions):
        values = []
        for substitution in substitutions:
            id, stat = substitution.split('.')
            id = id.lower()
            stat = stat[0].lower() + stat[1:]
            if stat == 'pERCENTAGE': # buer catalyst
                stat = 'percentage'
            not_found = True
            for effect in iter_effects(tier):
                if effect['id'].lower() == id:
                    value = get_true_value(effect[stat])
                    values.append(value)
                    not_found = False
                    break
            if not_found:
                for effect in iter_effects(feature, ['tiers']):
                    if effect['id'].lower() == id:
                        value = get_true_value(effect[stat])
                        values.append(value)
                        break
        return values

    def build_tiers(feature, tierlist, substitutions):
        tiers = []
        for pointer in tierlist:
            tier = follow_id(components, pointer)
            tiers.append({
                'level': tier['unlockAtLevel'],
                'values': build_values(feature, tier, substitutions)
            })
        return tiers

    def build_features(featurelist):
        features = []
        for pointer in featurelist:
            feature = follow_id(components, pointer)
            tierlist = feature['tiers']['Array']
            substitutions = feature['substitutions']['Array']
            data = {
                'description': feature['description'],
                'tiers': build_tiers(feature, tierlist, substitutions)
            }

            ### fill in missing data
            # # level 9 value for center stage
            if data['description'] == 'Char_Cerebella_SUP_CenterStage_Feat2_Desc':
                data['tiers'][8]['values'] = [13]
            # # resurrect values for forbidden procedure
            if data['description'] == 'SA_Valentine_BB4':
                data['tiers'][0]['values'] = [0.15]
                data['tiers'][1]['values'] = [0.2]
                data['tiers'][2]['values'] = [0.25]
            # double check if there are enough values for all placeholders
            variables = set(re.findall(placeholder, corpus['en'].get(feature['description'], '')))
            for i, tier in enumerate(data['tiers']):
                if len(tier['values']) < len(variables):
                    print('Warning: Missing ability data for tier {} ({}) of feature \'{}\'.'.format(i, tier, data['description']))

            # afaik only marquees have subtitles
            if has_subtitles:
                data['title'] = feature['title']
            features.append(data)
        return features

    title = base['1 string m_Name']
    componentlist = base['0 vector m_Component']['1 Array Array']
    for pointerdata in componentlist:
        pointer = pointerdata['0 ComponentPair data']['0 PPtr<Component> component']
        component = follow_id(components, pointer)
        if 'title' in component and 'features' in component:
            return {
                'title': component['title'],
                'features': build_features(component['features']['Array'])
            }
    return {}

def get_characters(character_keys, variant_keys):
    characters = {}
    for character_key in character_keys:
        character = monolith[character_key]
        id = create_id(characters, character)
        ca = follow_id(monolith, character['characterAbility'])
        ma_key, ma_subkey = None, None # prevent assigning previous ma
        for variant_key in variant_keys:
            variant = monolith[variant_key]
            if is_dummy(variant):
                continue
            base_key = str(variant['baseCharacter']['m_PathID'])
            if base_key == character_key:
                ma_key = variant['superAbility']
                break
        character = {
            'name': character['displayName'],
            'ca': build_character_ablity(ca),
            'ma': build_ability(ma_key, True),
            'pa': build_ability(read_obj(phonebook[phone.assets['signatureabilities'].container[character['prestigeAbility']['resourcePath']].path_id]))
        }
        characters[id] = character
    return characters

def get_variants(variant_keys):
    variants = {}
    for variant_key in variant_keys:
        variant = monolith[variant_key]
        if is_dummy(variant):
            continue
        id = create_id(variants, variant)
        character = follow_id(monolith, variant['baseCharacter'])
        if character == {}:
            print('Warning: Cannot find {} for \'{}\'.'.format(variant['baseCharacter'], id))
        sa_key = variant['signatureAbility']
        variants[id] = {
            'base': character['humanReadableGuid'],
            'name': variant['displayVariantName'],
            'quote': variant['variantQuote'],
            'tier': variant['initialTier'],
            'element': variant['elementAffiliation'],
            'stats': variant['baseScaledValuesByTier']['Array'],
            'sa': build_ability(sa_key),
            'fandom': corpus['en'][variant['displayVariantName']]
        }
    return variants

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = monolith[character_key]
        for pointer in character['specialMoves']['Array']:
            sm = follow_id(monolith, pointer)
            id = create_id(sms, sm)
            if sm['cooldownTimes']['Array'] == [-1]: # competitive pvp burst
                continue
            icon = follow_id(monolith, sm['palettizedIcon'])
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
        character = monolith[character_key]
        for pointer in character['blockbusters']['Array']:
            bb = follow_id(monolith, pointer)
            id = create_id(bbs, bb)
            icon = follow_id(monolith, bb['palettizedIcon'])
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
        catalyst = monolith[catalyst_key]
        id = create_id(catalysts, catalyst)
        characters = []
        elements = []
        constraint = follow_id(monolith, catalyst['abilityConstraint'])
        if 'charactersNeeded' in constraint:
            for pointer in constraint['charactersNeeded']['Array']:
                character = follow_id(monolith, pointer)
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

def get_ability(thing):
    return read_obj(phone.container[thing['resourcePath']])

if __name__ == '__main__':
    phonebook = dict(all_assets('signatureabilities'))
    corpus = get_corpus()

    character_keys = get_keys(['characterAbility', 'englishVoArtist'])
    variant_keys = get_keys(['baseCharacter', 'displayVariantName', 'variantQuote'])
    # catalyst_keys = get_keys(['randomCharacter', 'randomElement'])

    ### study marquee ability of specific character
    for charkey in character_keys:
        if monolith[charkey]['humanReadableGuid'] == 'va':
            break
    for varkey in variant_keys:
        var = monolith[varkey]
        if str(var['baseCharacter']['m_PathID']) == charkey and not is_dummy(var):
            break


    def dereference(pointer):
        if pointer['m_PathID'] in phonebook:
            return read_obj(phonebook[pointer['m_PathID']])
        return {}

    def build_ability(zxc, has_subtitles=False):
        visited = set()
        def iter_effects(data, skip_keys=[], root=True):
            'Iterate through all effects nested within an object.'
            if root:
                skip_keys.append('randomModifierList') # prevent faulty values e.g. for circular breathing
                visited.clear()
            if isinstance(data, dict):
                if 'm_PathID' in data:
                    m_PathID = data.get('m_PathID')
                    if m_PathID not in visited:
                        data = dereference(data)
                    visited.add(m_PathID)
                if 'id' in data:
                    yield data
                for key in data:
                    if key not in skip_keys:
                        for subdata in iter_effects(data[key], skip_keys, False):
                            yield subdata
            elif isinstance(data, list):
                for item in data:
                    for subdata in iter_effects(item, skip_keys, False):
                        yield subdata

        def get_true_value(value):
            if isinstance(value, str):
                return float(value)
            if isinstance(value, dict):
                return value['value'] / 2048
            return value

        def build_values(feature, tier, substitutions):
            values = []
            for substitution in substitutions:
                id, stat = substitution.split('.')
                id = id.lower()
                stat = stat[0].lower() + stat[1:]
                if stat == 'pERCENTAGE': # buer catalyst
                    stat = 'percentage'
                not_found = True
                for effect in iter_effects(tier):
                    if effect['id'].lower() == id:
                        value = get_true_value(effect[stat])
                        values.append(value)
                        not_found = False
                        break
                if not_found:
                    for effect in iter_effects(feature, ['tiers']):
                        if effect['id'].lower() == id:
                            value = get_true_value(effect[stat])
                            values.append(value)
                            break
            return values

        def build_tiers(feature, tierlist, substitutions):
            tiers = []
            for pointer in tierlist:
                tier = dereference(pointer)
                tiers.append({
                    'level': tier['unlockAtLevel'],
                    'values': build_values(feature, tier, substitutions)
                })
            return tiers

        def build_features(featurelist):
            features = []
            for pointer in featurelist:
                feature = dereference(pointer)
                data = {
                    'title': feature['title'], # ma only
                    'description': feature['description'],
                    'tiers': build_tiers(feature, feature['tiers'], feature['substitutions'])
                }

                # resurrect values for forbidden procedure
                if data['description'] == 'SA_Valentine_BB4':
                    print(data['description'], data['tiers'])
                    data['tiers'][0]['values'] = [0.15]
                    data['tiers'][1]['values'] = [0.2]
                    data['tiers'][2]['values'] = [0.25]
                # double check if there are enough values for all placeholders
                variables = set(re.findall(placeholder, corpus['en'].get(feature['description'], '')))
                for i, tier in enumerate(data['tiers']):
                    if len(tier['values']) < len(variables):
                        print('Warning: Missing ability data for tier {} ({}) of feature \'{}\'.'.format(i, tier, data['description']))

                features.append(data)
            return features

        container = read_obj(phone.container[zxc['resourcePath']])
        for component in container['m_Component']:
            ability = dereference(component['component'])
            if 'title' in ability and 'features' in ability:
                return {
                    'title': ability['title'],
                    'features': build_features(ability['features'])
                }
        return {}
    build_ability(var['superAbility'])

    # main = get_ability(var['superAbility'])
    # for x in main['m_Component']:
    #     w = phonebook[x['component']['m_PathID']]
    #     if 'title' in w and 'features' in w:
    #         print(w['title'], w['features'])
    # phonebook[3299978497162081884]
    # key, subkey = follow_resource(monolith[varkey]['superAbility'])
    # monoglobal[key]

    ### study how build_ability handles certain ability data
    # sa = follow_id(monolith, monolith[charkey]['specialMoves']['Array'][2])
    # k, sk = follow_resource(sa['signatureAbility'])
    # monoglobal[k][sk]
    # build_ability(k, sk)

    characters = get_characters(character_keys, variant_keys)
    variants = get_variants(variant_keys)
    # sms = get_sms(character_keys)
    # bbs = get_bbs(character_keys)
    # catalysts = get_catalysts(catalyst_keys)

    file.mkdir('data_processing/output')

    file.save(characters, 'data_processing/output/characters.json')
    file.save(variants, 'data_processing/output/variants.json')
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
        file.save(corpus_core, 'data_processing/output/{}.json'.format(language))

    # with open('data_processing/output/corpus_en.json', 'w') as file:
    #     json.dump(corpus['en'], file, indent=4, separators=(',', ': '))
