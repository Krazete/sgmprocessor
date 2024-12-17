import re
import json
import UnityPy
from functools import lru_cache
from data_processing import file

### DATA INITIALIZATION ###

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

### MAIN FUNCTIONS ###

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
    id = ptr['m_PathID']
    if id in sa0.keys():
        return read_obj(sa0[ptr['m_PathID']])
    return {}

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
        warn('Unintuitive ID:', id, expected=True) # todo: make better message here

    dupe = False
    while id in parent:
        dupe = True
        id += '_'
    if dupe: # warn about a possible ID inconsistency which may need manual fixing
        warn('A non-unique ID has been detected and renamed:', id, expected=(id == 'rCopy_' or '-sm-' in id or '-bb-' in id))

    return id

def is_collectible(variant):
    'True if Variant has Marquee Ability (e.g. no Sparring Partners or Competitive Fighters).'
    return variant['superAbility']['resourcePath'] != ''

def get_true_value(value):
    'Return true value of ability data numbers.'
    if isinstance(value, str):
        return float(value)
    if isinstance(value, dict):
        return value['value'] / 2048
    return value

def build_character_ablity(abilityptr):
    ability = sa0_get_id(abilityptr)
    return {
        'title': ability['title'],
        'description': ability['description']
    }

def build_prestige_ability(abilityptr, cid):
    ability = sig_get_rp(abilityptr)

    def get_extra(ptr, key):
        extra = sig_get_id(ptr)
        return get_true_value(extra[key])

    componentptrs = ability['m_Component']
    for componentptr in componentptrs:
        component = sig_get_id(componentptr['component'])
        if 'title' in component and 'description' in component:
            match cid:
                case 'an': extra = {'starPower': 1}
                case 'be': extra = {'secondsElapsed': component['secondsElapsed']}
                case 'mf': extra = {'evasion': get_extra(component['evasionModifier'], 'duration')} # interchangeable with 'guardBreakModifier'
                case 'um': extra = {'hungerDifference': 1, 'regen': get_extra(component['regenModifier'], 'percentMaxLife')}
                case 'va': extra = {'healthRecovered': 1, 'resurrection': get_extra(component['resurrectionModifier'], 'value')}
                case _: extra = {}
            return {
                'title': component['title'],
                'description': component['description'],
                'chargeRate': get_true_value(component['chargePerAction']),
                'base': get_true_value(component['baseBonus']),
                'lvlBonus': get_true_value(component['bonusPerLevels']['numerator']) / component['bonusPerLevels']['denominator'],
                'maxBonus': get_true_value(component['maxLevelBonus']) # todo: truncate this to the hundredths
            } | extra

