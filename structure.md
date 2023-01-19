# Structure

This document is a reference to show what the output data looks like.

## Characters

```json
{
    "sq": {
        "name": "Char_Squigly_Name",
        "ca": {
            "title": "Char_Squigly_CA_Title",
            "description": "Char_Squigly_CA_Desc"
        },
        "ma": {
            "title": "Char_Squigly_SUP_FrightNight_Title",
            "features": [
                {
                    "title": "Char_Squigly_SUP_FrightNight_Feat1_Title",
                    "description": "Char_Squigly_SUP_FrightNight_Feat1_Desc",
                    "tiers": [
                        {"level": 1, "values": [5]},
                        {"level": 2, "values": [6]},
                        {"level": 3, "values": [7]},
                        {"level": 4, "values": [8]},
                        {"level": 5, "values": [9]},
                        {"level": 6, "values": [10]},
                        {"level": 7, "values": [11]},
                        {"level": 8, "values": [12]},
                        {"level": 9, "values": [13]},
                        {"level": 10, "values": [14]},
                        {"level": 11, "values": [15]}
                    ]
                },
                {
                    "title": "Char_Squigly_SUP_FrightNight_Feat2_Title",
                    "description": "Char_Squigly_SUP_FrightNight_Feat2_Desc",
                    "tiers": [
                        {"level": 1, "values": [5]},
                        {"level": 2, "values": [6]},
                        {"level": 3, "values": [7]},
                        {"level": 4, "values": [8]},
                        {"level": 5, "values": [9]},
                        {"level": 6, "values": [10]},
                        {"level": 7, "values": [11]},
                        {"level": 8, "values": [12]},
                        {"level": 9, "values": [13]},
                        {"level": 10, "values": [14]},
                        {"level": 11, "values": [15]}
                    ]
                }
            ]
        },
        "pa": {
            "title": "Char_Squigly_PA_Title",
            "description": "Char_Squigly_PA_Desc",
            "base": 7,
            "chargeRate": 12,
            "lvlBonus": -045,
            "maxBonus": -0.595703125
        }
    }
}
```

## Variants

```json
{
    "nDepart": {
        "base": "sq",
        "name": "Char_Squigly_S_V1_Name",
        "quote": "Variant_Description_Squigly_NearlyDeparted",
        "tier": 1,
        "element": 5,
        "stats": [
            {"attack": 122, "lifebar": 945},
            {"attack": 220, "lifebar": 1701},
            {"attack": 396, "lifebar": 3062}
        ],
        "sa": {
            "title": "Char_Squigly_SA_Abracadaver_Title",
            "features": [
                {
                    "description": "Char_Squigly_SA_Abracadaver_Desc",
                    "tiers": [
                        {"level": 1, "values": [5]},
                        {"level": 2, "values": [6]},
                        {"level": 3, "values": [8]}
                    ]
                },
                {
                    "description": "Char_Squigly_SA_Abracadaver_Desc2",
                    "tiers": [
                        {"level": 1, "values": [50, 15]},
                        {"level": 2, "values": [50, 20]},
                        {"level": 3, "values": [50, 25]}
                    ]
                }
            ]
        },
        "fandom": "Nearly Departed"
    }
}
```
## Moves

### Special Moves

```json
{
    "sq-sm-burst-g": {
        "base": "sq",
        "title": "SA_General_Burst_Title",
        "icon": "squigly_sm2_burst.png",
        "type": 0,
        "tier": 2,
        "cost": 1,
        "gear": 0, /* unused? */
        "damage": [],
        "attack": [0], /* unused? */
        "cooldown": [18, 18, 16, 16, 16, 14, 14, 14, 12, 12, 12, 10, 10, 10, 8],
        "ability": {
            "title": "SA_General_Burst_Title", /* unused? */
            "features": [
                {
                    "description": "SA_SMGeneric_Curse",
                    "tiers": [
                        {"level": 1, "values": [5]},
                        {"level": 6, "values": [7]},
                        {"level": 15, "values": [10]}
                    ]
                }
            ]
        }
    }
}
```

### Blockbusters

```json
{
    "sq-bb-rod-g": {
        "base": "sq",
        "title": "Squigly_BB5_T3_RageOfTheDragon_Title",
        "icon": "squigly_bb5_rageofthedragon.png",
        "type": 1,
        "tier": 2,
        "cost": 7,
        "gear": 6, /* unused? */
        "damage": [3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 6],
        "attack": [1.2, 1.2, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.5],
        "strength": 3, /* unused? */
        "ability": {
            "title": "Squigly_BB5_T3_RageOfTheDragon_Title", /* unused? */
            "features": [
                {
                    "description": "SA_Squigly_BB5_Rage",
                    "tiers": [
                        {"level": 3, "values": [5]},
                        {"level": 9, "values": [7]},
                        {"level": 15, "values": [10]}
                    ]
                },
                {
                    "description": "SA_Squigly_BB5_Rage2",
                    "tiers": [
                        {"level": 3, "values": [50, 10]}
                    ]
                }
            ]
        }
    }
}
```

## Catalysts

*Catalysts are currently unimplemented. This structure is based on old data.*

```json
{
    "cat-rtSend-char-g": {
        "base": "sq",
        "title": "Catalyst_ReturnToSender",
        "tier": 2,
        "icon": "SkullModifierIcon",
        "randomCharacter": 0,
        "randomElement": 0,
        "ability": {
            "features": [
                "description": "",
                "tiers": [
                    {"unlock": 1, "value": []},
                    {"unlock": 2, "value": []},
                    {"unlock": 3, "value": []},
                    {"unlock": 4, "value": []},
                    {"unlock": 5, "value": []},
                    {"unlock": 6, "value": []},
                    {"unlock": 7, "value": []},
                    {"unlock": 8, "value": []},
                    {"unlock": 9, "value": []},
                    {"unlock": 10, "value": []},
                    {"unlock": 11, "value": []}
                ]
            ]
        }
    }
}
```
