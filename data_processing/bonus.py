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
    total = 0
    for lootTableSet in reel['lootTableSets']:
        total += lootTableSet['weight']
    for lootTableSet in reel['lootTableSets']:
        print('{}% Chance'.format(lootTableSet['weight'] * 100 / total))
        setptr = lootTableSet['lootTableSet']
        set = sa0_get_id(setptr)
        for tableptr in set['lootTables']:
            table = sa0_get_id(tableptr)
            for loot in table['loots']:
                charptr = loot['loot']['character']
                char = sa0_get_id(charptr)
                print('\t' + corpus['en'][char['displayVariantName']])

def mine_relic_id(relic_id):
    relic = sa0_get_id({'m_PathID': relic_id})
    mine_relic(relic)

lootTypes = {
    0: 'Canopy Coin',
    1: 'Theonite',
    3: 'Fighter',
    4: 'Relic',
    5: 'Move',
    6: 'Relic Shard',
    7: 'Skill Point',
    9: 'Key',
    10: 'Elemental Shard'
}

def mine_loot(loot):
    amount = loot['amount']
    lootType = loot['lootType']
    plural = 's' if lootType != 1 and amount > 1 else ''
    lootName = lootTypes.get(lootType, 'Unknown [{}]'.format(lootType))

    extra = ''
    match lootType:
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
            extra = '{3} {4}, {2}'.format(*table['m_Name'].split('_'))
        case 6:
            extra = ['Bronze', 'Silver', 'Gold', 'Diamond'][loot['rarityTier']]
        case 7:
            baseptr = loot['baseCharacter']
            base = sa0_get_id(baseptr)
            extra = corpus['en'][base['displayName']]
        case 9:
            extra = ['Bronze', 'Silver', 'Gold', 'Diamond'][loot['rarityTier']]
        case 10:
            extra = ['Neutral', 'Fire', 'Water', 'Air', 'Dark', 'Light'][loot['elementType']] # Neutral index is a guess
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

def mine_query(name):
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

if __name__ == '__main__':
    # mine_corpus()

    mine_query('Squigly')
    mine_query('BlackDahlia')
    mine_query('Painwheel')
    mine_query('Valentines')
    mine_query('Water')

    mine_relic_id(14419)
