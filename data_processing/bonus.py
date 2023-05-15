from data_processing.main import *
corpus['en'][''] = ''

def mine_corpus():
    with open('data_processing/output/corpus_en.json', 'w') as file:
        json.dump(corpus['en'], file, indent=4, separators=(',', ': '))

# lootKeys = [
#     'lootType',
#     'amount',
#     'gear',
#     'character',
#     'reel',
#     'consumable',
#     'baseCharacter',
#     'rarityTier',
#     'elementType',
#     'nodeModifier',
#     'voucherDenomination',
#     'nestedLootTable'
# ]

def mine_relic(reel):
    print('{} ({})'.format(corpus['en'][reel['title']], reel['m_Name']))
    total = 0
    for lootTableSet in reel['lootTableSets']:
        total += lootTableSet['weight']
    for lootTableSet in reel['lootTableSets']:
        print('\t{}% Chance'.format(lootTableSet['weight'] * 100 / total))
        setptr = lootTableSet['lootTableSet']
        set = sa0_get_id(setptr)
        for tableptr in set['lootTables']:
            table = sa0_get_id(tableptr)
            subtotal = 0
            for loot in table['loots']:
                subtotal += loot['weight']
            for loot in table['loots']:
                print('\t\t{:.3f}%'.format(loot['weight'] * 100 / subtotal), end="")
                mine_loot(loot['loot'])

def mine_relic_id(relic_id):
    relic = sa0_get_id({'m_PathID': relic_id})
    mine_relic(relic)

lootTypes = {
    0: 'Canopy Coin',
    1: 'Theonite',
    2: 'Move',
    3: 'Fighter',
    4: 'Relic',
    5: 'Randomized', # usually a move in pf rewards, varies in gifts
    6: 'Relic Shard',
    7: 'Skill Point',
    9: 'Key',
    10: 'Elemental Shard',
    11: 'Elemental Essence',
    12: 'Rift Coin',
    16: 'Double XP Boost (4h)',
    20: 'Double XP Boost (12h)',
    23: 'Retake',
    24: 'Golden Retake'
}

def mine_loot(loot):
    amount = loot['amount']
    lootType = loot['lootType']
    plural = 's' if lootType != 1 and amount > 1 else ''
    lootName = lootTypes.get(lootType, 'Unknown [{}]'.format(lootType))

    extra = ''
    match lootType:
        case 2:
            gearptr = loot['gear']
            gear = sa0_get_id(gearptr)
            extra = '{}, {}'.format(['Bronze', 'Silver', 'Gold', 'Diamond'][gear['tier']], corpus['en'][gear['title']])
        case 3:
            charptr = loot['character']
            char = sa0_get_id(charptr)
            extra = corpus['en'][char['displayVariantName']]
        case 4:
            reelptr = loot['reel']
            reel = sa0_get_id(reelptr)
            extra = '{}, ID: {}'.format(corpus['en'][reel['title']], reelptr['m_PathID'])
        case 5:
            tableptr = loot['nestedLootTable']
            table = sa0_get_id(tableptr)
            try:
                extra = '{3} {4}, {2}'.format(*table['m_Name'].split('_'))
            except:
                extra = table['m_Name']
        case 6:
            extra = ['Bronze', 'Silver', 'Gold', 'Diamond'][loot['rarityTier']]
        case 7:
            baseptr = loot['baseCharacter']
            base = sa0_get_id(baseptr)
            extra = corpus['en'][base['displayName']]
        case 9:
            extra = ['Bronze', 'Silver', 'Gold', 'Diamond'][loot['rarityTier']]
        case 10:
            extra = ['Neutral', 'Fire', 'Water', 'Air', 'Dark', 'Light'][loot['elementType']] # neutral doesn't exist
        case 11:
            extra = ['Neutral', 'Fire', 'Water', 'Air', 'Dark', 'Light'][loot['elementType']] # neutral is just a placeholder
        case 23:
            baseptr = loot['baseCharacter']
            base = sa0_get_id(baseptr)
            extra = corpus['en'][base['displayName']]
        case _:
            if lootType not in lootTypes:
                from pprint import pprint
                pprint(loot)
    extra_suffix = ' ({})'.format(extra) if extra else extra

    print('\t{:7d} {}'.format(amount, lootName + plural) + extra_suffix)

