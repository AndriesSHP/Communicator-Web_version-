# import os
# import csv
# from tkinter import filedialog
# from tkinter import *
# from tkinter.ttk import *
import datetime

# from Bootstrapping import *
from Expr_Table_Def import idea_uid_col, \
    lh_uid_col, rel_type_uid_col, rel_type_name_col, rh_uid_col
from Create_output_file import Open_output_file, Save_expressions_in_file


class Anything:
    ''' Anything is an instance of the class.
        However, not everything has the same attributes.
        The attributes of something is determined by its category according to the taxonomy.
    '''

    def __init__(self, uid, name, category=None):
        self.uid = uid
        # Name (out of context) at time of creation of the object
        self.name = name
        # Candidate_names = rh object names that need to be verified later with lh object names
        self.candidate_names = []
        self.defined = False
        # Categories are upper level concepts: individual, kind, etc.
        # for guiding logic and the GUI views
        # If category not specified than allocate 'anything' as category.
        self.category = category if category is not None else 'anything'
        self.names_in_contexts = []  # [lang_uid, comm_uid, name, naming_rel_uid, description]
        self.relations = []  # expressions (including used names)
        self.base_phrases = []
        self.base_phrases_in_contexts = []
        self.inverse_phrases = []
        self.inverse_phrases_in_contexts = []
        # Supertypes are the direct supertype objects
        # that duplicate the uid refs in specialization relations (subset), invalid for individuals
        self.supertypes = []
        # Subtypes are the direct subtype objects
        # that duplicate the uid refs in specialization relations (subset), invalid for individuals
        self.subtypes = []
        # Classifiers are kinds, that duplicate the uid refs in classification relations (subset)
        self.classifiers = []
        # Individuals, are individual things
        # that duplicate the uid refs in classification relations (subset), invalid for kinds
        self.individuals = []
        # Parts are the parts of kinds or of individual things (duplicates part-whole relations)
        self.parts = []
        # Aspects are the aspects and intrinsic aspects of kinds or of individual things
        # (duplicates possession relations)

        date = datetime.date.today()
        subject_name = self.name
        self.header1 = ['Gellish', 'English', 'Version', '9.0', date, 'Results',
                        'about ' + subject_name]

    def add_name_in_context(self, name_in_context):
        ''' add name or alias to collection of names:
            name_in_context = (languageUID, communityUID, naming_relationUID, name, descr).
        '''
        if name_in_context not in self.names_in_contexts:
            self.names_in_contexts.append(name_in_context)

    def add_must_phrase(self, name_in_context):
        """ Test whether name_in_context is a phrase that starts with 'shall',
            if yes, then add a base phrase or inverse phrase that starts with 'must'.
            name_in_context = languageUID, communityUID, name, naming_relationUID, descr
        """
        new_phrase = ''
        phrase = name_in_context[2]
        phrase_parts = phrase.split(' ')
        # If phrase is an English phrase that starts with 'shall'
        # then a new phrase is added in which shall is replaced by must
        if name_in_context[0] == '910036' and len(phrase_parts) > 2 \
                and phrase_parts[0] == 'shall':
            new_phrase = 'must' +  phrase[5:]
            new_name_in_context = name_in_context[:]
            new_name_in_context[2] = new_phrase
            if new_name_in_context not in self.names_in_contexts:
                self.names_in_contexts.append(new_name_in_context)
                naming_rel_uid = new_name_in_context[3]
        return new_phrase

    def add_relation(self, relation):
        ''' add relation object to collection of relations with self.'''
        if relation not in self.relations:
            self.relations.append(relation)
        else:
            print('Duplicate relation uid {} ignored: '.format(relation.uid))

    def add_classifier(self, classifier):   # only applicable for individuals
        if classifier not in self.classifiers:
            self.classifiers.append(classifier)

    def add_supertype(self, supertype):     # only applicable for kinds
        if supertype not in self.supertypes:
            self.supertypes.append(supertype)

    def add_subtype(self, subtype):         # only applicable for kinds
        if subtype not in self.subtypes:
            self.subtypes.append(subtype)

    def add_individual(self, individual):   # only applicable for kinds
        if individual not in self.individuals:
            self.individuals.append(individual)

    def add_part(self, part):   # applicable for individual things and for kinds
        if part not in self.parts:
            self.parts.append(part)

    def add_first_role(self, kind_of_role):
        self.first_role = kind_of_role

    def add_second_role(self, kind_of_role):
        self.second_role = kind_of_role

    def add_role_player(self, kind_of_role_player):
        self.role_player = kind_of_role_player

    def add_first_role_player(self, kind_of_role_player):
        self.first_role_player = kind_of_role_player

    def add_second_role_player(self, kind_of_role_player):
        self.second_role_player = kind_of_role_player

    def show(self, network):
        uid = self.uid
        query_results = []
        print('\nProduct model of object UID: {}'.format(uid))
        for nam in self.names_in_contexts:
            if len(nam) > 0:
                if nam[4] != '':
                    print('  Name: {} {}.'.format(nam[2], nam[0:2]))
                    print('  Description: {}'.format(nam[4]))
                else:
                    print('  Name: {} {}.'.format(nam[2], nam[0:2]))
            else:
                print('  Name: {}.'.format(self.name))
        # Show all relations
        for rel in self.relations:
            lh = network.uid_dict[rel.expression[lh_uid_col]]
            if len(lh.names_in_contexts) > 0:
                # pref_name should be determined by preferences
                lh_pref_name = lh.names_in_contexts[0][2]
            else:
                lh_pref_name = lh.name
                print('  LH name in context missing:', lh.name, lh.names_in_contexts)
            rh = network.uid_dict[rel.expression[rh_uid_col]]
            if len(rh.names_in_contexts) > 0:
                # pref_name should be determined by preferences
                rh_pref_name = rh.names_in_contexts[0][2]
            else:
                rh_pref_name = rh.name
            print('  Idea {}: ({}) {} ({}) {} ({}) {}'.
                  format(rel.uid,
                         rel.expression[lh_uid_col], lh_pref_name,
                         rel.expression[rel_type_uid_col], rel.expression[rel_type_name_col],
                         rel.expression[rh_uid_col], rh_pref_name))
            query_results.append(rel.expression)

        save_on_file = input('\nSave query results on output file? (y/n): ')
        if save_on_file == 'y':
            lang_name = 'English'
            serialization = 'CSV'
            output_file = Open_output_file(query_results, self.name, lang_name, serialization)
            Save_expressions_in_file(query_results, output_file, self.header1, serialization)

    def __repr__(self):
        # return(self.uid, self.names_in_contexts)
        return(' ({}) {}'.format(self.uid, self.names_in_contexts))

    def add_base_phrase(self, phrase_in_context):
        self.base_phrases_in_contexts.append(phrase_in_context)
        if phrase_in_context[2] not in self.base_phrases:
            self.base_phrases.append(phrase_in_context[2])

    def add_inverse_phrase(self, phrase_in_context):
        self.inverse_phrases_in_contexts.append(phrase_in_context)
        if phrase_in_context[2] not in self.inverse_phrases:
            self.inverse_phrases.append(phrase_in_context[2])


