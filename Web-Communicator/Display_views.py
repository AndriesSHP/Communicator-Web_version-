import os
import operator

import remi.gui as gui
from remi_ext import TreeTable, SingleRowSelectionTable  # MultiRowSelectionTable

from tkinter import filedialog, Tk

from Bootstrapping import ini_out_path, basePhraseUID, inversePhraseUID
from Expr_Table_Def import lh_name_col, rel_type_name_col, rh_name_col, status_col, \
    lh_uid_col, rel_type_uid_col, rh_uid_col, idea_uid_col, phrase_type_uid_col, \
    uom_uid_col, uom_name_col, full_def_col, \
    lh_role_uid_col, lh_role_name_col, rh_role_uid_col, rh_role_name_col, \
    expr_col_ids, header3

from Create_output_file import Create_gellish_expression, Convert_numeric_to_integer, \
    Open_output_file
from Occurrences_diagrams import Occurrences_diagram
from utils import open_file
from Anything import Relation

class Display_views():
    """ Various models about object(s)
        are created resulting from a query on a semantic network
        and the models are presented in various treeviews in a notebook.
    """
    def __init__(self, gel_net, user_interface):
        self.gel_net = gel_net
        self.user_interface = user_interface
        self.root = user_interface.root
        self.GUI_lang_index = user_interface.GUI_lang_index
        self.uid_dict = gel_net.uid_dict
        self.container = user_interface.container

        self.network_model = []
        self.rels_in_network_model = []
        self.kind_model = []
        self.prod_model = []
        self.expr_table = []
        self.summ_model = []
        self.summ_objects = []
        self.taxon_model = []
        self.possibilities_model = []
        self.indiv_model = []
        self.indiv_objects = []
        self.info_model = []
        self.all_subtypes = []
        self.occ_model = []
        self.involv_table = []
        self.seq_table = []
        self.part_whole_occs = []
        self.taxon_hierarchy = {}
        self.net_hierarchy = {}
        self.net_parents = []
        self.net_ideas = []

        self.taxon_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.summary_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.possibility_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.indiv_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.occ_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.taxon_aspect_uids = ['', '', '', '']
        self.taxon_column_names = ['', '', '', '']
        self.taxon_uom_names = ['', '', '', '']
        self.summ_aspect_uids = ['', '', '', '']
        self.summ_column_names = ['', '', '', '']
        self.summ_uom_names = ['', '', '', '']
        self.possib_aspect_uids = ['', '', '', '', '']
        self.possib_column_names = ['', '', '', '', '']
        self.possib_uom_names = ['', '', '', '', '']
        self.indiv_aspect_uids = ['', '', '', '', '']
        self.indiv_column_names = ['', '', '', '', '']
        self.indiv_uom_names = ['', '', '', '', '']
        self.kinds = ['kind', 'kind of physical object', 'kind of occurrence',
                      'kind of aspect', 'kind of role', 'kind of relation', 'number']
        self.specialization_uids = ['1146', '1726', '5396', '1823']

        self.subs_head = ['Subtypes', 'Subtypen']
        self.comp_head = ['Part hierarchy', 'Compositie']
        self.occ_head = ['Occurrences', 'Gebeurtenissen']
        # self.role_head = ['Role', 'Rol']
        # self.involv_head = ['Involved', 'Betrokkene']
        self.kind_head = ['Kind', 'Soort']
        self.aspect_head = ['Aspect', 'Aspect']
        self.part_occ_head = ['Part occurrence', 'Deelgebeurtenis']
        self.info_head = ['Document', 'Document']
        self.name_head = ['Name', 'Naam']
        self.parent_head = ['Parent concept', 'Hoger concept']
        self.comm_head = ['Community', 'Taalgemeenschap']
        self.unknown = ['unknown', 'onbekend']
        self.unknown_kind = ['unknown kind', 'onbekende soort']
        self.unknown_val = ['unknown value', 'onbekende waarde']

        self.occ_aspects = ['', '', '', '', '', '', '', '', '', '', '']
        self.occ_kinds = ['', '', '', '', '', '', '', '', '', '', '']
        self.occ_uoms = ['', '', '', '', '', '', '', '', '', '', '']

        self.num_idea_uid = 211000000
        self.classification = ['is classified as a', 'is geclassificeerd als een']
        self.nr_of_occurrencies = 0
        self.max_nr_of_rows = 500   # in treeviews

        self.selected_obj = None
        self.modified_object = None
        self.modification = None

    def empty_models(self):
        """ Make models empty enabling the creation of new models."""
        self.network_model[:] = []
        self.rels_in_network_model[:] = []
        self.kind_model[:] = []
        self.prod_model[:] = []
        self.expr_table[:] = []
        self.taxon_model[:] = []
        # self.taxon_objects[:] = []
        self.summ_model[:] = []
        self.summ_objects[:] = []
        self.possibilities_model[:] = []
        # self.possib_objects[:] = []
        self.indiv_model[:] = []
        self.indiv_objects[:] = []
        self.info_model[:] = []
        self.all_subtypes[:] = []
        self.occ_model[:] = []
        self.involv_table[:] = []
        self.seq_table[:] = []
        self.part_whole_occs[:] = []
        self.taxon_hierarchy.clear()
        self.net_hierarchy.clear()  # levels of objects in network hierarchy
        self.net_parents[:] = []  # included parent objects in network model
        self.net_ideas[:] = []

        self.summ_aspect_uids[:] = ['', '', '', '']
        self.summ_column_names[:] = ['', '', '', '']
        self.summ_uom_names[:] = ['', '', '', '']
        self.taxon_aspect_uids[:] = ['', '', '', '']
        self.taxon_column_names[:] = ['', '', '', '']
        self.taxon_uom_names[:] = ['', '', '', '']
        self.possib_aspect_uids[:] = ['', '', '', '', '']
        self.possib_column_names[:] = ['', '', '', '', '']
        self.possib_uom_names[:] = ['', '', '', '', '']
        self.indiv_aspect_uids[:] = ['', '', '', '', '']
        self.indiv_column_names[:] = ['', '', '', '', '']
        self.indiv_uom_names[:] = ['', '', '', '', '']

    def Build_product_views(self, obj_list):
        """ Create product model views for one or more objects in obj_list."""
        self.empty_models()

        for obj in obj_list:
            lang_name, comm_name, preferred_name, descr = \
                self.user_interface.Determine_name_in_context(obj)
            obj.name = preferred_name
            self.object_in_focus = obj

            # Initialize subtype list of object in focus
            # Excluding duplicates due to multiple inheritance
            self.all_subtypes[:] = []
            # If object is excluded because it did not satisfy a condition then skip it
            if obj in self.user_interface.query.ex_candids:
                self.Display_message(
                    'Excluded candidate-1: {}'.format(obj.name),
                    'Uitgesloten kandidaat-1: {}'.format(obj.name))
                continue
            self.subtype_level = 0
            self.taxon_hierarchy[obj] = 0
            self.net_hierarchy[obj] = 0
            self.Build_single_product_view(obj)

    def Build_single_product_view(self, obj):
        """ Create various model views for a single object (obj),
            being either an individual thing or a kind.
            This includes at least the following models (views):
            network model, kind_model, prod_model, expr_table (with Gellish expressions),
            taxon_model (taxonomy view), summ_model (multi-product view),
            possibilities_model and indiv_model.
        """
        # Verify whether object is excluded from list of candidates
        if obj in self.user_interface.query.ex_candids:
            self.Display_message(
                'Excluded candidate: {}'.format(obj.name),
                'Uitgesloten kandidaat: {}'.format(obj.name))
            return

        self.implied_parts_dict = {}
        self.nr_of_occurrencies = 0
        self.occ_in_focus = 'no'
        # nr_of_occ_aspect_kinds = 3
        self.decomp_level = 0
        role = ''

        if self.subtype_level == 0:
            self.Create_prod_model_view_header(obj)

        # If object_in_focus is a kind, then collect its supertypes
        if obj.category in self.kinds:
            # Find preferred name of object in required language and community
            lang_name, comm_name, obj_name, descr = \
                self.user_interface.Determine_name_in_context(obj)
            obj.name = obj_name

            # Search for the first supertype relation
            # that generalizes the obj
            if len(obj.supertypes) == 0:
                # No supertypes found for kind: report omission
                # super_uid = 0
                # super_name = 'Not found'
                descrOfKind = ''
                self.Display_message(
                    'No supertype of {} found.'.format(obj.name),
                    'Geen supertype van {} gevonden.'.format(obj.name))
            else:
                # There is one or more supertype of the kind:
                # collect all generalization relations in the expr_table and the network
                for supertype in obj.supertypes:
                    if supertype not in self.net_parents:
                        for rel_obj in supertype.relations:
                            expr = rel_obj.expression
                            if rel_obj.rel_type.uid in self.specialization_uids:
                                # Verify if the obj is a subtype in the specialization relation
                                if (rel_obj.lh_obj == obj
                                        and expr[phrase_type_uid_col] == basePhraseUID) \
                                        or (rel_obj.rh_obj == obj
                                            and expr[phrase_type_uid_col] == inversePhraseUID):
                                    # Debug print('Super of sub:', supertype.name,
                                    #       expr[lh_name_col:rh_name_col+1])
                                    if len(self.expr_table) < self.max_nr_of_rows \
                                            and expr not in self.expr_table:
                                        self.expr_table.append(expr)
                                        self.Add_line_to_network_model(obj, rel_obj, expr)

            self.taxon_row[0] = obj.uid
            self.taxon_row[1] = obj.name
            self.taxon_row[3] = comm_name
            if len(obj.supertypes) > 0:
                lang_name, comm_name_supertype, supertype_name, descr_of_super = \
                    self.user_interface.Determine_name_in_context(obj.supertypes[0])
            else:
                supertype_name = self.unknown_kind[self.GUI_lang_index]
            self.taxon_row[2] = supertype_name   # name of the first supertype

            # Add object_in_focus to possibilities_model with comm_name of obj (not of supertype)
            # Second (extended) obj_name enables duplicate branches in display tree
            possib_row = [obj.uid, obj_name, obj_name, '', supertype_name, comm_name]
            if possib_row not in self.possibilities_model:
                self.possibilities_model.append(possib_row)

            # Find kinds of aspects and their values for kind_in_focus (and implied parts)
            self.Find_kinds_of_aspects(obj, role)
            self.Add_row_to_taxonomy(obj)

            # Find kinds of parts of kind in focus and their conceptual or qualitative aspects
            self.Find_kinds_of_parts_and_their_aspects(obj)

            # Find (qualitative) information about the kind in focus and build info_model
            self.Find_information_about_object(obj)

            # Determine whether the kind is a classifier for individual things
            # and collect individual things that are classified by the kind in focus
            self.Determine_individuals(obj)

            # Determine subtypes of kind_in_focus and build product models of those subtypes
            self.subtype_level += 1
            for sub in obj.subtypes:
                # Debug print('Sub_name, Obj_name:', sub.name, obj.name)
                if sub not in self.all_subtypes:
                    self.taxon_hierarchy[sub] = self.taxon_hierarchy[obj] + 1
                    self.all_subtypes.append(sub)
                    # Find the relation with the supertype and add it to the product model
                    for supertype in sub.supertypes:
                        for super_rel_obj in supertype.relations:
                            super_ex = super_rel_obj.expression
                            if super_rel_obj.rel_type.uid in self.specialization_uids:
                                # Verify whether the obj
                                # is the supertype in the specialization relation
                                if (super_rel_obj.lh_obj == sub
                                        and super_ex[phrase_type_uid_col] == basePhraseUID) \
                                        or (super_rel_obj.rh_obj == sub
                                            and super_ex[phrase_type_uid_col] == inversePhraseUID):
                                    if len(self.expr_table) < self.max_nr_of_rows \
                                            and super_ex not in self.expr_table:
                                        self.expr_table.append(super_ex)
                                    # Debug print('Additions:', sub.name,
                                    #       obj.name, super_ex[phrase_type_uid_col])
                                    self.Add_line_to_network_model(obj, super_rel_obj, super_ex)
                    self.Build_single_product_view(sub)
                else:
                    self.Display_message(
                        'Object {} is also a subtype of {}.'.
                        format(sub.name, obj.name),
                        'Object {} is ook een sybtype van {}.'.
                        format(sub.name, obj.name))

        # Individual thing: Object category is not a kind, thus indicates an indiv.
        # Verify whether the individual thing is classified (has one or more classifiers)
        elif len(obj.classifiers) == 0:
            self.Display_message(
                'For object {} neither a supertype nor a classifier is found.'.
                format(obj.name),
                'Voor object {} is geen supertype noch een classificeerder gevonden.'.
                format(obj.name))
        else:
            # An individual, such as an individual physical object or occurrence,
            # because the object_in_focus is classified (once or more times)
            # Search for the first classifying kind and classification relation
            # that classifies the object_in_focus
            classifier = obj.classifiers[0]
            # kind_uid is the kind that classifies the object_in_focus
            kind_uid = classifier.uid
            # Determine name etc. of the kind that classifies the object_in_focus
            lang_name, comm_name, kind_name, descrOfKind = \
                self.user_interface.Determine_name_in_context(classifier)

            # Verify whether the individual is an occurrence.
            if kind_uid in self.gel_net.subOccurrenceUIDs:
                obj.category = 'occurrence'

        # If obj is an occurrence then store occurrence in occ_model
        if obj.category == 'occurrence' or obj.category == 'kind of occurrence':
            self.nr_of_occurrencies += + 1

            # self.occ_model.append([occ.uid, occ.name, higher.name, involv.uid, kind_occ.uid,
            #                       occ.name, part_occ.name,
            #                       involv.name, kind_part_occ.name, role_of_involved])
            self.occ_model.append([obj.uid, '', '', '', '',
                                   obj.name, '', '', kind_name, ''])

        # Individual object_in_focus:
        # Find aspects, their classification and their values and UoMs
        # of the individual object_in_focus
        if obj.category in ['individual', 'physical object', 'occurrence']:
            lang_name, community_name, kind_name, descrOfKind = \
                self.user_interface.Determine_name_in_context(obj)
            # Summ_model table = obj.uid, obj.name, kind_name, community_name, aspects
            self.summary_row[0] = obj.uid
            self.summary_row[1] = obj.name
            self.summary_row[2] = kind_name
            self.summary_row[3] = community_name

            # indiv_model = obj.uid, obj.name, '', kind_name, community_name
            self.indiv_row[0] = obj.uid
            self.indiv_row[1] = obj.name
            self.indiv_row[2] = ''
            self.indiv_row[3] = kind_name
            self.indiv_row[4] = community_name

            # Find aspects of individual object_in_focus
            self.Find_aspects(obj, role)

            # Find parts and their aspects
            self.part_head_req = True
            self.Find_parts_and_their_aspects(obj)

        # self.parts_of_occ_table= []       # parts of occurrence in focus
        if obj.category != 'occurrence':
            # Search for occurrences about the object_in_focus
            # and for other objects that are involved in those occurrences.
            self.decomp_level = 0
            self.Occurs_and_involvs(obj)

    def Add_line_to_network_model(self, obj, rel_obj, expr):
        """ Add a row to the network_model for display in a network view.
            rel_obj is the relation object whereas lh or rh object is the object in focus.
            expr is the full expression.
            network_model = related_uid, focus_uid, focus_name, phrase, related_name,
                            kind_uid, related_name, focus_name, kind_name
            Branch is an expression that is added to the network_model.
        """
        if expr[idea_uid_col] not in self.net_ideas:
            self.net_ideas.append(expr[idea_uid_col])

            # If the left hand object is the current_focus,
            # then find the base phrase or inverse phrase for the relation
            # in the preferred language and language community
            # Debug print('Focus:', obj.name)
            if rel_obj.lh_obj == obj:
                # lh_obj is the current_focus
                # Determine the preferred name of the related object
                kind_name, kind_uid = self.Determine_preferred_kind_name(rel_obj.rh_obj)
                # Determine the preferred phrase for the kind of relation
                # Debug print('Base phrases:', expr[rel_type_name_col],
                #      rel_obj.rel_type.base_phrases)
                if expr[rel_type_name_col] in rel_obj.rel_type.base_phrases:
                    lang_name, comm_name, rel_type_phrase, full_def = \
                        self.user_interface.Determine_name_in_context(rel_obj.rel_type, 'base')
                else:
                    # Rel_type_name is an inverse phrase
                    lang_name, comm_name, rel_type_phrase, full_def = \
                        self.user_interface.Determine_name_in_context(rel_obj.rel_type, 'inverse')
                branch = [rel_obj.rh_obj.uid, rel_obj.lh_obj.uid, rel_obj.rel_type.uid,
                          rel_type_phrase, rel_obj.rh_obj.name, kind_uid,
                          expr[rh_name_col], expr[lh_name_col], kind_name]
                # Debug print('Expr-l  :', expr[lh_name_col:rh_name_col+1])
                # Debug print('Branch-l:', self.net_hierarchy[obj],
                #       rel_obj.phrase_type_uid, branch)
            elif rel_obj.rh_obj == obj:
                # rh_obj is the current_focus
                kind_name, kind_uid = self.Determine_preferred_kind_name(rel_obj.lh_obj)
                if expr[rel_type_name_col] in rel_obj.rel_type.base_phrases:
                    lang_name, comm_name, rel_type_phrase, full_def = \
                        self.user_interface.Determine_name_in_context(rel_obj.rel_type, 'inverse')
                else:
                    lang_name, comm_name, rel_type_phrase, full_def = \
                        self.user_interface.Determine_name_in_context(rel_obj.rel_type, 'base')
                branch = [rel_obj.lh_obj.uid, rel_obj.rh_obj.uid, rel_obj.rel_type.uid,
                          rel_type_phrase, rel_obj.lh_obj.name, kind_uid,
                          expr[lh_name_col], expr[rh_name_col], kind_name]
                # Debug print('Expr-r  :', expr[lh_name_col:rh_name_col+1])
                # Debug print('Branch-r:', self.net_hierarchy[obj],
                #             rel_obj.phrase_type_uid, branch)
            else:
                # Debug print('Object {} does not appear in idea {} '.
                #       format(obj.name, expr[lh_name_col:rh_name_col+1]))
                return

            # Add the branch to the network_model, if not yet present
            # if branch not in self.network_model:
            parent_uid = branch[1]
            rel_type_uid = branch[2]
            # Allocate level in the network hierarchy (add 2 because of inserted relation phrase
            if rel_obj.lh_obj == obj:
                if obj == self.object_in_focus:
                    self.net_hierarchy[rel_obj.rh_obj] = self.net_hierarchy[obj] + 2
                else:
                    self.net_hierarchy[rel_obj.rh_obj] = self.net_hierarchy[obj] + 1
            elif rel_obj.rh_obj == obj:
                if obj == self.object_in_focus:
                    self.net_hierarchy[rel_obj.lh_obj] = self.net_hierarchy[obj] + 2
                else:
                    self.net_hierarchy[rel_obj.lh_obj] = self.net_hierarchy[obj] + 1

            # If the branch is about the object in focus,
            # then insert an intermediate line with the expressed kind of relation
            if parent_uid == self.object_in_focus.uid and \
                    rel_type_uid not in self.rels_in_network_model:
                if len(self.rels_in_network_model) == 0:
                    # Append the root line to the network
                    kind_name, kind_uid = self.Determine_preferred_kind_name(self.object_in_focus)
                    root_line = [self.object_in_focus.uid, '', '', '', '', kind_uid,
                                 self.object_in_focus.name, '', kind_name]
                    # Debug print('Root branch:', root_line)
                    self.network_model.append(root_line)
                    self.net_hierarchy[self.object_in_focus] = 0
                    self.net_parents.append(self.object_in_focus)

                # Determine the relation type object from the rel_type_uid
                rel_obj = self.uid_dict[rel_type_uid]
                self.net_hierarchy[rel_obj] = 1
                # Append the intermediate line with the phrase of the kind of relation
                phrase = branch[3]
                focus_name = branch[7]
                intermediate = [rel_type_uid, parent_uid, '', '', '', '',
                                phrase, focus_name]
                # Debug print('Intermediate branch:', intermediate)
                self.network_model.append(intermediate)
                self.rels_in_network_model.append(rel_type_uid)

            # Determine the level in the network hierarchy
            child = self.uid_dict[branch[0]]
            if child not in self.net_parents:
                self.net_parents.append(child)
            parent = self.uid_dict[branch[1]]
            # Debug print('Parent-child', parent.name, branch[1],
            #       rel_type_phrase, child.name, branch[0])
            if parent not in self.net_parents:
                # Debug print('Add parent', parent.name, branch[1],
                #       rel_type_phrase, child.name, branch[0])
                self.net_hierarchy[parent] = 0
                self.net_parents.append(parent)

            # If the branch is a direct child of the object in focus,
            # and if the kind of relation is a possession of characteristic
            # or one of its subtypes
            # then determine that value of the characteristic and add it to the branch.
            if parent_uid == self.object_in_focus.uid:
                branch[1] = rel_type_uid
                branch[7] = rel_type_phrase
                if rel_type_uid in self.gel_net.subPossAspUIDs:
                    # Determine the value of the aspect
                    qualifier = 'quantitative'
                    aspect = self.uid_dict[branch[0]]
                    equality, value_name, uom_name, value_uid, uom_uid = \
                        self.Determine_aspect_value(aspect, qualifier)
                    branch += [equality, value_name, uom_name]
                    # Debug print('Branch with values:', branch)
            self.network_model.append(branch)
            # Debug print('Branch-3:', rel_type_uid, branch)
            # else:
            # Debug print('Idea {} already included in network'.format(expr[idea_uid_col]))

    def Create_prod_model_view_header(self, obj):
        """ Create prod_model and kind_model view header."""
        # Verify if object is classified or has a supertype
        status_text = ['accepted', 'geaccepteerd']
        # === should become the status of the classification cr specialization relation ===
        if len(obj.classifiers) == 0 and len(obj.supertypes) == 0:
            print('Object category:', obj.category)
            obj_kind_uid = ''
            obj_kind_name = self.unknown[self.GUI_lang_index]
            status = status_text[self.GUI_lang_index]
        else:
            obj_kind_uid = obj.kind.uid
            lang_name, comm_name, obj_kind_name, descr = \
                self.user_interface.Determine_name_in_context(obj.kind)
            status = 'unknown'
        is_a = ['is a ', 'is een ']
        form_text = ['Product form for:', 'Product formulier voor:']
        kind_text = ['Kind:', 'Soort:']
        descr_text = ['Description:', 'Omschrijving:']
        if len(obj.names_in_contexts) > 0:
            description = is_a[self.GUI_lang_index] + obj_kind_name \
                + '' + obj.names_in_contexts[0][4]
        else:
            description = is_a[self.GUI_lang_index] + obj_kind_name

        # Product name and kind (line_type = 1)
        prod_line_0 = [obj.uid, obj_kind_uid, '', 1,
                       form_text[self.GUI_lang_index], obj.name, '', '',
                       kind_text[self.GUI_lang_index], obj_kind_name, '', '', '', status]
        prod_line_1 = ['', '', '', 2, '', descr_text[self.GUI_lang_index], description,
                       '', '', '', '', '', '', '']
        # Intermediate header line (line_type = 3)
        prod_head_indiv = [['', '', '', 3, '', '', '', '', 'Aspect', 'Kind of aspect',
                            '>=<', 'Value', 'UoM', 'Status'],
                           ['', '', '', 3, '', '', '', '', 'Aspect', 'Soort aspect',
                            '>=<', 'Waarde', 'Eenheid', 'Status']]
        prod_head_kind = [['', '', '', 3, '', '', '', '', 'Kind of aspect', '',
                           '>=<', 'Value', 'UoM', 'Status'],
                          ['', '', '', 3, '', '', '', '', 'Soort aspect', '',
                           '>=<', 'Waarde', 'Eenheid', 'Status']]

        self.line_nr = 3
        # prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr, part,
        #                '', '', kindOfPart, aspect.name, kindOfAspect, value, UoM, status]
        # prod_line_4 = [part_of_part.uid, part_kind_uid, aspect_uid, self.line_nr, '',
        #                partOfPart, '', kindOfPart, aspect.name, kindOfAspect, value, UoM, status]
        # prod_line_5 = [occur_uid, occ_kind_uid, aspect_uid, self.line_nr, occur,
        #                '', '', kindOfOcc, aspect.name, kindOfAspect, value, UoM, status]
        # prod_line_6 = [inv_obj.uid, inv_kind_uid, aspect_uid, self.line_nr, '',
        #                invObject, role, kindOfInv, aspect.name, kindOfAspect, value, UoM, status]
        # prod_line_7 = [part_uid, part_kind_uid,aspect_uid, self.line_nr, '',
        #                '', '', '', aspect.name, kindOfAspect, value, UoM, status]
        # prod_line_8 = [obj.uid, obj_kind_uid, file_uid, self.line_nr, obj,
        #                document, '', kind_of_document, file, kind_of_file, '', '', status]

        if obj.category in self.kinds:
            self.kind_model.append(prod_line_0)
            if len(obj.supertypes) > 1:
                for super_type in obj.supertypes[1:]:
                    lang_name, comm_name, supert_type_name, descr = \
                        self.user_interface.Determine_name_in_context(super_type)
                    supertype_line = [obj.uid, super_type.uid, '', 1,
                                      '', '', '', '', '', supert_type_name]
                    # Debug print('supertype_line', supertype_line)
                    self.kind_model.append(supertype_line)
            self.kind_model.append(prod_line_1)
            self.kind_model.append(prod_head_kind[self.GUI_lang_index])
        else:
            # Category is individual
            self.prod_model.append(prod_line_0)
            # If there are several classifiers, then add a line per classifier
            if len(obj.classifiers) > 1:
                for classifier in obj.classifiers[1:]:
                    lang_name, comm_name, classifier_name, descr = \
                        self.user_interface.Determine_name_in_context(classifier)
                    self.prod_model.append([obj.uid, classifier.uid, '', 1,
                                            '', '', '', '', '', classifier_name])
            self.prod_model.append(prod_line_1)
            self.prod_model.append(prod_head_indiv[self.GUI_lang_index])

    def Find_aspects(self, indiv, role):
        """ Search for aspects of an individual thing (indiv)
            and their qualifications or quantifications.
            Store expressions in expr_table and relations in network model
            Store search results in lines in prod_model and summ_model and indiv_model
            indiv = the individual thing
            kind.name = the name of the kind of individual thing
            (for messages only)
            decomp_level = decomposition_level:
              0 = whole object, 1 = part, 2 = part of part, etc.
            categoryInFocus = category of the object in focus,
              being individual or phys object or occurrence
            The prod_model line_type is 3A: aspects of a product
              conform the header line for aspects (line type 3).
        """
        # Search for aspects and their values
        self.nr_of_aspects = 0  # nr of found aspects for this indiv object
        aspect_uid = ''
        aspect_name = ''
        equality = ''

        # Determine the kind that classifies the individual object
        # If the individual object is not classified
        # then the classifying kind is called 'unknown'
        if len(indiv.classifiers) == 0:
            indiv.kind_uid = ''
            indiv.kind_name = self.unknown_kind[self.GUI_lang_index]
        else:
            # Determine the preferred name of the first classifier of the individual object
            lang_name_cl, comm_name_cl, pref_cl_name, descr = \
                self.user_interface.Determine_name_in_context(indiv.classifiers[0])
            indiv.kind_uid = indiv.classifiers[0].uid
            indiv.kind_name = pref_cl_name

        for rel_obj in indiv.relations:
            expr = rel_obj.expression
            qualifier = None
            # Add each expression with an idea about the object in focus
            # to the expr_table
            if len(self.expr_table) < self.max_nr_of_rows \
               and expr not in self.expr_table:
                self.expr_table.append(expr)

            # Find possession of aspect relations (or its subtypes)
            if indiv.uid == expr[lh_uid_col] \
               and expr[rel_type_uid_col] in self.gel_net.subPossAspUIDs:
                if expr[phrase_type_uid_col] == basePhraseUID:
                    aspect_uid = expr[rh_uid_col]
                    qualifier = 'quantitative'
                else:
                    self.Display_message(
                        'The phrase type uid of idea {} is incompatible '
                        'with the expression.'.format(expr.uid),
                        'De uid van de soort frase van idee {} is niet compatibel '
                        'met de uitdrukking.'.format(expr.uid))
            # And for the inverse
            elif indiv.uid == expr[rh_uid_col] \
                    and expr[rel_type_uid_col] in self.gel_net.subPossAspUIDs:
                if expr[phrase_type_uid_col] == inversePhraseUID:
                    aspect_uid = expr[lh_uid_col]
                    qualifier = 'quantitative'
                else:
                    self.Display_message(
                        'The phrase type uid of idea {} is incompatible '
                        'with the expression.'.format(expr.uid),
                        'De uid van de soort frase van idee {} is niet compatibel '
                        'met de uitdrukking.'.format(expr.uid))
            else:
                # It is not a possession of (intrinsic) aspect relation,
                # thus search for possession of a qualitative aspect relations
                # and for an <is made of> relation
                if indiv.uid == expr[lh_uid_col] \
                        and expr[rel_type_uid_col] in ['5843', '5423']:
                    if expr[phrase_type_uid_col] == basePhraseUID:
                        aspect_uid = expr[rh_uid_col]
                        qualifier = 'qualitative'
                elif indiv.uid == expr[rh_uid_col] \
                        and expr[rel_type_uid_col] in ['5843', '5423']:
                    if expr[phrase_type_uid_col] == inversePhraseUID:
                        aspect_uid = expr[lh_uid_col]
                        qualifier = 'qualitative'
                else:
                    continue

            # An aspect is found or a qualitative aspect is found
            status = expr[status_col]
            self.nr_of_aspects += 1
            # Add a line to the network_model (derived from the expression)
            if indiv == self.object_in_focus:
                self.Add_line_to_network_model(indiv, rel_obj, expr)

            # Find the aspect object from its uid
            # being the aspect in the <has as aspect> relation
            # or the qualitative aspect in a qualification relation (such as <is made of>)
            aspect = self.uid_dict[aspect_uid]
            aspect_name = aspect.name

            # Determine the value of the aspect
            equality, value_name, uom_name, value_uid, uom_uid = \
                self.Determine_aspect_value(aspect, qualifier)

            # Verify if aspect has a known value
            if value_uid == '':
                value_name = self.unknown_val[self.GUI_lang_index]
                self.Display_message(
                    'Aspect {} ({}) has no value.'.
                    format(aspect_name, aspect_uid),
                    'Aspect {} ({}) heeft geen waarde.'.
                    format(aspect_name, aspect_uid))
            else:
                # Determine (in)equality symbol
                if expr[rel_type_uid_col] == '5026':
                    equality = '>'
                elif expr[rel_type_uid_col] == '5027':
                    equality = '<'
                elif expr[rel_type_uid_col] == '5489':
                    equality = '>='
                elif expr[rel_type_uid_col] == '5490':
                    equality = '<='

            # Store result in various models (display views)
            # Network_model and expr_table
            # If quantitative sspect value is found
            # then add expression to and expr_table
            if (qualifier == 'quantitative' or qualifier == 'quantitative') \
                    and value_name != self.unknown_val[self.GUI_lang_index]:
                if len(self.expr_table) < self.max_nr_of_rows \
                   and expr not in self.expr_table:
                    self.expr_table.append(expr)
                # Add aspect values to network model line (ToBeDone)
                # self.Add_line_to_network_model(indiv, rel_obj, expr)

            # Summary table (summ_model)
            #   A summary is a table for multiple individual things (not parts)
            #   with for each object (or product) one row of aspect values.
            #   The table has two header rows
            #   one with the kinds of aspects and another with the units of measure.

            # If the object is the object_in_focus and not one of its parts,
            # then collect the aspect in a summary_table.
            if self.decomp_level == 0:
                # Build summary_view table header
                # with list of kinds of aspects (summ_column_names)
                if aspect.kind_name not in self.summ_column_names \
                   and len(self.summ_column_names) <= 14:
                    self.summ_aspect_uids.append(aspect.kind_uid)
                    self.summ_column_names.append(aspect.kind_name)
                    self.summ_uom_names.append(uom_name)
                # Search in header row which column suits the aspect.kind_uid
                # Values start at position 4.
                self.summ_ind = 3
                for kind_uid in self.summ_aspect_uids[4:]:
                    self.summ_ind += + 1
                    # Build list of values conform list of aspects.
                    # Note: summary_row[0] = uid of indiv
                    if kind_uid == aspect.kind_uid:
                        # Debug print('Aspects of phys:', indiv.name, len(self.summ_aspect_uids),
                        #      aspect_name, aspect.kind_name, self.summ_ind, value_name)
                        # Add value_name to proper field in summary_row (in summ_model)
                        self.summary_row[self.summ_ind] = value_name
                        # Verify whether units of measure are identical
                        if uom_name != self.summ_uom_names[self.summ_ind]:
                            self.Display_message(
                                'The unit of measure {} ({}) of the value of {} differs '
                                'from summary table header UoM {}.'.
                                format(uom_name, uom_uid, aspect_name,
                                       self.summ_uom_names[self.summ_ind]),
                                'De meeteenheid {} ({}) van de waarde van {} verschilt '
                                'van de overzichtstabel kop_eenheid {}.'.
                                format(uom_name, uom_uid, aspect_name,
                                       self.summ_uom_names[self.summ_ind]))

            # If the object in focus is not a kind, then add aspect row to prod_model.
            if self.object_in_focus.category not in self.kinds:
                # indiv_tree
                # If the object is the object_in_focus and not one of its subtypes,
                # then collect the aspect in an indiv_row for insertion in a prod_model.
                if self.subtype_level == 0:
                    # Build individual_view table header with list of aspects
                    # (indiv_column_names)
                    # Debug print('Aspect kind', aspect.uid, aspect_name)
                    if aspect.kind_name not in self.indiv_column_names \
                       and len(self.indiv_column_names) <= 15:
                        self.indiv_aspect_uids.append(aspect.kind_uid)
                        self.indiv_column_names.append(aspect.kind_name)
                        self.indiv_uom_names.append(uom_name)
                    self.indiv_ind = 4
                    for kind_uid in self.indiv_aspect_uids[5:]:
                        self.indiv_ind += + 1
                        # Build list of values conform list of aspects.
                        # Note: summary_row[0] = uid of indiv
                        if aspect.kind_uid == kind_uid:
                            # Debug print('Aspects of phys:',
                            #      indiv.name, len(self.indiv_aspect_uids),
                            #      aspect_name, aspect.kind_name, self.indiv_ind, value_name)
                            # Add value_name to proper field in indiv_row
                            self.indiv_row[self.indiv_ind] = value_name
                            if uom_name != self.indiv_uom_names[self.indiv_ind]:
                                if uom_name == '':
                                    self.Display_message(
                                        'The unit of measure of the value of {} is missing.'.
                                        format(aspect_name),
                                        'De meeteenheid van de waarde van {} ontbreekt.'.
                                        format(aspect_name))
                                else:
                                    self.Display_message(
                                        'The unit of measure {} ({}) of the value of {} differs '
                                        'from the table header UoM {}.'.
                                        format(uom_name, uom_uid, aspect_name,
                                               self.indiv_uom_names[self.indiv_ind]),
                                        'De meeteenheid {} ({}) van de waarde van {} verschilt '
                                        'van de eenheid {} in de kop van de tabel.'.
                                        format(uom_name, uom_uid, aspect_name,
                                               self.indiv_uom_names[self.indiv_ind]))

                # Prod_model
                # Create prod_model text line for output view
                self.line_nr += 1
                # Debug print('Aspect of obj.:', self.decomp_level, self.nr_of_aspects,
                #             indiv.name, aspect_name)
                if self.decomp_level == 0 and self.nr_of_aspects == 1:
                    prod_line_3 = [indiv.uid, indiv.kind_uid, aspect_uid,
                                   self.line_nr, indiv.name, role, '', indiv.kind_name,
                                   aspect_name, aspect.kind_name, equality,
                                   value_name, uom_name, status]
                elif self.decomp_level == 1 and self.nr_of_aspects == 1:
                    prod_line_3 = [indiv.uid, indiv.kind_uid, aspect_uid,
                                   self.line_nr, indiv.name, role, '', indiv.kind_name,
                                   aspect_name, aspect.kind_name, equality,
                                   value_name, uom_name, status]
                elif self.decomp_level == 2 and self.nr_of_aspects == 1:
                    prod_line_3 = [indiv.uid, indiv.kind_uid, aspect_uid,
                                   self.line_nr, role, indiv.name, '', indiv.kind_name,
                                   aspect_name, aspect.kind_name, equality,
                                   value_name, uom_name, status]
                elif self.decomp_level == 3 and self.nr_of_aspects == 1:
                    prod_line_3 = [indiv.uid, indiv.kind_uid, aspect_uid,
                                   self.line_nr, '', role, indiv.name, indiv.kind_name,
                                   aspect_name, aspect.kind_name, equality,
                                   value_name, uom_name, status]
                else:
                    prod_line_3 = [indiv.uid, indiv.kind_uid, aspect_uid,
                                   self.line_nr, '', '', '', '',
                                   aspect_name, aspect.kind_name, equality,
                                   value_name, uom_name, status]
                if len(self.prod_model) < self.max_nr_of_rows:
                    # Debug print('Prod_line 3:', prod_line_3)
                    self.prod_model.append(prod_line_3)

        # If aspect is possessed by object_in_focus (thus not possessed by a part)
        # then add row to summ_model
        # Debug print('Indiv', self.decomp_level, indiv.name, self.summary_row)
        if self.decomp_level == 0:
            if len(self.summ_model) < self.max_nr_of_rows:
                if indiv not in self.summ_objects:
                    self.summ_objects.append(indiv)
                    # If summary row is about object in focus,
                    # then make parent of object in focus blank
                    # because treeview requires that parent is known or blank
                    if self.summary_row[0] == self.object_in_focus.uid:
                        self.summary_row[2] = ''
                    self.summ_model.append(self.summary_row[:])

            self.summary_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']

        # For whole and for parts of whole create a row in indiv_model (composition model)
        # Although not for an occurences and not when object in focus is a kind.
        if self.occ_in_focus != 'occurrence' \
                and self.object_in_focus.category not in self.kinds:
            if len(self.indiv_model) < self.max_nr_of_rows \
                    and indiv not in self.indiv_objects:
                self.indiv_objects.append(indiv)
                # If indiv row is about object in focus,
                # then make whole of object in focus blank
                # because treeview requires that whole is known or blank
                if self.indiv_row[0] == self.object_in_focus.uid:
                    self.indiv_row[2] = ''
                self.indiv_model.append(self.indiv_row[:])

        self.indiv_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
        return

    def Determine_aspect_value(self, aspect, qualifier):
        """ Determine the equality, value and unit of measure of the aspect object.
            And if found, then add expression to expr_table and network_model.
        """
        # Verify if the aspect of the individual object is classified
        # (thus no qualitative aspect found)
        if qualifier is 'quantitative':
            # Normal individual aspect found (not a qualitative aspect such as a substance)
            # aspect_name = aspect.name

            # Determine the kind that classifies the individual aspect
            if len(aspect.classifiers) == 0:
                aspect.kind_uid = ''
                aspect.kind_name = self.unknown_kind[self.GUI_lang_index]
            else:
                # Determine the preferred name of the first classifier
                # of the individual aspect
                # Debug print('Lang_prefs for classifier of aspect', self.reply_lang_pref_uids,
                #      aspect.classifiers[0].names_in_contexts)
                lang_name_as, comm_name_as, pref_kind_name, descr = \
                    self.user_interface.Determine_name_in_context(aspect.classifiers[0])
                aspect.kind_uid = aspect.classifiers[0].uid
                aspect.kind_name = pref_kind_name

            # Determine the value of the aspect
            value_uid = ''
            value_name = 'unknown'
            uom_uid = ''
            uom_name = ''
            equality = '='

            # Find the first qualification or quantification relation for the aspect
            for rel_obj in aspect.relations:
                expr = rel_obj.expression

                # Add expression to expr_table and to network_model
                if len(self.expr_table) < self.max_nr_of_rows \
                   and expr not in self.expr_table:
                    self.expr_table.append(expr)

                # Search for the first expression that qualifies or quantifies the aspect
                # by searching for the kinds of qualifying relations or their subtypes
                if aspect.uid == expr[lh_uid_col]:
                    if expr[rel_type_uid_col] in self.gel_net.subQualUIDs \
                       or expr[rel_type_uid_col] in self.gel_net.subQuantUIDs:
                        if len(self.expr_table) < self.max_nr_of_rows:
                            value_uid = expr[rh_uid_col]
                            value_name = expr[rh_name_col]
                            uom_uid = expr[uom_uid_col]
                            uom_name = expr[uom_name_col]
                    else:
                        continue
                elif aspect.uid == expr[rh_uid_col]:
                    if expr[rel_type_uid_col] in self.gel_net.subQualUIDs \
                       or expr[rel_type_uid_col] in self.gel_net.subQuantUIDs:
                        if len(self.expr_table) < self.max_nr_of_rows:
                            value_uid = expr[lh_uid_col]
                            value_name = expr[lh_name_col]
                            uom_uid = expr[uom_uid_col]
                            uom_name = expr[uom_name_col]
                    else:
                        continue
                else:
                    continue

                # If the found value_uid is not a whole number
                # or is outside the standard whole number range,
                #    then determine the value name in the preferred language
                #    (and in the preferred language community)
                # Debug print('Value', aspect_uid, value_uid, value_name, expr[0:25])
                numeric_uid, integer = Convert_numeric_to_integer(value_uid)
                if integer is False or numeric_uid not in range(1000000000, 3000000000):
                    value = self.uid_dict[value_uid]
                    lang_name, comm_name, value_name, descr = \
                        self.user_interface.Determine_name_in_context(value)

        elif qualifier is 'qualitative':
            # Qualitative aspect found (e.g. a substance such as PVC)
            equality = '='
            # Determine the first supertype of the qualitative aspect
            if len(aspect.supertypes) > 0:
                super_aspect = aspect.supertypes[0]
            # super_aspect = self.uid_dict['431771']     # subtance or stuff
            lang_name, comm_name, pref_kind_name, descr = \
                self.user_interface.Determine_name_in_context(super_aspect)
            aspect.kind_name = pref_kind_name
            aspect.kind_uid = super_aspect.uid  # '431771'
            value_uid = aspect.uid
            # Determine preferred name of qualitative value
            lang_name, comm_name, value_name, descr = \
                self.user_interface.Determine_name_in_context(aspect)
            uom_uid = ''
            uom_name = ''

        return equality, value_name, uom_name, value_uid, uom_uid

    def Find_information_about_object(self, obj):
        """ Search for information and files about the object obj
            (kind or individual)
            (and its supertypes?) and build info_model.
            - info_row('values') =
                [info.uid, obj.uid, carrier.uid, directory_name,
                 info.name, super_info_name, obj.name,
                 carrier.name, carrier_kind_name].
        """
        # obj_head = ['Object', 'Object']
        info_head = ['Document', 'Document']
        dir_head = ['Directory', 'Directory']
        kind_of_doc_head = ['Kind', 'Soort']
        file_head = ['File', 'File']
        kind_of_file_head = ['Kinf of file', 'Soort file']
        # status_head = ['Status', 'Status']
        descr_avail_text = ['Description available',
                            'Omschrijving beschikbaar']
        info_header = True

        for rel_obj in obj.relations:
            expr = rel_obj.expression
            # Verify whether object <is a kind that is described by> (5620) information
            #                       <is described by information>    (1273) information
            if expr[rel_type_uid_col] in ['5620', '1911', '5631', '1273']:
                if expr[lh_uid_col] == obj.uid:
                    info_uid = expr[rh_uid_col]
                elif expr[rh_uid_col] == obj.uid:
                    info_uid = expr[lh_uid_col]
                else:
                    continue

                # Information is identified.
                info = self.uid_dict[info_uid]
                # Create header line_type 8 info,
                # only the first time for prod_model or kind_model
                if obj == self.object_in_focus and info_header:
                    self.line_nr += 1
                    prod_head_8 = ['', '', '', self.line_nr,
                                   info_head[self.GUI_lang_index],
                                   dir_head[self.GUI_lang_index], '',
                                   kind_of_doc_head[self.GUI_lang_index],
                                   file_head[self.GUI_lang_index],
                                   kind_of_file_head[self.GUI_lang_index], '', '', '', '']
                    #               status_head[self.GUI_lang_index]]
                    # Debug print('obj.cat', obj.category)
                    if obj.category in self.kinds:
                        self.kind_model.append(prod_head_8)
                    else:
                        self.prod_model.append(prod_head_8)
                    info_header = False

                # Add line about info to expr_table and to netwerk_model
                self.expr_table.append(expr)
                if obj == self.object_in_focus:
                    self.Add_line_to_network_model(obj, rel_obj, expr)
                # Determine the name of the supertype of info
                # and verify if info is presented on a carrier.
                # And store full description of the info
                qualified = False
                presented = False
                super_info_uid = ''
                super_info_name = self.unknown[self.GUI_lang_index]
                info.description = ''
                for rel_info in info.relations:
                    info_expr = rel_info.expression
                    info_status = info_expr[status_col]
                    # Determine the qualifier of the info (its supertype)
                    if info_expr[rel_type_uid_col] in self.gel_net.specialRelUIDs:
                        super_info_uid = info_expr[rh_uid_col]
                        super_info_name = info_expr[rh_name_col]
                        info.description = info_expr[full_def_col]
                        qualified = True
                        self.expr_table.append(info_expr)

                    # Verify whether info <is presented on> (4996) physical object
                    # (typically an electronic data file)
                    # or info <is presented on at least one of> (5627)
                    # collection of physical objects
                    elif info_expr[rel_type_uid_col] in ['4996', '5627']:
                        if info_expr[lh_uid_col] == info.uid:
                            carrier_uid = info_expr[rh_uid_col]
                        elif info_expr[rh_uid_col] == info.uid:
                            carrier_uid = info_expr[lh_uid_col]
                        else:
                            continue

                        # Info is presented on a carrier
                        presented = True
                        self.expr_table.append(info_expr)
                        # self.Add_line_to_network_model(info, rel_info, info_expr)

                        carrier = self.uid_dict[carrier_uid]
                        if len(carrier.classifiers) > 0:
                            carrier_kind_name = carrier.classifiers[0].name
                        else:
                            carrier_kind_name = self.unknown[self.GUI_lang_index]

                        # Find directory where carrier file is located
                        directory_name = ''
                        for rel_carrier in carrier.relations:
                            car_expr = rel_carrier.expression
                            # Verify whether the carrier <is an element of> (1227) directory
                            if car_expr[rel_type_uid_col] == '1227':
                                if car_expr[lh_uid_col] == carrier.uid:
                                    directory_uid = car_expr[rh_uid_col]
                                elif info_expr[rh_uid_col] == carrier.uid:
                                    directory_uid = car_expr[lh_uid_col]
                                else:
                                    continue
                                # Directory for carrier is found
                                directory = self.uid_dict[directory_uid]
                                self.expr_table.append(car_expr)
                                # self.Add_line_to_network_model(carrier, rel_carrier, car_expr)
                                directory_name = directory.name

                        if directory_name == '':
                            self.Display_message(
                                'The name of the directory for file {} is unknown.'.
                                format(carrier.name),
                                'De naam van de directory voor file {} is onbekend.'.
                                format(carrier.name))

                        # Store info about object in info_model
                        # Debug print('Carrier {} is located on directory {}.'.
                        #      format(carrier.name, directory_name))
                        info_row = [info.uid, obj.uid, carrier.uid, directory_name,
                                    info.name, super_info_name, directory_name, obj.name,
                                    carrier.name, carrier_kind_name]
                        self.info_model.append(info_row)

                        # Store info about object in prod_model or kind_model
                        if obj == self.object_in_focus:
                            self.line_nr += + 1
                            prod_line_8 = [info.uid, super_info_uid, carrier.uid, self.line_nr,
                                           info.name, directory_name, '',
                                           super_info_name, carrier.name, carrier_kind_name,
                                           '', '', '', info_status]
                            if obj.category in self.kinds:
                                self.kind_model.append(prod_line_8)
                            else:
                                self.prod_model.append(prod_line_8)

                if qualified is False:
                    self.Display_message(
                        'A qualification relation for information {} is missing.'.
                        format(info.name),
                        'Een kwalificatierelatie voor {} ontbreekt.'.
                        format(info.name))

                # If info is not presented on a carrier then store text
                if presented is False:
                    # Store info (text) about object in info_model
                    info_row = [info.uid, obj.uid, info.description, '',
                                info.name, super_info_name, '', obj.name, '',
                                descr_avail_text[self.GUI_lang_index], '', '']
                    self.info_model.append(info_row)

                    # Store info about object in prod_model or kind_model
                    if obj == self.object_in_focus:
                        self.line_nr += + 1
                        prod_line_8 = [info.uid, super_info_uid, obj.uid, self.line_nr,
                                       info.name, '', '',
                                       super_info_name, '', '', '', '', '', info_status]
                        if obj.category in self.kinds:
                            self.kind_model.append(prod_line_8)
                        else:
                            self.prod_model.append(prod_line_8)

    def Find_parts_and_their_aspects(self, obj):
        """ Search for parts of individual object obj
            (and their aspects) in expr_table.
            Store results in prod_model or occ_model.
        """
        part2_head = ['Part of part', 'Deel van deel']
        part3_head = ['Further part', 'Verder deel']
        kind_head = ['Kind', 'Soort']

        # self.coll_of_subtype_uids = []
        self.nr_of_parts = 0
        self.decomp_level += 1
        if self.decomp_level > 3:
            self.decomp_level += -1
            return
        # Debug print('Indentation_level of parts of:', self.decomp_level, name,obj.uid)

        # Search for <has as part> relation or any of its subtypes
        part_uid = ''
        for rel_obj in obj.relations:
            expr = rel_obj.expression
            if expr[rel_type_uid_col] in self.gel_net.subComposUIDs:
                if expr not in self.expr_table:
                    self.expr_table.append(expr)
                    # Debug print('Rel_obj-parts', rel_obj.lh_obj.uid, rel_obj.lh_obj.name,
                    #      rel_obj.rel_type.base_phrases[0], rel_obj.rh_obj.name)
                    if obj == self.object_in_focus:
                        self.Add_line_to_network_model(obj, rel_obj, expr)

                # If base phrase <is a part of> and right hand is the object in focus
                # then lh is a part
                if expr[phrase_type_uid_col] == basePhraseUID:
                    if obj.uid == expr[rh_uid_col]:
                        part_uid = expr[lh_uid_col]

                # If inverse phrase <has as part> and left hand is the object in focus
                # then rh is a part
                elif expr[phrase_type_uid_col] == inversePhraseUID:
                    if obj.uid == expr[lh_uid_col]:
                        part_uid = expr[rh_uid_col]
                else:
                    self.Display_message(
                        'The uid of the phrase type {} is incorrect'.
                        format(expr[phrase_type_uid_col]),
                        'De uid van de soort frase {} is niet correct'.
                        format(expr[phrase_type_uid_col]))
                    continue

                if part_uid != '':
                    # There is an explicit part found; create part_header, prod_head_4,
                    # the first time only
                    if self.part_head_req is True:
                        self.line_nr += 1
                        prod_head_4 = ['', '', '', self.line_nr,
                                       self.comp_head[self.GUI_lang_index],
                                       part2_head[self.GUI_lang_index],
                                       part3_head[self.GUI_lang_index],
                                       kind_head[self.GUI_lang_index], '', '', '', '', '']
                        if len(self.prod_model) < self.max_nr_of_rows:
                            # Header of part list
                            self.prod_model.append(prod_head_4)
                        self.part_head_req = False
                    part = self.uid_dict[part_uid]

                    status = expr[status_col]

                    # Verify if the classification of the part is known
                    if len(part.classifiers) == 0:
                        part_kind_uid = ''
                        part_kind_name = self.unknown_kind[self.GUI_lang_index]
                    else:
                        part_kind_uid = part.classifiers[0].uid
                        # Determine name etc. of the kind that classifies the part
                        if len(part.classifiers[0].names_in_contexts) > 0:
                            # Debug print('Part classifier names', self.reply_lang_pref_uids,
                            #      part.classifiers[0].names_in_contexts)
                            lang_name, comm_name, part_kind_name, descrOfKind = \
                                self.user_interface.Determine_name_in_context(part.classifiers[0])
                        else:
                            part_kind_name = part.classifiers[0].name
                            # Debug print('Part_classifier_name', part_kind_name)
                            # comm_name = self.unknown[self.GUI_lang_index]

                    # Determine the preferred name of the part
                    if len(part.names_in_contexts) > 0:
                        lang_name, community_name, part_name, descrOfKind = \
                            self.user_interface.Determine_name_in_context(part)
                    else:
                        part_name = part.name
                        community_name = self.unknown[self.GUI_lang_index]
                        self.Display_message(
                            'Part {} has no defined name for its language community.'.
                            format(part.name),
                            'Deel {} heeft geen gedefinieerde naam van zijn taalgemeenschap.'.
                            format(part.name))

                    # indiv_model = obj.uid, obj.name, whole_name, kind_name, community_name
                    self.indiv_row[0] = part.uid
                    self.indiv_row[1] = part_name
                    self.indiv_row[2] = obj.name
                    self.indiv_row[3] = part_kind_name
                    self.indiv_row[4] = community_name
                    # self.coll_of_subtype_uids.append(part.uid)

                    # Search for aspects of part
                    role = ''
                    self.Find_aspects(part, role)

                    # if no aspects of part found, record part only (in prod_model)
                    if self.nr_of_aspects == 0:
                        self.line_nr += + 1
                        if self.decomp_level == 1:
                            prod_line_4 = [part.uid, part_kind_uid, '',
                                           self.line_nr, part.name, '', '',
                                           part_kind_name, '', '', '', '', '', status]
                        elif self.decomp_level == 2:
                            prod_line_4 = [part.uid, part_kind_uid, '',
                                           self.line_nr, '', part.name, '',
                                           part_kind_name, '', '', '', '', '', status]
                        elif self.decomp_level == 3:
                            prod_line_4 = [part.uid, part_kind_uid, '',
                                           self.line_nr, '', '', part.name,
                                           part_kind_name, '', '', '', '', '', status]
                        if self.decomp_level < 4:
                            if len(self.prod_model) < self.max_nr_of_rows:
                                self.prod_model.append(prod_line_4)

                    # Search for parts of part and their aspects
                    self.Find_parts_and_their_aspects(part)

        self.decomp_level += -1

    def Find_kinds_of_aspects(self, obj, role):
        """ Search for kinds of aspects that can/shall or are by definition possessed
            by a kind of thing (obj)
            and search for their qualitative subtypes
            and possible collection of allowed values.
            obj = the kind in focus or its part
            role = the role played by an involved object that is involved in an occurrence
            decomp_level = decomposition level:
                           0 = whole object, 1 = part, 2 = part of part, etc.
            obj.category = category of the object,
                here being kind, kind of phys object or kind of occurrence.
        """
        # unknown_super = ['unknown supertype', 'onbekend supertype']
        # noValuesText = ['No specification', 'Geen specificatie']
        self.has_as_subtypes = ['has as subtypes', 'heeft als subtypes']

        # Collect all relations in expr_table
        # and include line in network_model view
        for rel_obj in obj.relations:
                expr = rel_obj.expression
                if len(self.expr_table) < self.max_nr_of_rows and expr not in self.expr_table:
                    self.expr_table.append(expr)

        # Search for expressions that are <can have as aspect a> kind of relation
        # or subtypes of that kind of relation
        # with the obj.uid (or its supertypes) at left or at right.

        # Initialize number of kinds of aspects that are possessed by this kind of object
        self.nr_of_aspects = 0
        value_name = ''
        aspect_uid = ''
        aspect_name = ''
        uom_uid = ''
        uom_name = ''
        equality = ''
        status = ''

        # Determine preferred obj name
        if len(obj.names_in_contexts) > 0:
            lang_name, comm_name, obj_name, descr = \
                self.user_interface.Determine_name_in_context(obj)
        else:
            obj_name = obj.name

        # Collect list of obj and its supertypes in the complete hierarchy
        # for searching inherited aspects
        all_supers = self.Determine_supertypes(obj)

        # For each object in the hierarchy find aspects and inherited aspect values
        # that are inherited from its supertype objects but exclude the roles
        for obj_i in all_supers:
            value_presence = False
            for rel_obj in obj_i.relations:
                expr = rel_obj.expression
                # Find expression with poss_of_aspect relations about the object
                # (or its supertype)
                if expr[lh_uid_col] == obj_i.uid \
                        and (expr[rel_type_uid_col] in self.gel_net.subConcPossAspUIDs
                             and not expr[rel_type_uid_col] in self.gel_net.conc_playing_uids):
                    aspect_uid = expr[rh_uid_col]
                    aspect_name = expr[rh_name_col]
                    role_uid = expr[rh_role_uid_col]
                    # role_name = expr[rh_role_name_col]
                elif expr[rh_uid_col] == obj_i.uid \
                        and (expr[rel_type_uid_col] in self.gel_net.subConcPossAspUIDs
                             and not expr[rel_type_uid_col] in self.gel_net.conc_playing_uids):
                    aspect_uid = expr[lh_uid_col]
                    aspect_name = expr[lh_name_col]
                    role_uid = expr[lh_role_uid_col]
                    # role_name = expr[lh_role_name_col]
                else:
                    continue

                # There is a kind of aspect found.
                # Add a line to the network model and to other models when applicable
                # Debug print('Found kind of aspect:', obj_i.name, aspect_name,
                #       expr[lh_uid_col:rh_name_col + 1])
                if obj_i == self.object_in_focus:
                    self.Add_line_to_network_model(obj_i, rel_obj, expr)
                self.nr_of_aspects += 1

                status = expr[status_col]
                role_name = ''
                equality = '='
                value_uid = ''
                value_name = ''
                uom_uid = ''
                uom_name = ''
                value_presence = False

                # Search for values/constraints for the kind of aspect
                # Therefore, find a rh_role object (intrinsic aspect)
                # of the <can have as aspect a> relation.
                if role_uid != '':
                    role = self.uid_dict[role_uid]
                    role_name = role.name

                    # Find collection of allowed values
                    # or other criterion, constraints or value for intrinsic aspect, if any.
                    for rel_obj2 in role.relations:
                        expr2 = rel_obj2.expression
                        # Find collection of qualitative aspects for intrinsic aspect (=role),
                        # if any.
                        if role_uid == expr2[lh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.qualOptionsUIDs:
                            value_uid = expr2[rh_uid_col]   # collection of allowed values
                            value_name = expr2[rh_name_col]
                            value_presence = True
                            break
                        elif role_uid == expr2[rh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.qualOptionsUIDs:
                            value_uid = expr2[lh_uid_col]   # collection of allowed values
                            value_name = expr2[lh_name_col]
                            value_presence = True
                            break

                        # Find conceptual compliancy criterion, (4951)
                        # for intrinsic aspect (=role), if any.
                        elif role_uid == expr2[lh_uid_col] \
                                and expr2[lh_role_uid_col] in self.gel_net.concComplUIDs:
                            value_uid = expr2[rh_uid_col]   # compliancy criterion or constraint
                            value_name = expr2[rh_name_col]
                            value_presence = True
                            break
                        elif role_uid == expr2[rh_uid_col] \
                                and expr2[rh_role_uid_col] in self.gel_net.concComplUIDs:
                            value_uid = expr2[lh_uid_col]   # compliancy criterion or constraint
                            value_name = expr2[lh_name_col]
                            value_presence = True
                            break

                        # Find conceptual quantification (1791) for intrinsic aspect (=role),
                        # if any.
                        elif role_uid == expr2[lh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs:
                            value_uid = expr2[rh_uid_col]   # value (on a scale)
                            value_name = expr2[rh_name_col]
                            uom_uid = expr2[uom_uid_col]
                            uom_name = expr2[uom_name_col]
                            value_presence = True
                            break
                        elif role_uid == expr2[rh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs:
                            value_uid = expr2[lh_uid_col]   # value (on a scale)
                            value_name = expr2[lh_name_col]
                            uom_uid = expr2[uom_uid_col]
                            uom_name = expr2[uom_name_col]
                            value_presence = True
                            break

                        # Find conceptual compliance criterion/qualif (4902)
                        # for intrinsic aspect (=role), if any.
                        elif role_uid == expr2[lh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.subConcComplRelUIDs:
                            # Compliance criterion or def qualification
                            value_uid = expr2[rh_uid_col]
                            value_name = expr2[rh_name_col]
                            value_presence = True
                            break
                        elif role_uid == expr2[rh_uid_col] \
                                and expr2[rel_type_uid_col] in self.gel_net.subConcComplRelUIDs:
                            # Compliance criterion or def qualification
                            value_uid = expr2[lh_uid_col]
                            value_name = expr2[lh_name_col]
                            value_presence = True
                            break

                # Determine preferred names for aspect, aspect_supertype, and value
                # Preferred aspect name
                asp = self.uid_dict[aspect_uid]
                if len(asp.names_in_contexts) > 0:
                    lang_name, comm_name, aspect_name, descr = \
                        self.user_interface.Determine_name_in_context(asp)
                else:
                    aspect_name = asp.name

                # Preferred supertype name
                if len(asp.supertypes) > 0:
                    if len(asp.supertypes[0].names_in_contexts) > 0:
                        lang_name, comm_name, asp_supertype_name, descr = \
                            self.user_interface.Determine_name_in_context(asp.supertypes[0])
                    else:
                        asp_supertype_name = asp.supertypes[0].name
                else:
                    asp_supertype_name = self.unknown[self.GUI_lang_index]

                # Preferred value name
                if value_uid != '':
                    value = self.uid_dict[value_uid]
                    lang_name, comm_name, value_name, descr = \
                        self.user_interface.Determine_name_in_context(value)
                else:
                    value_name = ''

                # If subtype_level == 0 (the obj is object in focus or its part)
                # then create a row in the possibilities_model
                #   for any decomp_level
                if self.subtype_level == 0:
                    self.Add_row_to_poss_model(obj, obj_name, aspect_name,
                                               asp_supertype_name, value_name, uom_name)

                # Debug print('obj_i', value_presence, obj_i.name, self.nr_of_aspects, aspect_name,
                #       value_name, len(self.taxon_aspect_uids))

                if value_presence is True:
                    # Debug print('Value present:', obj_i.name, aspect_name, value_name)
                    if len(self.expr_table) < self.max_nr_of_rows:
                        self.expr_table.append(expr2)
                        # The value and uom are added to the aspect line in the network_model
                        # self.Add_line_to_network_model(asp, rel_obj2, expr2)
                        # *** ToBeDone

                    if self.decomp_level == 0:
                        # Build taxon view header add a column for aspects if not yet included
                        if value_presence is True \
                           and aspect_name not in self.taxon_column_names \
                           and len(self.taxon_column_names) <= 14:
                            # Debug print('Summm_header', aspect_name, len(self.taxon_aspect_uids))
                            self.taxon_aspect_uids.append(aspect_uid)
                            self.taxon_column_names.append(aspect_name)
                            self.taxon_uom_names.append(uom_name)
                        self.taxon_ind = 3
                        # Debug print('Sums:',len(self.taxon_aspect_uids), self.taxon_aspect_uids,
                        #      self.taxon_column_names, value_name)
                        # Find column in taxon_row where value should be stored
                        for kind_uid in self.taxon_aspect_uids[4:]:
                            self.taxon_ind += + 1
                            # Build list of values conform list of aspects.
                            if kind_uid == aspect_uid:
                                # Debug print('Aspects of phys:',len(self.taxon_aspect_uids),
                                #       aspect_name, self.taxon_ind, value_name)
                                self.taxon_row[self.taxon_ind] = value_name
                                # Check whether there the uom corresponds with the table uom
                                # (when there is a value)
                                if value_name != '' \
                                   and uom_name != self.taxon_uom_names[self.taxon_ind]:
                                    self.Display_message(
                                        'Unit of measure {} ({}) of the value of {} differs'
                                        'from taxon table header UoM {}'.
                                        format(uom_name, uom_uid, aspect_name,
                                               self.taxon_uom_names[self.taxon_ind]),
                                        'Meeteenheid {} ({}) van de waarde van {} verschilt'
                                        'van de taxonomietabel kop_eenheid {}'.
                                        format(uom_name, uom_uid, aspect_name,
                                               self.taxon_uom_names[self.taxon_ind]))

                # Add a line of Line_type 3 to kind_model
                # if not a subtype of object in focus (subtype_level == 0)
                # Debug print('Kind model-3:', self.subtype_level, self.decomp_level,
                #       self.nr_of_aspects, obj.name, aspect_name)
                if self.subtype_level == 0:
                    if len(obj.supertypes) > 0:
                        supertype_uid = obj.supertypes[0].uid
                        supertype_name = obj.supertypes[0].name
                    else:
                        supertype_uid = ''
                        supertype_name = self.unknown_kind[self.GUI_lang_index]
                    self.Add_line_type3_to_kind_model(
                        obj_i.uid, supertype_uid, aspect_uid,
                        obj.name, role_name, supertype_name, aspect_name,
                        equality, value_name, uom_name, status)

                # Determine implied part if any
                # by determining whether the possessed aspect is an intrinsic aspect, because
                # rel_type is a <has by definition as intrinsic aspect a> relation (6149)
                # or its subtype
                # If that is the case, then it implies that
                #    there is an implied part of the object in focus that possesses the aspect
                if expr[rel_type_uid_col] in ['6149', '5848']:
                    # Determine the implied part and its possessed aspect
                    # from the definition of the intrinsic aspect
                    intr_aspect = self.uid_dict[aspect_uid]
                    part_uid = ''
                    part_name = 'undefined'
                    asp_of_part_uid = ''
                    asp_of_part_name = 'undefined'
                    for rel_asp in intr_aspect.relations:
                        expr_asp = rel_asp.expression

                        # If lh_uid is the kind of intr_aspect
                        # and rel_type is <is by definition an intrinsic aspect of a> (5738)
                        # then rh_obj is the kind of part  (and inverse)
                        if expr_asp[lh_uid_col] == aspect_uid \
                                and expr_asp[rel_type_uid_col] == '5738':
                            part_uid = expr_asp[rh_uid_col]
                            part_name = expr_asp[rh_name_col]
                        elif expr_asp[rh_uid_col] == aspect_uid \
                                and expr_asp[rel_type_uid_col] == '5738':
                            part_uid = expr_asp[lh_uid_col]
                            part_name = expr_asp[lh_name_col]

                        # If lh_uid is the kind of intr_aspect
                        # and rel_type is <is by definition an intrinsic> (5817)
                        # then rh_obj is the kind of aspect of the kind of part  (and inverse)
                        if expr_asp[lh_uid_col] == aspect_uid \
                                and expr_asp[rel_type_uid_col] == '5817':
                            asp_of_part_uid = expr_asp[rh_uid_col]
                            asp_of_part_name = expr_asp[rh_name_col]
                        if expr_asp[rh_uid_col] == aspect_uid \
                                and expr_asp[rel_type_uid_col] == '5817':
                            asp_of_part_uid = expr_asp[lh_uid_col]
                            asp_of_part_name = expr_asp[lh_name_col]

                    # Debug print('Whole {} has implied part ({}) {} '
                    #      'identified with aspect ({}) {}.'.
                    #      format(obj.name, part_uid, part_name,
                    #             asp_of_part_uid, asp_of_part_name))
                    key = (part_uid, asp_of_part_uid)
                    self.implied_parts_dict[key] = (part_name, asp_of_part_uid,
                                                    asp_of_part_name,
                                                    equality, value_name, uom_name, status)

        #        if obj.category == 'kind of occurrence':
        #            # Build list of kinds of aspects (occ_column_names) for OccView
        #            if aspect.kind not in self.occ_kinds:
        #                nrOfAspOccKinds = nrOfAspOccKinds + 1
        #                self.occ_aspects[nrOfAspOccKinds] = aspect_name
        #                self.occ_kinds  [nrOfAspOccKinds] = aspect.kind
        #                self.occ_uoms   [nrOfAspOccKinds] = uom_name
        #                self.taxon_ind = 3
        #                for kind_name in self.occ_kinds[4:]:
        #                    self.taxon_ind += 1
        #                    # Build list of values conform list of aspects.
        #                    # Note: sumRow[0] = component
        #                    if aspect.kind == kind_name:
        #                        # Debug print('Aspects of occ :', nrOfAspOccKinds, aspect_name,
        #                               aspect.kind, self.taxon_ind, value_name)
        #                        occRow[self.taxon_ind] = value_name
        #                        if uom_name != self.occ_uoms[self.taxon_ind]:
        #        # If not a kind of occurrence, then build header for summaryTable
        #        elif self.decomp_level == 0:

    def Add_row_to_poss_model(self, obj, obj_name, aspect_name,
                              asp_supertype_name, value_name, uom_name):
        ''' Create and add a row for possible characteristics of part.
            Add a header row only preceding the first aspect (self.nr_of_aspects == 1).
        '''
        possible_aspect_text = ['possible characteristic of a ',
                                'mogelijk kenmerk van een ']
        of_text = [' (of ', ' (van ']
        # Add a header row above the first aspect
        if self.nr_of_aspects == 1:
            self.poss_asp_of_obj_text = \
                possible_aspect_text[self.GUI_lang_index] + obj_name
            self.possibility_row[0] = obj.uid
            self.possibility_row[1] = obj_name
            self.possibility_row[2] = self.poss_asp_of_obj_text
            self.possibility_row[3] = obj_name  # parent
            self.possibilities_model.append(self.possibility_row[:])

        # Add a row for the aspect and its possible value and unit of measure
        if len(self.possibilities_model) < self.max_nr_of_rows:
            if len(obj.names_in_contexts) > 0:
                # The community uid == obj.names_in_contexts[0][1]
                community_name = \
                    self.gel_net.community_dict[obj.names_in_contexts[0][1]]
            else:
                community_name = self.unknown[self.GUI_lang_index]
            self.possibility_row[0] = obj.uid
            self.possibility_row[1] = aspect_name
            self.possibility_row[2] = \
                aspect_name + of_text[self.GUI_lang_index] + obj_name + ')'
            self.possibility_row[3] = self.poss_asp_of_obj_text
            # Debug print('Aspect:', obj_name, asp.uid, aspect_name, value_name)
            self.possibility_row[4] = asp_supertype_name
            self.possibility_row[5] = community_name  # of obj
            self.possibility_row[6] = value_name
            self.possibility_row[7] = uom_name
            if self.possibility_row not in self.possibilities_model:
                self.possibilities_model.append(self.possibility_row[:])
            else:
                print('Duplicate possibility row', len(self.possibilities_model),
                      self.possibility_row)
            self.possibility_row = \
                ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

    def Add_row_to_taxonomy(self, obj):
        ''' For an obj (object_in_focus) (thus not a part)
            create a row in taxon_model
            Taxon_model: uid, name, preferred name of super, comm, aspect values
                     or: uid, 'has as subtypes', name, blank.
        '''
        # Debug print('Tax aspects:', self.taxon_hierarchy[obj], self.subtype_level,
        #             obj.name, self.taxon_row)
        if len(obj.supertypes) > 0:
            # Create a row in the taxonomy per direct supertype
            for supertype in obj.supertypes:
                lang_name, comm_name_super, preferred_name, descr = \
                    self.user_interface.Determine_name_in_context(supertype)
                self.taxon_row[2] = preferred_name  # of the supertype
                if len(self.taxon_model) < self.max_nr_of_rows:
                    # If taxon row is about object in focus,
                    # then make supertype of object in focus empty
                    # Because treeview parent (taxon_row[2] should be supertype or blank.
                    # Debug print('Subtype_level-1:', self.subtype_level,
                    #      self.object_in_focus.uid,
                    #      self.object_in_focus.name, obj.uid, obj.name, self.taxon_row[0:4])
                    if self.taxon_row[0] == self.object_in_focus.uid:
                        self.taxon_row[2] = ''
                        self.taxon_model.append(self.taxon_row[:])
                    # Debug print('Super-1:', self.taxon_hierarchy[obj], self.subtype_level,
                    #       supertype.name, self.object_in_focus.name, self.taxon_row[0:6])

                    # If the object is not a subtype of the object_in_focus,
                    # then insert an inter_row header line for the subtypes
                    if self.taxon_hierarchy[obj] == 0:
                        has_as_subs_uid = '1146'
                        rel_obj = self.uid_dict[has_as_subs_uid]
                        self.taxon_hierarchy[rel_obj] = 1
                        inter_row = [has_as_subs_uid,
                                     self.has_as_subtypes[self.GUI_lang_index],
                                     obj.name, '']
                        self.taxon_model.append(inter_row)

                    # If taxon_row[2] (the 'supertype name') is the object_in_focus.name,
                    # then make the object a sub of the inter_row
                    else:
                        if self.taxon_row[2] == self.object_in_focus.name:
                            self.taxon_row[2] = self.has_as_subtypes[self.GUI_lang_index]
                        self.taxon_model.append(self.taxon_row[:])
        else:
            # The obj (object in focus) has no defined supertype(s)
            self.taxon_row[2] = ''  # self.unknown[self.GUI_lang_index]
            self.taxon_model.append(self.taxon_row[:])
            # If the object is not a subtype of the object_in_focus,
            # then insert an inter_row header line for the subtypes
            if self.subtype_level == 0:
                inter_row = [obj.uid,
                             self.has_as_subtypes[self.GUI_lang_index],
                             obj.name, '']
                self.taxon_model.append(inter_row)

        self.taxon_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']

    def Determine_preferred_kind_name(self, obj):
        """ Determine the preferred name of the first kind that classifies obj
            or the name of the first supertype of obj.
        """
        kind = None
        if len(obj.classifiers) > 0:
            kind = obj.classifiers[0]
        elif len(obj.supertypes) > 0:
            kind = obj.supertypes[0]
        if kind is not None:
            lang_name, comm_name, kind_name, full_def = \
                self.user_interface.Determine_name_in_context(kind)
            kind_uid = kind.uid
        else:
            kind_uid = self.unknown[self.GUI_lang_index]
            kind_name = self.unknown_kind[self.GUI_lang_index]
        return kind_name, kind_uid

    def Determine_supertypes(self, obj):
        """ Collect a list of obj and its supertypes, including super_supers, etc."""
        all_supers = []
        direct_supers = obj.supertypes
        if len(direct_supers) > 0:
            for super_d in direct_supers:
                if super_d not in all_supers:
                    all_supers.append(super_d)
            for super_i in all_supers:
                super_supers = super_i.supertypes
                if len(super_supers) > 0:
                    for super_super in super_supers:
                        if super_super not in all_supers:
                            all_supers.append(super_super)
        all_supers.append(obj)
        return all_supers

    def Find_kinds_of_parts_and_their_aspects(self, obj):
        """ Search for explicit kinds of parts of obj
            and combine them with implied kinds of parts.
            decomp_level (composition_level): 0=whole, 1=part, 2=part_of_part, etc.
        """
        part2_head = ['Part of part', 'Deel van deel']
        part3_head = ['Further part', 'Verder deel']
        super_head = ['Supertype', 'Supertype']
        of_text = [' (of ', ' (van ']

        role = ''
        self.part_head_req = True
        # Search for kinds of parts of object_in_focus
        for rel_obj in obj.relations:
                expr = rel_obj.expression
                if expr[lh_uid_col] == obj.uid \
                   and expr[rel_type_uid_col] in self.gel_net.subConcComposUIDs \
                   and expr[phrase_type_uid_col] == '1986':
                    part_uid = expr[rh_uid_col]
                    part_name = expr[rh_name_col]
                    # role_uid = expr[rh_role_uid_col]
                    # role_name = expr[rh_role_name_col]
                elif expr[rh_uid_col] == obj.uid \
                        and expr[rel_type_uid_col] in self.gel_net.subConcComposUIDs \
                        and expr[phrase_type_uid_col] == '6066':
                    part_uid = expr[lh_uid_col]
                    part_name = expr[lh_name_col]
                    # role_uid = expr[lh_role_uid_col]
                    # role_name = expr[lh_role_name_col]
                else:
                    continue

                # There is an explicit kind of part found (part_uid);
                # create part_header in kind_model, the first time only
                # Debug print('Kind of part', part_name)
                self.decomp_level += 1
                if self.subtype_level == 0:
                    if self.part_head_req is True:
                        self.line_nr += 1
                        prod_head_4 = ['', '', '', self.line_nr,
                                       self.comp_head[self.GUI_lang_index],
                                       part2_head[self.GUI_lang_index],
                                       part3_head[self.GUI_lang_index],
                                       super_head[self.GUI_lang_index], '', '', '', '', '', '']
                        if len(self.kind_model) < self.max_nr_of_rows:
                            # Add header of part to kind_model
                            self.kind_model.append(prod_head_4)
                        self.part_head_req = False

                # Add the compostion expression to the expr_table table and network_model
                if len(self.expr_table) < self.max_nr_of_rows:
                    self.expr_table.append(expr)
                    if obj == self.object_in_focus:
                        self.Add_line_to_network_model(obj, rel_obj, expr)

                # Determine preferred name of object (= kind)
                if len(obj.names_in_contexts) > 0:
                    lang_name, community_name, obj_name, descr_of_obj = \
                        self.user_interface.Determine_name_in_context(obj)
                else:
                    obj_name = obj.name

                # Determine preferred name of (kind of) part
                part = self.uid_dict[part_uid]
                if len(part.names_in_contexts) > 0:
                    lang_name, community_name, part_name, descr_of_part = \
                        self.user_interface.Determine_name_in_context(part)
                else:
                    part_name = part.name
                    community_name = self.unknown[self.GUI_lang_index]

                # Determine preferred name of first supertype of part
                if len(part.supertypes) > 0:
                    if len(part.supertypes[0].names_in_contexts) > 0:
                        lang_name, comm_kind_name, part_kind_name, descr_of_kind = \
                            self.user_interface.Determine_name_in_context(part.supertypes[0])
                    else:
                        part_kind_name = part.supertypes[0].name
                else:
                    part_kind_name = self.unknown_kind[self.GUI_lang_index]
                    if part.category == 'anything':
                        part.category = 'kind'

                # Create row about possible kind of part in possibilities_model
                self.possibility_row[0] = part.uid
                self.possibility_row[1] = part_name
                self.possibility_row[2] = \
                    part_name + of_text[self.GUI_lang_index] + obj_name + ')'
                self.possibility_row[3] = obj_name  # parent
                self.possibility_row[4] = part_kind_name
                self.possibility_row[5] = community_name  # of part
                # Add possibility for part to possibilities_model
                if self.possibility_row not in self.possibilities_model:
                    self.possibilities_model.append(self.possibility_row[:])

                # Search for aspects of the kind of part
                self.Find_kinds_of_aspects(part, role)
                if self.nr_of_aspects > 0:
                    # Verify consistency between aspect values and implied aspect values.
                    # === to be completed ===

                    # Debug print('*** Nr of aspects to be verified', self.nr_of_aspects)
                    # Verify whether there are implied parts with aspect values
                    if len(self.implied_parts_dict) > 0:
                        for key, implied_tuple in self.implied_parts_dict:
                            if part.uid == key[0]:
                                self.Display_message(
                                    'Object ({}) {} has part ({}) {}'
                                    'with implied aspect ({}) {}.'.
                                    format(obj.uid, obj.names_in_contexts[0][2], key[0],
                                           implied_tuple(0), implied_tuple(1),
                                           implied_tuple(2)),
                                    'Object ({}) {} heeft als deel ({}) {}'
                                    'met als geïmpliceerd aspect ({}) {}.'.
                                    format(obj.uid, obj.names_in_contexts[0][2], key[0],
                                           implied_tuple(0), implied_tuple(1),
                                           implied_tuple(2)))
                                del self.implied_parts_dict[key]
                self.decomp_level += -1

        # If there are implied kinds of parts left, then create kind_model lines.
        if self.subtype_level == 0 and len(self.implied_parts_dict) > 0:
            # Debug print('Nr of implied parts', len(self.implied_parts_dict))

            # There is an implied part left.
            # Thus create a part_header in the kind_model,
            # the first time only
            if self.part_head_req is True:
                self.line_nr += 1
                # Define the header of the part list
                prod_head_4 = ['', '', '', self.line_nr,
                               self.comp_head[self.GUI_lang_index],
                               part2_head[self.GUI_lang_index],
                               part3_head[self.GUI_lang_index],
                               super_head[self.GUI_lang_index], '', '', '', '', '']
                if len(self.kind_model) < self.max_nr_of_rows:
                    self.kind_model.append(prod_head_4)
                self.part_head_req = False

            # Create kind_model line(s) for implied part(s)
            self.decomp_level += 1
            for key, implied_tuple in self.implied_parts_dict.items():
                self.nr_of_aspects = 1
                part_name = implied_tuple[0]
                if len(self.uid_dict[key[0]].supertypes) > 0:
                    part_kind_uid = self.uid_dict[key[0]].supertypes[0].uid
                    part_kind_name = self.uid_dict[key[0]].supertypes[0].name
                else:
                    part_kind_uid = ''
                    part_kind_name = 'kind'
                aspect_name = implied_tuple[2]
                equality = implied_tuple[3]
                value_name = implied_tuple[4]
                uom_name = implied_tuple[5]
                status = 'implied'
                # subtype_of_part_level = 0

                if self.subtype_level == 0:
                    self.Add_line_type3_to_kind_model(
                        key[0], part_kind_uid, implied_tuple[1],
                        part_name, role, part_kind_name, aspect_name,
                        equality, value_name, uom_name, status)
            self.decomp_level += -1

    def Add_line_type3_to_kind_model(self, part_uid, part_kind_uid, aspect_uid,
                                     part_name, role, part_kind_name,
                                     aspect_name, equality, value_name, uom_name, status):
        """ Create a line_type 3 for kind model view."""
        self.line_nr += 1
        # Decomp_level = 0 means whole object, 1 means: part (2 = part of part, etc.)
        if self.decomp_level == 1 and self.nr_of_aspects <= 1:
            prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr,
                           part_name, role, '', part_kind_name, aspect_name, '', equality,
                           value_name, uom_name, status]
        # Decomp_level = 2 means: part of part
        elif self.decomp_level == 2 and self.nr_of_aspects == 1:
            prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr,
                           role, part_name, '', part_kind_name, aspect_name, '', equality,
                           value_name, uom_name, status]
        elif self.decomp_level == 3 and self.nr_of_aspects == 1:
            prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr,
                           '', role, part_name, part_kind_name, aspect_name, '', equality,
                           value_name, uom_name, status]
##        # Subtype_level > 0 means: subtype
##        elif subtype_level > 0 and self.nr_of_aspects == 1:
##            prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr,
##                           part_name, role, '', part_kind_name, aspect_name, '', equality,
##                           value_name, uom_name, status]
        else:
            prod_line_3 = [part_uid, part_kind_uid, aspect_uid, self.line_nr,
                           '', '', '', '', aspect_name, '', equality,
                           value_name, uom_name, status]

        if len(self.kind_model) < self.max_nr_of_rows:
            self.kind_model.append(prod_line_3)

    def Determine_individuals(self, obj):
        """ Determine whether a kind_in_focus (obj) or one of its subtypes
            is a classifier for individual things.
            If so, then add the individual things to taxonomy (taxon_model) of kinds.
            Also search for aspects of the individual thing and,
            if found, add them as a row to summ_model.
        """
        has_as_individuals = ['classifies as individual ',
                              'classificeert als individuele ']
        first_time = True

        for rel_obj in obj.relations:
            expr = rel_obj.expression
            # Find a classification relation for the kind_in_focus
            if expr[rel_type_uid_col] in self.gel_net.sub_classif_uids:

                # Find the individual object that is classified
                if expr[lh_uid_col] == obj.uid:
                    indiv_uid = expr[rh_uid_col]
                elif expr[rh_uid_col] == obj.uid:
                    indiv_uid = expr[lh_uid_col]
                else:
                    continue

                # Individual thing uid is found via classification relation.
                # Store the expression in the expr_table for display and possible export
                # and add a line to the network_model
                if len(self.expr_table) < self.max_nr_of_rows:
                    self.expr_table.append(expr)
                    # self.Add_line_to_network_model(obj, rel_obj, expr)

                # Set level in the hierarchy two higher because of classif relation
                indiv = self.uid_dict[indiv_uid]
                self.taxon_hierarchy[indiv] = self.taxon_hierarchy[obj] + 1

                # Find aspects of the individual thing, if any
                # and add them to summary table.
                # Do not add aspects to a prod_model because
                # the object in focus is a kind.
                community_name = self.gel_net.community_dict[indiv.names_in_contexts[0][1]]
                self.summary_row[0] = indiv.uid
                self.summary_row[1] = indiv.name
                self.summary_row[2] = indiv.classifiers[0].name
                self.summary_row[3] = community_name

                role = ''
                self.Find_aspects(indiv, role)

                # Insert an intermediate inter_row header for classified individual things
                # in the taxonomy; the first time only
                if first_time is True:
                    has_as_ind_uid = '1225'
                    classif = self.uid_dict[has_as_ind_uid]
                    header_text = has_as_individuals[self.GUI_lang_index] + obj.name
                    inter_row = [has_as_ind_uid, header_text, obj.name, '']
                    self.taxon_model.append(inter_row)
                    self.taxon_hierarchy[classif] = self.taxon_hierarchy[obj] + 1
                    first_time = False

                # Create a row in the taxonomy for an individual thing
                # under the header for individual things
                lang_name, community_name, preferred_name, descr = \
                    self.user_interface.Determine_name_in_context(indiv)
                self.taxon_row[0] = indiv.uid
                self.taxon_row[1] = preferred_name
                self.taxon_row[2] = header_text
                self.taxon_row[3] = community_name

                self.taxon_model.append(self.taxon_row[:])
                self.taxon_row = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']

    def Occurs_and_involvs(self, obj):
        """ Search for occurrences in which the obj (in focus) is involved.
            The occurrences are related with an involver role
            or one of its subtypes to the (physical) object_in_focus
            and search for (physical) objects
            that are involved in those occurrences in various roles.
            Search for aspects of the occurrences (such as duration).
            Store results in prod_model and the composition in partWholeOcc.
        """
        occur_head = ['Occurrences', 'Gebeurtenissen']
        role_head = ['Role', 'Rol']
        involv_head = ['Involved object', 'Betrokken object']
        kind_head = ['Kind', 'Soort']
        # Debug print('**** Occurs_and_involvs:',obj.uid, obj.name, obj.category)

        nr_of_occur = 0
        self.occ_in_focus = 'no'
        self.line_nr += + 1

        # Search for occurences (involver role players)
        # via UID and <involved> role or its subtypes
        for rel_obj in obj.relations:
            expr = rel_obj.expression
            if (expr[rh_uid_col] == obj.uid
                    and expr[rel_type_uid_col] in self.gel_net.subInvolvUIDs):
                occ_uid = expr[lh_uid_col]
                # occ_name = expr[lh_name_col]
            elif expr[lh_uid_col] == obj.uid \
                    and expr[rel_type_uid_col] in self.gel_net.subInvolvUIDs:
                occ_uid = expr[rh_uid_col]
                # occ_name = expr[rh_name_col]
            else:
                continue

            # An occurrence is found
            nr_of_occur += 1
            occ = self.uid_dict[occ_uid]
            occ_name = occ.name
            self.decomp_level = 1  # An occurence has the same level effect as a part
            # Debug print('Occ     :',obj.name, occ_uid, occ_name, 'roles:',
            #      expr[rel_type_name_col], expr[lh_role_name_col], expr[rh_role_name_col])

            # Display occurrences header, only the first time
            if nr_of_occur == 1:
                prod_head_5 = ['', '', '', self.line_nr,
                               occur_head[self.GUI_lang_index], role_head[self.GUI_lang_index],
                               involv_head[self.GUI_lang_index], kind_head[self.GUI_lang_index],
                               '', '', '', '', '']
                self.prod_model.append(prod_head_5)

            # Add occurence that involves object to expr_table and network model
            if len(self.expr_table) < self.max_nr_of_rows:
                self.expr_table.append(expr)
                if obj == self.object_in_focus:
                    self.Add_line_to_network_model(obj, rel_obj, expr)

            # Record the role playing occurrence in occ_model
            # Find classifying kind of occurrence
            if len(occ.classifiers) > 0:
                occ_kind = occ.classifiers[0]
                occ_kind_name = occ_kind.name
                occ_kind_uid = occ_kind.uid
            else:
                self.Display_message(
                    'Occurrence {} classifier is unknown.'.format(occ.name),
                    'Gebeurtenis {} classificeerder is onbekend.'.format(occ.name))
                occ_kind_name = self.unknown[self.GUI_lang_index]
                occ_kind_uid = ''

            self.occ_model.append([occ.uid, occ.name, '', '', occ_kind_uid,
                                   occ.name, '', '', occ_kind_name, ''])
            # Debug print('Occ-3:',[nr_of_occur, occ.name, occ_uid, occ_kind_name])

            status = expr[status_col]
            occ_role = ''
            self.occ_in_focus = 'occurrence'
            # Find possession of aspect relations for aspects of occurrence
            self.Find_aspects(occ, occ_role)

            # If no aspects found then line without aspects
            # (otherwise line is included in Find_aspects
            if self.nr_of_aspects == 0:
                self.line_nr += + 1
                prod_line_5 = [occ.uid, occ_kind.uid, '',
                               self.line_nr, occ_name, '', '',
                               occ_kind_name, '', '', '', '', '', status]
                self.prod_model.append(prod_line_5)

            # Search for objects that are involved in the found occurrence
            # decomp_level determines print layout in product model.
            self.decomp_level = 3
            for rel_occ in occ.relations:
                expr_occ = rel_occ.expression
                # Search <is involved in> or <is involving>
                # or any of its subtypes relations in occ
                # excluding the object in focus (obj)
                if expr_occ[rh_uid_col] != obj.uid \
                        and (expr_occ[lh_uid_col] == occ.uid
                             and expr_occ[rel_type_uid_col] in self.gel_net.subInvolvUIDs):
                    involved_uid = expr_occ[rh_uid_col]
                    # involved_name = expr_occ[rh_name_col]
                    inv_role_name = expr_occ[rh_role_name_col]
                elif expr_occ[lh_uid_col] != obj.uid \
                        and (expr_occ[rh_uid_col] == occ.uid
                             and expr_occ[rel_type_uid_col] in self.gel_net.subInvolvUIDs):
                    involved_uid = expr_occ[lh_uid_col]
                    # involved_name = expr_occ[lh_name_col]
                    inv_role_name = expr_occ[lh_role_name_col]
                else:
                    continue

                # An object is found that is involved in the occurrence
                involved = self.uid_dict[involved_uid]
                # Debug print('Involved:',obj.uid, involved.uid, involved.name,
                #      'roles:',expr_occ[lh_role_uid_col],expr_occ[rh_role_uid_col])

                self.expr_table.append(expr_occ)
                # self.Add_line_to_network_model(occ, rel_occ, expr_occ)
                status = expr_occ[status_col]

                # Determine the kind of the involved individual object
                if len(involved.classifiers) > 0:
                    involved_kind = involved.classifiers[0]
                    involved_kind_name = involved_kind.name
                else:
                    self.Display_message(
                        'The involved object {} has no classifier.'.
                        format(involved.name),
                        'Het betrokken object {} heeft geen classificeerder.'.
                        format(involved.name))
                    involved_kind_name = self.unknown[self.GUI_lang_index]

                # Search for aspects of objects that are involved in occurrence
                # Find possession of aspect relations of involved object
                self.Find_aspects(involved, inv_role_name)

                # if no aspects of part found, then record part only
                if self.nr_of_aspects == 0:
                    self.line_nr += + 1
                    prod_line_6 = [involved.uid, involved_kind.uid, '',
                                   self.line_nr, '', inv_role_name, involved.name,
                                   involved_kind_name, '', '', '', '', '', status]
                    self.prod_model.append(prod_line_6)

            # Search for successors or predecessors of found occurrence
            #   with inputs and outputs and parts (? see below)
            self.Determine_sequences_of_occurrences(occ)

            # Search for parts of found occurrence and parts of parts, etc.
            occ_part_level = 1
            self.Determine_parts_of_occur(occ, occ_part_level)
        self.decomp_level = 0

    def Determine_sequences_of_occurrences(self, occ):
        """ Build occurrences (activities or processes or events)
            and their components
            with sequences between the occurrences and between components
            in the seq_table and inputs and outputs in involv_table.
            seq_table: previus_obj, next_obj.
            involv_table: occur_obj, involved_obj, role_obj (of invObj), invKindName.
            p_occ_table: whole_obj, part_obj, kindOfPartName.
        """
        # Debug print('Determine_sequences_of_occurrences',occ.uid, occ.name)
        # part_uids = []
        nr_of_sequences = 0
        nr_of_ins_and_outs = 0
        # nr_of_parts = 0
        # Build sequence table (seq_table) for sequence of occurrences
        for rel_occ in occ.relations:
            expr = rel_occ.expression
            # Search for predecessor - successor relations
            if expr[rh_uid_col] == occ.uid and expr[rh_role_uid_col] in self.gel_net.subNextUIDs:
                predecessor = self.uid_dict[expr[lh_uid_col]]
                self.seq_table.append([predecessor, occ])
                nr_of_sequences += 1
            # And for the inverse expressions
            elif expr[lh_uid_col] == occ.uid and expr[lh_role_uid_col] in self.gel_net.subNextUIDs:
                predecessor = self.uid_dict[expr[rh_uid_col]]
                self.seq_table.append([predecessor, occ])
                nr_of_sequences += 1

            # Search for inputs and outputs (streams) in involv_table
            elif expr[lh_uid_col] == occ.uid \
                    and expr[rel_type_uid_col] in self.gel_net.subInvolvUIDs:
                involved = self.uid_dict[expr[rh_uid_col]]
                if len(involved.classifiers) > 0:
                    inv_kind_name = involved.classifiers[0].name
                else:
                    inv_kind_name = self.unknown[self.GUI_lang_index]
                rel_type = self.uid_dict[expr[rel_type_uid_col]]
                inv_role_kind = rel_type.second_role

                self.involv_table.append([occ, involved, inv_role_kind, inv_kind_name])
                nr_of_ins_and_outs += 1

            # Search for inverse relation
            elif expr[rh_uid_col] == occ.uid \
                    and expr[rel_type_uid_col] in self.gel_net.subInvolvUIDs:
                involved = self.uid_dict[expr[lh_uid_col]]
                if len(involved.classifiers) > 0:
                    inv_kind_name = involved.classifiers[0].name
                else:
                    inv_kind_name = self.unknown[self.GUI_lang_index]
                rel_type = self.uid_dict[expr[rel_type_uid_col]]
                inv_role_kind = rel_type.second_role

                self.involv_table.append([occ, involved, inv_role_kind, inv_kind_name])
                nr_of_ins_and_outs += 1

        if len(occ.parts) > 0:
            # Determine sequences, IOs and parts of parts
            for part_occ in occ.parts:
                self.Determine_sequences_of_occurrences(part_occ)

    def Determine_parts_of_occur(self, occ, occ_part_level):
        """ Determine whole-parts hierarchy for occurrences
            Store results in prod_model.
        """
        parts = False
        part_head = ['Part occurrence', 'Deelgebeurtenis']
        kind_part_head = ['Kind of part', 'Soort deel']
        for rel_occ in occ.relations:
            expr = rel_occ.expression
            if expr[lh_uid_col] == occ.uid \
               and expr[rel_type_uid_col] in self.gel_net.subComposUIDs:
                # A part occurrence is found
                # Create header line, only after finding a part the first time
                if parts is False:
                    self.line_nr += + 1
                    prod_line_7 = ['', '', '', self.line_nr, '',
                                   part_head[self.GUI_lang_index],
                                   '', kind_part_head[self.GUI_lang_index],
                                   '', '', '', '', '', '']
                    self.prod_model.append(prod_line_7)
                    parts = True
                part_occ = self.uid_dict[expr[rh_uid_col]]
                status = expr[status_col]

                self.expr_table.append(expr)
                # self.Add_line_to_network_model(occ, rel_occ, expr)

                if len(part_occ.classifiers) > 0:
                    kind_part_occ = part_occ.classifiers[0]
                    kind_part_occ_uid = kind_part_occ.uid
                    kind_part_occ_name = kind_part_occ.name
                else:
                    self.Display_message(
                        'The part of occurrnce {} has no classifier'.
                        format(part_occ.name),
                        'De deelgebeurtenis {} heeft geen classificeerder'.
                        format(part_occ.name))
                    kind_part_occ = self.unknown[self.GUI_lang_index]
                    kind_part_occ_uid = '0'
                    kind_part_occ_name = self.unknown[self.GUI_lang_index]

                if occ_part_level < 2:
                    self.line_nr += + 1
                    prod_line_8 = [part_occ.uid, kind_part_occ_uid, '', self.line_nr, '',
                                   part_occ.name, '',
                                   kind_part_occ_name, '', '', '', '', '', status
                                   ]
                    self.prod_model.append(prod_line_8)
                    self.nr_of_occurrencies += + 1
                    involv_uid = ''
                    role_of_involved = ''
                    self.occ_model.append([part_occ.uid, part_occ.name, occ.name, involv_uid,
                                           kind_part_occ_uid, '', part_occ.name, '',
                                           kind_part_occ_name, role_of_involved])

                # Add whole, part and kind of part occurrence to part_whole_occs hierarchy
                self.part_whole_occs.append([occ, part_occ, kind_part_occ])

                # Search for part on next decomposition level (part_of_part of occurrence)
                part_level = occ_part_level + 1
                self.Determine_parts_of_occur(part_occ, part_level)

    def Display_notebook_views(self):
        """ For each non-empty model define and display a view in a notebook tab."""
        # Define and display Network view sheet
        if len(self.network_model) > 0:
            self.Define_and_display_network()

        # Define and display Taxonomic view sheet for kinds of products
        if len(self.taxon_model) > 0:
            self.Define_and_display_taxonomy_of_kinds()

        # Define and display Possibilities_view sheet of kind
        # if len(self.possibilities_model) > 0:
        #     self.Define_and_display_possibilities_of_kind()

        # Define and display model of kind
        if len(self.kind_model) > 0:
            self.Define_and_display_kind_view()

        # Define and display summary_view sheet for individual products
        if len(self.summ_model) > 0:
            self.Define_and_display_summary_sheet()

        # Define and display individual_view sheet for composition based view
        if len(self.indiv_model) > 0:
            self.Define_and_display_individual_model()

        # Define and display product_model_sheet view
        if len(self.prod_model) > 0:
            self.Define_and_display_product_model_view()

        # Define and display data_sheet view
        if len(self.prod_model) > 0:
            self.Define_and_display_data_sheet()

        # Activities view
        if len(self.occ_model) > 0:
            self.Define_and_display_activity_view()

        # Define and display Documents_view sheet
        if len(self.info_model) > 0:
            self.Define_and_display_documents()

        # Define and Display Expression sheet view
        if len(self.expr_table) > 0:
            self.Define_and_display_expressions_view()

    def Display_message(self, text_en, text_nl):
        if self.GUI_lang_index == 1:
            self.user_interface.log_messages.append(text_nl)
        else:
            self.user_interface.log_messages.append(text_en)

    def Define_and_display_network(self):
        """ Define a network view and
            display the network of relations about the concept in focus.
        """
        # Destroy earlier network_frame
        try:
            self.user_interface.views_noteb.remove_child(self.network_tree)
        except AttributeError:
            pass

        self.Define_network_view()

        self.Display_network_view()

    def Define_network_view(self):
        """ Define a network sheet for display of network_model (a list of network rows)
            for display in a tab of Notebook.
        """
        network_text = ['Network of ', 'Netwerk van ']
        self.network_name = network_text[self.GUI_lang_index] + self.object_in_focus.name
        self.network_frame = gui.VBox(width='100%', height='80%',
                                      style={'overflow': 'auto',
                                             'background-color': '#eeffdd'})
        self.user_interface.views_noteb.add_tab(self.network_frame,
                                                self.network_name, self.tab_cb(self.network_name))

        net_button_text = ['Display network of left object', 'Toon netwerk van linker object']
        lh_button_text = ['Display details of left object', 'Toon details van linker object']
        rh_button_text = ['Display details of kind', 'Toon details van soort']
        classif_button_text = ['Classify left individual object',
                               'Classificeer linker individueel object']
        self.close_button_text = ['Close', 'Sluit']

        self.network_button_row = gui.HBox(height=20, width='100%')

        self.net_button = gui.Button(net_button_text[self.GUI_lang_index], width='20%', height=20)
        self.net_button.attributes['title'] = 'Press button after selection of left hand object'
        self.net_button.onclick.connect(self.Prepare_lh_object_network_view)

        self.lh_button = gui.Button(lh_button_text[self.GUI_lang_index], width='20%', height=20)
        self.lh_button.attributes['title'] = 'Press button after selection of left hand object'
        self.lh_button.onclick.connect(self.Prepare_lh_network_object_detail_view)

        self.rh_button = gui.Button(rh_button_text[self.GUI_lang_index], width='15%', height=20)
        self.rh_button.attributes['title'] = 'Press button after selection of right hand object'
        self.rh_button.onclick.connect(self.Prepare_rh_network_object_detail_view)

        self.classif_button = gui.Button(classif_button_text[self.GUI_lang_index],
                                         width='20%', height=20)
        self.classif_button.attributes['title'] = \
            'Press button after selection of left hand individual object'
        self.classif_button.onclick.connect(self.Prepare_for_classification)

        self.close_network = gui.Button(self.close_button_text[self.GUI_lang_index],
                                        width='15%', height=20)
        self.close_network.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_network.onclick.connect(
            self.user_interface.Close_tag,
            self.user_interface.views_noteb,
            self.network_name)

        self.network_button_row.append(self.net_button)
        self.network_button_row.append(self.lh_button)
        self.network_button_row.append(self.rh_button)
        self.network_button_row.append(self.classif_button)
        self.network_button_row.append(self.close_network)
        self.network_frame.append(self.network_button_row)

        self.network_tree = TreeTable(
            width='100%',
            style={'overflow': 'scroll', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        # Add a table heading row
        eqal_head = ['>=<', '>=<']
        valu_head = ['Value', 'Waarde']
        unit_head = ['Unit', 'Eenheid']
        content = [(self.name_head[self.GUI_lang_index],
                    self.parent_head[self.GUI_lang_index],
                    self.kind_head[self.GUI_lang_index],
                    eqal_head[self.GUI_lang_index],
                    valu_head[self.GUI_lang_index],
                    unit_head[self.GUI_lang_index])]
        self.network_tree.append_from_list(content, fill_title=True)
        self.network_tree.on_table_row_click.connect(self.Determine_table_row_values)
        # self.network_tree.on_table_row_click.connect(self.Prepare_network_object_detail_view)
        self.network_frame.append(self.network_tree)

    def tab_cb(self, tab_name):
        self.user_interface.views_noteb.select_by_name(tab_name)

    def Determine_table_row_values(self, widget, row, item):
        ''' Determine the values in the row that is selected in the table.'''
        self.row_widgets = list(row.children.values())
        self.row_values = []
        if len(self.row_widgets) > 0:
            for widget in self.row_widgets:
                self.row_values.append(widget.get_text())
        print('Selected row values:', self.row_values)

    def Display_network_view(self):
        """ Display a network of all related things
            that are directly related to the object in focus in a gui.TreeView.
            network_model = related_uid, focus_uid, focus_name, phrase, related_name,
                            kind_uid, related_name, focus_name, kind_name.
        """
        # Display self.network_model rows in self.network_tree TreeView
        parent_uids = []
        remembered_name = ''
        sub_level = 0
        parent_text = ['has', 'heeft', 'classifies', 'classificeert',
                       'is', 'can', 'kan', 'shall', 'moet']
        widget_dict = {}  # key, value = name, widget
        # Initialize the list of included names of things
        # included = []
        for network_line in self.network_model:
            child_uid = network_line[0]
            # child = self.uid_dict[child_uid]
            # Verify whether the parent_uid (network_line[1]),
            # is blank or is in the list of parents.
            # Determine whether hierarchy of sub_sub concepts shall be open or not
            openness = 'false'
            parent_uid = network_line[1]
            if parent_uid == '':
                target_level = 0
            else:
                parent = self.uid_dict[parent_uid]
                target_level = self.net_hierarchy[parent] + 1
            child_name = network_line[6]
            parent_name = network_line[7]
            # Debug print('sub-target-pre:', sub_level, target_level,
            #       parent_uid, parent_name, child_uid, child_name)
            if parent_uid == '' or parent_uid in parent_uids:
                if parent_uid == self.object_in_focus.uid:
                    parent_uids.append(parent_uid)
                    openness = 'true'
                relation = False
                color = '#ffff99'
                # Indentation
                # If child_name starts with a term that denotes a relation
                # then store parent name and indent
                term_in_name = child_name.partition(' ')
                if term_in_name[0] in parent_text:
                    remembered_name = parent_name
                    relation = True
                    color = '#eeffdd'
                    openness = 'true'
                    self.network_tree.begin_fold()
                    sub_level += 1
                elif sub_level > 0 and target_level > sub_level:
                    self.network_tree.begin_fold()
                    sub_level += 1
                if target_level < sub_level:
                    while target_level < sub_level:
                        sub_level += -1
                        self.network_tree.end_fold()
                # Debug print('sub-target-post:', sub_level, target_level,
                #       parent_uid, parent_name, child_uid, child_name)

                net_row_widget = gui.TableRow()
                net_row_widget.attributes['treeopen'] = openness
                widget_dict[child_name] = net_row_widget
                if relation is False and parent_name != '':
                    net_row_widget.uid = network_line[0]
                for index, field in enumerate(network_line[6:]):
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': color})
                    if relation is False:
                        # If row is not a relation while parent is a relation name
                        # then replace relation name with remembered parent name
                        strings = field.partition(' ')
                        if strings[0] in parent_text:
                            row_item = gui.TableItem(text=remembered_name,
                                                     style={'text-align': 'left',
                                                            'background-color': color})
                        net_row_widget.append(row_item, field)
                    elif index < 1:
                        # Relation line: only the first field to be displayed
                        net_row_widget.append(row_item, field)
                    if index == 0:
                        row_item.uid = network_line[0]
                self.network_tree.append(net_row_widget, child_name)
                if child_uid not in parent_uids:
                    parent_uids.append(child_uid)
            else:
                # Parent not in parents
                print('Parent name "{}" does not appear in network'.format(parent_name))

    def Define_and_display_taxonomy_of_kinds(self):
        # Destroy earlier taxon_frame
        try:
            self.taxon_frame.destroy()
        except AttributeError:
            pass

        self.Define_taxonomy_sheet()

        self.Display_taxonomy_view()

    def Define_taxonomy_sheet(self):
        """ Define a taxonomy sheet for display of taxon_model (a list of taxon_rows)
            for display in a tab of Notebook.
        """
        taxon_text = ['Taxonomy', 'Taxonomie']
        self.taxon_name = taxon_text[self.GUI_lang_index] + ' of ' + self.object_in_focus.name
        self.taxon_frame = gui.VBox(width='100%', height='100%',
                                    style='background-color:#eeffdd')
        self.user_interface.views_noteb.add_tab(self.taxon_frame,
                                                self.taxon_name, self.tab_cb(self.taxon_name))
        self.taxon_button_row = gui.HBox(height=20, width='100%')

        detail_text = ['Object details', 'Objectdetails']
        self.taxon_detail = gui.Button(detail_text[self.GUI_lang_index],
                                       width='15%', height=20)
        self.taxon_detail.attributes['title'] = 'Show details of selected left hand item'
        self.taxon_detail.onclick.connect(self.Taxon_detail_view)

        # Request for classification of the earlier selected individual thing
        classify_button_text = ['Classify', 'Classificeer']
        self.taxon_classify = gui.Button(classify_button_text[self.GUI_lang_index],
                                         width='15%', height=20)
        self.taxon_classify.attributes['title'] = 'Classify earlier selected individual ' \
                                                  'by the selected kind'
        self.taxon_classify.onclick.connect(self.Classify_individual)

        self.taxon_close = gui.Button(self.close_button_text[self.GUI_lang_index],
                                      width='15%', height=20)
        self.taxon_close.attributes['title'] = 'Press button when you want to remove this tag'
        self.taxon_close.onclick.connect(self.user_interface.Close_tag,
                                         self.user_interface.views_noteb,
                                         self.taxon_name)

        self.taxon_button_row.append(self.taxon_detail)
        self.taxon_button_row.append(self.taxon_classify)
        self.taxon_button_row.append(self.taxon_close)
        self.taxon_frame.append(self.taxon_button_row)

        self.taxon_tree = TreeTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#ddffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        taxon_headings = [['Name', 'Kind', 'Community'],
                          ['Naam', 'Soort', 'Gemeenschap']]
        # nr_of_cols = len(self.taxon_column_names)
        self.taxon_column_names[1:4] = taxon_headings[self.GUI_lang_index]
        taxon_heads = []
        taxon_heads.append(tuple(self.taxon_column_names[1:]))
        self.taxon_tree.append_from_list(taxon_heads, fill_title=True)
        self.taxon_tree.on_table_row_click.connect(self.Determine_table_row_values)
        # self.taxon_tree.on_table_row_click.connect(self.Prepare_network_object_detail_view)
        self.taxon_frame.append(self.taxon_tree)

        # Display header row with units of measure
        uom_color = '#ccf'
        name = 'uom'
        taxon_row_widget = gui.TableRow()
        for index, field in enumerate(self.taxon_uom_names[1:]):
            taxon_row_item = gui.TableItem(text=field,
                                           style={'text-align': 'left',
                                                  'background-color': uom_color})
            taxon_row_widget.append(taxon_row_item, field)
        self.taxon_tree.append(taxon_row_widget, name)

    def Display_taxonomy_view(self):
        """ Display a treeview with the taxonomy of the kind in focus
            including also aspect values of the kind and its subtypes.
            Taxon_model: uid, name, name_of_super, comm, aspect values
                     or: uid, 'has as subtypes', name_of_super, blank.
        """
        # Display self.taxon_model rows in self.taxon_tree
        parents = []
        parent = ''
        sub_level = 0
        nr_of_cols = len(self.taxon_column_names)
        super_texts = ['has', 'heeft', 'classifies', 'classificeert']
        for taxon_line in self.taxon_model:
            uid = taxon_line[0]
            obj = self.uid_dict[uid]
            target_level = self.taxon_hierarchy[obj] + 1
            # Debug print('Taxon_model:', sub_level, target_level, taxon_line)
            name_of_super = taxon_line[2]
            # Debug print('Taxon_line', taxon_line)
            # If the supertype name (taxon_line[2]) is blank or in the list of parents,
            # then display the line
            if name_of_super == '' or name_of_super in parents:
                # Skip duplicates
                # if self.taxon_tree.exists(taxon_line[1]):
                #     continue
                # else:
                name = taxon_line[1]
                relation = False
                color = '#ddffdd'  # light green
                term = name.partition(' ')
                # Debug print('Tax:', sub_level, name, name_of_super, parents)
                # Indentation:
                # If name denotes a 'has as subtypes' or 'classifies' or equivalent
                # then store parent name and indent
                if term[0] in super_texts:
                    relation = True
                    parent = name_of_super
                    color = '#aaffaa'  # medium green
                    self.taxon_tree.begin_fold()
                    sub_level += 1
                elif sub_level > 0 and target_level > sub_level:
                    self.taxon_tree.begin_fold()
                    sub_level += 1
                elif target_level < sub_level:
                    while target_level < sub_level:
                        sub_level += -1
                        self.taxon_tree.end_fold()

                taxon_row_widget = gui.TableRow()
                # Determine color of individual 'classified' things
                parts_super = name_of_super.partition(' ')
                if parts_super[0] in super_texts[2:]:
                    color_ind = '#ffdddd'
                else:
                    color_ind = color
                for index, field in enumerate(taxon_line[1:nr_of_cols]):
                    taxon_row_item = gui.TableItem(
                        text=field,
                        style={'text-align': 'left',
                               'background-color': color_ind})
                    if relation is False:
                        # If row (taxon_line[1]) is not a 'has as subtypes' etc.
                        # and super_name is a 'has as subtypes'
                        # then replace super_name by parent (=object_in_focus.name)
                        strings = field.partition(' ')
                        if strings[0] in super_texts:
                            taxon_row_item = gui.TableItem(
                                text=parent,
                                style={'text-align': 'left',
                                       'background-color': color_ind})
                        taxon_row_widget.append(taxon_row_item, field)
                    elif index < 1:
                        # Relation ('has as subtypes' etc.),
                        # thus display only the first field
                        taxon_row_widget.append(taxon_row_item, field)
                    if index == 0:
                        taxon_row_item.uid = taxon_line[0]
                self.taxon_tree.append(taxon_row_widget, name)
                parents.append(name)

    def Define_and_display_summary_sheet(self):
            # Destroy earlier summary_frame
            try:
                self.summ_frame.destroy()
            except AttributeError:
                pass
            self.Define_summary_sheet()
            self.Display_summary_view()

    def Define_summary_sheet(self):
        """ Define a summary_sheet for display of summ_model(a list of summary_rows)
            for a list of individual things for display in a tab of Notebook.
            Summ_model table = obj.uid, obj.name, kind_name, community_name, aspects.
        """
        # Determine tab text
        summ_text = ['List of ', 'Lijst van ']
        indiv_text = ['individual things', 'individuele dingen']
        plurality = ['s', 'en']
        if self.object_in_focus.category in self.kinds:
            self.summ_name = summ_text[self.GUI_lang_index] + self.object_in_focus.name \
                + plurality[self.GUI_lang_index]
        else:
            self.summ_name = summ_text[self.GUI_lang_index] + indiv_text[self.GUI_lang_index] \
                + '(' + self.object_in_focus.name + ')'

        self.summ_frame = gui.VBox(width='100%', height='100%',
                                   style='background-color:#eeffdd')
        self.user_interface.views_noteb.add_tab(self.summ_frame,
                                                self.summ_name, self.tab_cb(self.summ_name))
        summ_head_text = ['Aspects per object of a particular kind',
                          'Aspecten per object van een bepaalde soort']
        self.summ_frame.attributes['title'] = summ_head_text[self.GUI_lang_index]

        self.summ_button_row = gui.HBox(height=20, width='100%')

        self.summ_detail_text = ['Display details', 'Toon details']
        self.summ_detail = gui.Button(self.summ_detail_text[self.GUI_lang_index],
                                      width='15%', height=20)
        self.summ_detail.attributes['title'] = 'First select a row, then press button ' \
                                               'for display of details about selected item'
        self.summ_detail.onclick.connect(self.Summ_detail_view)
        self.summ_button_row.append(self.summ_detail)

        self.close_summ = gui.Button(self.close_button_text[self.GUI_lang_index],
                                     width='15%', height=20)
        self.close_summ.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_summ.onclick.connect(self.user_interface.Close_tag,
                                        self.user_interface.views_noteb,
                                        self.summ_name)
        self.summ_button_row.append(self.close_summ)

        self.summ_frame.append(self.summ_button_row)

        self.summ_table = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})

        # Summary table: UID, Name, Kind, Community, Aspect{1,n)
        self.summ_column_names[0:4] = ['UID', 'Name', 'Kind', 'Community']
        summ_heading = []
        summ_heading.append(tuple(self.summ_column_names[1:]))
        self.summ_table.append_from_list(summ_heading, fill_title=True)
        self.summ_table.on_table_row_click.connect(self.Determine_table_row_values)
        self.summ_frame.append(self.summ_table)

        self.uom_color = '#ccf'
        self.sum_color = '#cfc'

    def Display_summary_view(self):
        """ Display a summary view that provides a list of items and their aspects."""
        # Display the header row with units of measure in summ_table table view
        summ_uom_widget = gui.TableRow(style={'text-align': 'left'})
        for index, field in enumerate(self.summ_uom_names[1:]):
            color = self.uom_color
            summ_uom_item = gui.TableItem(text=field,
                                          style={'text-align': 'left',
                                                 'background-color': color})
            summ_uom_widget.append(summ_uom_item, field)
        self.summ_table.append(summ_uom_widget, 'UoM')

        # Display the various summ_model rows in summ_table table view
        # Select displayed columns
        nr_of_cols = len(self.summ_column_names)
        # Sort the table by product name
        self.summ_model_sorted = []
        for row in self.sort_table(self.summ_model, 1):
            self.summ_model_sorted.append(row)
        # Display the summary table
        for summ_line in self.summ_model_sorted:
            summ_row_widget = gui.TableRow(style={'text-align': 'left'})
            for index, field in enumerate(summ_line[1:nr_of_cols]):
                color = self.sum_color
                summ_row_item = gui.TableItem(text=field,
                                              style={'text-align': 'left',
                                                     'background-color': color})
                if index == 0:
                    summ_row_item.uid = summ_line[0]
                summ_row_widget.append(summ_row_item, field)
            self.summ_table.append(summ_row_widget, summ_line[1])

    def sort_table(self, table, col=0):
        return sorted(table, key=operator.itemgetter(col))

    def Define_and_display_possibilities_of_kind(self):
        # Destroy earlier possib_frame
        try:
            self.possib_frame.destroy()
        except AttributeError:
            pass

        self.Define_possibilities_view()
        self.Display_possibilities_view()

    def Define_possibilities_view(self):
        """ Define a possibilities_sheet for display of possibilities_model
            (a list of possib_rows)
            for display in a tab of Notebook.
        """
        # Determine tab text
        possib_text = ['Possibilities for ', 'Mogelijkheden voor ']
        self.possib_name = possib_text[self.GUI_lang_index] + self.object_in_focus.name
        # Define frame and add to tabs
        self.possib_frame = gui.VBox(width='100%', height='100%',
                                     style='background-color:#eeffdd')
        possib_head = ['Possible aspects per object of a particular kind',
                       'Mogelijke aspecten per object van een bepaalde soort']
        self.possib_frame.attributes['title'] = possib_head[self.GUI_lang_index]
        self.user_interface.views_noteb.add_tab(self.possib_frame,
                                                self.possib_name,
                                                self.tab_cb(self.possib_name))
        possib_button_text = ['Display details of left object',
                              'Toon details van linker object']
        possib_button_row = gui.HBox(height=20, width='100%')

        possib_button = gui.Button(possib_button_text[self.GUI_lang_index],
                                   width='20%', height=20)
        possib_button.attributes['title'] = 'Press button after selection of left hand object'
        possib_button.onclick.connect(self.Possibilities_detail_view)

        close_possib_view = gui.Button(self.close_button_text[self.GUI_lang_index],
                                       width='15%', height=20)
        close_possib_view.attributes['title'] = 'Press button when you want to remove this tag'
        close_possib_view.onclick.connect(
            self.user_interface.Close_tag,
            self.user_interface.views_noteb,
            self.possib_name)

        possib_button_row.append(possib_button)
        possib_button_row.append(close_possib_view)
        self.possib_frame.append(possib_button_row)

        self.possib_tree = TreeTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        # Possib_model = obj.uid, obj.name, ext_name, parent, kind, community, aspect(0,n)
        poss_headings = [[('Kind', 'Community')], [('Soort', 'Taalgemeenschap')]]
        poss_headings[0][0] += tuple(self.possib_column_names[6:])
        poss_headings[1][0] += tuple(self.possib_column_names[6:])
        # nr_of_cols = len(self.possib_column_names)

        self.possib_tree = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        self.possib_tree.append_from_list(poss_headings[self.GUI_lang_index], fill_title=True)
        self.possib_tree.on_table_row_click.connect(self.Determine_table_row_values)
        self.possib_frame.append(self.possib_tree)

        self.uom_color = '#ccf'
        self.sum_color = '#cfc'

    def Display_possibilities_view(self):
        ''' Create a table of possibilities for a given kind.
            possib_row = [obj.uid, obj_name, obj_name, '', supertype_name, comm_name].
        '''
        # Display header row with units of measure
        uom_widget = gui.TableRow(style={'text-align': 'left'})
        for index, field in enumerate(self.possib_uom_names[1:]):
            color = self.uom_color
            uom_item = gui.TableItem(text=field,
                                     style={'text-align': 'left',
                                            'background-color': color})
            uom_widget.append(uom_item, field)
        self.possib_tree.append(uom_widget, 'UoM')
        # Display self.possibilities_model rows in self.possib_tree
        parents = []
        for possib_line in self.possibilities_model:
            # If item parent is blank (has no defined parent, thus item is a top item)
            # or the parent appeared already,
            # then display the row in the tree
            if possib_line[3] == '' or possib_line[3] in parents:
                # Debug print('Possib_line', possib_line)
                # Possib_line[3] is the whole
                row_widget = gui.TableRow(style={'text-align': 'left'})
                for index, field in enumerate(possib_line[1:]):
                    color = self.sum_color
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': color})
                    if index == 0:
                        row_item.uid = possib_line[0]
                    row_widget.append(row_item, field)
                self.possib_tree.append(row_widget, possib_line[1])
                parents.append(possib_line[2])

    def Define_and_display_individual_model(self):
        # Destroy earlier indiv_frame
        try:
            self.indiv_frame.destroy()
        except AttributeError:
            pass

        self.Define_composition_view()

        # Display composition sheet
        self.Display_composition_view()

    def Define_composition_view(self):
        """ Define a view for display of an individual thing and its composition
            (indiv_model, a list of indiv_rows)
            for display in a tab of Notebook.
        """
        self.indiv_frame = gui.VBox(width='100%', height='100%',
                                    style={'overflow': 'auto',
                                           'background-color': '#eeffdd'})
        indiv_text = ['Composition of ', 'Samenstelling van ']
        self.indiv_name = indiv_text[self.GUI_lang_index] + self.object_in_focus.name
        self.user_interface.views_noteb.add_tab(self.indiv_frame, self.indiv_name,
                                                self.tab_cb(self.indiv_name))
        self.indiv_button_row = gui.HBox(height=20, width='100%')

        indiv_button_text = ['Display details',
                             'Toon details']
        self.indiv_button = gui.Button(indiv_button_text[self.GUI_lang_index],
                                       width='15%', height=20)
        self.indiv_button.attributes['title'] = 'Select a row, ' \
                                                'then display details of left hand object'
        self.indiv_button.onclick.connect(self.Indiv_detail_view)

        self.close_indiv = gui.Button(self.close_button_text[self.GUI_lang_index],
                                      width='15%', height=20)
        self.close_indiv.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_indiv.onclick.connect(self.user_interface.Close_tag,
                                         self.user_interface.views_noteb,
                                         self.indiv_name)
        self.indiv_button_row.append(self.indiv_button)
        self.indiv_button_row.append(self.close_indiv)
        self.indiv_frame.append(self.indiv_button_row)

        self.indiv_tree = TreeTable(
            width='100%',
            style={'overflow': 'scroll', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        indiv_headings = [[('Kind', 'Community')], [('Soort', 'Taalgemeenschap')]]
        # nr_of_cols = len(self.indiv_column_names)

        indiv_headings[0][0] += tuple(self.indiv_column_names[5:])
        indiv_headings[1][0] += tuple(self.indiv_column_names[5:])
        # Debug print('Indiv col name:', indiv_headings)
        self.indiv_tree.append_from_list(indiv_headings[self.GUI_lang_index], fill_title=True)
        self.indiv_tree.on_table_row_click.connect(self.Determine_table_row_values)
        self.indiv_frame.append(self.indiv_tree)

        self.uom_color = '#ccf'
        self.sum_color = '#cfc'

    def Display_composition_view(self):
        """ Display rows in indiv_model (composition of individual object)
            in composition sheet view.
            indiv_model = obj.uid, obj.name, whole_name, kind_name, community_name,
                          value(0:m).
        """
        # Display header row with units of measure
        name = 'uom'
        row_widget = gui.TableRow(style={'text-align': 'left',
                                         'background-color': self.uom_color})
        for index, field in enumerate(self.indiv_uom_names[3:]):
            row_item = gui.TableItem(text=field,
                                     style={'text-align': 'left',
                                            'background-color': self.uom_color})
            row_widget.append(row_item, field)
        self.indiv_tree.append(row_widget, name)

        # Display self.indiv_model rows in self.indiv_tree
        indiv_parents = []
        for indiv_line in self.indiv_model:
            # Indiv_line[2] is the whole
            if indiv_line[2] == '' or indiv_line[2] in indiv_parents:
                indiv_name = indiv_line[1]
                row_widget = gui.TableRow()
                for index, field in enumerate(indiv_line[3:]):
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': self.sum_color})
                    if index == 0:
                        row_item.uid = indiv_line[0]
                    row_widget.append(row_item, field)
                self.indiv_tree.append(row_widget, indiv_name)
                indiv_parents.append(indiv_line[1])

    def Define_and_display_expressions_view(self):
        # Destroy earlier expression_frame
        try:
            self.expr_frame.destroy()
        except AttributeError:
            pass

        self.Define_expressions_view()
        self.Display_expressions_view()

    def Define_expressions_view(self):
        """ Define expressions view sheet for display of expr_table in Notebook tab."""
        # Determine tab text
        expr_text = ['Expressions about ', 'Uitdrukkingen over ']
        indiv_text = ['individual things', 'individuele dingen']
        plurality = ['s', 'en']
        if self.object_in_focus.category in self.kinds:
            self.expr_name = expr_text[self.GUI_lang_index] + self.object_in_focus.name \
                + plurality[self.GUI_lang_index]
        else:
            self.expr_name = expr_text[self.GUI_lang_index] + indiv_text[self.GUI_lang_index] \
                + '(' + self.object_in_focus.name + ')'
        self.expr_frame = gui.VBox(width='100%', height='100%',
                                   style='background-color:#eeffdd')
        self.user_interface.views_noteb.add_tab(self.expr_frame, self.expr_name,
                                                self.tab_cb(self.expr_name))
        details = ['Details of LH object', 'Details van linker object']
        expr_context_text = ['Contextual facts', 'Contextuele feiten']
        save_on_CSV_file = ['Save on CSV file', 'Opslaan op CSV file']
        save_on_JSON_file = ['Save on JSON file', 'Opslaan op JSON file']

        self.expr_button_row = gui.HBox(height=20, width='100%')

        # Define button for display of details about lh_obj in selected row
        expr_detail = gui.Button(details[self.GUI_lang_index],
                                 width='15%', height=20)
        expr_detail.attributes['title'] = 'First select a row, the press this button for ' \
                                          'display of details of left hand object'
        expr_detail.onclick.connect(self.Expr_lh_obj_detail_view)
        self.expr_button_row.append(expr_detail)

        # Define button for display of contextual facts
        context_button = gui.Button(expr_context_text[self.GUI_lang_index],
                                    width='15%', height=20)
        context_button.attributes['title'] = 'First select a row, the press this button for ' \
                                             'display of contextual facts about selected item'
        context_button.onclick.connect(self.Contextual_facts)
        self.expr_button_row.append(context_button)

        save_CSV_button = gui.Button(save_on_CSV_file[self.GUI_lang_index],
                                     width='15%', height=20)
        save_CSV_button.attributes['title'] = 'First select a row, the press this button ' \
                                              'for storing expressions on CSV file'
        save_CSV_button.onclick.connect(self.Save_on_CSV_file)
        self.expr_button_row.append(save_CSV_button)

        save_JSON_button = gui.Button(save_on_JSON_file[self.GUI_lang_index],
                                      width='15%', height=20)
        save_JSON_button.attributes['title'] = 'First select a row, the press this button ' \
                                               'for storing expressions on JSON file'
        save_JSON_button.onclick.connect(self.Save_on_JSON_file)
        self.expr_button_row.append(save_JSON_button)

        self.close_expr = gui.Button(self.close_button_text[self.GUI_lang_index],
                                     width='15%', height=20)
        self.close_expr.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_expr.onclick.connect(self.user_interface.Close_tag,
                                        self.user_interface.views_noteb,
                                        self.expr_name)
        self.expr_button_row.append(self.close_expr)

        self.expr_frame.append(self.expr_button_row)

        self.expr_view_table = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})

        # col_heads = ('seq', 'Lang_UID', 'Language', 'CommUID', 'Community',
        #              'Reality', 'Intent_UID', 'Intent_Name', 'Lh_Card', 'Lh_UID',
        #              'Lh_Name', 'LhRole_UID', 'LhRole_Name', 'Validity_UID', 'Validity_context',
        #              'Idea_UID', 'Idea_Descr', 'Rel_UID', 'Kind_of_relation', 'Phrase_UID',
        #              'RhRole_UID', 'RhRole_Name', 'Rh_Card', 'Rh_UID', 'Rh_Name',
        #              'Partial_Def', 'Description', 'Uom_UID', 'UoM', 'Acc_UID',
        #              'Acc_Name', 'Pick_UID', 'Pick_Name', 'Remarks', 'Status',
        #              'Reason', 'Succ_UID', 'DateStartVal', 'DateStartAv', 'DateCC', 'DateLatCh',
        #              'Orignator_UID', 'Originator_Name', 'Author_UID', 'Author_Name',
        #              'Addr_UID', 'Addr_Name', 'References', 'Expr_UID', 'Coll_UID',
        #              'Coll_Name', 'File_Name', 'Lh_Comm', 'Rh_Comm', 'Rel_Comm')
        displaycolumns = [('Lang_Name', 'Community', 'Lh_UID', 'Lh_Name', 'Idea_UID',
                           'Rel_type_UID', 'Rel_type_Name', 'Rh_UID', 'Rh_Name',
                           'Uom_UID', 'UoM', 'Remarks', 'Status')]

        self.expr_view_table.append_from_list(displaycolumns, fill_title=True)
        self.expr_view_table.on_table_row_click.connect(self.Determine_table_row_values)
        self.expr_frame.append(self.expr_view_table)

    def Display_expressions_view(self):
        ''' Display expressions from self.expr_table in Table view.'''
        for expr_line in self.expr_table:
            row_widget = self.Prepare_expr_row_widget(expr_line[2:35],
                                                      expr_line[idea_uid_col],
                                                      self.val_color)
            self.expr_view_table.append(row_widget, expr_line[idea_uid_col])

    def Prepare_expr_row_widget(self, row, uid, row_color):
        col_ids = [0, 2, 7, 8, 13, 15, 16, 21, 22, 25, 26, 31, 32]
        row_widget = gui.TableRow()
        for index, field in enumerate(row):
            if index in col_ids:
                row_item = gui.TableItem(text=field,
                                         style={'text-align': 'left',
                                                'background-color': row_color})
                row_widget.append(row_item, field)
        return row_widget

    def Save_on_CSV_file(self):
        """ Saving query results in a CSV file in Gellish Expression Format."""
        import csv
        import time

        date = time.strftime("%x")
        # Create 3 header records of file
        header1 = ['Gellish', 'Nederlands', 'Version', '9.0', date, 'Query results',
                   'Query results about ' + self.object_in_focus.name, '', '', '', '', '']
        # header2 = expr_col_ids from initial settings in Expr_Table_Def
        # header3 is taken from Expr_Table_Def

        # Open an output file for saving the header lines and the expr_table
        # Note: the r upfront the string (rawstring) is
        #       to avoid interpretation as a Unicode string (and thus giving an error)
        # ini_out_path from bootstrapping
        ini_file_name = 'QueryResults.csv'
        outputFile = filedialog.asksaveasfilename(filetypes=(("CSV files", "*.csv"),
                                                             ("All files", "*.*")),
                                                  title="Enter a file name",
                                                  initialdir=ini_out_path,
                                                  initialfile=ini_file_name,
                                                  parent=self.expr_frame)
        if outputFile == '':
            outputFile = ini_file_name
            self.Display_message(
                'File name for saving is blank or file selection is cancelled. '
                'If generated, the file is saved under the name <{}>'.
                format(outputFile),
                'De filenaam voor opslaan is blanco of the file opslag is gecancelled. '
                'Indien de file is gemaakt, dan is hij opgeslagen met de naam <{}>'.
                format(outputFile))

        queryFile = open(outputFile, mode='w', newline='')
        fileWriter = csv.writer(queryFile, dialect='excel', delimiter=';')

        # Save the expr_table results in a CSV file, including three header lines
        # Write the three header lines and then the file content from expr_table
        fileWriter.writerow(header1)
        fileWriter.writerow(expr_col_ids)
        fileWriter.writerow(header3)
        for expression in self.expr_table:
            fileWriter.writerow(expression)

        queryFile.close()
        self.Display_message(
            'File {} is saved.'.format(outputFile),
            'File {} is opgeslagen.'.format(outputFile))

        # Open written file in Excel
        open_file(outputFile)

    def Save_on_JSON_file(self):
        """ Saving query results in a JSON file in Gellish Expression Format."""
        subject_name = 'Query results'
        lang_name = 'Nederlands'
        serialization = 'json'
        Open_output_file(self.expr_table, subject_name, lang_name, serialization)

    def Define_and_display_kind_view(self):
        # Destroy earlier kind_frame
        try:
            self.kind_frame.destroy()
        except AttributeError:
            pass

        self.Define_kind_model_view()
        self.Display_kind_model_view()

    def Define_kind_model_view(self):
        """ Define a kind model view tab for a kind in Notebook.
            Kind_model = part_uid, part_kind_uid, aspect_uid,
                         LineNr, Object, part, part of part, Kind, Aspect, Kind of aspect,
                         >=<, Value, UoM, Status.
        """
        # Determine tab text
        kind_text = ['Knowledge about ', 'Kennis over ']
        self.kind_name = kind_text[self.GUI_lang_index] + self.object_in_focus.name
        # Define frame and add to tabs
        self.kind_frame = gui.VBox(width='100%', height='100%',
                                   style='background-color:#eeffdd')
        self.user_interface.views_noteb.add_tab(self.kind_frame,
                                                self.kind_name, self.tab_cb(self.kind_name))
        lh_button_text = ['Display details of LH object', 'Toon details van linker object']
        kind_button_text = ['Display details of kind', 'Toon netwerk van de soort']
        aspect_button_text = ['Display details of aspect or file',
                              'Toon details van aspect of file']

        kind_button_row = gui.HBox(height=20, width='100%')

        lh_button = gui.Button(lh_button_text[self.GUI_lang_index],
                               width='20%', height=20)
        lh_button.attributes['title'] = 'Press button after selection of left hand object'
        lh_button.onclick.connect(self.Kind_detail_view_left)

        kind_button = gui.Button(kind_button_text[self.GUI_lang_index], width='20%', height=20)
        kind_button.attributes['title'] = 'Press button after selection of kind'
        kind_button.onclick.connect(self.Kind_detail_view_middle)

        aspect_button = gui.Button(aspect_button_text[self.GUI_lang_index], width='20%', height=20)
        aspect_button.attributes['title'] = 'Press button after selection of aspect'
        aspect_button.onclick.connect(self.Kind_detail_view_right)

        close_kind_view = gui.Button(self.close_button_text[self.GUI_lang_index],
                                     width='15%', height=20)
        close_kind_view.attributes['title'] = 'Press button when you want to remove this tag'
        close_kind_view.onclick.connect(
            self.user_interface.Close_tag,
            self.user_interface.views_noteb,
            self.kind_name)

        kind_button_row.append(lh_button)
        kind_button_row.append(kind_button)
        kind_button_row.append(aspect_button)
        kind_button_row.append(close_kind_view)
        self.kind_frame.append(kind_button_row)

        self.kind_tree = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        kind_tree_head = [[('Object', '', '', 'Supertype', 'Aspect', 'Kind of aspect',
                            '>=<', 'Value', 'UoM', 'Status')],
                          [('Object', '', '', 'Supertype', 'Aspect', 'Soort aspect',
                           '>=<', 'Waarde', 'Eenheid', 'Status')]]
        self.kind_tree.append_from_list(kind_tree_head[self.GUI_lang_index], fill_title=True)
        self.kind_tree.on_table_row_click.connect(self.Determine_table_row_values)
        self.kind_frame.append(self.kind_tree)

        # self.focus_color = '#9f9'  # hell green
        self.head_color = '#bfb'
        self.val_color = '#dfd'  # light green
        self.avail_color = '#fdf'  # yellow
        self.missing_color = '#fcc'  # red

    def Display_kind_model_view(self):
        """ Display a model view of a kind: Display kind_model in self.kind_tree.
            prod_line_0 = [obj.uid, obj_kind_uid, '', 1,
                           'Product form for:', obj.name, '', '',
                           kind_text[self.GUI_lang_index], obj_kind_name, '', '', '', status]
            Kind_model = part_uid, part_kind_uid, aspect_uid, Line_type,
                         Object, part, part of part, Kind, Aspect, Kind of aspect,
                         >=<, Value, UoM, Status.
        """
        unknown_val = ['unknown', 'onbekend', 'unknown value', 'onbekende waarde']
        unknown_kind = ['unknown', 'onbekend', 'unknown kind', 'onbekende soort']
##        level0Part = ''
##        level1Part = ''
##        level2Part = ''

        for kind_line in self.kind_model:
            head_line = []
            line_type = kind_line[3]
            name = kind_line[4]
            # Debug print('kind_line:',kind_line)
            # If line_type == 1 then prepare header line for level 0 object
            # Note: line_type == 2 is skipped in this view
            if line_type == 1:
                head_line.append(kind_line[4])
                head_line.append(kind_line[5])
                head_line.append('')
                head_line.append(kind_line[9])
                kind_row_widget = gui.TableRow(style={'text-align': 'left',
                                                      'background-color': self.val_color})
                for index, field in enumerate(head_line):
                    kind_row_item = gui.TableItem(text=field,
                                                  style={'text-align': 'left',
                                                         'background-color': self.avail_color})
                    kind_row_widget.append(kind_row_item, field)
                self.kind_tree.append(kind_row_widget, name)

##                previusPart = level0Part
            # In kind_treeview line_type 2 to 3 (indicated in kind_line[3])
            # are not displayed.
            elif line_type > 3:
                # Debug print('Value tags:', value_tags)
                row_widget = gui.TableRow(style={'text-align': 'left',
                                                 'background-color': self.val_color})
                for index, field in enumerate(kind_line[4:]):
                    # Set background color depending on head or not and aspect and value
                    # If char kind is unknown background color is yellow
                    # If value is missing then backgroumd color is yellow
                    # If the line is a header line, then set color to head_color
                    head = False
                    if kind_line[4] in self.comp_head or kind_line[4] in self.occ_head or \
                       kind_line[4] in self.info_head or kind_line[8] in self.aspect_head or \
                       kind_line[5] in self.part_occ_head or kind_line[4] in self.subs_head:
                        color = self.head_color
                        head = True
                    else:
                        color = self.val_color
                    if index == 3 and field in unknown_kind:
                        color = self.missing_color
                    if index == 7 and not head:
                        if field == '' or field in unknown_val:
                            color = self.missing_color
                        else:
                            color = self.avail_color
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': color})
                    if index == 0:
                        row_item.uid = kind_line[0]
                    row_widget.append(row_item, field)
                self.kind_tree.append(row_widget, name)

##                # If the line is a header line, then continue to next line
##                if head is True:
##                    continue
##                # If the line is a value line and there is a name of a part
##                #    then remember the part as a previous part
##                elif kind_line[4] != '':
##                    level1Part = id
##                    previusPart = level0Part
##                elif kind_line[5] != '':
##                    level2Part = id
##                    previusPart = level1Part
##                elif kind_line[6] != '':
##                    previusPart = level2Part

    def Select_kind_row(self, emitter, row, item):
        ''' Determine the row values that are selected in the kind_view table.'''
        # LineNr, Object, part, part of part, Kind, Aspect, Kind of aspect,
        #                 >=<, Value, UoM, Status.
        # Determine UID and Name of selected option
        kind_row = list(row.children.values())
        self.kind_uid = ''
        kind_values = []
        uids = []
        if len(kind_row) > 0:
            for field in kind_row:
                kind_values.append(field.get_text())
            for field in kind_row[1:7]:
                uids.append(field.uid)
            # Debug print('Kind data:', kind_values, uids)
        return kind_values, uids

    def Define_and_display_product_model_view(self):
        # Debug print('prod_model',self.prod_model)
        # Destroy earlier product_frame
        try:
            self.prod_frame.destroy()
        except AttributeError:
            pass

        self.Define_product_model_view()
        # Debug print('len prod model', len(self.prod_model))
        # Display prod_model in Composition_sheet view
        self.Display_product_model_view()

    def Define_product_model_view(self):
        """ Product_model view tab sheet in Notebook
            Preceded by a frame with a number of buttons corresponding with binds.
        """
        self.prod_frame = gui.VBox(width='100%', height='100%',
                                   style={'overflow': 'auto',
                                          'background-color': '#eeffdd'})
        prod_text = ['Product model of ', 'Productmodel van ']
        self.prod_name = prod_text[self.GUI_lang_index] + self.object_in_focus.name
        self.user_interface.views_noteb.add_tab(self.prod_frame, self.prod_name,
                                                self.tab_cb(self.prod_name))
        self.prod_button_row = gui.HBox(height=20, width='100%')

        lh_button_text = ['Display details',
                          'Toon details']
        self.lh_button = gui.Button(lh_button_text[self.GUI_lang_index], width='15%', height=20)
        self.lh_button.attributes['title'] = 'Select a row, ' \
                                             'then display details of left hand object'
        self.lh_button.onclick.connect(self.Prod_detail_view)

        tax_button_text = ['Taxonomy of kind',
                           'Taxonomie van soort']
        self.tax_button = gui.Button(tax_button_text[self.GUI_lang_index], width='15%', height=20)
        self.tax_button.attributes['title'] = 'Select a row, then display taxonomy of classifier'
        self.tax_button.onclick.connect(self.Prod_taxonomy)

        asp_button_text = ['Details of aspect',
                           'Details van aspect']
        self.asp_button = gui.Button(asp_button_text[self.GUI_lang_index],
                                     width='20%', height=20)
        self.asp_button.attributes['title'] = 'Select a row, ' \
                                              'then display details of aspect'
        self.asp_button.onclick.connect(self.Prod_aspect)

        classif_button_text = ['Classify',
                               'Classificeer']
        self.classif_button = gui.Button(classif_button_text[self.GUI_lang_index],
                                         width='20%', height=20)
        self.classif_button.attributes['title'] = 'Select a row, ' \
                                                  'then Clcssify the left hand object'
        self.classif_button.onclick.connect(self.Prod_classification)

        self.close_prod = gui.Button(self.close_button_text[self.GUI_lang_index],
                                     width='15%', height=20)
        self.close_prod.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_prod.onclick.connect(self.user_interface.Close_tag,
                                        self.user_interface.views_noteb,
                                        self.prod_name)
        self.prod_button_row.append(self.close_prod)

        self.prod_button_row.append(self.lh_button)
        self.prod_button_row.append(self.tax_button)
        self.prod_button_row.append(self.asp_button)
        self.prod_button_row.append(self.classif_button)
        self.prod_button_row.append(self.close_prod)
        self.prod_frame.append(self.prod_button_row)

        self.prod_tree = TreeTable(
            width='100%',
            style={"overflow": "auto", "background-color": "#eeffaa",
                   "border-width": "2px", "border-style": "solid",
                   "font-size": "12px", 'table-layout': 'auto',
                   'text-align': 'left'})
        prod_tree_head = [[('', '', '', 'Kind', 'Aspect', 'Kind of aspect',
                            '>=<', 'Value', 'UoM', 'Status')],
                          [('', '', '', 'Soort', 'Aspect', 'Soort aspect',
                            '>=<', 'Waarde', 'Eenheid', 'Status')]]
        self.prod_tree.append_from_list(prod_tree_head[self.GUI_lang_index], fill_title=True)
        self.prod_tree.on_table_row_click.connect(self.Determine_table_row_values)
        self.prod_frame.append(self.prod_tree)

        self.focus_color = '#9f9'  # hell green
        self.head_color = '#bfb'  # dark green
        self.val_color = '#dfd'  # light green
        self.available = 'yellow'
        self.missing = '#fcc'  # red

    def Display_product_model_view(self):
        """ Display prod_model in self.prod_tree."""
        unknown_val = ['unknown value', 'onbekende waarde']
        unknown_kind = ['unknown kind', 'onbekende soort']
        further_part = ['Further part', 'Verder deel']
        kind_of_part = ['Kind of part', 'Soort deel']
        possible_roles = False  # No roles expected

        for prod_line_0 in self.prod_model:
            prod_line = prod_line_0[:]
            head_line = []
            line_type = prod_line[3]
            str_line = str(line_type)
            # Debug print('Prod_line:', prod_line)
            # If line_type == 1
            # then prepare header line from prod_line for level 0 object
            # Note: line_type == 2 and 3 are skipped in this view
            if line_type == 1:
                name = prod_line[5]
                head_line = prod_line[0:4]
                head_line.append(name)
                head_line.append('')
                head_line.append('')
                head_line.append(prod_line[9])
                prod_row_widget = gui.TableRow(style={'text-align': 'left',
                                                      'background-color': self.val_color})
                for index, field in enumerate(head_line[4:]):
                    prod_row_item = gui.TableItem(text=field,
                                                  style={'text-align': 'left',
                                                         'background-color': self.available})
                    prod_row_widget.append(prod_row_item, field)
                self.prod_tree.append(prod_row_widget, name)
            # Note: line_type == 2 and 3 are skipped in this view
            elif line_type == 4:
                prod_name = prod_line[4] + str_line
                prod_row_widget = gui.TableRow()
                for index, field in enumerate(prod_line[4:]):
                    prod_row_item = gui.TableItem(text=field,
                                                  style={'text-align': 'left',
                                                         'background-color': self.head_color})
                    if index == 0:
                        prod_row_item.uid = prod_line[0]
                    prod_row_widget.append(prod_row_item, field)
                self.prod_tree.append(prod_row_widget, prod_name)

            # In prod_tree view line_type 2 and 3 are not displayed.
            elif line_type > 4:
                # Set color at default 'val_color' for each field in a line
                value_colors = []
                for col in range(0, 14):
                    value_colors.append(self.val_color)

                # If the line is a header line
                if prod_line[4] in self.comp_head or prod_line[4] in self.occ_head or \
                   prod_line[4] in self.info_head or prod_line[8] in self.aspect_head or \
                   prod_line[5] in self.part_occ_head or prod_line[4] in self.subs_head:
                    # Set color to 'head_color' for each field in the header line
                    for col in range(0, 14):
                        value_colors[col] = self.head_color
                    prod_name = prod_line[4] + str_line
                    # Determine whether roles may appear in prod_line[4]
                    # in lines following the header line
                    # to avoid that they are included in the indented hierarchy
                    if prod_line[4] in self.occ_head:
                        possible_roles = True
                    elif prod_line[5] in self.part_occ_head:
                        possible_roles = False
                    # Remove header texts 'Further part' and 'Kind of part'
                    if prod_line[6] in further_part:
                        prod_line[6] = ''
                    if prod_line[7] in kind_of_part:
                        continue  # prod_line[7] = ''

                # If the line is a value line (thus not a header line)
                # and there is a name of a part
                # then remember the part as a previous part
                elif prod_line[4] != '':
                    prod_name = prod_line[4] + str_line
                elif prod_line[5] != '':
                    prod_name = prod_line[5] + str_line
                elif prod_line[6] != '':
                    prod_name = prod_line[6] + str_line
                else:
                    prod_name = prod_name + str_line

                # Set tag background color depending on value
                # If value is missing then backgroumd color is yellow
                if prod_line[11] in unknown_val:
                    value_colors[11] = self.missing
                elif prod_line[11] != '':
                    value_colors[11] = self.available
                if prod_line[9] in unknown_kind:
                    value_colors[9] = self.missing

                if possible_roles is True and prod_line[4] == '':
                    prod_name = '' + str_line

                # Insert line in prod_tree
                # Debug print('Values:', prod_line[1], type(prod_line[1]))
                prod_row_widget = gui.TableRow(style={'text-align': 'left'})
                for index, field in enumerate(prod_line[4:]):
                    color = value_colors[index + 4]
                    prod_row_item = gui.TableItem(text=field,
                                                  style={'text-align': 'left',
                                                         'background-color': color})
                    if index == 0:
                        prod_row_item.uid = prod_line[0]
                    prod_row_widget.append(prod_row_item, field)
                self.prod_tree.append(prod_row_widget, prod_name)

    def Define_and_display_data_sheet(self):
        # Destroy earlier data sheet
        try:
            self.data_sheet.destroy()
        except AttributeError:
            pass

        self.Define_data_sheet()
        # Display prod_model in Data_sheet view
        self.Display_data_sheet_view()

    def Define_data_sheet(self):
        # Define ProductView tab in Notebook = = = = = = = = = = = = = = = = = = =
        # Product_sheet is canvas for scrollbar
        self.data_sheet_frame = gui.VBox(width='100%', height='100%',
                                         style={'overflow': 'auto',
                                                'background-color': '#eeffdd'})
        data_text = ['Data sheet of ', 'Productformulier van ']
        self.data_name = data_text[self.GUI_lang_index] + self.object_in_focus.name
        self.user_interface.views_noteb.add_tab(self.data_sheet_frame, self.data_name,
                                                self.tab_cb(self.data_name))
        self.data_button_row = gui.HBox(height=20, width='100%')

        self.close_data = gui.Button(self.close_button_text[self.GUI_lang_index],
                                     width='15%', height=20)
        self.close_data.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_data.onclick.connect(self.user_interface.Close_tag,
                                        self.user_interface.views_noteb,
                                        self.data_name)
        self.data_button_row.append(self.close_data)
        self.data_sheet_frame.append(self.data_button_row)

        self.data_table = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        self.data_table.on_table_row_click.connect(self.Determine_table_row_values)
        self.data_sheet_frame.append(self.data_table)

    def Display_data_sheet_view(self):
        """ Produce a view of a product model in the form of a datasheet."""
        unknown_val = ['unknown value', 'onbekende waarde']
        unknown_kind = ['unknown kind', 'onbekende soort', 'anything', 'iets']

        # Set column widths in data sheet
        col_width = [4, 20, 10, 10, 20, 15, 20, 4, 10, 5, 10]
        line_nr = -1
        for prod_row in self.prod_model:
            line = prod_row[3:]
            line_type = line[0]
            line_nr += 1
            column_nr = -1
            head = False
            header_1 = False
            header_2 = False
            header_3 = False
            body = False
            back = 'white'
            # fore = 'black'
            data_row_widget = gui.TableRow(style={'text-align': 'left'})
            for field_value in line:
                column_nr += 1
                field_str =str(field_value)
                # span = 1
                column_width = col_width[column_nr]

                # Detect start of header line 1:
                # Line_type == 1 means field_value 1 in column 0 and header_1
                if column_nr == 0 and line_type == 1:
                    header_1 = True
##                if header_1 is True:
##                    if column_nr == 2:
##                        span = 3
##                    elif column_nr == 6:
##                        span = 5

                # Display on line 1 the line nr, 'Product form' label and the 'kind' label
                if header_1 is True and column_nr in [0, 1, 5]:
                    back = '#dfb'  # light green
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)

                # Display on line 1 the product_name and kind_name (with another background color)
                if header_1 is True and column_nr in [2, 6]:
                    back = 'white'
                    # fore = 'black'
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)

                # Detect start of header line 2: Value 2 in column 0 means line_type2 and header_2
                if column_nr == 0 and line_type == 2:
                    header_2 = True

                # Display on line 2 the description text
                if header_2 is True and column_nr == 3:
                    # span = 8
                    back = 'white'
                    # fore = 'black'
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)
                # Display on line 2 the description label
                if header_2 is True and column_nr in range(0, 3):
                    back = '#dfb'
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)

                # Detect start of header line 3:
                # Value 3 in column 0 means line_type3 and header_3
                if column_nr == 0 and line_type == 3:
                    header_3 = True
                    line_nr += + 1

                # Display the line 3 subsequent values
                if header_3 is True:
                    back = '#dfb'
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)

                # Detect start of body values: Value >3 in column 0 means body of values
                if column_nr == 0 and line_type > 3:
                    body = True
                # Display the subsequent body values on line type > 3
                if body is True:
                    # Set background color
                    # depending on either header, value present or 'unknown'
                    if (column_nr == 1 and (field_value in self.comp_head
                                            or field_value in self.occ_head
                                            or field_value in self.info_head)) \
                            or (column_nr == 2 and (field_value in self.part_occ_head)):
                        # Header line detected; set background color accordingly
                        head = True
                        back = '#dfb'
                    if column_nr == 8 and field_value != '':
                        back = 'yellow'
                    elif head is not True:
                        back = 'white'
                    if field_value in unknown_val:
                        field_value = unknown_val[self.GUI_lang_index]
                        back = '#fcc'
                    elif field_value in unknown_kind:
                        field_value = unknown_kind[self.GUI_lang_index]
                        back = '#fcc'
                    # Display subsequent body values
                    field = gui.TableItem(text=field_str, width=column_width, height=20,
                                          style={'background-color': back})
                    data_row_widget.append(field)
            self.data_table.append(data_row_widget)

    def Define_and_display_activity_view(self):
        # Destroy earlier activity sheet
        try:
            self.act_frame.destroy()
        except AttributeError:
            pass

        self.Define_activity_view()
        # Display occ_model in Activity sheet view
        self.Display_activity_view()

    def Define_activity_view(self):
        ''' Define the layout for display of an activity model.
            act_model = ['OccUID', 'OccName', 'ParentOccName', 'InvolvUID', 'KindOccUID',
                         'OccName', 'PartName', 'Involved', 'Kind', 'Role'].
        '''
        act_text = ['Activities about ', 'Activiteiten betreffende ']
        self.act_name = act_text[self.GUI_lang_index] + self.object_in_focus.name
        self.act_frame = gui.VBox(width='100%', height='80%',
                                  style={'overflow': 'auto',
                                         'background-color': '#eeffdd'})
        self.user_interface.views_noteb.add_tab(self.act_frame,
                                                self.act_name, self.tab_cb(self.act_name))
        self.act_button_row = gui.HBox(height=20, width='100%')

        self.close_act = gui.Button(self.close_button_text[self.GUI_lang_index],
                                    width='15%', height=20)
        self.close_act.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_act.onclick.connect(
            self.user_interface.Close_tag,
            self.user_interface.views_noteb,
            self.act_name)
        self.act_button_row.append(self.close_act)
        self.act_frame.append(self.act_button_row)

        occ_text = ['Occurrence', 'Gebeurtenis']
        part_text = ['Part occurrence', 'Deelgebeurtenis']
        inv_text = ['Involved object', 'Betrokken object']
        kind_text = ['Kind', 'Soort']
        role_text = ['Role', 'Rol']
        display_cols = [(occ_text[self.GUI_lang_index],
                        part_text[self.GUI_lang_index],
                        inv_text[self.GUI_lang_index],
                        kind_text[self.GUI_lang_index],
                        role_text[self.GUI_lang_index])]
        self.act_tree = SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'scroll', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'})
        self.act_tree.append_from_list(display_cols, fill_title=True)
        self.act_tree.on_table_row_click.connect(self.Determine_table_row_values)
        self.act_frame.append(self.act_tree)

        self.uom_color = '#ccf'
        self.act_color = '#dfd'
        self.head_color = '#dfd'

    def Display_activity_view(self):
        """ Display occurrences (activities, processes and events) in self.act_tree.
            Followed by a display of IDEF0 diagram(s).
        """
        self.top_occurrences = []
        for occ_line in self.occ_model:
            # Debug print('OccTree:', occ_line)
            # If higher part (occ_line[2]) is blank (= has no parent)
            # then occ_line[0] contains top occ_UID
            if occ_line[2] == '':
                top_occ = self.uid_dict[occ_line[0]]
                self.top_occurrences.append(top_occ)
            self.occ_level = 0
            # Display self.act_tree line
            self.Display_occurrence_tree_line(occ_line)

        # IDEF0: Display drawings of occurrences
        diagram = Occurrences_diagram(self.user_interface, self.gel_net)
        diagram.Create_occurrences_diagram(self.top_occurrences, self.object_in_focus)

    def Display_occurrence_tree_line(self, occ_line):
        """ Display occurrences compositions with inputs and outputs and roles.
            occ_line = line in occ_model
            occ_model.append([occ.uid, occ.name, parent.name, involv.uid, kind_occ.uid,
                              occ.name, part_occ.name, involv.name,
                              kind_part_occ.name, role_of_involved])
            involv_table: occ, involved, inv_role_kind, inv_kind_name.
        """
        # Debug print('Occ_line:', occ_line)
        self.occ_color = '#ddf'
        self.io_color = '#eef'

        # Display the occurrence
        # parent_name = occ_line[2]
        child_name = occ_line[1]
        openness = 'true'
        act_row_widget = gui.TableRow()
        act_row_widget.attributes['treeopen'] = openness
        # widget_dict[child_name] = act_row_widget
        for index, field in enumerate(occ_line[5:]):
            row_item = gui.TableItem(text=field,
                                     style={'text-align': 'left',
                                            'background-color': self.occ_color})
            act_row_widget.append(row_item, field)
            if index == 0:
                row_item.uid = occ_line[0]
        self.act_tree.append(act_row_widget, child_name)

        # Find and display its involved inputs and outputs
        # involv_table = occ, involved_obj, inv_role_kind, inv_kind_name
        for occ, involved_obj, inv_role_kind, inv_kind_name in self.involv_table:
            row_name = involved_obj.name + ' ' + inv_role_kind.name
            io_line = ['', '', '', '', '', '', '',
                       involved_obj.name, inv_kind_name, inv_role_kind.name]
            # Debug print('involv-line:', occ_line[1],
            #             occ.uid, involved_obj.uid, io_line)
            # If uid of occurrence == uid of object
            # that has inputs or outputs then display io_line
            if occ_line[0] == occ.uid:
                inv_row_widget = gui.TableRow()
                inv_row_widget.attributes['treeopen'] = openness
                for index, field in enumerate(io_line[5:]):
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': self.io_color})
                    if index == 0:
                        row_item.uid = occ.uid
                    inv_row_widget.append(row_item, field)
                self.act_tree.append(inv_row_widget, row_name)
        self.occ_level = 1

    def Define_and_display_documents(self):
        """ Define documents view and display documents in view."""
        # Destroy earlier documents sheet
        try:
            self.doc_frame.destroy()
        except AttributeError:
            pass

        self.Define_documents_sheet()
        self.Display_documents_sheet()

    def Define_documents_sheet(self):
        doc_text = ['Documents', 'Documenten']
        self.doc_name = doc_text[self.GUI_lang_index] + ' about ' + self.object_in_focus.name
        self.doc_frame = gui.VBox(width='100%', height='100%',
                                  style='background-color:#eeffdd')
        self.user_interface.views_noteb.add_tab(self.doc_frame,
                                                self.doc_name, self.tab_cb(self.doc_name))
        self.doc_button_row = gui.HBox(height=20, width='100%')
        self.doc_frame.append(self.doc_button_row)

        # If info_kind is a description then display the destription
        #   else open the file in the file format that is defined by its file extension
        self.info_button_text = ['Display information', 'Toon informatie']
        self.info_doc = gui.Button(self.info_button_text[self.GUI_lang_index],
                                   width='20%', height=20)
        self.info_doc.attributes['title'] = 'Display the selected text or file content'
        self.info_doc.onclick.connect(self.Doc_detail_view)
        self.doc_button_row.append(self.info_doc)

        # Determine and display a product view of the object
        # about which the document provides info
        self.object_button_text = ['Object model', 'Objectmodel']
        self.object_doc = gui.Button(self.object_button_text[self.GUI_lang_index],
                                     width='20%', height=20)
        self.object_doc.attributes['title'] = 'Display the selected text or file content'
        self.object_doc.onclick.connect(self.Object_detail_view)
        self.doc_button_row.append(self.object_doc)

        self.close_doc = gui.Button(self.close_button_text[self.GUI_lang_index],
                                    width='15%', height=20)
        self.close_doc.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_doc.onclick.connect(self.user_interface.Close_tag,
                                       self.user_interface.views_noteb,
                                       self.doc_name)
        self.doc_button_row.append(self.close_doc)

        headings = ['info', 'obj', 'carrier', 'directory', 'Info', 'Kind of info', 'Directory',
                    'Name of object', 'File name', 'Kind of file']
        display_cols = list(headings[4:])
        doc_heading = []
        doc_heading.append(tuple(display_cols))
        self.doc_table = SingleRowSelectionTable(
            width='100%',
            style={"overflow": "auto", "background-color": "#eeffaa",
                   "border-width": "2px", "border-style": "solid",
                   "font-size": "12px", 'table-layout': 'auto',
                   'text-align': 'left'})
        self.doc_table.on_table_row_click.connect(self.Select_info)
        self.doc_table.append_from_list(doc_heading, fill_title=True)
        self.doc_frame.append(self.doc_table)

    def Display_documents_sheet(self):
        """ Display information about texts and documents file for selection
            for display of textual information, document content or object model.
            - info_row('values') =
                [info.uid, obj.uid, carrier.uid, directory_name,
                 info.name, super_info_name, obj.name,
                 carrier.name, carrier_kind_name].
        """
        color = '#eeffdd'
        for info_line in self.info_model:
            name = info_line[4]
            info_row_widget = gui.TableRow()
            for index, field in enumerate(info_line[4:]):
                info_row_item = gui.TableItem(text=field,
                                              style={'text-align': 'left',
                                                     'background-color': color})
                if index == 0:
                    info_row_item.uid = info_line[0]
                    info_row_item.description = info_line[2]
                elif index == 3:
                    info_row_item.uid = info_line[2]
                info_row_widget.append(info_row_item, field)
            self.doc_table.append(info_row_widget, name)

    def Expr_lh_obj_detail_view(self, widget):
        """ Find the selected left hand object from a user selection row,
            being a row in the displayed part of the expr_table
            that is displayed in the expr_view_table widget.
            And define and display its detail view.
        """
        uid_col = 2
        self.selected_obj = self.uid_dict[self.row_values[uid_col]]
        self.Display_message(
            'Display product details of: {}'.format(self.selected_obj.name),
            'Toon productdetails van: {}'.format(self.selected_obj.name))

        if self.selected_obj.category in ['kind', 'kind of physical object',
                                          'kind of occurrence', 'kind of aspect',
                                          'kind of role', 'kind of relation']:
            self.Define_and_display_kind_detail_view(self.selected_obj)
        else:
            self.Define_and_display_individual_detail_view(self.selected_obj)

    def Prepare_lh_object_network_view(self, widget):
        """ Set the uid of the left hand object in a selected treeview row
            as the chosen object
            for display of a new network view and other views.
        """
        # tree_values = self.Determine_network_tree_values()
        if len(self.row_widgets[0]) > 0:
            chosen_object_uid = self.row_widgets[0].uid
            print('uid:', chosen_object_uid)
            # Build single product model (list with one element)
            obj_list = []
            obj = self.uid_dict[chosen_object_uid]
            obj_list.append(obj)
            self.Build_product_views(obj_list)
            # Display query results in notebook sheets
            self.Display_notebook_views()

    def Prepare_lh_network_object_detail_view(self, widget):
        """ Set the uid of the left hand object
            in a selected network treeview row
            as the chosen object for display of details.
        """
        # tree_values = self.Determine_network_tree_values()
        if len(self.row_values) > 0:
            chosen_object_uid = self.row_values[0]
            self.Determine_category_of_object_view(chosen_object_uid, self.row_values)
            self.Determine_category_of_object_view(chosen_object_uid, self.row_values)

    def Prepare_rh_network_object_detail_view(self, widget):
        """ Set the uid of the right hand object
            in a selected network treeview row
            as the chosen object for display of details.
        """
        # tree_values = self.Determine_network_tree_values()
        if len(self.row_values) > 4:
            chosen_object_uid = self.row_values[4]
            self.Determine_category_of_object_view(chosen_object_uid, self.row_values)

    def Prepare_for_classification(self):
        """ Find the selected left classifier object from a user selection
            in the network that is displayed in the network_tree view.
            When the classification button was used the taxonomy of the selected kind
            is displayed and a search for a second classifier in the taxonomy
            (the subtype hierarchy of the selected kind) is started.
            The aspects of the individual object are used to create selection criteria for the
            subtypes in the hierarchy.
            The taxonomy of the selected kind is displayed for selection of the classifier.
        """
        # similar to def Prod_taxonomy(self, sel):
        # tree_values = self.Determine_network_tree_values()
        if len(self.row_values) > 0:
            if self.row_values[4] == '' or self.row_values[4] == 'unknown':
                self.Display_message(
                    'Classifying kind of object is unknown.',
                    'Classificerende soort object is onbekend.')
            else:
                kind_uid = str(self.row_values[4])
                individual_object_uid = str(self.row_values[0])
                self.Classification_of_individual_thing(individual_object_uid, kind_uid)
        else:
            self.Display_message(
                'Select an item, then click the classification button for classying the object.',
                'Selecteer een object, click dan op de classifikatieknop '
                'om het object te classificeren')

    def Classification_of_individual_thing(self, to_be_classified_object_uid, kind_uid):
        """ Start a classification process for a modified_object = to be classified
            by a subtype of a current classifying kind.
            When completed, a classification relation is added to the classified object.
        """
        self.modification = 'classification started'
        kind = self.uid_dict[kind_uid]
        self.modified_object = self.uid_dict[to_be_classified_object_uid]
        self.Display_message(
            'Present the taxonomy of the kind <{}> that classifies <{}> '
            'for selection of a subtype that classifies the object'.
            format(kind.name, self.modified_object.name),
            'Presenteer de taxonomie van de soort <{}> die classificeerder is van <{}> '
            'voor het selecteren van een subtype die het object classificeert'.
            format(kind.name, self.modified_object.name))

        # Formulate query_spec including conditions from aspects of individual, if any
        self.user_interface.query.Formulate_query_spec_from_individual(kind)
        self.user_interface.query.Create_query_file()
        self.user_interface.query.Interpret_query_spec()

        obj_list = []
        obj_list.append(kind)
        self.Build_product_views(obj_list)
        # Display taxonomy in taxon view
        self.Define_and_display_taxonomy_of_kinds()
        # Display possibilities of kind in possibilities view
        self.Define_and_display_possibilities_of_kind()

        if len(self.info_model) > 0:
            self.Define_and_display_documents()