def mine_pf(pf):
    print(pf['humanReadableGuid'])
    if 'actSelectContent' in pf:
        title = pf['actSelectContent']['title']
        subtitle = pf['actSelectContent']['subtitle']
        print('{} ({})'.format(corpus['en'][title], corpus['en'][subtitle]))
    for side in ['player', 'enemy']:
        if side + 'FightModifiers' in pf:
            print('{} Modifiers:'.format(side).upper())
            for modptr in pf[side + 'FightModifiers']:
                mod = build_ability(modptr)
                print('\t' + corpus['en'][mod['title']])
                for feature in mod['features']:
                    values = (0 if x is None else x for x in feature['tiers'][0]['values'])
                    print('\t' + corpus['en'][feature['description']].format(*values))
    print('minScore:', pf.get('minScore', 0))
    for league in ['scoreBased', 'percentile', 'rank']:
        print('{} Rewards:'.format(league).upper())
        for i, rewards in enumerate(pf.get(league + 'Rewards', [])):
            # if len(rewards['loots']):
            print('\tTier {}:'.format(i))
            for loot in rewards['loots']:
                mine_loot(loot)
    print()

def mine_pfset(pfset):
    for pfptr in pfset['contentDatas']:
        pf = sa0_get_id(pfptr)
        mine_pf(pf)

def event_search(name):
    'Get info about the queried prize fights or daily events.'
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            if 'Event' in monotype:
                typetree = typetrees[monotype]
                monotree = mono.read_typetree(typetree)
                if name in monotree['m_Name']:
                    if 'contentDatas' in monotree: # skip redundant EventSets
                        continue
                        mine_pfset(monotree)
                    else:
                        mine_pf(monotree)

def relic_search(name):
    'Get info about the queried relics.'
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            if 'GachaData' == monotype:
                typetree = typetrees[monotype]
                monotree = mono.read_typetree(typetree)
                if name in monotree['m_Name']:
                    mine_relic(monotree)

def mine_gifts():
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            if 'LootTableSet' == monotype:
                typetree = typetrees[monotype]
                monotree = mono.read_typetree(typetree)
                if 'SocialGifts' in monotree['m_Name']:
                    print(monotree['m_Name'])
                    for tableptr in monotree['lootTables']:
                        table = sa0_get_id(tableptr)
                        print('\t', table['m_Name'])
                        subtotal = 0
                        for loot in table['loots']:
                            subtotal += loot['weight']
                        # print('\t\t', subtotal)
                        for loot in table['loots']:
                            # print('\t\t', loot['weight'])
                            print('\t\t{:.3f}%'.format(loot['weight'] * 100 / subtotal), end="")
                            mine_loot(loot['loot'])
                            nested = sa0_get_id(loot['loot']['nestedLootTable'])
                            nestedtotal = 0
                            for nestedloot in nested['loots']:
                                nestedtotal += nestedloot['weight']
                            # print('\t\t\t', nestedtotal)
                            for nestedloot in nested['loots']:
                                # print('\t\t\t', nestedloot['weight'])
                                print('\t\t\t{:.3f}%'.format(nestedloot['weight'] * 100 / nestedtotal), end="")
                                mine_loot(nestedloot['loot'])

if __name__ == '__main__':
    # mine_corpus()

    event_search('Squigly')
    event_search('BlackDahlia')
    event_search('Painwheel')
    event_search('Valentines')
    event_search('Water')

    mine_relic_id(14419) 

    relic_search('SpecialForces') # a spotlight relic
    # relic_search('') # all relics

    # relic function comparison
    event_search('Costume') # halloween prize fight
    relic_search('Spooky') # halloween relic
    mine_relic_id(14417) # halloween relic too
