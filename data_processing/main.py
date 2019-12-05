from data_processing import file

monosharedraw = file.load('data_processing/input/MonoBehaviourShared', True)
monoshared = monosharedraw['sharedassets0.assets.split0']
monoglobal = file.load('data_processing/input/MonoBehaviourGlobal', True)
corpus = file.load('data_processing/input/TextAsset')

def get_keys(attributes):
    'Get monoshared keys of objects with certain attributes.'
    keys = set()
    for key in monoshared:
        has_all_attributes = True
        for attribute in attributes:
            if attribute not in monoshared[key]:
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

def follow_resource(pointer):
    'Get monoglobal key and subkey referenced by resourcePath object.'
    if 'resourcePath' in pointer:
        for key in monoglobal:
            for subkey in monoglobal[key]:
                base = monoglobal[key][subkey].get('0 GameObject Base', {})
                path = base.get('1 string m_Name')
                if path == pointer['resourcePath']:
                    return key, subkey
    return '', ''

def create_id(parent, data):
    'Retrieve ID from data and alter it to be unique if necessary.'
    id = data['humanReadableGuid']
    if id == '':
        id = data['guid']
    while id in parent:
        id += '_'
    return id

def is_dummy(variant):
    return variant['superAbility']['resourcePath'] == ''

def build_character_ablity(ability):
    if 'title' in ability and 'description' in ability:
        return {
            'title': ability['title'],
            'description': ability['description']
        }
    return {} # for fukua

def build_ability(ability_key, ability_subkey, has_subtitles=False):
    if ability_key not in monoglobal:
        return {}
    components = monoglobal[ability_key]
    base = components[ability_subkey]['0 GameObject Base']

    def iter_effects(data, skip_keys=[]):
        'Iterate through all effects nested within an object.'
        if isinstance(data, dict):
            if 'm_PathID' in data:
                data = follow_id(components, data)
            if 'id' in data:
                yield data
            for key in data:
                if key not in skip_keys:
                    for subdata in iter_effects(data[key], skip_keys):
                        yield subdata
        elif isinstance(data, list):
            for item in data:
                for subdata in iter_effects(item, skip_keys):
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

def get_characters(character_keys, variant_keys): # where is beowulf's file?
    characters = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        id = build_id(characters, character)
        ca = follow_id(monoshared, character['characterAbility'])
        ma_key, ma_subkey = None, None # prevent assigning previous ma
        for variant_key in variant_keys:
            variant = monoshared[variant_key]
            if is_dummy(variant):
                continue
            base_key = str(variant['baseCharacter']['m_PathID'])
            if base_key == character_key:
                ma_key, ma_subkey = follow_resource(variant['superAbility'])
                break
        character = {
            'name': character['displayName'],
            'ca': build_character_ablity(ca),
            'ma': build_ability(ma_key, ma_subkey, True)
        }
        characters[id] = character
    return characters

def get_variants(variant_keys):
    variants = {}
    for variant_key in variant_keys:
        variant = monoshared[variant_key]
        if is_dummy(variant):
            continue
        id = create_id(variants, variant)
        character = follow_id(monoshared, variant['baseCharacter'])
        if character == {}:
            print('Cannot find', variant['baseCharacter'], 'for', id)
        sa_key, sa_subkey = follow_resource(variant['signatureAbility'])
        variants[id] = {
            'base': character['humanReadableGuid'],
            'name': variant['displayVariantName'],
            'quote': variant['variantQuote'],
            'tier': variant['initialTier'],
            'element': variant['elementAffiliation'],
            'stats': variant['baseScaledValuesByTier']['Array'],
            'sa': build_ability(sa_key, sa_subkey),
            'fandom': corpus['en'][variant['displayVariantName']]
        }
    return variants

