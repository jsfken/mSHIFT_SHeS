
##### Specify observed values

mortality_conditions = [
    ('15-19', 97,
     [{
         'column': 'age',
         'condition': lambda x: x < 20,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 15,
             'boolean_operator': 'and'
         }]
     ),

    ('20-24', 194,
     [{
         'column': 'age',
         'condition': lambda x: x < 25,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 19,
             'boolean_operator': 'and'
         }]
     ),
    ('25-29', 266,
     [{
         'column': 'age',
         'condition': lambda x: x < 30,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 24,
             'boolean_operator': 'and'
         }]
     ),
    ('30-34', 373,
     [{
         'column': 'age',
         'condition': lambda x: x < 35,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 29,
             'boolean_operator': 'and'
         }]
     ),
    ('35-39', 559,
     [{
         'column': 'age',
         'condition': lambda x: x < 40,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 34,
             'boolean_operator': 'and'
         }]
     ),
    ('40-44', 826,
     [{
         'column': 'age',
         'condition': lambda x: x < 45,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 39,
             'boolean_operator': 'and'
         }]
     ),
    ('45-49', 1150,
     [{
         'column': 'age',
         'condition': lambda x: x < 50,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 45,
             'boolean_operator': 'and'
         }]
     ),
    ('50-54', 1642,
     [{
         'column': 'age',
         'condition': lambda x: x < 55,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 49,
             'boolean_operator': 'and'
         }]
     ),

    ('55-59', 2298,
     [{
         'column': 'age',
         'condition': lambda x: x < 60,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 54,
             'boolean_operator': 'and'
         }]
     ),
    ('60-64', 3241,
     [{
         'column': 'age',
         'condition': lambda x: x < 65,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 59,
             'boolean_operator': 'and'
         }]
     ),

    ('65-69', 4351,
     [{
         'column': 'age',
         'condition': lambda x: x < 70,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 64,
             'boolean_operator': 'and'
         }]
     ),
    ('70-74', 6236,
     [{
         'column': 'age',
         'condition': lambda x: x < 75,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 69,
             'boolean_operator': 'and'
         }]
     ),

    ('75-79', 7621,
     [{
         'column': 'age',
         'condition': lambda x: x < 80,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 74,
             'boolean_operator': 'and'
         }]
     ),
    ('80-84', 9551,
     [{
         'column': 'age',
         'condition': lambda x: x < 85,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 79,
             'boolean_operator': 'and'
         }]
     ),

    ('85-89', 9686,
     [{
         'column': 'age',
         'condition': lambda x: x < 90,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 84,
             'boolean_operator': 'and'
         }]
     ),

    ('90+', 9737,
     [{
         'column': 'age',
         'condition': lambda x: x < 200,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 89,
             'boolean_operator': 'and'
         }]
     ),

]

diabetes_conditions = [
    ('16-19', 20,
     [{
         'column': 'age',
         'condition': lambda x: x < 20,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 15,
             'boolean_operator': 'and'
         }]
     ),
    ('20-29', 293,
     [{
         'column': 'age',
         'condition': lambda x: x < 30,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 19,
             'boolean_operator': 'and'
         }]
     ),

    ('30-39', 1254,
     [{
         'column': 'age',
         'condition': lambda x: x < 40,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 29,
             'boolean_operator': 'and'
         }]
     ),

    ('40-49', 3010,
     [{
         'column': 'age',
         'condition': lambda x: x < 50,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 39,
             'boolean_operator': 'and'
         }]
     ),

    ('50-59', 5976,
     [{
         'column': 'age',
         'condition': lambda x: x < 60,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 49,
             'boolean_operator': 'and'
         }]
     ),

    ('60-69', 5884,
     [{
         'column': 'age',
         'condition': lambda x: x < 70,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x > 59,
             'boolean_operator': 'and'
         }]
     ),

    ('70+', 5773,
     [{
         'column': 'age',
         'condition': lambda x: x > 69,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 200,
             'boolean_operator': 'and'
         }]
     )
]

CVD_conditions = [

    ('M 0-44', 593,
     [{
         'column': 'age',
         'condition': lambda x: x < 45,
         'boolean_operator': None
     },
         {
             'column': 'Sex',
             'condition': lambda x: x == 0,
             'boolean_operator': 'and'
         }]
     ),

    ('M 45-64', 5582,
     [{
         'column': 'age',
         'condition': lambda x: x > 44,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 65,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 0,
             'boolean_operator': 'and'
         }]
     ),

    ('M 65-74', 4349,
     [{
         'column': 'age',
         'condition': lambda x: x > 64,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 75,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 0,
             'boolean_operator': 'and'
         }]
     ),

    ('M 75+', 5709,
     [{
         'column': 'age',
         'condition': lambda x: x > 74,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 200,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 0,
             'boolean_operator': 'and'
         }]
     ),

    ('F 0-44', 260,
     [{
         'column': 'age',
         'condition': lambda x: x < 45,
         'boolean_operator': None
     },
         {
             'column': 'Sex',
             'condition': lambda x: x == 1,
             'boolean_operator': 'and'
         }]
     ),

    ('F 45-64', 2519,
     [{
         'column': 'age',
         'condition': lambda x: x > 44,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 65,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 1,
             'boolean_operator': 'and'
         }]
     ),

    ('F 65-74', 2610,
     [{
         'column': 'age',
         'condition': lambda x: x > 64,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 75,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 1,
             'boolean_operator': 'and'
         }]
     ),

    ('F 75+', 6389,
     [{
         'column': 'age',
         'condition': lambda x: x > 74,
         'boolean_operator': None
     },
         {
             'column': 'age',
             'condition': lambda x: x < 200,
             'boolean_operator': 'and'
         },
         {
             'column': 'Sex',
             'condition': lambda x: x == 1,
             'boolean_operator': 'and'
         }]
     )
]