def build_ability(abilityptr):
    ability = sig_get_rp(abilityptr)

    def build_value(subx, suby, level, tier, feature):
        for ptr in feature['triggerConditions']: # if it doesn't change, it's not in tiers
            modifier = sig_get_id(ptr)
            if modifier['id'] == subx:
                return modifier[suby]
        for ptr in feature['provokerConditions']: # if it doesn't change, it's not in tiers
            modifier = sig_get_id(ptr)
            if modifier['id'] == subx:
                return modifier[suby]

        for ptr in tier['triggerConditions']:
            modifier = sig_get_id(ptr)
            if modifier['id'] == subx:
                return modifier[suby]
        for ptr in tier['provokerConditions']:
            modifier = sig_get_id(ptr)
            if modifier['id'] == subx:
                return modifier[suby]

        for modifierset in tier['modifierSets']:
            for modifierptr in modifierset['modifiers']:
                modifier = sig_get_id(modifierptr)
                if modifier['id'] == subx:
                    try:
                        return modifier[suby]
                    except:
                        return modifier[suby.lower()] # hacky fix for rBlonde
                if 'delayedModifier' in modifier:
                    delay = sig_get_id(modifier['delayedModifier'])
                    if 'id' in delay and delay['id'] == subx:
                        return delay[suby]
                if 'convertTo' in modifier:
                    converttt = sig_get_id(modifier['convertTo'])
                    if 'id' in converttt and converttt['id'] == subx:
                        return converttt[suby]
                if 'effects' in modifier:
                    for xptr in modifier['effects']:
                        x = sig_get_id(xptr['modifier'])
                        if 'id' in x and x['id'] == subx:
                            return x[suby]

        for modifier in tier['additionalStringSubstitutions']:
            if modifier['id'] == subx and suby in modifier:
                return modifier[suby]

        for subfeatureptr in feature['subFeatures']: # recurse through subfeatures
            subfeature = sig_get_id(subfeatureptr)
            for subtierptr in subfeature['tiers']:
                subtier = sig_get_id(subtierptr)
                sublevel = subtier['unlockAtLevel']
                if level == sublevel:
                    subvalue = build_value(subx, suby, level, subtier, subfeature)
                    if subvalue:
                        return subvalue

        for subfeatureptr in feature['subFeatures']: # recurse through subfeatures and ignore level checks
            subfeature = sig_get_id(subfeatureptr)
            for subtierptr in subfeature['tiers']:
                subtier = sig_get_id(subtierptr)
                sublevel = subtier['unlockAtLevel']
                subvalue = build_value(subx, suby, level, subtier, subfeature)
                if subvalue:
                    warn('Value for ability extracted from feature without regard for tier level.')
                    print('\tSubstitution:', subx, suby)
                    print('\tValue:', get_true_value(subvalue))
                    print('\tLevel:', level)
                    print('\tAbility:', corpus['en'][feature['description']])
                    return subvalue

    def build_tier(tierptr, feature, substitutions):
        tier = sig_get_id(tierptr)
        level = tier['unlockAtLevel']

        return {
            "level": level,
            "values": [get_true_value(build_value(subx, suby, level, tier, feature)) for subx, suby in substitutions]
        }

    def build_feature(featureptr):
        feature = sig_get_id(featureptr)
        substitutions = []
        for sub in feature['substitutions']: # e.g. BLEED.Duration, ARMOR.StacksOnProc, HEALTH.PercentMaxLife
            if '.' not in sub:
                continue
            subx, suby = sub.split('.')
            substitutions.append([subx.upper(), suby[0].lower() + suby[1:]])
        blah = { # todo: refine the addition of the title attribute for marquee abilities
            'description': feature['description'],
            'tiers': [build_tier(tierptr, feature, substitutions) for tierptr in feature['tiers']]
        }
        if 'title' in feature and feature['title'] != '':
            blah['title'] = feature['title']
        return blah

    if 'm_Component' in ability: # because some moves don't have abilities
        componentptrs = ability['m_Component']
        for componentptr in componentptrs:
            component = sig_get_id(componentptr['component'])
            if 'title' in component and 'features' in component:
                return {
                    'title': component['title'],
                    'features': [build_feature(featureptr) for featureptr in component['features']]
                }
    return {}

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
            'pa': build_prestige_ability(character['prestigeAbility'], id)
        }
    return characters

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

