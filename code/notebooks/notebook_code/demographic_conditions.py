condition_0 = ('Overall',
               [{
        'column': 'Sex',
        'condition': 'NO_FILTER',
        'boolean_operator': None
    }] )

condition_1 = ('Men',
               [{
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': None
    }] )


condition_2 = ('Women',
               [{
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }] )

condition_3 = ('16-24',
               [{
        'column': 'age',
        'condition': lambda x: x < 25,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 15,
        'boolean_operator': 'and'
    }])

condition_4 = ('25-34',
               [{
        'column': 'age',
        'condition': lambda x: x < 35,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 24,
        'boolean_operator': 'and'
    }])

condition_5 = ('35-44',
               [{
        'column': 'age',
        'condition': lambda x: x < 45,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 34,
        'boolean_operator': 'and'
    }])

condition_6 = ('45-54',
               [{
        'column': 'age',
        'condition': lambda x: x < 55,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 44,
        'boolean_operator': 'and'
    }])

condition_7 = ('55-64',
               [{
        'column': 'age',
        'condition': lambda x: x < 65,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 54,
        'boolean_operator': 'and'
    }])


condition_8 = ('65-74',
               [{
        'column': 'age',
        'condition': lambda x: x < 75,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 64,
        'boolean_operator': 'and'
    }])

condition_9 = ('75+',
               [{
        'column': 'age',
        'condition': lambda x: x > 74,
        'boolean_operator': None
    }])

condition_10 = ('BMI < 25kg/m2',
               [{
        'column': 'BMI',
        'condition': lambda x: x < 25,
        'boolean_operator': None
    }])


condition_11 = ('BMI 25-29kg/m2',
               [{
        'column': 'BMI',
        'condition': lambda x: x < 30,
        'boolean_operator': None
    },
    {
        'column': 'BMI',
        'condition': lambda x: x >= 25,
        'boolean_operator': 'and'
    }])

condition_12 = ('BMI >= 30kg/m2',
               [{
        'column': 'BMI',
        'condition': lambda x: x >= 30,
        'boolean_operator': None
    }])

condition_13 = ('SIMD 1 (most deprived)',
               [{
        'column': 'SIMD1',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }])

condition_14 = ('SIMD 2',
               [{
        'column': 'SIMD2',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }])


condition_15 = ('SIMD 3',
               [{
        'column': 'SIMD3',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }])

condition_16 = ('SIMD 4',
               [{
        'column': 'SIMD4',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }])

condition_17 = ('SIMD 5 (least deprived)',
               [{
        'column': 'SIMD5',
        'condition': lambda x: x == 1,
        'boolean_operator': None
    }])


condition_18 = ('Women 16-24',
               [{
        'column': 'age',
        'condition': lambda x: x < 25,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 15,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_19 = ('Men 16-24',
               [{
        'column': 'age',
        'condition': lambda x: x < 25,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 15,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])


condition_20 = ('Women 25-34',
               [{
        'column': 'age',
        'condition': lambda x: x < 35,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 24,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_21 = ('Men 25-34',
               [{
        'column': 'age',
        'condition': lambda x: x < 35,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 24,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])

condition_22 = ('Women 35-44',
               [{
        'column': 'age',
        'condition': lambda x: x < 45,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 34,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])


condition_23 = ('Men 35-44',
               [{
        'column': 'age',
        'condition': lambda x: x < 45,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 34,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])

condition_24 = ('Women 45-54',
               [{
        'column': 'age',
        'condition': lambda x: x < 55,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 44,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_25 = ('Men 45-54',
               [{
        'column': 'age',
        'condition': lambda x: x < 55,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 44,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])

condition_26 = ('Women 55-64',
               [{
        'column': 'age',
        'condition': lambda x: x < 65,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 54,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_27 = ('Men 55-64',
               [{
        'column': 'age',
        'condition': lambda x: x < 65,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 54,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])

condition_28 = ('Women 65-74',
               [{
        'column': 'age',
        'condition': lambda x: x < 75,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 64,
        'boolean_operator': 'and'
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_29 = ('Men 65-74',
               [{
        'column': 'age',
        'condition': lambda x: x < 75,
        'boolean_operator': None
    },
    {
        'column': 'age',
        'condition': lambda x: x > 64,
        'boolean_operator': 'and'
    },
    {

        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])


condition_30 = ('Women 75+',
               [{
        'column': 'age',
        'condition': lambda x: x > 74,
        'boolean_operator': None
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 1,
        'boolean_operator': 'and'
    }
    ])

condition_31 = ('Men 75+',
               [{
        'column': 'age',
        'condition': lambda x: x > 74,
        'boolean_operator': None
    },
    {
        'column': 'Sex',
        'condition': lambda x: x == 0,
        'boolean_operator': 'and'
    }
    ])

condition_32 = ('RRPM >= 70g/day',
               [{
        'column': 'Total RRPM baseline',
        'condition': lambda x: x >= 70,
        'boolean_operator': None
    }
    ])

condition_33 = ('RRPM >= 60g/day',
               [{
        'column': 'Total RRPM baseline',
        'condition': lambda x: x >= 60,
        'boolean_operator': None
    }
    ])

condition_34 = ('RRPM >= 31g/day',
               [{
        'column': 'Total RRPM baseline',
        'condition': lambda x: x >= 31,
        'boolean_operator': None
    }
    ])

condition_35 = ('Dairy lower tertile',
               [{
        'column': 'Total dairy',
        'condition': lambda x: x <= 119.2,
        'boolean_operator': None
    }
    ])

condition_36 = ('Dairy middle tertile',
               [{
        'column': 'Total dairy',
        'condition': lambda x: x > 119.2,
        'boolean_operator': None
    },
                {
        'column': 'Total dairy',
        'condition': lambda x: x <= 270.2,
        'boolean_operator': 'and'
    }
    ])

condition_37 = ('Dairy upper tertile',
               [{
        'column': 'Total dairy',
        'condition': lambda x: x > 270.2,
        'boolean_operator': None
    }
    ])