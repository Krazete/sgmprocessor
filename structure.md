# Fighters

Example:

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
                    {"unlock": 1, "value": [5]},
                    {"unlock": 2, "value": [6]},
                    {"unlock": 3, "value": [7]},
                    {"unlock": 4, "value": [8]},
                    {"unlock": 5, "value": [9]},
                    {"unlock": 6, "value": [10]},
                    {"unlock": 7, "value": [11]},
                    {"unlock": 8, "value": [12]},
                    {"unlock": 9, "value": [13]},
                    {"unlock": 10, "value": [14]},
                    {"unlock": 11, "value": [15]}
                ]
            },
            {
                "title": "Char_Squigly_SUP_FrightNight_Feat2_Title",
                "description": "Char_Squigly_SUP_FrightNight_Feat2_Desc",
                "tiers": [
                    {"unlock": 1, "value": [5]},
                    {"unlock": 2, "value": [6]},
                    {"unlock": 3, "value": [7]},
                    {"unlock": 4, "value": [8]},
                    {"unlock": 5, "value": [9]},
                    {"unlock": 6, "value": [10]},
                    {"unlock": 7, "value": [11]},
                    {"unlock": 8, "value": [12]},
                    {"unlock": 9, "value": [13]},
                    {"unlock": 10, "value": [14]},
                    {"unlock": 11, "value": [15]}
                ]
            }
        ]
    }
}

# Variants

Example:

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
                    {"unlock": 1, "value": [5]},
                    {"unlock": 2, "value": [6]},
                    {"unlock": 3, "value": [8]}
                ],
            },
            {
                "description": "Char_Squigly_SA_Abracadaver_Desc2",
                "tiers": [
                    {"unlock": 1, "value": [50, 15]},
                    {"unlock": 2, "value": [50, 20]},
                    {"unlock": 3, "value": [50, 25]}
                ],
            }
        ]
    }
}

# Moves

## Special Moves

Example:

"sq-sm-oTake-g": {
    "base": "sq",
    "title": "Char_Squigly_SM1_Name",
    "type": 0,
    "tier": 2,
    "cost": 2,
    <!-- "gear": 0, -->
    "damage": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    <!-- "attack": [0], -->
    "cooldown": [20, 20, 18, 18, 18, 16, 16, 16, 14, 14, 14, 12, 12, 12, 10],
    "ability": {
        <!-- "title": "SA_General_Outtake_Title", -->
        "features": [
            {
                "description": "SA_General_Outtake_Desc",
                "tiers": [
                    {"unlock": 0, "value": []}
                ]
            }
        ]
    }
}

## Blockbusters

Example:

"sq-bb-rod-g": {
    "base": "sq",
    "title": "Squigly_BB5_T3_RageOfTheDragon_Title",
    "type": 1,
    "tier": 2,
    "cost": 7,
    <!-- "gear": 6, -->
    "damage": [3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 6],
    "attack": [1.2, 1.2, 1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.5],
    "ability": {
        <!-- "title": "Squigly_BB5_T3_RageOfTheDragon_Title", -->
        "features": [
            {
                "description": "SA_Squigly_BB5_Rage",
                "tiers": [
                    {"unlock": 3, "value": [5]},
                    {"unlock": 9, "value": [7]},
                    {"unlock": 15, "value": [10]}
                ]
            },
            {
                "description": "SA_Squigly_BB5_Rage2",
                "tiers": [
                    {"unlock": 3, "value": [50, 10]}
                ]
            }
        ]
    }
}

# Catalysts

Example:

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
