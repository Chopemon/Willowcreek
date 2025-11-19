// =================================================================
// WILLOW CREEK 2025 - AUTO-GENERATED FROM PYTHON SIMULATION
// =================================================================
// Generated: 2025-09-05T12:00:00
// Simulation Day: 5
// NPCs: 41
// Relationships: 2
// =================================================================

console.log("=== [PYTHON-EXPORT] Loading simulation state ===");

const shared = context.character.shared_context;

// =================================================================
// NPCS
// =================================================================

shared.npcs = [
  {
    "fullName": "Alex Sturm",
    "firstName": "Alex",
    "lastName": "Alex",
    "age": 13,
    "gender": "male",
    "homeAddress": "Oak St",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 0.397836,
      "conscientiousness": 0.351453,
      "extroversion": 4.173862,
      "agreeableness": 5.683819,
      "neuroticism": 5.133844
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.928409327989285,
      "entertainment": 7.666611631319261
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Anna Thompson",
    "firstName": "Anna",
    "lastName": "Anna",
    "age": 7,
    "gender": "female",
    "homeAddress": "204 Maple Ave",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.290813,
      "conscientiousness": 10.0,
      "extroversion": 5.832778,
      "agreeableness": 7.493819,
      "neuroticism": 5.481561
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.155981364267385,
      "entertainment": 7.30679398095425
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Caty Kunitz",
    "firstName": "Caty",
    "lastName": "Caty",
    "age": 38,
    "gender": "female",
    "homeAddress": "309 Pine Way",
    "currentLocation": "home",
    "occupation": "Housewife",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 3.763969,
      "conscientiousness": 6.964199,
      "extroversion": 0.0,
      "agreeableness": 6.196679,
      "neuroticism": 3.727165
    },
    "needs": {
      "hunger": 9.838514146766114,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.102203482773506,
      "entertainment": 7.792772234228384
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Christine Brunn",
    "firstName": "Christine",
    "lastName": "Christine",
    "age": 35,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Psychiatrist (Magnolia Clinic)",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.597579,
      "conscientiousness": 6.113596,
      "extroversion": 3.324912,
      "agreeableness": 6.124439,
      "neuroticism": 5.684116
    },
    "needs": {
      "hunger": 9.499986706926142,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.878733680013738,
      "entertainment": 7.476067568990164
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Damien Voss",
    "firstName": "Damien",
    "lastName": "Damien",
    "age": 32,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Massage Therapist (Harmony Studio)",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.140214,
      "conscientiousness": 2.957089,
      "extroversion": 6.194405,
      "agreeableness": 4.10337,
      "neuroticism": 2.340838
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.958078531590171,
      "sleep": 10.0,
      "hygiene": 5.0243159750623025,
      "entertainment": 7.47575434504957
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Daniel Carter",
    "firstName": "Daniel",
    "lastName": "Daniel",
    "age": 40,
    "gender": "male",
    "homeAddress": "202 Maple Ave",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 7.027457,
      "conscientiousness": 5.866066,
      "extroversion": 0.27894,
      "agreeableness": 8.05611,
      "neuroticism": 4.404586
    },
    "needs": {
      "hunger": 9.472859354213302,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.053613115940956,
      "entertainment": 7.521978235099537
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "David Madison",
    "firstName": "David",
    "lastName": "David",
    "age": 31,
    "gender": "male",
    "homeAddress": "307 Pine Way",
    "currentLocation": "home",
    "occupation": "Librarian",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 6.916288,
      "conscientiousness": 3.155592,
      "extroversion": 3.036156,
      "agreeableness": 6.667326,
      "neuroticism": 5.266349
    },
    "needs": {
      "hunger": 9.6955407720176,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.029233672591297,
      "entertainment": 7.5474036379394525
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Elena Sturm",
    "firstName": "Elena",
    "lastName": "Elena",
    "age": 8,
    "gender": "male",
    "homeAddress": "103 Oak St",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.54378,
      "conscientiousness": 4.541425,
      "extroversion": 6.968251,
      "agreeableness": 9.92635,
      "neuroticism": 4.367425
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.916277846666263,
      "sleep": 10.0,
      "hygiene": 4.9808484780420015,
      "entertainment": 7.460917862024702
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Emma Pearson",
    "firstName": "Emma",
    "lastName": "Emma",
    "age": 18,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.829327,
      "conscientiousness": 4.859485,
      "extroversion": 2.521026,
      "agreeableness": 3.238859,
      "neuroticism": 4.441226
    },
    "needs": {
      "hunger": 9.603083145656784,
      "social": 9.98986618594312,
      "sleep": 10.0,
      "hygiene": 5.048919556731071,
      "entertainment": 7.463425564688209
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Eva Seinfeld",
    "firstName": "Eva",
    "lastName": "Eva",
    "age": 10,
    "gender": "male",
    "homeAddress": "406 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 6.87339,
      "conscientiousness": 4.542482,
      "extroversion": 5.822272,
      "agreeableness": 6.793291,
      "neuroticism": 4.827252
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.019861555696146,
      "entertainment": 7.374169692970728
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Eve Madison",
    "firstName": "Eve",
    "lastName": "Eve",
    "age": 7,
    "gender": "male",
    "homeAddress": "307 Pine Way",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.847411,
      "conscientiousness": 5.11641,
      "extroversion": 6.102655,
      "agreeableness": 4.490733,
      "neuroticism": 5.810004
    },
    "needs": {
      "hunger": 9.8451739524711,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.889421421299877,
      "entertainment": 7.43063945977362
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Hanna",
    "firstName": "Hanna",
    "lastName": "Hanna",
    "age": 17,
    "gender": "male",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.735617,
      "conscientiousness": 4.246878,
      "extroversion": 3.136352,
      "agreeableness": 3.49425,
      "neuroticism": 5.580698
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.821140427183565,
      "sleep": 10.0,
      "hygiene": 4.986389893263121,
      "entertainment": 7.583381126791441
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Hiro Lockheart",
    "firstName": "Hiro",
    "lastName": "Hiro",
    "age": 13,
    "gender": "male",
    "homeAddress": "305 Pine Way",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.690948,
      "conscientiousness": 4.343396,
      "extroversion": 6.543053,
      "agreeableness": 3.263712,
      "neuroticism": 1.619594
    },
    "needs": {
      "hunger": 9.961591311879308,
      "social": 9.988402561951773,
      "sleep": 10.0,
      "hygiene": 5.173456283547577,
      "entertainment": 7.757255450715628
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Isabella Ruiz",
    "firstName": "Isabella",
    "lastName": "Isabella",
    "age": 31,
    "gender": "female",
    "homeAddress": "303 Pine Way",
    "currentLocation": "home",
    "occupation": "Yoga Instructor/Lingerie Model",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.48636,
      "conscientiousness": 8.237734,
      "extroversion": 5.604053,
      "agreeableness": 1.297712,
      "neuroticism": 3.616137
    },
    "needs": {
      "hunger": 9.870614039022966,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.975520641815936,
      "entertainment": 7.377281505872531
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Ivy",
    "firstName": "Ivy",
    "lastName": "Ivy",
    "age": 7,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.710395,
      "conscientiousness": 6.112153,
      "extroversion": 6.19869,
      "agreeableness": 6.839387,
      "neuroticism": 4.715073
    },
    "needs": {
      "hunger": 9.984406182773757,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.048984010145557,
      "entertainment": 7.5089838267474525
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "James Seinfeld",
    "firstName": "James",
    "lastName": "James",
    "age": 48,
    "gender": "male",
    "homeAddress": "406 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Police Chief (WCPD)",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 3.980721,
      "conscientiousness": 4.736326,
      "extroversion": 1.137891,
      "agreeableness": 6.397135,
      "neuroticism": 7.636457
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.183926451726096,
      "entertainment": 7.4137964260852165
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "John Sturm",
    "firstName": "John",
    "lastName": "John",
    "age": 37,
    "gender": "male",
    "homeAddress": "103 Oak St",
    "currentLocation": "home",
    "occupation": "Oil worker",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.497621,
      "conscientiousness": 0.295917,
      "extroversion": 7.46777,
      "agreeableness": 5.820695,
      "neuroticism": 7.288845
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.988746455968611,
      "sleep": 10.0,
      "hygiene": 5.146994507831384,
      "entertainment": 7.619854457406522
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Ken Blake",
    "firstName": "Ken",
    "lastName": "Ken",
    "age": 38,
    "gender": "male",
    "homeAddress": "301 Pine Way",
    "currentLocation": "home",
    "occupation": "Navy SEAL",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 7.113134,
      "conscientiousness": 3.127525,
      "extroversion": 7.271963,
      "agreeableness": 3.979794,
      "neuroticism": 7.25556
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.78472424007945,
      "sleep": 10.0,
      "hygiene": 4.8409403526075,
      "entertainment": 7.579153820058719
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Kenny Lockheart",
    "firstName": "Kenny",
    "lastName": "Kenny",
    "age": 45,
    "gender": "male",
    "homeAddress": "305 Pine Way",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.933291,
      "conscientiousness": 7.309082,
      "extroversion": 3.579258,
      "agreeableness": 5.294132,
      "neuroticism": 0.564198
    },
    "needs": {
      "hunger": 9.549965207297578,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.043061464505515,
      "entertainment": 7.5448893144142675
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Lianna Carter",
    "firstName": "Lianna",
    "lastName": "Lianna",
    "age": 16,
    "gender": "male",
    "homeAddress": "202 Maple Ave",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.570951,
      "conscientiousness": 6.097186,
      "extroversion": 3.559278,
      "agreeableness": 4.565672,
      "neuroticism": 4.044448
    },
    "needs": {
      "hunger": 9.610289451088779,
      "social": 9.971888382062296,
      "sleep": 10.0,
      "hygiene": 4.993155084785043,
      "entertainment": 7.36598556061657
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Lily Harper",
    "firstName": "Lily",
    "lastName": "Lily",
    "age": 40,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Art Teacher",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.542619,
      "conscientiousness": 4.178745,
      "extroversion": 2.667147,
      "agreeableness": 6.216197,
      "neuroticism": 4.873328
    },
    "needs": {
      "hunger": 9.65313239313156,
      "social": 9.89848824818349,
      "sleep": 10.0,
      "hygiene": 5.000923806680951,
      "entertainment": 7.585539566175282
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Lisa Thompson",
    "firstName": "Lisa",
    "lastName": "Lisa",
    "age": 42,
    "gender": "male",
    "homeAddress": "204 Maple Ave",
    "currentLocation": "home",
    "occupation": "Teacher/Caregiver",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 7.069572,
      "conscientiousness": 3.681721,
      "extroversion": 3.938792,
      "agreeableness": 5.247293,
      "neuroticism": 5.00405
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.932510500772516,
      "sleep": 10.0,
      "hygiene": 4.96567459885985,
      "entertainment": 7.546993319767202
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Lucas Ruiz",
    "firstName": "Lucas",
    "lastName": "Lucas",
    "age": 13,
    "gender": "male",
    "homeAddress": "303 Pine Way",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.008905,
      "conscientiousness": 2.587086,
      "extroversion": 9.716566,
      "agreeableness": 2.191718,
      "neuroticism": 5.001327
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.957404613232423,
      "sleep": 10.0,
      "hygiene": 4.663119414546729,
      "entertainment": 7.707260681382246
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Luke Stephens",
    "firstName": "Luke",
    "lastName": "Luke",
    "age": 13,
    "gender": "male",
    "homeAddress": "404 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.622745,
      "conscientiousness": 4.816776,
      "extroversion": 10.0,
      "agreeableness": 3.9045,
      "neuroticism": 2.197679
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.910147790610091,
      "entertainment": 7.658399626869595
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Maria Sturm",
    "firstName": "Maria",
    "lastName": "Maria",
    "age": 34,
    "gender": "female",
    "homeAddress": "103 Oak St",
    "currentLocation": "home",
    "occupation": "Nurse",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.479064,
      "conscientiousness": 2.776868,
      "extroversion": 5.463587,
      "agreeableness": 4.435927,
      "neuroticism": 6.787729
    },
    "needs": {
      "hunger": 10.0,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.138890030121886,
      "entertainment": 7.819624515210692
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Maria Kallio",
    "firstName": "Maria",
    "lastName": "Maria",
    "age": 43,
    "gender": "female",
    "homeAddress": "408 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Housewife",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.443642,
      "conscientiousness": 3.80549,
      "extroversion": 6.680658,
      "agreeableness": 7.380031,
      "neuroticism": 5.803441
    },
    "needs": {
      "hunger": 9.743194630666045,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.9054716418078,
      "entertainment": 7.589764215341265
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Michael Blake",
    "firstName": "Michael",
    "lastName": "Michael",
    "age": 14,
    "gender": "male",
    "homeAddress": "301 Pine Way",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.721163,
      "conscientiousness": 4.595968,
      "extroversion": 5.525722,
      "agreeableness": 3.091042,
      "neuroticism": 6.542834
    },
    "needs": {
      "hunger": 9.679333906207429,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.929740658352468,
      "entertainment": 7.459761056973608
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Milo",
    "firstName": "Milo",
    "lastName": "Milo",
    "age": 4,
    "gender": "male",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.874985,
      "conscientiousness": 3.515737,
      "extroversion": 4.397163,
      "agreeableness": 2.692608,
      "neuroticism": 4.831562
    },
    "needs": {
      "hunger": 9.669337938034909,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.121041348345671,
      "entertainment": 7.631654120743657
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Mindy Kunitz",
    "firstName": "Mindy",
    "lastName": "Mindy",
    "age": 13,
    "gender": "male",
    "homeAddress": "309 Pine Way",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 3.226082,
      "conscientiousness": 2.507831,
      "extroversion": 5.902683,
      "agreeableness": 2.199574,
      "neuroticism": 4.190076
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.898223793319564,
      "sleep": 10.0,
      "hygiene": 5.021365241815402,
      "entertainment": 7.343192025257871
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Pastor Naomi",
    "firstName": "Pastor",
    "lastName": "Pastor",
    "age": 48,
    "gender": "male",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Lutheran Pastor",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 6.352716,
      "conscientiousness": 8.514874,
      "extroversion": 5.02209,
      "agreeableness": 4.471746,
      "neuroticism": 1.478144
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.93445269374213,
      "sleep": 10.0,
      "hygiene": 4.962593212454206,
      "entertainment": 7.221943278971008
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Nate",
    "firstName": "Nate",
    "lastName": "Nate",
    "age": 37,
    "gender": "male",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.451183,
      "conscientiousness": 5.658197,
      "extroversion": 6.696243,
      "agreeableness": 5.93263,
      "neuroticism": 4.803024
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.897733490027868,
      "sleep": 10.0,
      "hygiene": 5.056950373646553,
      "entertainment": 7.249661951361105
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Nina Blake",
    "firstName": "Nina",
    "lastName": "Nina",
    "age": 25,
    "gender": "female",
    "homeAddress": "301 Pine Way",
    "currentLocation": "home",
    "occupation": "Yoga Instructor/Instagram Model",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.592971,
      "conscientiousness": 1.503155,
      "extroversion": 7.662303,
      "agreeableness": 5.140405,
      "neuroticism": 4.253529
    },
    "needs": {
      "hunger": 9.111784394082829,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.058191176854142,
      "entertainment": 7.53349186152603
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Nora Blake",
    "firstName": "Nora",
    "lastName": "Nora",
    "age": 10,
    "gender": "male",
    "homeAddress": "301 Pine Way",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 2.8397,
      "conscientiousness": 1.496691,
      "extroversion": 5.597468,
      "agreeableness": 3.381877,
      "neuroticism": 3.408779
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.988917407669389,
      "sleep": 10.0,
      "hygiene": 4.804223155201319,
      "entertainment": 7.401212054517214
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Penny Lockheart",
    "firstName": "Penny",
    "lastName": "Penny",
    "age": 15,
    "gender": "male",
    "homeAddress": "305 Pine Way",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 1.693936,
      "conscientiousness": 8.078584,
      "extroversion": 3.644905,
      "agreeableness": 4.872345,
      "neuroticism": 5.52179
    },
    "needs": {
      "hunger": 9.714769202448938,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.778908558738176,
      "entertainment": 7.645805268491965
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Rose Stephens",
    "firstName": "Rose",
    "lastName": "Rose",
    "age": 16,
    "gender": "male",
    "homeAddress": "404 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.952434,
      "conscientiousness": 6.293277,
      "extroversion": 3.515254,
      "agreeableness": 6.437327,
      "neuroticism": 7.32946
    },
    "needs": {
      "hunger": 9.79488575988933,
      "social": 9.870452122492544,
      "sleep": 10.0,
      "hygiene": 4.9288979008911795,
      "entertainment": 7.239584032809382
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Sarah Madison",
    "firstName": "Sarah",
    "lastName": "Sarah",
    "age": 26,
    "gender": "female",
    "homeAddress": "307 Pine Way",
    "currentLocation": "home",
    "occupation": "Artist/Art Cooperative Owner",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.277126,
      "conscientiousness": 6.270633,
      "extroversion": 5.341176,
      "agreeableness": 6.733644,
      "neuroticism": 6.288242
    },
    "needs": {
      "hunger": 9.422352041386906,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.027139182562165,
      "entertainment": 7.223869726146225
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Scarlet Carter",
    "firstName": "Scarlet",
    "lastName": "Scarlet",
    "age": 38,
    "gender": "female",
    "homeAddress": "202 Maple Ave",
    "currentLocation": "home",
    "occupation": "School teacher",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 5.674478,
      "conscientiousness": 6.8226,
      "extroversion": 3.450141,
      "agreeableness": 4.931218,
      "neuroticism": 6.865779
    },
    "needs": {
      "hunger": 9.834126578716306,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 5.068834943280381,
      "entertainment": 7.771050773009176
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Steve Kallio",
    "firstName": "Steve",
    "lastName": "Steve",
    "age": 15,
    "gender": "male",
    "homeAddress": "408 Willow Creek Dr",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.465656,
      "conscientiousness": 4.121758,
      "extroversion": 3.751816,
      "agreeableness": 3.318257,
      "neuroticism": 5.038311
    },
    "needs": {
      "hunger": 9.962693291404577,
      "social": 9.98668441782164,
      "sleep": 10.0,
      "hygiene": 4.9414574838637195,
      "entertainment": 7.293185318276003
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Tessa",
    "firstName": "Tessa",
    "lastName": "Tessa",
    "age": 35,
    "gender": "female",
    "homeAddress": "Unknown",
    "currentLocation": "home",
    "occupation": "Housewife",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 4.801377,
      "conscientiousness": 3.136907,
      "extroversion": 3.866617,
      "agreeableness": 4.480266,
      "neuroticism": 8.371876
    },
    "needs": {
      "hunger": 9.916487444748745,
      "social": 9.777287608635374,
      "sleep": 10.0,
      "hygiene": 5.169912924562149,
      "entertainment": 7.269090597045659
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Tim Thompson",
    "firstName": "Tim",
    "lastName": "Tim",
    "age": 17,
    "gender": "male",
    "homeAddress": "204 Maple Ave",
    "currentLocation": "home",
    "occupation": "Student",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 3.516403,
      "conscientiousness": 5.351213,
      "extroversion": 4.923534,
      "agreeableness": 6.237944,
      "neuroticism": 5.969031
    },
    "needs": {
      "hunger": 9.872947349592938,
      "social": 10.0,
      "sleep": 10.0,
      "hygiene": 4.905797874323954,
      "entertainment": 7.473688459210937
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  },
  {
    "fullName": "Tom Kunitz",
    "firstName": "Tom",
    "lastName": "Tom",
    "age": 15,
    "gender": "male",
    "homeAddress": "309 Pine Way",
    "currentLocation": "home",
    "occupation": "Resident",
    "birthMonth": 1,
    "birthDay": 1,
    "personality": {
      "openness": 6.171355,
      "conscientiousness": 5.07697,
      "extroversion": 5.865145,
      "agreeableness": 6.331482,
      "neuroticism": 6.621928
    },
    "needs": {
      "hunger": 10.0,
      "social": 9.877303218947251,
      "sleep": 10.0,
      "hygiene": 5.145344005725328,
      "entertainment": 7.445284575980431
    },
    "psychState": {
      "drunk": 0.0,
      "lonely": 0.0,
      "frustrated": 0.0,
      "horny": 0.0,
      "angry": 0.0,
      "depressed": 0.0,
      "anxious": 0.0
    }
  }
];

