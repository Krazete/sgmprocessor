import json
import re
from mwclient import Site

def signin(): # use https://skullgirlsmobile.fandom.com/wiki/Special:BotPasswords
    global sgmw
    if 'sgmw' not in globals():
        sgmw = Site('skullgirlsmobile.fandom.com', path='/')
    if not sgmw.logged_in:
        with open('wikibotlogin.txt', 'r') as fp:
            sgmw.login(
                fp.readline().strip(),
                fp.readline().strip()
            )
    return sgmw

def updateFighterData():
    with open('data_processing/output/version.txt', 'r') as fp:
        version = fp.read()
    
    page = sgmw.pages['Module:FighterData']
    matches = re.findall(r'Version (\d+\.\d+\.\d+)', page.text())
    if matches:
        fdversion = matches[0]

    if fdversion != version:
        content = writeFighterData(version)
        response = page.edit(content, '{} (bot update)'.format(version))
        result = response.get('result', 'Unknown')
        print('Result:', result)

def writeFighterData(version):
    tiers = ['Bronze', 'Silver', 'Gold', 'Diamond']
    elements = ['Neutral', 'Fire', 'Water', 'Wind', 'Dark', 'Light']

    with open('../sgm/data/characters.json', 'r', encoding='utf-8') as fp:
        characters = json.load(fp)
    with open('../sgm/data/variants.json', 'r', encoding='utf-8') as fp:
        variants = json.load(fp)
    with open('../sgm/data/en.json', 'r', encoding='utf-8') as fp:
        corpus = json.load(fp)
    
    lines = [
        '-- Version {}'.format(version),
        'local p = {}',
        '',
        '-- [Variant Name] = {Base Character, Base Tier, Element}',
        'p.fighters = {'
    ]

    cvis = [[
        corpus[characters[variants[vid]['base']]['name']],
        corpus[variants[vid]['name']],
        vid
    ] for vid in variants]
    cvis.sort()

    comment = ''
    for cvi in cvis:
        if comment != cvi[0]:
            comment = cvi[0]
            lines.append('\t-- {}'.format(cvi[0]))
        lines.append('\t[\'{}\'] = {{\'{}\', \'{}\', \'{}\'}},'.format(
                re.sub(r'\'', '\\\'', cvi[1]),
                re.sub(r'\'', '\\\'', cvi[0]),
                tiers[variants[cvi[2]]['tier']],
                elements[variants[cvi[2]]['element']]
        ))
    
    lines += [
        '}',
        '',
        'return p'
    ]

    return '\n'.join(lines)

if __name__ == '__main__':
    signin()
    updateFighterData()
