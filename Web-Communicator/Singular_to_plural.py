from Anything import Anything
from Gellish_file import Gellish_file
from SemanticNetwork import Semantic_Network


class Plurality:
    ''' A plurality and the rules to derive a plurality from a singular kind.'''
    def __init__(self, gel_net, current_file):
        self.coll_comm_uid = '2849'
        self.foreign_comm_uid = 'foreign'
        self.gel_net = gel_net
        self.current_file = current_file
        
    def convert_singular_to_plural(self, obj):
        ''' Tranform the English names_in_contexts of a kind
            in singular to the names_in_contexts of a kind in plural.
            And generate a unique identifier for the collection of things
            by concatenating the UID of the singular kind with the prefix coll:.
            And generate a relation between the two.
            name_in_context = languageUID, communityUID, name, naming_relationUID, descr
        '''
        exception_uids = ['730000']
        collections = ['collection', 'kind of relation']
        individuals = ['individual', 'occurrence', 'relation']

        # Verify whether obj category is a singular kind,
        # thus it's category is not a collection and
        # the uid has not a prefix that is 'coll:' and it is not an exception,
        # and it is not an individual thing.
        parts = obj.uid.split(':')
        if obj.uid not in exception_uids and obj.category not in collections \
           and not (len(parts) > 1 and parts[0] == 'coll') \
           and obj.category not in individuals:
            # Determine the uid of the plural thing by concatination with 'coll:'
            # and create the object with a preliminar name
            uid_plural = 'coll:' + obj.uid
            singular_name = obj.name
            plurality_name = singular_name + 's'
            self.coll = Anything(uid_plural, plurality_name)
            self.coll.category = 'collection'

            # Find the name for the plural thing for every English name in context
            if len(obj.names_in_contexts) > 0:
                self.first_name = True

                for name_in_context in obj.names_in_contexts:
                    # Verify if name is in English
                    if name_in_context[0] == '910036':
                        self.determine_english_plural(name_in_context)

                    # Determine Dutch plural name
                    elif name_in_context[0] == '910037':
                        self.determine_dutch_plural(name_in_context)

            # Debug print('Plurals:', plural.uid, plural.name, len(plural.names_in_contexts))
            for name_in_context in self.coll.names_in_contexts:
                # Debug print('Plural:', plural.name, plural.uid, name_in_context)
                print('UID and Name of plurality:', self.coll.uid, name_in_context[2])

            self.add_rel_between_single_and_collection(obj, self.coll)
            for relation in obj.relations:
                print('Expression:', obj.name, relation)

    def determine_english_plural(self, name_in_context):
        ''' Tranform the English names_in_contexts of a kind
            in singular to the names_in_contexts of a kind in plural.
        '''
        add_es = ['s', 'x', 'z']
        add_es2 = ['sh', 'ch']
        ch_as_k = {'stomach': 'stomachs', 'epoch': 'epochs'}
        ex_us = ['bus', 'octopus']
        ex_fez = {'fez': 'fezzes', 'gas': 'gasses'}
        ex_roof = ['roof', 'belief', 'chef', 'chief', 'spoof']
        consonants = []
        vowels = ['a', 'e', 'i', 'o', 'u']
        unchanged = ['sheep', 'series', 'species', 'deer', 'fish', 'aircraft']
        ex_dict_photo = ['photo', 'piano', 'halo']
        ex_os = ['banjo', 'cargo', 'flamingo', 'fresco', 'ghetto', 'holo', 'mango',
                 'memento', 'motto', 'tornado', 'tuxedo', 'vulcano']
        irregular = {'child': 'children',
                     'goose': 'geese',
                     'man': 'men',
                     'woman': 'women',
                     'tooth': 'teeth',
                     'foot': 'feet',
                     'mouse': 'mice',
                     'person': 'people'}
        latin_plurals = {'antenna': 'antennae',
                         'appendix': 'appendices',
                         'cactus': 'cacti',
                         'curriculum': 'curricula',
                         'formula': 'formulae',
                         'index': 'indices',
                         'millennium': 'millennia',
                         'referendum': 'referenda',
                         'stadium': 'stadia',
                         'terminus': 'termini',
                         'thesaurus': 'thesauri',
                         'vortex': 'vortices'}
        loanwords = {'alga': 'algae',
                     'alumnus': 'alumni',
                     'larva': 'larvae',
                     'espresso': 'espressos',
                     'risotto': 'risottos',
                     'paparazzo': 'paparazzi'}

        # Initialize option for two variants of plural names
        singular_name = name_in_context[2]
        plurality_name_2 = ''
        # Check name or end of name

        # Irregular plurals
        if singular_name in irregular:
            plurality_name = irregular[singular_name]

        # Loanwords
        elif singular_name in loanwords:
            plurality_name = loanwords[singular_name]

        # Loanwords from French
        elif len(singular_name) >= 3 and singular_name[-3:] == 'eau':
            plurality_name = singular_name + 's'
            plurality_name_2 = singular_name + 'x'

        # Rule 11: Some nouns don’t change at all when they’re pluralized.
        # To distinguish them their name will be preceded by 'collection of '.
        elif singular_name in unchanged:
            plurality_name = 'collection of ' + singular_name
            plurality_name_2 = singular_name

        # Rule 8: If the singular noun ends in -us,
        # then the plural ending is frequently replacing -us by -i.
        elif singular_name[-2:] == 'us' and not singular_name in ex_us:
            plurality_name = singular_name[0:-2] + 'i'

        # Rule 9: If the singular noun ends in -is,
        # then the plural ending replaces -is by -es (usually coming from Greek).
        elif singular_name[-2:] == 'is':
            plurality_name = singular_name[0:-2] + 'es'

        # Rule 2: If the singular noun ends in -s, -ss, -sh, -ch, -x, or -z,
        # then add -es to the end.
        elif singular_name[-1] in add_es or singular_name[-2:] in add_es2:

            # Rule 3: In some cases, singular nouns ending in -s or -z,
            # require doubling the -s or -z prior to adding the -es.
            if singular_name in ex_fez:
                plurality_name = ex_fez[singular_name]
            elif singular_name in ch_as_k:
                plurality_name = ch_as_k[singular_name]
            else:
                plurality_name = singular_name + 'es'

        # Rule 4: If the noun ends in a consonant or a single vowel plus -f or -fe,
        # then the f is often changed to -ve before adding the -s.
        elif singular_name[-1] == 'f' or singular_name[-2:] == 'fe':
            # TBD: check nouns which end in two vowels plus -f
            # usually form plurals in the normal way, with just an -s
            if singular_name in ex_roof:
                plurality_name = singular_name + 's'
            elif singular_name[-1] == 'f':
                plurality_name = singular_name[0:-1] + 'ves'
            else:
                plurality_name = singular_name[0:-2] + 'ves'

        # Rule 5: If a singular noun ends in -y
        elif singular_name[-1] == 'y':

            # Rule 5a: and the letter before the -y is a consonant,
            # then change the ending to -ies.
            if singular_name[-2] not in vowels:
                plurality_name = singular_name[0:-1] + 'ies'

            # Rule 6: and the letter before the -y is a vowel,
            # then simply add an -s to make it plural.
            else:
                plurality_name = singular_name + 's'

        # Rule 7: If the singular noun ends in -o,
        # then add -es to make it plural,
        # except for nouns that have a vowel before the final -o, then just add -s.
        elif singular_name[-1] == 'o':
            if singular_name in ex_dict_photo or singular_name[-2] in vowels:
                plurality_name = singular_name + 's'
            elif singular_name in ex_os:
                plurality_name = singular_name + 's'
                plurality_name_2 = singular_name + 'es'
            else:
                plurality_name = singular_name + 'es'

        # rule 10: If the singular noun ends in -on,
        # then the plural ending replaces -on by -a.
        elif singular_name[-2:] == 'on':
            plurality_name = singular_name[0:-2] + 'a'
        else:

            # Rule 1: To make all remaining regular nouns plural, add -s to the end.
            plurality_name = singular_name + 's'

        # Determine plural name(s) in context(s)
        plurality_name_in_context = name_in_context[:]
        plurality_name_in_context[2] = plurality_name
        plurality_name_in_context[4] = \
            'is a collection of which each element is a ' + singular_name + '.'
        self.coll.add_name_in_context(plurality_name_in_context)
        # Add a second name (synonym) when found
        if plurality_name_2 != '':
            plurality_name_in_context_2 = name_in_context[:]
            plurality_name_in_context_2[1] = self.coll_comm_uid
            plurality_name_in_context_2[2] = plurality_name_2
            plurality_name_in_context_2[4] = \
                'is a collection of which each element is a ' + singular_name + '.'
            self.coll.add_name_in_context(plurality_name_in_context_2)
        # Add a latin plural name (synonym) when found
        if singular_name in latin_plurals:
            plurality_name_3 = latin_plurals[singular_name]
            plurality_name_in_context_3 = name_in_context[:]
            plurality_name_in_context_3[1] = self.foreign_comm_uid
            plurality_name_in_context_3[2] = plurality_name_3
            plurality_name_in_context_3[4] = \
                'is a collection of which each element is a ' + singular_name + '.'
            self.coll.add_name_in_context(plurality_name_in_context_3)
        if self.first_name is True:
            self.coll.name = plurality_name_in_context[2]
            self.first_name = False

    def determine_dutch_plural(self, name_in_context):
        ''' Tranform the Dutch names_in_contexts of a kind
            in singular to the names_in_contexts of a kind in plural.
        '''
        irregular = ['dominee', 'kanarie', 'ruzie', 'felicitatie', 'tafel', 'computer',
                     'radio', 'bamboe']
        double_vowel = ['aa', 'ee', 'oo', 'uu']
        vowel = ['a', 'e', 'i', 'o', 'u', 'y']
        vowel_e = ['a', 'i', 'o', 'u', 'y']
        end_ie_add_s = ['balie', 'reactie', 'repetitie']
        both_s_and_en = ['individu', 'residu']
        abbrev_quote_s = ['cd', 'tv', 'wc', 'BV']
        role_of_person = ['bekende', 'gepensioneerde', 'werkende']
        emphasis_not_on_last = ['bacterie', 'porie', 'chemicalie']
        emphasis_on_last = ['bacterie', 'porie', 'chemicalie']
        latin = []
        last_two = ['el', 'em', 'en', 'er', 'um']
        last_three = ['erd', 'aar']
        last_four = ['aard']
        eur = ['eur']
        foon = ['foon']
        oor_or_ier = ['oor', 'ier']
        loanwords_s = ['elektricien', 'depot', 'tram', 'duel']

        # Temporal emphasis_not_on_last_sylable (irrespective of ending with -ie)
        emphasis_not_on_last_sylable = True
        # Temporal title_or_profession
        title_or_profession = True  # role of person?

        # Initialize option for two variants of plural names
        singular_name = name_in_context[2]
        plurality_name_2 = ''

        # Check name or end of name

        # Irregular plurals
        if singular_name in irregular:
            plurality_name = singular_name + 's'

        # Abbreviations
        elif singular_name in abbrev_quote_s:
            plurality_name = singular_name + "'s"

        # Singulars with two plurals one ending with -s and the other ending with -en
        elif singular_name in both_s_and_en:
            plurality_name = singular_name + 'en'
            plurality_name_2 = singular_name + "'s"

        # Rule 4d: Loanwords which plurals end on -s
        elif singular_name in loanwords_s:
            plurality_name = singular_name + 's'

        # Loanwords from French ending with eau
        elif len(singular_name) >= 3 and singular_name[-3:] == 'eau':
            plurality_name = singular_name + 's'

        # Rule 4: If the end of the sigular terminates with a single -e
        # preceded by a consonant, except for a title_or_profession
        # then the plural is the singular followed by -s.
        elif singular_name[-1] == 'e' and singular_name[-2] not in vowel :
            if singular_name in role_of_person:
                plurality_name = singular_name + 'n'
            else:
                plurality_name = singular_name + 's'

        # Rule 5.1: If the last char is a single vowel
        # then the plural is the singular followed by -'s.
        elif singular_name[-1] in vowel_e and singular_name[-2] not in vowel:
            plurality_name = singular_name + "'s"

        # Rule 4a: If emphasis is not on the last syllable and
        # ending with the last two chars in last_two
        # or the last three ending with last_three
        # then the plural is the singular followed by -s.
        elif emphasis_not_on_last_sylable \
                and (singular_name[-2:] in last_two
                     or (len(singular_name) >= 3 and singular_name[-3:] in last_three)
                     or (len(singular_name) >= 4 and singular_name[-4:] in last_four)):
            plurality_name = singular_name + 's'

        # Role 4b: If last syllable is emphasized and ending with -eur or -foon
        # then the plural is the singular followed by -s.
        # elif emphasis_on_last \
        elif ((len(singular_name) >= 3 and singular_name[-3:] in eur)
              or (len(singular_name) >= 4 and singular_name[-4:] in foon)):
            plurality_name = singular_name + 's'

        # Role 4c: If a title_or_profession and ending on -oor or -ier
        # then the plural is the singular followed by -s. 
        # elif title_or_profession \
        elif len(singular_name) >= 3 and singular_name[-3:] in oor_or_ier:
            plurality_name = singular_name + 's'

        # Rule 6: If the last two characters are -ee, then ën is added.
        elif singular_name[-2:] == 'ee':
            plurality_name = singular_name + 'ën'

        # Rule 7b: If the last two characters are -ie
        # and the emphasis is on the last syllable, then -e is replaced by -iën.
        elif singular_name[-2:] == 'ie':
            # Exceptions
            if singular_name in end_ie_add_s:
                plurality_name = singular_name + 's'
            # Emphasis not on the last sylable
            elif singular_name not in emphasis_not_on_last:
                plurality_name = singular_name + 'ën'

            # Rule 7a: If the last two characters are -ie
            # and the emphasis is not on the last syllable, then -e is replaced by iën.
            else:
                plurality_name = singular_name[:-1] + 'ën'

        # Rule 2: If the two but last characters are two identical vowels (a, e, o, u)
        # then replace the two vowels by one and add 'en' (note that ii is never occurring).
        elif len(singular_name) >= 3 and singular_name[-3:-1] in double_vowel:
            plurality_name = singular_name[:-2] + singular_name[-1] + 'en'

        # Rule 3: If the end is a single vowel followed by a consonant
        # then the consonant is duplicated and followed by 'en'.
        # ** Note: Sometimes the plural changes the sound into a long sound,
        #    then no consonant shall be added (e.g.: dak - daken).
        elif len(singular_name) >= 3 and singular_name[-3] not in vowel and \
                singular_name[-2] in vowel and singular_name[-1] not in vowel:
            plurality_name = singular_name + singular_name[-1] + 'en'

        # Rule 1: To make all remaining nouns plural, add -en to the singular form.
        else:
            plurality_name = singular_name + 'en'

        # Determine plural name(s) in context(s)
        plurality_name_in_context = name_in_context[:]
        plurality_name_in_context[2] = plurality_name
        plurality_name_in_context[4] = \
            'is een verzameling waarvan elk element is geclassificeerd als een ' \
            + singular_name + '.'
        self.coll.add_name_in_context(plurality_name_in_context)

        # Add a second name (synonym) when found
        if plurality_name_2 != '':
            plurality_name_in_context_2 = name_in_context[:]
            plurality_name_in_context_2[1] = self.coll_comm_uid
            plurality_name_in_context_2[2] = plurality_name_2
            plurality_name_in_context_2[4] = \
                'is een verzameling waarvan elk element is geclassificeerd als een ' \
                + singular_name + '.'
            self.coll.add_name_in_context(plurality_name_in_context_2)

        if self.first_name is True:
            self.coll.name = plurality_name_in_context[2]
            self.first_name = False

    def add_rel_between_single_and_collection(self, particular, plurality):
        ''' After creating a plural kind from a singular kind,
            relate both explicitly by a relation of kind
            4843: is classifier of each element of (6066), with as inverse
            4843: each of which element is classified as a (1986).
        '''
        rel_kind_uid = '4843'
        base_phrase = ['is classifier of each element of',
                       'is classificeerder van elk element van']
        self.current_file.Add_a_relation_to_related_objects(particular, plurality,
                                                            rel_kind_uid, base_phrase)