def get_sms(character_keys):
    sms = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        for pointer in character['specialMoves']['Array']:
            sm = follow_id(monoshared, pointer)
            id = create_id(sms, sm)
            icon = follow_id(monoshared, sm['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
            sma_key, sma_subkey = follow_resource(sm['signatureAbility'])
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
                'ability': build_ability(sma_key, sma_subkey)
            }
    return sms

def get_bbs(character_keys):
    bbs = {}
    for character_key in character_keys:
        character = monoshared[character_key]
        for pointer in character['blockbusters']['Array']:
            bb = follow_id(monoshared, pointer)
            id = create_id(bbs, bb)
            icon = follow_id(monoshared, bb['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
            bba_key, bba_subkey = follow_resource(bb['signatureAbility'])
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
                'ability': build_ability(bba_key, bba_subkey)
            }
    return bbs

def get_catalysts(catalyst_keys): #
    catalysts = {}
    for catalyst_key in catalyst_keys:
        catalyst = monoshared[catalyst_key]
        id = create_id(catalysts, catalyst)
        catalysts[id] = {
            'title': catalyst['title'],
            'tier': catalyst['tier'],
            'icon': catalyst['icon']['resourcePath'],
            'characterLock': catalyst['randomCharacter'],
            'elementLock': catalyst['randomElement'],
            'constraint': {}
        }

        # constraint = follow_id(monoshared, catalyst['abilityConstraint'])
        # print
        # if 'charactersNeeded' in constraint:
        #     character_ref = constraint['charactersNeeded']['Array'][0]
        #     character = follow_id(monoshared, character_ref)
        #     if 'humanReadableGuid' in character:
        #         data['constraint']['base'] = character['humanReadableGuid']
        #     else:
        #         data['constraint']['base'] = 'be'
        # if 'elementsNeeded' in constraint:
        #     data['constraint']['element'] = constraint['elementsNeeded']['Array'][0]

        # if catalyst['signatureAbility']['resourcePath'] != '':
        #     skasdasd, skasdasdasdk = follow_resource(catalyst['signatureAbility'])
        #     print(id, catalyst['signatureAbility'], follow_resource(catalyst['signatureAbility']))
        #     data['ability'] = build_ability(skasdasd, skasdasdasdk)
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
    character_keys = get_keys(['characterAbility', 'englishVoArtist'])
    variant_keys = get_keys(['baseCharacter', 'displayVariantName', 'variantQuote'])
    catalyst_keys = get_keys(['randomCharacter', 'randomElement'])

    ### study marquee ability of specific character
    # for charkey in character_keys:
    #     if monoshared[charkey]['humanReadableGuid'] == 'va':
    #         break
    # for varkey in variant_keys:
    #     if str(monoshared[varkey]['baseCharacter']['m_PathID']) == charkey:
    #         break
    # key, subkey = follow_resource(monoshared[varkey]['superAbility'])
    # monoglobal[key]

    ### study how build_ability handles certain ability data
    # sa = follow_id(monoshared, monoshared[charkey]['specialMoves']['Array'][2])
    # k, sk = follow_resource(sa['signatureAbility'])
    # monoglobal[k][sk]
    # build_ability(k, sk)

    characters = get_characters(character_keys, variant_keys)
    variants = get_variants(variant_keys)
    sms = get_sms(character_keys)
    bbs = get_bbs(character_keys)
    moves = {**sms, **bbs}
    # catalysts = get_catalysts(catalyst_keys)

    file.resetdir('data_processing/output')

    file.save(characters, 'data_processing/output/characters.json')
    file.save(variants, 'data_processing/output/variants.json')
    file.save(moves, 'data_processing/output/moves.json')
    # file.save(catalysts, 'data_processing/output/catalysts.json')

    corpus_keys = set()
    corpus_keys |= get_corpus_keys(characters)
    corpus_keys |= get_corpus_keys(variants)
    corpus_keys |= get_corpus_keys(moves)
    # corpus_keys |= get_corpus_keys(catalysts)

    for language in corpus:
        corpus_core = {key: corpus[language][key] for key in corpus_keys if key in corpus[language]}
        corpus_core[''] = 'UNDEFINED'
        file.save(corpus_core, 'data_processing/output/{}.json'.format(language))