##    def Prepare_network_object_detail_view(self, widget):  # , row, item):
##        """ Find the selected left hand object from a user selection with left button
##            in the network_model that is displayed in the network_tree view.
##        """
##        self.Determine_network_tree_values()
##        widget_name = widget.get_value()
##        # Debug print('Selected for detail network:', widget_name, widget.uid)
##        # self.selected_obj = self.gel_net.uid_dict[widget.uid]
##        tree_values = [widget.uid, widget_name]
##        self.Determine_category_of_object_view(widget.uid, tree_values)

##    def Determine_network_tree_values(self):
##        """ Determine the values on a selected row in a network TreeTable."""
##        # fields = list(row.children.values())
##        self.row_values
##        tree_values = []
##        if len(fields) > 0:
##            for field in fields:
##                value = field.get_text()
##                tree_values.append(value)
##            print('Selected row:', tree_values)
##        else:
##            self.Display_message(
##                'No item found. Fist select a row, then click a button.',
##                'Geen object gevonden. Selecteer eerst een rij, click daarna op een knop.')
##        return tree_values

    def Determine_category_of_object_view(self, chosen_object_uid, row_values):
        """ Determine kind of chosen object and as a consequence models and views."""
        description_text = ['description', 'beschrijving']
        obj_descr_title = ['Information about ', 'Informatie over ']

        if chosen_object_uid != '':
            self.selected_obj = self.uid_dict[str(chosen_object_uid)]

            # If info_kind is a description then display the destription in messagebox
            if len(row_values) > 8 and row_values[8] in description_text:
                self.messagebox(obj_descr_title[self.GUI_lang_index] + self.selected_obj.name,
                                self.selected_obj.description)
            else:
                self.Display_message(
                    'Display object details of: {}'.format(self.selected_obj.name),
                    'Weergave van objectdetails van: {}'.format(self.selected_obj.name))
                if self.selected_obj.category in self.gel_net.categories_of_kinds:
                    self.Define_and_display_kind_detail_view(self.selected_obj)
                else:
                    self.Define_and_display_individual_detail_view(self.selected_obj)

            if len(self.info_model) > 0:
                self.Define_and_display_documents()

    def Kind_detail_view_left(self, widget):
        """ Find the selected left hand object from a user selection
            in the kind_table that is displayed in the kind_tree view.
            And determine and display its details.
        """
        description_text = ['description', 'beschrijving']
        obj_descr_title = ['Information about ', 'Informatie over ']
        row_values = self.row_values
        obj_uid = self.row_widgets[0].uid
        # Debug print('Kind_detail_left:', cur_item, row_values)
        self.selected_obj = self.uid_dict[obj_uid]

        # If info_kind is a description then display the destription in messagebox
        if row_values[7] in description_text:
            self.messagebox(obj_descr_title[self.GUI_lang_index] + self.selected_obj.name,
                            self.selected_obj.description)
        else:
            print('Display kind details of: {}'.format(self.selected_obj.name))
            self.Define_and_display_kind_detail_view(self.selected_obj)

    def Kind_detail_view_middle(self, widget):
        """ Find the selected left supertype object from a user selection with middle button
            in the kind_table that is displayed in the kind_tree view.
            Then determine and display its taxonomy.
        """
        if len(self.row_widgets) > 0:
            kind_uid = self.row_widgets[3].uid
            if kind_uid not in ['', 'kind', 'unknown', 'onbekend']:
                self.selected_obj = self.uid_dict[kind_uid]

                self.Display_message(
                    'Display the taxonomy of: {}'.format(self.selected_obj.name),
                    'Weergave van de taxonomie van: {}'.format(self.selected_obj.name))
                obj_list = []
                obj_list.append(self.selected_obj)
                self.Build_product_views(obj_list)
                # Display taxonomy of selected kind
                self.Define_and_display_taxonomy_of_kinds()
                if len(self.info_model) > 0:
                    self.Define_and_display_documents()
            else:
                self.Display_message(
                    'The classifying kind of the object is unknown.',
                    'De classificerende soort van het object is onbekend.')
        else:
            self.Display_message(
                'Select a line before clicking the details button.',
                'Selecteer een regel voor het clicken van de details knop.')

    def Kind_detail_view_right(self, widget):
        """ Find the selected kind of aspect or file from a user selection with right button
            in the kind_table that is displayed in the kind_tree view.
            And determine and display the aspect or file content.
        """
        row_values = self.row_values
        if len(row_values) == 0:
            self.Display_message(
                'No item is selected. '
                '\nFirst select a line with a single left mouse button click, '
                '\nthen click the right mouse button.',
                'Er is geen object geselecteerd. '
                '\nSelecteer eerst een regel met een enkele lenker muisclick '
                '\nclick daarna de rechter muisknop.')
            return
        # Debug print('Kind_detail_right:',row_values)
        if len(row_values) > 8:
            # If row_values[8] contains a dot(.)
            # then it is interpreted as a file.name with file extension,
            # else it is interpreted as a selected kind of aspect name
            parts = row_values[8].rsplit('.', maxsplit=1)
            if len(parts) == 1:
                self.Display_message(
                    'The name <{}> does not contain a file extension, although expected. '
                    'The name is now interpreted as a kind of aspect.'.
                    format(row_values[8]),
                    'De naam <{}> bevat geen file extensie, hoewel dat wel verwacht wordt. '
                    'Die naam is nu geïnterpreteerd als een soort aspect.'.
                    format(row_values[8]))
                self.selected_obj = row_values[2]
                self.Display_message(
                    'Display the aspect details of: {}'.format(self.selected_obj.name),
                    'Weergave van de aspectdetails van: {}'.format(self.selected_obj.name))
                # Display taxonomy of selected kind
                self.Define_and_display_taxonomy_of_kinds()
            else:
                # Open the file in the file format that is defined by its file extension
                # from directory+file_name
                file_path = os.path.join(row_values[5], row_values[8])
                normalized_path = os.path.normpath(file_path)
                open_file(normalized_path)
        else:
            self.Display_message(
                'There is no right hand object found to be displayed.',
                'Er is geen rechter object gevonden om weergegeven te worden.')

    def Prod_detail_view(self, widget, row, item):
        """ Identify the selected individual object at the left hand of the row
            in the prod_table and display its details in a prod_tree view.
        """
        description_text = ['description', 'beschrijving']
        obj_descr_title = ['Information about ', 'Informatie over ']
        row_values = self.row_values
        obj_uid = self.row_widgets[0].uid
        # Debug print('Prod_detail_left:', cur_item, row_values)
        if len(row_values) > 0:
            if row_values[0] != '':
                self.selected_obj = self.uid_dict[obj_uid]

                # If info_kind is a description
                # then display the destription in messagebox
                if row_values[7] in description_text:
                    self.messagebox(obj_descr_title[self.GUI_lang_index]
                                    + self.selected_obj.name,
                                    self.selected_obj.description)
                else:
                    self.Display_message(
                        'Display of product details of: {}'.format(self.selected_obj.name),
                        'Weergave van de productdetails van: {}'.format(self.selected_obj.name))
                    self.Define_and_display_individual_detail_view(self.selected_obj)

                if len(self.info_model) > 0:
                    self.Define_and_display_documents()

    def Prod_taxonomy(self):
        """ Identify the classifier of the left hand object from a user selection
            in the prod_table that is displayed in the prod_table view.
            Display the taxonomy of the selected kind.
        """
        row_values = self.row_values
        # Debug print('Prod_detail_middle:', sel.type, sel.keysym,
        #             cur_item, row_values, type(row_values[1]))
        if len(row_values) > 0:
            kind_uid = row_values[1]
            individual_object_uid = row_values[0]
            if kind_uid != '':
                self.selected_obj = self.uid_dict[individual_object_uid]
                # Build views for selected kind and display views
                self.Display_message(
                    'Display taxonomy and possibilities of kind: {}'.
                    format(self.selected_obj.name),
                    'Weergave van de taxonomie en mogelijkheden van soort: {}'.
                    format(self.selected_obj.name))
                obj_list = []
                obj_list.append(self.selected_obj)
                self.Build_product_views(obj_list)
                # Display taxonomy in taxon view
                self.Define_and_display_taxonomy_of_kinds()
                # Display possibilities of kind in possibilities view
                self.Define_and_display_possibilities_of_kind()

                if len(self.info_model) > 0:
                    self.Define_and_display_documents()
            else:
                self.Display_message(
                    'The kind of object is unknown.',
                    'De soort object is onbekend.')
        else:
            self.Display_message(
                "Select an item, then click the taxonomy button "
                "for display of the taxonomy of the classifier.",
                "Selecteer een regel, click dan de taxonomieknop "
                "voor het weergeven van de taxonomie van de classificeerder.")

    def Prod_classification(self, sel):
        """ Identify the selected classifier of the left hand object from a user selection
            in the prod_table that is displayed in the prod_tree view.
            Start a search for a second classifier in the taxonomy
            (the subtype hierarchy of the selected kind).
            The aspects of the individual object are used to create selection criteria
            for the subtypes in the hierarchy.
            The taxonomy of the selected kind is displayed for selection of the classifier.
        """
        cur_item = self.prod_tree.focus()
        item_dict = self.prod_tree.item(cur_item)
        tree_values = list(item_dict['values'])
        # Debug print('Prod_detail_middle:', sel.type, sel.keysym,
        #             cur_item, tree_values, type(tree_values[1]))

        if len(tree_values) > 0:
            kind_uid = str(tree_values[1])
            individual_object_uid = str(tree_values[0])
            if kind_uid != '':
                self.selected_obj = self.uid_dict[individual_object_uid]
                # Perform a classification process by display the taxonomy of kind
                # and selection of one of its subtypes
                self.Classification_of_individual_thing(individual_object_uid, kind_uid)
            else:
                self.Display_message(
                    'The kind of object is unknown.',
                    'De soort object is onbekend.')
        else:
            self.Display_message(
                "Select an item, then click the classification button "
                "for classying the object.",
                "Selecteer een regel, click dan de classifikatieknop "
                "voor het classificeren van het object.")

    def Prod_aspect(self, sel):
        """ Identify the selected aspect or file from a user selection with right button
            in the prod_table abd display its details in the prod_tree view.
        """
        cur_item = self.prod_tree.focus()
        if cur_item == '':
            self.Display_message(
                'No item selected. First select item with single left button click. '
                'Then click right button.',
                'Er is geen object deselecteerd. '
                'Kies eerst een regel met een enkele click van de linkermuisknop. '
                'Click daarna met de rechtermuisknop.')
            return
        item_dict = self.prod_tree.item(cur_item)
        tree_values = list(item_dict['values'])
        # Debug print('Prod_detail_right:',cur_item, tree_values)

        if len(tree_values) > 8:
            # If tree_values[8] contains a dot(.)
            # then it is interpreted as a file.name with file extension,
            # else it is interpreted as an selected aspect
            parts = tree_values[8].rsplit('.', maxsplit=1)
            if len(parts) == 1:
                if str(tree_values[2]) == '':
                    self.Display_message(
                        'There is no right hand object found to be displayed.',
                        'Er is geen rechter object gevonden om weergegeven te worden.')
                else:
                    self.Display_message(
                        'The name of right hand object {} does not contain a file extension. '
                        'It is interpreted as an aspect.'.
                        format(tree_values[8]),
                        'De naam van het rechter object <{}> bevat geen file extensie. '
                        'Het is geïnterpreteerd als een aspect.'.
                        format(tree_values[8]))
                    self.selected_obj = self.uid_dict[str(tree_values[2])]
                    self.Display_message(
                        'Display aspect details of: {}'.format(self.selected_obj.name),
                        'Weergave van aspectdetails van: {}'.format(self.selected_obj.name))
                    self.Define_and_display_individual_detail_view(self.selected_obj)
            else:
                # Open the file in the file format that is defined by its file extension
                # from directory+file_name
                file_path = os.path.join(tree_values[5], tree_values[8])
                normalized_path = os.path.normpath(file_path)
                open_file(normalized_path)
        else:
            self.Display_message(
                'There is no right hand object found to be displayed.',
                'Er is geen rechter object gevonden om weergegeven te worden.')

    def Taxon_detail_view(self, widget):
        """ Find the selected object from a user selection that is made
            in the taxon_model that is displayed in the taxon_tree view.
            Then create a detail view of the selected item
        """
        # taxon_values = widget.get_text()
        # Debug print('Taxon selected kind:', self.row_values)
        kind_uid = widget.uid
        self.selected_obj = self.uid_dict[kind_uid]

        # Button 'Detail view is used, thus Create a detail view
        self.Define_and_display_kind_detail_view(self.selected_obj)

    def Classify_individual(self, widget):
        ''' Classify an earlier selected individual thing (candidate that is not yet classified)
            by the kind that is selected in the taxonomy view through
            adding a classification relation to the individual thing
            as well as to the kind in the semantic network.
        '''
        if self.modification == 'classification started':
            # Debug print('Taxon selected kind:', self.modified_object.name,
            #             self.selected_obj.name)
            # Append selected classifier to an individual modified_object,
            # by adding a classification relation to that object
            self.Add_classification_relation()
            self.modification = 'classification completed'

            # Display modified product view
            self.Define_and_display_individual_detail_view(self.modified_object)
            self.Display_message(
                'A classification of <{}> by classifier <{}> is added '
                'to the semantic network'.
                format(self.modified_object.name, self.selected_obj.name),
                'Een classifikatie van <{}> door classificeerder <{}> is toegevoegd '
                'aan het semantische netwerk.'.
                format(self.modified_object.name, self.selected_obj.name))
        else:
            if self.modified_object is None:
                self.Display_message(
                    'First select an individual thing before classifying it',
                    'Selecteer eerst een individueel iets voor het te classificeren')
            if self.selected_obj is None:
                self.Display_message(
                    'First select a kind and then classify '
                    'an earlier selected individual thing by that kind',
                    'Selecteer eerst een soort en classificeerd dan '
                    'een eerder geselecteerd individueel iets door die soort')
            if self.modified_object is not None and self.selected_obj is not None:
                self.Display_message(
                    'The classification of {} by classifier {} is NOT performed.'.
                    format(self.modified_object.name, self.selected_obj.name),
                    'De classifikatie van <{}> door classificeerder <{}> is NIET uitgevoerd.'.
                    format(self.modified_object.name, self.selected_obj.name))

    def Add_classification_relation(self):
        """ Append the (selected) kind as a classifier to the modified_object,
            and then add a classification relation to the classified individual thing
            as well as to the classifying kind.
        """
        statement = ['statement', 'bewering']
        self.modified_object.classifiers.append(self.selected_obj)

        # Add a classification expression to the list of expressions
        # of the classified object
        # First determine the first available free idea uid in the range
        max_num_uid = 212000000
        for num_uid in range(self.num_idea_uid, max_num_uid):
            idea_uid = str(num_uid)
            if idea_uid in self.idea_uids:
                continue
            else:
                self.num_idea_uid = num_uid
                self.idea_uids.append(idea_uid)
                break
            self.Display_message(
                'There is no uid for the idea available in the range {} to {}.'.
                format(self.num_idea_uid, max_num_uid),
                'Er is geen uid voor het idee beschikbaar in de range {} tot {}.'.
                format(self.num_idea_uid, max_num_uid))

        lang_uid = self.modified_object.names_in_contexts[0][0]
        lang_name = self.gel_net.lang_uid_dict[lang_uid]
        comm_uid = self.modified_object.names_in_contexts[0][1]
        comm_name = self.gel_net.community_dict[comm_uid]
        lang_comm = [lang_uid, lang_name, comm_uid, comm_name]
        lh_uid_name = [self.modified_object.uid, self.modified_object.name]
        rel_uid_phrase_type = ['1225', self.classification[self.GUI_lang_index], basePhraseUID]
        rh_role_uid_name = ['', '']
        # e.g. 43769, 'roofwindow'
        rh_uid_name = [self.selected_obj.uid, self.selected_obj.name]
        uom_uid_name = ['', '']
        description = ''
        intent_uid_name = ['491285', statement[self.GUI_lang_index]]
        rel_type = self.uid_dict['1225']
        gellish_expr = Create_gellish_expression(lang_comm, idea_uid, intent_uid_name,
                                                 lh_uid_name, rel_uid_phrase_type,
                                                 rh_role_uid_name, rh_uid_name,
                                                 uom_uid_name, description)
        relation = Relation(self.modified_object, rel_type, self.selected_obj,
                            basePhraseUID, '', gellish_expr)
        self.modified_object.add_relation(relation)
        self.selected_obj.add_relation(relation)

    def Summ_detail_view(self, widget):
        """ Find the selected object from a user selection that is made
            in the summ_model that is displayed in the summ_table view.
        """
        # summ_row_values = self.row_values
        # obj_uid = self.row_widgets[0].uid

        self.selected_obj = self.uid_dict[str(self.row_values[0])]
        # Debug print('Display of product details of:',self.row_values[0], self.selected_obj.name)
        # Create a detail view
        self.Define_and_display_individual_detail_view(self.selected_obj)

    def Possibilities_detail_view(self, widget):
        """ Find the selected object from a user selection that is made
            in the possibilities_model that is displayed in the possib_tree view.
        """
        # item_dict = self.possib_tree.selection()
        cur_item = self.possib_tree.focus()
        item_dict = self.possib_tree.item(cur_item)
        # Debug print('Detail view item:', item_dict['values'])
        tree_values = list(item_dict['values'])

        self.selected_obj = self.uid_dict[str(tree_values[0])]
        # Debug print('Display product details of:',tree_values[0], self.selected_obj.name)
        # Create a detail view
        self.Define_and_display_kind_detail_view(self.selected_obj)

    def Indiv_detail_view(self, widget):
        """ Find the selected object from a user selection that is made
            in the indiv_model that is displayed in the indiv_tree view.
        """
        # row_values = self.row_values
        obj_uid = self.row_widgets[0].uid
        self.selected_obj = self.uid_dict[obj_uid]
        # Debug print('Display product details of:', self.row_values[0], self.selected_obj.name)
        # Create a detail view
        self.Define_and_display_individual_detail_view(self.selected_obj)

    def Define_and_display_kind_detail_view(self, kind_obj):
        """ Create a detail view of a kind from a user selection
            and display the view in the kind_model view.
        """
        self.object_in_focus = kind_obj
        self.network_model[:] = []
        self.possibilities_model[:] = []
        self.kind_model[:] = []
        self.info_model[:] = []
        self.expr_table[:] = []
        self.all_subtypes[:] = []
        self.subtype_level = 0
        self.decomp_level = 0
        self.taxon_hierarchy[kind_obj] = 0
        self.net_hierarchy[kind_obj] = 0

        self.Build_single_product_view(kind_obj)

        if len(self.kind_model) > 0:
            self.Define_and_display_kind_view()

        if len(self.info_model) > 0:
            self.Define_and_display_documents()

        if len(self.expr_table) > 0:
            self.Define_and_display_expressions_view()

    def Define_and_display_individual_detail_view(self, individual_obj):
        """ Create a detail view of an individual object
            and display the view in the prod_model view.
        """
        self.prod_model[:] = []
        self.info_model[:] = []
        self.expr_table[:] = []
        self.object_in_focus = individual_obj
        self.subtype_level = 0
        self.decomp_level = 0
        self.Build_single_product_view(individual_obj)

        if len(self.prod_model) > 0:
            self.Define_and_display_product_model_view()

        if len(self.prod_model) > 0:
            self.Define_and_display_data_sheet()

        if len(self.info_model) > 0:
            self.Define_and_display_documents()

        if len(self.expr_table) > 0:
            self.Define_and_display_expressions_view()

    def Select_info(self, emitter, row, item):
        ''' Determine the row values that are selected in the info_view table.'''
        # Determine UID and Name of selected option
        info_row = list(row.children.values())
        self.object_uid = ''
        if len(info_row) > 0:
            self.info = info_row[0].get_text()
            self.kind_of_info = info_row[1].get_text()
            self.info_uid = info_row[0].uid
            self.info_text = info_row[0].description
            self.directory_name = info_row[2].get_text()
            self.object_uid = info_row[3].uid
            self.object_name = info_row[3].get_text()
            self.file_name = info_row[4].get_text()
            # Debug print('Display info:', self.info_uid, self.info,
            #       self.kind_of_info, self.directory)

    def Doc_detail_view(self, widget):
        """ Find the selected object from a user selection
            in the info_model that is displayed in the doc_table view.
            Determine and display a description text
            or launch an application to display the content of the selected file.
            - info_row('values') = [info.name, super_info_name, directory_name, obj.name,
                                    carrier.name, carrier_kind_name].
        """
        # info_row = widget.get_text()
        # Debug print('Selected info_row:', info_row)
        # If info_kind is a description then display the description
        description_text = ['description', 'beschrijving']
        if self.kind_of_info in description_text:
            # Debug print('Information {} is not presented on a carrier '
            #             'but is as follows:\n   {}'.
            #      format(info_row[4], info_row[2]))
            description_title = ['Information about ', 'Informatie over ']
            self.messagebox(description_title[self.GUI_lang_index] + self.object_name,
                            self.info_text)
        else:
            # Verify whether file name (info_row[3]) is presented on a file
            # And verify whether the file name has a file extension (indicated by a dot(.))
            parts = self.file_name.rsplit('.', maxsplit=1)
            if len(parts) == 1:
                self.Display_message(
                    'File name {} does not have a file extension'.format(self.object_name),
                    'Filenaam {} bevat geen file extensie'.format(self.object_name))
            else:
                # Open the file in the file format that is defined by its file extension
                if self.directory_name != '':
                    if not self.directory_name.startswith(os.sep):
                        # By default, we look in the app root dir.
                        # This assumes the app was started from the CommunicatorSource dir.
                        self.directory_name = ".." + os.sep + self.directory_name
                    file_path = os.path.join(self.directory_name, self.file_name)
                    normalized_path = os.path.normpath(file_path)
                    # Debug print('File path:', normalized_path)
                    open_file(normalized_path)

    def messagebox(self, box_title, text):
        ''' Display the text in a pop-up message box with box tile.'''
        self.message_box = gui.GenericDialog(title=box_title, message=text,
                                             style={'width': '400px', 'display': 'block',
                                                    'overflow': 'auto', 'text-align': 'left',
                                                    'background-color': '#eeffdd'})
        self.message_box.show(self.user_interface)

    def Object_detail_view(self, widget):
        """ Find the selected object from a user selection
            in the info_model that is displayed in the doc_table view.
            Determine and display a product view of the object
            about which the document provides info.
            - info_row('values') = [info.name, super_info_name, directory_name, obj.name,
                                    carrier.name, carrier_kind_name].
        """
        if self.object_uid != '':
            self.selected_obj = self.uid_dict[self.object_uid]
            # Debug print('Display product details of: {}'.format(self.selected_obj.name))
            self.Define_and_display_kind_detail_view(self.selected_obj)

            if len(self.info_model) > 0:
                self.Define_and_display_documents()

    def Contextual_facts(self, widget):
        ''' Display the contextual facts about the selected idea in expr_table.'''
        columns = ('Language', 'Community', 'Lh_UID', 'Lh_Name', 'Idea_UID',
                   'Rel_type_UID', 'Rel_type_Name', 'Rh_UID', 'Rh_Name',
                   'Uom_UID', 'UoM', 'Remarks', 'Status')
        head = ['Contextual facts about idea ', 'Contextuele feiten over idee ']
        idea_col = 4
        box_title = head[self.GUI_lang_index] + self.row_values[idea_col]
        # row_values[3, 6, 8] = lh_name, rel_type_name, rh_name
        text = 'idea: ' + self.row_values[3] + ' <' + self.row_values[6] + '> ' \
               + self.row_values[8]
        self.context_box = gui.GenericDialog(title=box_title, message=text,
                                             style={'width': '600px', 'display': 'block',
                                                    'overflow': 'auto', 'text-align': 'left',
                                                    'background-color': '#eeffdd'})
        # widget.children[key]
        # Language
        field_widget = gui.TextInput()
        field_widget.set_value(self.row_values[0])
        self.context_box.add_field_with_label(columns[0], columns[0], field_widget)
        # Community
        field_widget = gui.TextInput()
        field_widget.set_value(self.row_values[1])
        self.context_box.add_field_with_label(columns[1], columns[1], field_widget)

        self.context_box.show(self.user_interface)


class User_interface():
    def __init__(self):
        pass

    def Query_net(self):
        print('Query_net')

    def Stop_Quit(self):
        print('Stop_Quit')

    def build_network(self):
        print('Create and buid network')

    def Dump_net(self):
        print('Dump_net')


class Semantic_network():
    def __init__(self, name):
        self.name = name


if __name__ == "__main__":
    root = Tk()
    user_interface = User_interface()
    gel_net = Semantic_network('name')
    views = Display_views(gel_net)
    views.GUI_lang_index = 0
    views.lang_name = 'English'
    views.categoryInFocus = 'kind'

    views.user_interface.Define_notebook()
    views.Display_notebook_views()
    root.mainloop()