if __name__ == "__main__":
    # Test
    name = ''
    language_uid_en = '910036'  # English
    language_uid_nl = '910037'  # Dutch
    community_uid = '492014'  # Gellish
    naming_relation_uid = '5117'
    test_names = {'1': 'cat',
                  '2': 'house',
                  '3': 'truss',
                  '4': 'bus',
                  '5': 'marsh',
                  '6': 'lunch',
                  '7': 'tax',
                  '8': 'blitz',
                  '9': 'fez',
                  '10': 'gas',
                  '11': 'wife',
                  '12': 'wolf',
                  '13': 'roof',
                  '14': 'belief',
                  '15': 'chef',
                  '16': 'chief',
                  '17': 'city',
                  '18': 'puppy',
                  '19': 'ray',
                  '20': 'boy',
                  '21': 'patato',
                  '22': 'tomato',
                  '23': 'photo',
                  '24': 'piano',
                  '25': 'halo',
                  '26': 'vulcano',
                  '27': 'cactus',
                  '28': 'focus',
                  '29': 'analysis',
                  '30': 'ellipsis',
                  '31': 'phenomenon',
                  '32': 'criterion',
                  '33': 'sheep',
                  '34': 'series',
                  '35': 'species',
                  '36': 'deer',
                  '37': 'child',
                  '38': 'man',
                  '39': 'woman',
                  '40': 'antenna',
                  '41': 'appendix',
                  '42': 'bureau',
                  '43': 'espresso',
                  '44': 'pizza',
                  '45': 'spagetti',
                  '46': 'fresco',
                  'coll:47': 'batches',
                  '48': 'Paris',
                  '49': 'is a part of'}
    test_names_nl = {'1': 'boek',
                     '2': 'kast',
                     '3': 'berg',
                     '4': 'knoop',
                     '5': 'plaat',
                     '6': 'avontuur',
                     '7': 'wasmand',
                     '8': 'zetpil',
                     '9': 'kraag',
                     '10': 'balie',
                     '11': 'reactie',
                     '12': 'tafel',
                     '13': 'computer',
                     '14': 'cadeau',
                     '15': 'baby',
                     '16': 'taxi',
                     '17': 'piano',
                     '18': 'oma',
                     '19': 'opa',
                     '17': 'cd',
                     '18': 'tv',
                     '19': 'wc',
                     '20': 'idee',
                     '21': 'wee',
                     '22': 'trofee',
                     '23': 'dominee',
                     '24': 'bacterie',
                     '25': 'porie',
                     '26': 'allergie',
                     '27': 'kopie',
                     '28': 'calorie',
                     '29': 'theorie',
                     '30': 'melodie',
                     '31': 'radio',
                     '32': 'ziekte',
                     '33': 'werkende',
                     '34': 'repetitie',
                     '35': 'bamboe',
                     '36': 'keuken',
                     '37': 'monteur',
                     '38': 'telefoon',
                     '39': 'bankier',
                     '40': 'depot',
                     '41': 'BV'}

    lang = input("Enter language 'en' or 'nl': ")
    if lang == 'nl':
        names = test_names_nl
        language_uid = language_uid_nl
    else:
        names = test_names
        language_uid = language_uid_en
    GUI_lang_index = 0
    net_name = 'Net'
    gel_net = Semantic_Network(GUI_lang_index, net_name)
    rel_kind_uid = '4843'
    rel_type = Anything(rel_kind_uid, 'is classifier of each element of')
    gel_net.uid_dict[rel_kind_uid] = rel_type
    path_and_name = ''
    current_file = Gellish_file(path_and_name, gel_net)
    plurality = Plurality(gel_net, current_file)
    # Test list or test names from manual input
    for uid in names:
    # while name != 'end':
        name = names[uid]
        # name = input("Enter name or 'end': ")
        # uid = name  # Only in case of manual input
        obj = Anything(uid, name)
        if uid == '48':
            obj.category = 'individual'
        elif uid == '49':
            obj.category = 'kind of relation'
        descr = 'something'
        name_in_context = [language_uid, community_uid, name, naming_relation_uid, descr]
        obj.add_name_in_context(name_in_context)
        print('UID and Name of singular:', obj.uid, obj.name)  # obj.names_in_contexts)

        plurality.convert_singular_to_plural(obj)