class Relation(Anything):
    ''' lh, rel_type, rh, phrase_type, uom and expression
        that expresses a binary relation with contextual facts.
        Contextual facts are about this object.
        Default category is 'binary relation'
    '''
    def __init__(self, lh_obj, rel_type, rh_obj, phrase_type_uid, uom, expression,
                 category=None):
        # intention_type = None
        self.uid = expression[idea_uid_col]
        self.lh_obj = lh_obj
        self.rel_type = rel_type
        self.rh_obj = rh_obj
        self.phrase_type_uid = phrase_type_uid
        self.uom = uom
        # The intention_type default is 491285 (statement)
        self.expression = expression
        # The category of a relation (default: 'binary relation') is the highlevel category.
        self.category = category if category is not None else 'binary relation'

    def add_contextual_fact(self, cont_fact):
        try:
            self.cont_facts.append(cont_fact)
        except AttributeError:
            self.cont_facts = [cont_fact]

    def __repr__(self):
        # return(self.uid, self.lh_uid, self.rel_type_uid, self.phrase_type_uid, self.rh_uid)
        return("Idea: {} lh_uid: {} ({}) {} rh_uid: {}".
               format(self.uid, self.lh_obj.uid, self.rel_type.uid,
                      self.phrase_type_uid, self.rh_obj.uid))


if __name__ == "__main__":
    # Test
    from SemanticNetwork import Semantic_Network
    language_uid_en = '910036'  # English
    language_uid_nl = '910037'  # Dutch
    community_uid = '492014'  # Gellish
    test_phrases = {'1': 'rel',
                    '2': 'shall have as part a',
                    '3': 'shall be a part of a',
                    '4': 'must be a part of a'}
    GUI_lang_index = 0
    net_name = 'Net'
    gel_net = Semantic_Network(GUI_lang_index, net_name)
    names = test_phrases
    language_uid = language_uid_en
    gel_net.lang_uid_dict[language_uid] = language_uid_en
    naming_relation_uid = '6066'
    base_naming_relation_uid = '6066'
    inv_naming_relation_uid = '1986'
    gel_net.total_base_phrases = []
    gel_net.total_inverse_phrases = []
    for uid in names:
        name = names[uid]
        obj = Anything(uid, name)
        obj.category = 'kind of relation'
        descr = 'something'
        name_in_context = [language_uid, community_uid, name, naming_relation_uid, descr]
        obj.add_name_in_context(name_in_context)

        new_phrase = obj.add_must_phrase(name_in_context)

        if naming_relation_uid == '6066':
            gel_net.total_base_phrases.append(new_phrase)
            naming_relation_uid = inv_naming_relation_uid
        else:
            gel_net.total_inverse_phrases.append(new_phrase)
            naming_relation_uid = base_naming_relation_uid
        print('Phrase/New phrase: {} / {}'.format(name_in_context, new_phrase))
