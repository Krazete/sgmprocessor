import json
import UnityPy
from data_processing import file

loc = UnityPy.load('data_processing/input/localization')

corpus = {}
for key in loc.container:
    val = loc.container[key].read()
    language = val.name
    translations = json.loads(bytes(val.script))
    corpus[language] = translations

def find(q, n=16):
    'Find relevant keys within the specific character limit.'
    for i in corpus['en']:
        if q.lower() in corpus['en'][i].lower() and len(corpus['en'][i]) < n:
            print(i)
            for lang in corpus:
                print('{:>9s} {}'.format(lang, corpus[lang][i]))
# find('catalyst')

keys = [
    'Key_DisplayName',
    'Key_Fighter',
    'SkillTree_Gear',
    'Key_NodeModifier',
    'MainMenu_Collection', # unused
    'Version_Login',
    'Popup_Download_Confirm_Header',
    'Collection_Characters',
    'Collection_SMoves',
    'Gear_Filter_Assists',
    'Gear_Filter_Assists_Plural',
    'Collection_NodeModifiers',
    'Maze_Artifacts',
    'Ranked_Rating', # unused (pluralized in css)
    'Loading_Status_Loading',
    'Popup_Error_Header',

    'Stat_AttackFlat_Label',
    'Stat_HealthFlat_Label',
    'Sort_FS',
    'SkillTree_CharacterAbility_Title',
    'CharacterDetails_SA',
    'SkillTree_SuperAbility_Title',
    'Key_PrestigeAbility',
    'LabBattle_Map_Offense_Main',
    'LabBattle_Map_Defense_Main',

    'Status_Unblockable',
    'SM_Damage',
    'GearDetails_AssistBonusDamage',
    'None',
    'Dmg_00_VeryLow',
    'Dmg_01_Low',
    'Dmg_02_Medium',
    'Dmg_03_High',
    'Dmg_04_VeryHigh',
    'Dmg_05_Ultra',
    'SM_Cooldown',
    'Stat_Seconds_Full',
    'Stat_Seconds_Short', # unused
    'SM_Upgrade',
    'Sell',

    'Key_Options',
    'Stat_Lvl', # unused
    'Character_Evolve_Button',
    'Character_Sorting_Level',
    'None',
    'Gear_Filter_All',

    'TeamSelect_Filter',
    'TeamSelect_Sort',
    'Key_Alphabetical',
    'SkillTree_AtkNode_Title',
    'SkillTree_HealthNode_Title',
    'Key_Element',
    'Sort_Tier',
    'Sort_Type'
]

common = {key: {language: corpus[language][key] for language in corpus} for key in keys}

file.mkdir('data_processing/output')
file.save(common, 'data_processing/output/common.json', True)

file.save(corpus['en'], 'data_processing/output/corpus_en.json', True) # export the entire corpus too, in case searching is needed

# regex-search for:
#     "(.+?)": "(.+?)",?
# and replace with:
#     html[lang='$1'] :before {content: '$2';}
