from data_processing.main import *

def mine_corpus():
    with open('data_processing/output/corpus_en.json', 'w') as file:
        json.dump(corpus['en'], file, indent=4, separators=(',', ': '))

def mine_pf(name):
    for mono in sa0.values():
        if mono.type.name == 'MonoBehaviour':
            monotype = mono.read().m_Script.read().m_Name
            if monotype == 'EventSet':
                typetree = typetrees[monotype]
                monotree = mono.read_typetree(typetree)
                if 'Event_' + name in monotree['m_Name']:
                    for cdptr in monotree['contentDatas']:
                        cd = sa0_get_id(cdptr)
                        print(cd['humanReadableGuid'])
                        title = cd['actSelectContent']['title']
                        subtitle = cd['actSelectContent']['subtitle']
                        print('{} ({})'.format(corpus['en'][title], corpus['en'][subtitle]))
                        for side in ['player', 'enemy']:
                            for modptr in cd['enemyFightModifiers']:
                                print('{} Modifiers:'.format(side).upper())
                                mod = build_ability(modptr)
                                print('\t' + corpus['en'][mod['title']])
                                for feature in mod['features']:
                                    print('\t' + corpus['en'][feature['description']].format(*feature['tiers'][0]['values']))
                        print('minScore:', cd['minScore'])
                        for rewards in cd['scoreBasedRewards']:
                            for loot in rewards['loots']:
                                charptr = loot['character']
                                if charptr['m_PathID']:
                                    char = sa0_get_id(charptr)
                                    print('Grand Milestone Prize: {} ({})'.format(corpus['en'][char['displayVariantName']], char['humanReadableGuid']))
                        print()

if __name__ == '__main__':
    # mine_corpus()
    mine_pf('Squigly')
    mine_pf('BlackDahlia')