console.log("✓ Loaded " + shared.npcs.length + " NPCs");

// =================================================================
// RELATIONSHIPS
// =================================================================

shared.npcRelationships = {
  "John Sturm <-> Maria Sturm": {
    "npc1": "Maria Sturm",
    "npc2": "John Sturm",
    "type": "romantic",
    "level": 6,
    "attraction": 60,
    "history": []
  },
  "Alex Sturm <-> Maria Sturm": {
    "npc1": "Maria Sturm",
    "npc2": "Alex Sturm",
    "type": "family",
    "level": 7,
    "attraction": 0,
    "history": []
  }
};

console.log("✓ Loaded " + Object.keys(shared.npcRelationships).length + " relationships");

// =================================================================
// TIME SYSTEM
// =================================================================

shared.time = {
  "totalDays": 5,
  "currentDay": "Friday",
  "dayOfWeek": 5,
  "date": "September 05, 2025",
  "month": 9,
  "dayOfMonth": 5,
  "year": 2025,
  "hour": 12,
  "minute": 0,
  "season": "Autumn",
  "timeString": "12:00 PM"
};

console.log("✓ Time: " + shared.time.currentDay + " - " + shared.time.timeString);
console.log("✓ Season: " + shared.time.season);

// =================================================================
// STATISTICS
// =================================================================

shared.simulationStats = {
  "total_interactions": 0,
  "affairs": 0,
  "hookups": 0,
  "fights": 0,
  "birthdays": 0
};

console.log("=== [PYTHON-EXPORT] Load complete ===");
console.log("Total simulation days: " + shared.time.totalDays);