def get_sms():
    sms = {}
    for character in get_monos('BaseCharacterData'):
        for ptr in character['specialMoves']:
            sm = sa0_get_id(ptr)
            if sm['isInCompetitiveCollection']:
                continue
            id = create_id(sms, sm)
            icon = sa0_get_id(sm['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
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
                'ability': build_ability(sm['signatureAbility'])
            }
    return sms

def get_bbs():
    bbs = {}
    for character in get_monos('BaseCharacterData'):
        for ptr in character['blockbusters']:
            bb = sa0_get_id(ptr)
            if bb['isInCompetitiveCollection']:
                continue
            id = create_id(bbs, bb)
            icon = sa0_get_id(bb['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
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
                'ability': build_ability(bb['signatureAbility'])
            }
    return bbs

def get_gss():
    gss = {}
    for character in get_monos('AssistCharacterData'):
        for ptr in character['assistMoves']:
            gs = sa0_get_id(ptr)
            if gs['isInCompetitiveCollection']:
                continue
            id = create_id(gss, gs)
            icon = sa0_get_id(gs['palettizedIcon'])
            icon_name = icon['dynamicSprite']['resourcePath'].split('/')[-1]
            gss[id] = {
                'base': character['humanReadableGuid'],
                'icon': icon_name,
                'title': gs['title'],
                'name': gs['variantName'],
                'type': 1,
                'tier': gs['tier'],
                'element': gs['element'],
                # 'gear': gs['gearDamageTier'],
                # 'cost': gs['gearPointsCost'],
                'attack': gs['attackDamageMultipliers'],
                # 'damage': gs['damageIndicatorLevels'],
                'strength': gs['strengthLevel'],
                # 'bar': gs['superbarCost'], # idk what this is
                # 'rate': get_true_value(gs['usageProbabilityMultiplier']), # idk what this is
                'ability': build_ability(gs['signatureAbility'])
            }
    return gss

def get_catalysts():
    catalysts = {}
    for catalyst in get_monos('CollectibleNodeModifierData'):
        id = create_id(catalysts, catalyst)
        icon_name = catalyst['icon']['resourcePath'].split('/')[-1] # split just in case
        constraints = {}
        constraint = sa0_get_id(catalyst['abilityConstraint'])
        if constraint:
            if 'charactersNeeded' in constraint:
                constraints['characters'] = []
                for characterptr in constraint['charactersNeeded']:
                    character = sa0_get_id(characterptr)
                    constraints['characters'].append(character['humanReadableGuid'])
            if 'elementsNeeded' in constraint:
                constraints['elements'] = constraint['elementsNeeded']
        catalysts[id] = {
            'icon': icon_name,
            'title': catalyst['title'],
            'tier': catalyst['tier'],
            'constraints': constraints,
            'ability': build_ability(catalyst['signatureAbility'])
        }
    return catalysts

def get_artifacts():
    artifacts = {}
    for artifact in get_monos('MazeArtifactData'):
        id = create_id(artifacts, artifact)
        constraints = {}
        constraint = sa0_get_id(artifact['abilityConstraint'])
        if constraint:
            if 'charactersNeeded' in constraint:
                constraints['characters'] = []
                for characterptr in constraint['charactersNeeded']:
                    character = sa0_get_id(characterptr)
                    constraints['characters'].append(character['humanReadableGuid'])
            if 'elementsNeeded' in constraint:
                constraints['elements'] = constraint['elementsNeeded']
        artifacts[id] = {
            'title': artifact['title'],
            'tier': artifact['tier'],
            'constraints': constraints,
            'ability': build_ability(artifact['signatureAbility'])
        }
    return artifacts

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

### ANALYSIS ###

def tally_monotypes():
    monotypes = {}
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            monotypes.setdefault(monotype, 0)
            monotypes[monotype] += 1
    return monotypes

def analyze_prestige_ability(cid):
    standard_keys = [
        'm_GameObject',
        'm_Enabled',
        'm_Script',
        'm_Name',
        'title',
        'description',
        'chargePerAction',
        'baseBonus',
        'bonusPerLevels',
        'maxLevelBonus'
    ]
    for character in get_monos('BaseCharacterData'):
        if character['humanReadableGuid'] == cid:
            abilityptr = character['prestigeAbility']
            ability = sig_get_rp(abilityptr)
            for componentptr in ability['m_Component']:
                component = sig_get_id(componentptr['component'])
                if 'title' in component and 'description' in component:
                    description = corpus['en'][component['description']]
                    print(description)
                    print(re.findall('{(\d)}', description))
                    for key in component:
                        if key not in standard_keys:
                            try:
                                ck = sig_get_id(component[key])
                                print(key, {k: ck[k] for k in ck if k[:2] != 'm_' and ck[k]})
                            except:
                                print(key, component[key])
            break

def expand(obj): # pretty print an object, including all m_PathID pointers
    dfslog = []
    s = []
    def dfs(obj, lvl):
        indent = '  ' * lvl
        if isinstance(obj, dict):
            if 'm_PathID' in obj:
                pid = obj['m_PathID']
                s.append('{}(Path ID: {})'.format(indent, pid))
                if pid not in dfslog:
                    dfslog.append(pid)
                    s.append(indent + '{')
                    dfs(sig_get_id(obj), lvl + 1)
                    s.append(indent + '}')
            else:
                for k in obj:
                    s.append(indent + k + ':')
                    dfs(obj[k], lvl + 1)
        elif isinstance(obj, list):
            s.append(indent + '(List)')
            for i in obj:
                dfs(i, lvl + 1)
        else:
            s.append('{}{}'.format(indent, obj))
    dfs(obj, 0)
    return '\n'.join(s)

def analyze_ability(id):
    for variant in get_monos('VariantCharacterData'):
        if is_collectible(variant) and variant['humanReadableGuid'] == id:
            break
    print('VARIANT:\n', variant)
    abilityptr = variant['signatureAbility']
    ability = sig_get_rp(abilityptr)
    for componentptr in ability['m_Component']:
        component = sig_get_id(componentptr['component'])
        if 'title' in component and 'features' in component:
            print(component['title'])
            for featureptr in component['features']:
                feature = sig_get_id(featureptr)
                substitutions = []
                for substitution in feature['substitutions']:
                    x, y = substitution.split('.')
                    subx = x.upper()
                    suby = y[0].lower() + y[1:]
                    substitutions.append([subx, suby])
                    print(substitutions)

                    for tierptr in feature['tiers']:
                        tier = sig_get_id(tierptr)

                        for ptr in feature['triggerConditions']: # if it doesn't change, it's not in tiers
                            modifier = sig_get_id(ptr)
                            if modifier['id'] == subx:
                                print(modifier['id'], modifier[suby])
                        for ptr in feature['provokerConditions']: # if it doesn't change, it's not in tiers
                            modifier = sig_get_id(ptr)
                            if modifier['id'] == subx:
                                print(modifier['id'], modifier[suby])

                        for ptr in tier['triggerConditions']:
                            modifier = sig_get_id(ptr)
                            if modifier['id'] == subx:
                                print(modifier['id'], modifier[suby])
                        for ptr in tier['provokerConditions']:
                            modifier = sig_get_id(ptr)
                            if modifier['id'] == subx:
                                print(modifier['id'], modifier[suby])

                        for modifierset in tier['modifierSets']:
                            for modifierptr in modifierset['modifiers']:
                                modifier = sig_get_id(modifierptr)
                                if modifier['id'] == subx:
                                    print(modifier['id'], modifier[suby])
                                if 'delayedModifier' in modifier:
                                    delay = sig_get_id(modifier['delayedModifier'])
                                    if 'id' in delay and delay['id'] == subx:
                                        print(delay['id'], delay[suby])
                                if 'convertTo' in modifier:
                                    convertt = sig_get_id(modifier['convertTo'])
                                    if 'id' in convertt and convertt['id'] == subx:
                                        print(convertt['id'], convertt[suby])
                                if 'effects' in modifier:
                                    for xptr in modifier['effects']:
                                        x = sig_get_id(xptr['modifier'])
                                        if 'id' in x and x['id'] == subx:
                                            print(x['id'], x[suby])

                        for modifier in tier['additionalStringSubstitutions']:
                            if modifier['id'] == subx and suby in modifier:
                                print(modifier['id'], modifier[suby])
                    # if subx == 'DMG': # studying variant 'sSold'
                    #     with open('data_processing/output/analysis_sSold.txt', 'w') as fp:
                    #         fp.write(expand(tier))
                    #     assert False

    #             break

    # for key in feature:
    #     if key[:2] != 'm_':
    #         print(key, feature[key])

    # for key in tier:
    #     if key[:2] != 'm_':
    #         print(key, tier[key])

### UTILITY ###

def warn(*args, expected=[None]):
    print('(ignore)' if expected == True or expected[0] in expected[1:] else '[WARNING]', *args)

def sign(n):
    return 1 if n > 0 else -1 if n < 0 else 0

def check_sas():
    for key in variants:
        features = variants[key]['sa']['features']
        for i, feature in enumerate(features, 1):
            if i >= 3: # newer variants (>=6.0.0) tend to have extra empty SAs for some reason
                continue
            tiers = [tier['values'] for tier in feature['tiers']]
            constant = True
            for j in range(len(tiers[0])):
                if tiers[0][j] == None or tiers[1][j] == None or tiers[2][j] == None:
                    warn('\'None\' detected in SA:', key, expected=[(key, j), ('hCat', 2), ('wishfulEater', 2)])
                    if tiers[0][j] == None and tiers[1][j] == None and tiers[2][j] == None:
                        if j > 1:
                            print('\t(Probably ignorable, as this affects all tiers and occurs with SA{}.)'.format(j + 1))
                    continue
                avb = tiers[0][j] - tiers[1][j]
                bvc = tiers[1][j] - tiers[2][j]
                if sign(avb) != sign(bvc):
                    warn('Variant {}\'s SA{} is nonmonotonic at index {}: {}'.format(key, i, j, tiers), expected=[key, 'pShoot'])
                if sign(avb) != 0 or sign(bvc) != 0:
                    constant = False
            if constant:
                warn('Variant {}\'s SA{} is constant: {}'.format(key, i, tiers))

if __name__ == '__main__':
    characters = get_characters()
    variants = get_variants()
    sms = get_sms()
    bbs = get_bbs()
    gss = get_gss()
    catalysts = get_catalysts()
    artifacts = get_artifacts()

    check_sas()

    file.mkdir('data_processing/output')

    file.save(characters, 'data_processing/output/characters.json', True)
    file.save(variants, 'data_processing/output/variants.json', True)
    file.save(sms, 'data_processing/output/sms.json', True)
    file.save(bbs, 'data_processing/output/bbs.json', True)
    file.save(gss, 'data_processing/output/gss.json', True)
    file.save(catalysts, 'data_processing/output/catalysts.json', True)
    file.save(artifacts, 'data_processing/output/artifacts.json', True)

    corpus_keys = set()
    corpus_keys |= get_corpus_keys(characters)
    corpus_keys |= get_corpus_keys(variants)
    corpus_keys |= get_corpus_keys(sms)
    corpus_keys |= get_corpus_keys(bbs)
    corpus_keys |= get_corpus_keys(gss)
    corpus_keys |= get_corpus_keys(catalysts)
    corpus_keys |= get_corpus_keys(artifacts)

    for language in corpus:
        corpus_core = {key: corpus[language][key] for key in corpus_keys if key in corpus[language]}
        corpus_core[''] = 'UNDEFINED'
        file.save(corpus_core, 'data_processing/output/{}.json'.format(language), True)
