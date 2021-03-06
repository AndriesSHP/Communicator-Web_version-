import remi.gui as gui
from operator import itemgetter

from gellish_communicator.Anything import Anything
from gellish_communicator.Bootstrapping import is_called_uid
from gellish_communicator.Create_output_file import Convert_numeric_to_integer
from gellish_communicator.Expr_Table_Def import (
    lh_uid_col,
    lh_name_col,
    lh_role_uid_col,
    rel_type_uid_col,
    rh_uid_col,
    rh_name_col,
    rh_role_uid_col,
    uom_name_col,
)
from gellish_communicator.remi_ext import MultiRowSelectionTable, SingleRowSelectionTable


class Query_view():
    """ Defines a query window
        for specification of searched/queries in the semantic network
        of dictionary, knowledge and information,
        including the display of a textual definition, synonyms and translations.
        Args:
        search_for = either 'subject' or 'object' or 'kind of relation'.
        relator_obj = either None or lh_obj
    """
    def __init__(self, user_interface, search_for, relator_obj=None):
        self.user_interface = user_interface
        self.gel_net = user_interface.gel_net
        self.views = user_interface.views
        self.query = user_interface.query
        self.unknown_quid = user_interface.unknown_quid
        self.root = user_interface.root
        self.GUI_lang_pref_uids = user_interface.GUI_lang_pref_uids
        self.comm_pref_uids = user_interface.comm_pref_uids

        self.GUI_lang_name = self.user_interface.GUI_lang_name
        self.GUI_lang_uid = self.user_interface.GUI_lang_uid
        self.GUI_lang_index = self.user_interface.GUI_lang_index
        self.relator_obj = relator_obj
        self.search_for = search_for  # 'subject' or 'object' or 'kind of relation'

        self.cs = 'cs'  # case sensitive - to search string
        self.fe = 'fi'  # front end identical

        self.lh_options = []
        self.rh_options = []
        self.rel_options = []
        self.uom_options = []
        self.unknowns = []  # List of unkown objects that are denoted by an unknown in a query
        self.names_of_unknowns = []
        self.unknown_kind = ['unknown kind', 'onbekende soort']

        # Set default terms for query in user interface
        self.lh_terms = ['elektriciteitskabel', '3 aderige kabel', 'YMvK kabel',
                         'breedte', 'materiaal', 'isolatieplaat']
        self.lh_terms.sort()
        self.rel_terms = ['is een soort',
                          'kan als aspect hebben een',
                          'moet als aspect hebben een',
                          'heeft per definitie als aspect een',
                          'heeft per definitie een schaalwaarde gelijk aan',
                          'heeft per definitie een schaalwaarde kleiner dan',
                          'heeft per definitie een schaalwaarde groter dan',
                          'is per definitie gekwalificeerd als']
        self.rel_terms.sort()
        self.rh_terms = self.lh_terms[:]
        # self.rh_terms.sort() # copy of lh_terms that are already sorted
        self.uoms = ['m', 'mm', 'bar', 'deg C']
        self.uoms.sort()

        self.reply_lang_names = ("English", "Nederlands", "American", "Chinese")
        self.reply_language = ['The reply language is', 'De antwoordtaal is']

        self.q_aspects = []
        self.options_widget = False
        self.aliases_widget = False
        self.aspects_widget = False

    def on_table_row_click(self, emitter, row, item):
        self.views.Display_message(
            "Selected item: {}".format(item.get_text()),
            "Geselecteerd object: {}".format(item.get_text()))

    def Define_query_window(self):
        """ Specify a Search term or UID
            or a Query expression with unknowns and possible multiline conditions.
            Display options for found objects that satisfy the search or query.
            Display definition and aliases and translations of selected option.
            Initiate seach for information about selected option
            by selecting confirmation button.
        """
        search_text = ["Search for ", "Zoek naar "]
        if self.search_for == 'object':
            related_to = ['object related to ', 'object gerelateerd aan']
            self.search_name = search_text[self.GUI_lang_index] \
                + related_to[self.GUI_lang_index] + self.relator_obj.name
        else:
            self.search_name = search_text[self.GUI_lang_index] + self.search_for
        self.query_widget = gui.Widget(height='100%', width='100%',
                                       style={'display': 'block',
                                              'background-color': '#eeffdd'})
        self.user_interface.views_noteb.add_tab(self.query_widget,
                                                self.search_name,
                                                self.user_interface.tab_cb)
        self.query_widget.attributes['title'] = 'Specify a (part of a) name or uid ' \
                                                'and select one of the presented options'
        line_width = 750
        if self.search_for == 'object':
            line_width = 850
        self.first_line_widget = gui.HBox(height=20, width=line_width, margin='4px',
                                          style={'position': 'static',
                                                 'background-color': '#eeffdd'})
        # Define a reply language with the language selector
        lang_text = ['Reply language:', 'Antwoordtaal:']
        reply_text = ['Select the language used for display of search results',
                      'Kies de taal waarin zoekresultaten weergegeven worden']
        self.reply_lang_label = gui.Label(lang_text[self.GUI_lang_index], width=100, height=20,
                                          style={'margin-left': '10px'})
        self.reply_lang_label.attributes['title'] = reply_text[self.GUI_lang_index]

        # Set default language: reply_lang_names[0] = English, [1] = Nederlands
        self.rep_lang_default = self.GUI_lang_name
        self.reply_lang_box = gui.DropDown(self.reply_lang_names, width=100, height=20,
                                           style='background-color:#ffffc0')
        self.reply_lang_box.attributes['title'] = reply_text[self.GUI_lang_index]

        # Binding reply language choice
        self.reply_lang_box.onchange.connect(self.Determine_reply_language)

        # String commonality buttons
        self.case_sensitive = True
        self.front_end_match = True

        case_text = ["Case sensitive", "Hoofdletter gevoelig"]
        front_end = ["Front end match", "Beginletter(s) kloppen"]

        case_sensitive_box = gui.CheckBox(checked=True, width=10, height=20)
        case_sensitive_box.attributes['title'] = 'Tick when search string is case sensitive'
        case_sensitive_box.onchange.connect(self.set_case)
        case_sensitive_text = gui.Label(case_text[self.GUI_lang_index], width=110, height=20)
        case_sensitive_text.attributes['title'] = 'Tick when search string is case sensitive'

        front_end_box = gui.CheckBox(checked=True, width=10, height=20)
        front_end_box.attributes['title'] = \
            'Tick when search string shall match with first character(s) of found string'
        front_end_box.onchange.connect(self.set_front_end)
        front_end_text = gui.Label(front_end[self.GUI_lang_index], width=110, height=20)
        front_end_text.attributes['title'] = \
            'Tick when search string shall match with first character(s) of found string'

        # Define buttons for confimation of the selection and for closing the tag
        confirm = ['Confirm', 'Bevestig']
        close = ['Close', 'Sluit']
        confirm_button = gui.Button(confirm[self.GUI_lang_index], width=100, height=20)
        if self.search_for == 'subject':
            confirm_button.attributes['title'] = 'Confirm that selected option is searched for'
        else:
            confirm_button.attributes['title'] = 'Confirm that options for expression ' \
                                                 'of knowledge are selected'
        confirm_button.onclick.connect(self.formulate_expression)

        search_close = gui.Button(close[self.GUI_lang_index], width=100, height=20)
        search_close.attributes['title'] = 'Close the search window'
        search_close.onclick.connect(self.user_interface.Close_tag,
                                     self.user_interface.views_noteb,
                                     self.search_name)

        # Widget locations in grid
        self.first_line_widget.append(case_sensitive_box)
        self.first_line_widget.append(case_sensitive_text)
        self.first_line_widget.append(front_end_box)
        self.first_line_widget.append(front_end_text)
        self.first_line_widget.append(self.reply_lang_label)
        self.first_line_widget.append(self.reply_lang_box)
        self.first_line_widget.append(confirm_button)
        if self.search_for == 'object':
            file_text = ['Search file', 'Zoek file']
            file_button = gui.Button(file_text[self.GUI_lang_index], width=100, height=20)
            file_button.attributes['title'] = 'Search for document that is related to object'
            file_button.onclick.connect(self.Search_file_with_document)
            self.first_line_widget.append(file_button)
        self.first_line_widget.append(search_close)
        if self.search_for == 'object':
            file_text = ['Search file', 'Zoek file']
            file_button = gui.Button(file_text[self.GUI_lang_index], width=100, height=20)
            file_button.attributes['title'] = 'Search for document that is related to object'
            file_button.onclick.connect(self.Search_file_with_document)
            self.first_line_widget.append(file_button)
        self.query_widget.append(self.first_line_widget)

        # Set default values in StringVar's
        self.q_lh_name = ''
        self.q_rel_name = ''
        self.q_rh_name = ''
        self.q_uom_name = ''
        self.q_lh_uid = ''
        self.q_rel_uid = ''
        self.q_rh_uid = ''
        self.q_uom_uid = ''
        self.query.q_lh_uid = ''
        self.query.q_rel_uid = ''
        self.query.q_rh_uid = ''
        self.query.q_uom_uid = ''
        self.query.q_uom_name = ''

        lhCondQStr = []
        relCondQStr = []
        rhCondQStr = []
        uomCondQStr = []
        for i in range(0, 3):
            lhCondQStr.append('')
            relCondQStr.append('')
            rhCondQStr.append('')
            uomCondQStr.append('')

        lh_term = ["Search term", "Zoekterm"]
        # rel_term = ["Relation type phrase", "Relatietype frase"]
        # rh_term = ["Right hand term", "Rechter term"]
        # uom_term = ["Unit of measure", "Meeteenheid"]

        # Lh name label and uid label and uid widget
        self.third_line_widget = gui.HBox(height=20, width='100%',
                                          style='background-color:#eeffdd')
        self.label_frame = gui.HBox(height=20, width=300,
                                    style='background-color:#eeffdd')
        lh_name_label = gui.Label(lh_term[self.GUI_lang_index], height=20, width=160,
                                  style='background-color:#eeffdd')
        lh_name_label.attributes['title'] = 'Specify a text string as part of the name '\
                                            'of an object to be searched'
        lh_uid_label = gui.Label('UID:', height=20, width=40,
                                 style='background-color:#eeffdd')
        lh_uid_label.attributes['title'] = 'A unique identifier of the searched object '\
                                           '(specified or found)'

        self.q_lh_uid_widget = gui.TextInput(self.q_lh_uid, height=20, width=100,
                                             style={'background-color': '#ffffc0',
                                                    "border-width": "1px",
                                                    "border-style": "solid"})
        self.q_lh_uid_widget.attributes['title'] = 'A unique identifier of the searched object '\
                                                   '(specified or found'
        self.q_lh_uid_widget.onkeyup.connect(self.Lh_uid_command)
        self.label_frame.append(lh_name_label)
        self.label_frame.append(lh_uid_label)
        self.label_frame.append(self.q_lh_uid_widget)
        self.third_line_widget.append(self.label_frame)
        self.query_widget.append(self.third_line_widget)

        # Lh_name (line 4)
        self.fourth_line_widget = gui.HBox(height=84, width='100%',
                                           style={'background-color': '#eeffdd',
                                                  'justify-content': 'flex-start',
                                                  'align-items': 'flex-start'})
        self.query_widget.append(self.fourth_line_widget)
        self.name_frame = gui.VBox(height=85, width=300,
                                   style={'background-color': '#eeffdd',
                                          'justify-content': 'flex-start',
                                          'align-items': 'flex-start'})
        self.q_lh_name_widget = gui.TextInput(self.q_lh_name, height=20, width=300,
                                              style={'background-color': '#ffffb0',
                                                     'border-width': '1px',
                                                     'border-style': 'solid',
                                                     'justify-content': 'flex-start',
                                                     'align-items': 'flex-start'})
        self.q_lh_name_widget.attributes['title'] = 'Enter a text string that is (part of) '\
                                                    'a name of the searched object'
        self.q_lh_name_widget.onkeyup.connect(self.lh_search_cmd)
        self.name_frame.append(self.q_lh_name_widget)
        # When knowledge is added specify kind of relation and right hand object
        if self.search_for == 'object':
            self.query.q_lh_uid = self.relator_obj.uid
            self.query.q_lh_name = self.relator_obj.name
            self.q_lh_uid_widget.set_value(self.relator_obj.uid)
            self.q_lh_name_widget.set_value(self.relator_obj.name)
            self.q_rel_name_widget = gui.TextInput(self.q_rel_name, height=20, width=300,
                                                   style={'background-color': '#ffffb0',
                                                          'border-width': '1px',
                                                          'border-style': 'solid',
                                                          'justify-content': 'flex-start'})
            self.q_rel_name_widget.onkeyup.connect(self.rel_search_cmd)

            self.q_rh_name_widget = gui.TextInput(self.q_rh_name, height=20, width=300,
                                                  style={'background-color': '#ffffb0',
                                                         'border-width': '1px',
                                                         'border-style': 'solid',
                                                         'justify-content': 'flex-start'})
            self.q_rh_name_widget.onkeyup.connect(self.rh_search_cmd)

            self.q_uom_name_widget = gui.TextInput(self.q_rh_name, height=20, width=300,
                                                   style={'background-color': '#ffffb0',
                                                          'border-width': '1px',
                                                          'border-style': 'solid',
                                                          'justify-content': 'flex-start'})
            self.q_uom_name_widget.onkeyup.connect(self.uom_search_cmd)
            self.name_frame.append(self.q_rel_name_widget)
            self.name_frame.append(self.q_rh_name_widget)
            self.name_frame.append(self.q_uom_name_widget)
        else:
            self.dummy_widget = gui.Label('', height=63, width=300,
                                          style={'background-color': '#eeffdd'})
            self.name_frame.append(self.dummy_widget)
        self.fourth_line_widget.append(self.name_frame)

        # Definition display widget
        def_text = ['Definition of the selected object:',
                    'Definitie van het geselecteerde object:']
        def_label = gui.Label(def_text[self.GUI_lang_index], height=20, width='100%',
                              style={'background-color': '#eeffdd', 'margin-left': '5px'})
        def_label.attributes['title'] = 'First select an object below, '\
                                        'then its definition will appear'
        # fullDefQStr = ''
        self.full_def_widget = gui.TextInput(single_line=False, width='100%', height=85,
                                             style={'justify-content': 'flex-start',
                                                    'align-items': 'flex-start',
                                                    'margin-left': '5px',
                                                    'border-width': '1px',
                                                    'border-style': 'solid'})
        if self.search_for == 'object':
            self.full_def_widget.attributes['title'] = \
                'Enter the partial definitiom of the selected object, '\
                'typically starting with "that ..."'
        else:
            self.full_def_widget.attributes['title'] = \
                'Display of the definitiom of the selected object'
        self.third_line_widget.append(def_label)
        self.fourth_line_widget.append(self.full_def_widget)

        # Aliases, options and aspects boxes on sixth line
        self.sixth_line_box = gui.HBox(height=280, width='100%',
                                       style={'background-color': '#eeffdd'})
        self.sixth_line_box.style['justify-content'] = 'flex-start'

        self.query_widget.append(self.sixth_line_box)

        # Options and aliases in sixth_line_left_box
        self.sixth_line_left_box = gui.VBox(height=280, width='60%',
                                            style={'background-color': '#eeffdd'})
        self.sixth_line_left_box.style['justify-content'] = 'flex-start'
        self.sixth_line_left_box.style['align-items'] = 'flex-start'

        # Options for selection widgets definition
        self.options_box = gui.VBox(height=180, width='100%',
                                    style={'overflow': 'auto',
                                           'background-color': '#eeffdd',
                                           'border-width': '1px',
                                           'border-style': 'solid'})
        self.options_box.style['justify-content'] = 'flex-start'
        self.options_box.style['align-items'] = 'flex-start'
        options_title = ['A table for searching and selecting objects '
                         'from the semantic network (dictionary)',
                         'Een tabel voor het zoeken en selecteren van objecten '
                         'uit het semantische netwerk (woordenboek)']
        self.options_box.attributes['title'] = options_title[self.GUI_lang_index]
        select_term = ["Select one of the following options:",
                       "Kies één van de volgende opties:"]
        self.options_heading = gui.Label(select_term[self.GUI_lang_index],
                                         height=20, width='99%')
        uid_col = ['UID', 'UID']
        name_col = ['Name', 'Naam']
        kind_col = ['Kind', 'Soort']
        comm_col = ['Community', 'Taalgemeenschap']
        lang_col = ['Language', 'Taal']
        # rela_col = ['Relation UID', 'Relatie UID']
        # right_col = ['Right UID', 'Rechter UID']

        self.options_table = SingleRowSelectionTable(
            width='100%',
            style={'background-color': '#eeffdd',
                   'border-width': '1px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto'})
        self.options_table_head = [(uid_col[self.GUI_lang_index],
                                    name_col[self.GUI_lang_index],
                                    kind_col[self.GUI_lang_index],
                                    comm_col[self.GUI_lang_index],
                                    lang_col[self.GUI_lang_index])]
        self.options_table.append_from_list(self.options_table_head, fill_title=True)
        self.options_table.on_table_row_click.connect(self.process_selected_option)
        self.options_widget = False

        # Aliases define alias label and alias box
        self.alias_box = gui.VBox(height=100, width='100%',
                                  style={'overflow': 'auto',
                                         'background-color': '#eeffdd'})
        self.alias_box.style['justify-content'] = 'flex-start'
        self.alias_box.style['align-items'] = 'flex-start'
        aliasText = ['Aliases for the name of the selected object:',
                     'Aliases voor de naam van het geselecteerde object:']
        self.alias_label = gui.Label(aliasText[self.GUI_lang_index], height=20, width='100%')
        self.alias_label.attributes['title'] = 'A table with synonyms, abbreviations and ' \
                                               'translations of the name of the selected object'
        lang_text = ('Language', 'Taal')
        term_text = ('Term', 'Term')
        alias_text = ('Alias type', 'Aliastype')

        self.aliases_table_widget = gui.Table(width='100%',
                                              style={'background-color': '#eeffdd',
                                                     'border-width': '1px',
                                                     'border-style': 'solid',
                                                     'font-size': '12px',
                                                     'table-layout': 'auto'})
        self.aliases_table_head = [(lang_text[self.GUI_lang_index],
                                    term_text[self.GUI_lang_index],
                                    alias_text[self.GUI_lang_index])]
        self.aliases_table_widget.append_from_list(self.aliases_table_head, fill_title=True)
        self.aliases_widget = False

        # Aspect frame widget
        self.aspects_frame = gui.VBox(height='99%', width='40%',
                                      style={'background-color': '#eeffdd',
                                             'border-width': '1px', 'border-style': 'solid'})
        self.aspects_frame.style['justify-content'] = 'flex-start'
        self.aspects_frame.style['align-items'] = 'flex-start'
        # Aspects label widget
        aspect_text = ['Aspects and known possible values:',
                       'Aspecten en bekende mogelijke waarden:']
        self.aspects_label = gui.Label(aspect_text[self.GUI_lang_index], height=20, width='100%')
        self.aspects_label.attributes['title'] = 'Aspects of the selected object '\
                                                 'and their possible values'
        self.aspects_widget = False
        self.aspects_frame.append(self.aspects_label)

        # Aspects table view for selection on aspect value(s)
        aspect_col = ['Aspect', 'Aspect']
        eq_col = ['>=<', '>=<']
        value_col = ['Value', 'Waarde']
        uom_col = ['UoM', 'Eenheid']

        self.aspects_table = MultiRowSelectionTable(
            width='100%',
            style={'overflow': 'scroll', 'background-color': '#eeffdd',
                   'border-width': '1px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto'})
        self.aspects_table_head = [(aspect_col[self.GUI_lang_index],
                                    eq_col[self.GUI_lang_index],
                                    value_col[self.GUI_lang_index],
                                    uom_col[self.GUI_lang_index])]
        self.aspects_table.append_from_list(self.aspects_table_head, fill_title=True)

        self.aspects_table.on_table_row_click.connect(self.Determine_selected_aspects)
        self.aspects_frame.append(self.aspects_table)

        # Set the reply language initially identical to the GUI language
        self.user_interface.Set_reply_language(self.GUI_lang_name)
        self.views.Display_message(
            'The reply language is {}'.format(self.user_interface.reply_lang_name),
            'De antwoordtaal is {}'.format(self.user_interface.reply_lang_name))

    def Search_file_with_document(self, widget):
        """ Select one file in a dialog and relate the file to the object."""
        self.read_file_container = gui.Widget(style={'width': '220px', 'display': 'block',
                                                     'overflow': 'auto', 'text-align': 'center'})
        self.user_interface.container.append(self.read_file_container)
        # Select one or more files to be imported
        self.dialog = gui.FileSelectionDialog('File selection dialog',
                                              'Select one file',
                                              False, '.',
                                              style='background-color:#eeffdd')
        self.dialog.confirm_value.connect(self.on_fileselection_dialog_confirm)
        self.dialog.cancel_dialog.connect(self.on_dialog_cancel)
        self.dialog.show(self)

    def on_fileselection_dialog_confirm(self, widget, filelist):
        ''' A list() of filenames and folders is returned'''
        print('Selected file: {}'.format(filelist))
        self.file_path_names = filelist

    def on_dialog_cancel(self, widget):
        self.set_root_widget(self.user_interface.container)

    def set_root_widget(self, root_widget):
        self.user_interface.set_root_widget(root_widget)

    def Determine_reply_language(self, widget):
        ''' Get the user specified reply language and report it.'''
        reply_lang_name = self.reply_lang_box.get()
        self.user_interface.Set_reply_language(reply_lang_name)
        self.views.Display_message(
            'The reply language is {}'.format(self.user_interface.reply_lang_name),
            'De antwoordtaal is {}'.format(self.user_interface.reply_lang_name))

    def Lh_uid_command(self, widget, new_value):
        """ Search for UID in semantic network
            Search in vocabulary for left hand uid.
            == OptionsTable: option_nr, whetherKnown, langUIDres, commUIDres,
                             result_string, resultUID, is_called_uid, kindKnown, kind
        """
        self.search_for = 'subject'
        self.lh_options[:] = []
        if self.options_widget is False:
            self.add_options_table()
        # Remove possible earlier options by making the options_table empty
        self.options_table.empty()
        self.options_table.append_from_list(self.options_table_head, fill_title=True)

        # Determine lh_options for lh uid in query
        lh_uid = new_value  # self.q_lh_uid_widget.get()
        try:
            lh = self.gel_net.uid_dict[lh_uid]

            # Debug print("  Found lh: ", lh_uid, lh.name)
            # => lh_options: option_nr, whetherKnown, langUIDres, commUIDres, result_string,
            #                resultUID, is_called_uid, kindKnown, kind
            if len(lh.names_in_contexts) > 0:
                # Debug print('Lang_prefs:', self.gel_net.reply_lang_pref_uids)
                # Debug print('Names in contexts:', lh.names_in_contexts)
                # Build option with preferred name from names_in_contexts
                # Determine the full definition of the obj in the preferred language
                lang_name, comm_name, preferred_name, full_def = \
                    self.user_interface.Determine_name_in_context(lh)
                option = [1, 'known'] + [lang_name, comm_name, preferred_name] \
                    + [lh.uid, '5117', 'known', lh.kind.name]
                # Debug print('Lh_option', option)
                self.lh_options.append(option)

                # Display option in options table
                uid = option[5]
                name = option[4]
                kind_name = option[8]
                opt = [uid, name, kind_name, comm_name, lang_name]

                row_widget = gui.TableRow()
                for field in opt:
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left'})
                    row_widget.append(row_item, field)
                self.options_table.append(row_widget, opt[1])

                # Display lh_object uid
                self.query.q_lh_uid = lh_uid

            # Delete earlier definition text and replace by new full definition text
            self.full_def_widget.set_text(full_def)
        except KeyError:
            pass

    def add_options_table(self):
        """ Append heading and options_table to options_box
            and append options_box to sixth_line_left_box
            and that to sixth_line_box.
        """
        self.options_box.append(self.options_heading)
        self.options_box.append(self.options_table)
        self.options_widget = True
        self.sixth_line_left_box.append(self.options_box)
        self.sixth_line_box.append(self.sixth_line_left_box)

    def set_case(self, widget, new_value):
        ''' Depending on user input determine whether the search string is case sensitive'''
        case_sens = new_value  # self.case_sensitive_var.get()
        if case_sens:
            self.cs = 'cs'   # case sensitive
        else:
            self.cs = 'ci'   # case insensitive

    def set_front_end(self, widget, new_value):
        ''' Depending on user input determine whether the front end part of the found name
            should comply with the front end part of the search string.'''
        front_end = new_value
        if front_end:
            self.fe = 'fi'   # front end identical
        else:
            self.fe = 'pi'   # part identical

    def lh_search_cmd(self, widget, new_value):
        """ Search or Query in semantic network
            An entry in QueryWindow can be just a name (lh_string)
            (for search on UID see Lh_uid_command)
            or a full question with possible condition expressions:
            (lh_string, rel_string, rh_string optionally followed by one or more conditions):

            lhCommonality = case sensitivity: 'cs/ci';
                                  (partially/front end) identical 'i/pi/fi'
            lhCommonality = input('Lh-commonality
                                  (default: csfi-case sensitive, front-end identical): ')

            Search in vocabulary for left hand term as part of building a question.

            == Options_table: option_nr, whetherKnown, langUIDres, commUIDres,
                             result_string, resultUID, is_called_uid, kindKnown, kind
        """
        self.search_for = 'subject'

        self.option_search_cmd(widget, new_value)

        # Delete earlier definition text.
        full_def = ''
        self.full_def_widget.set_text(full_def)

    def option_search_cmd(self, widget, new_value):
        """ Search in semantic network for a string in vocabulary for candidates
            (lh_string, rel_string, rh_string, uom_string)
            commonality = the extent in which the found string
                          corresponds to the search string
                          (default: csfi-case sensitive, front-end identical)
            Search for string in vocabulary for candidates for right hand term
            and build a question

            == Options: option_nr, whetherKnown, langUIDres, commUIDres,
                        result_string, resultUID, is_called_uid, kindKnown, kind
        """
        self.string_commonality = self.cs + self.fe

        # If no options_table yet, then add options_table to sixth_line_left_box
        if self.options_widget is False:
            self.add_options_table()

        # Remove possible earlier options by making the options_table empty
        self.options_table.empty()
        self.options_table.append_from_list(self.options_table_head, fill_title=True)

        # Determine options for term in expression
        self.search_string = new_value
        self.found_any_uid, self.any_options = self.Solve_unknown()

        # == any_options: option_nr, whetherKnown, lang_uid, comm_uid,
        #       result_string, result_uid, is_called_uid, kindKnown, kind
        # If options are available,
        # then sort the list of options,
        # and determine lang_names and display options
        if len(self.any_options) > 0:
            if len(self.any_options) > 1:
                # Sort the list of options alphabetically by name
                self.any_options.sort(key=itemgetter(4))
            for option in self.any_options:
                lang_uid = option[2]
                comm_uid = option[3]
                if lang_uid == 0:
                    lang_name = 'unknown'
                else:
                    if self.GUI_lang_index == 1:
                        lang_name = self.gel_net.lang_dict_NL[lang_uid]
                    else:
                        lang_name = self.gel_net.lang_dict_EN[lang_uid]
                if comm_uid == 0:
                    comm_name = 'unknown'
                else:
                    comm_name = self.gel_net.community_dict[comm_uid]

                # Display option in options table
                uid = option[5]
                name = option[4]
                kind_name = option[8]
                opt = [uid, name, kind_name, comm_name, lang_name]
                row_widget = gui.TableRow()
                for field in opt:
                    row_item = gui.TableItem(text=field,
                                             style={'text-align': 'left'})
                    row_widget.append(row_item, field)
                self.options_table.append(row_widget, opt[1])

        # Delete earlier definition text.
        full_def = ''
        self.full_def_widget.set_text(full_def)

    def rel_search_cmd(self, widget, new_value):
        """ Search or Query in semantic network
            Entry in QueryWindow is a question with possible condition expressions
            (lh_string, rel_string, rh_string, uom_string):

            commonality = the extent in which the found string corresponds to the search string
                          (default: csfi-case sensitive, front-end identical)

            Search in vocabulary for left hand, relation type and right hand terms
            for building an expression (question or assertion/statement)

            == Options: option_nr, whetherKnown, langUIDres, commUIDres,
                        result_string, resultUID, is_called_uid, kindKnown, kind
        """
        self.search_for = 'kind of relation'

        self.option_search_cmd(widget, new_value)

    def rh_search_cmd(self, widget, new_value):
        """ Search or Query in semantic network
            An entry in QueryWindow (lh_string, rel_string, rh_string, uom)
            is a question with possible condition expressions:
            rhCommonality = input('Rh-commonality
                                  (default: csfi-case sensitive, front-end identical): ')
            Search for string in vocabulary for candidates for right hand term
            and build a question

            == Options: option_nr, whetherKnown, langUIDres, commUIDres,
                        result_string, resultUID, is_called_uid, kindKnown, kind
        """
        self.search_for = 'object'

        self.option_search_cmd(widget, new_value)

    def uom_search_cmd(self, widget, new_value):
        """ Search in semantic network for the unit of measure (uom)."""
        self.search_for = 'uom'

        self.option_search_cmd(widget, new_value)

    def Determine_selected_aspects(self, widget, row, item):
        ''' Determine one or more selected aspects and their values
            and add them to the query.
            Note: values for the same aspects are alternative options (or)
                  values for different aspects are additional requirements (and).
        '''
        aspect_value = []
        self.query.aspect_values = []
        for aspect_row in self.aspects_table.selected_row_list:
            for val in aspect_row.children.values():
                # Debug print('Aspect value:', val.get_text())
                aspect_value.append(val.get_text())
            print('Query aspects:', aspect_value)
            self.query.aspect_values.append(aspect_value)

    def Solve_unknown(self):
        """ Determine the available options (UIDs and names) in the dictionary
            that match the search_string.
            Collect options in lh, rel, rh and uom optionsTables for display and selection.
            - search_string = the string to be found in gel_dict
              with corresponding lang_uid and comm_uid.
            - self.string_commonality is one of:
              cipi, cspi, cii, csi, cifi, csfi
              (case (in)sensitive partial/front end identical

            Returnparameters:
            == options (Lh, Rel or Rh):
               option_nr, whetherKnown, langUIDres, commUIDres, result_string,
               resultUID, isCalled, objectTypeKnown, kind (of resultUID).
               OptionTables have basically the same table structure
                 as the namingTable, but is extended with extra columns.

            == Gel_dict columns: [lang_uid, comm_uid, term], [UID, naming_uid, part_def]

            Process: Determine whether search_string equals 'what' etc.
                     or whether it occurs one or more times in vocabulary Gel_dict.
            Collect options in OptionTables, for selecting a preferred option.
        """
        # Initialize indicator whether the search string is an unknown (UID 1-99) or not.
        whetherKnown = 'unknown'
        objectTypeKnown = 'unknown'
        option = []
        options = []
        unknown_terms = ['', '?', 'any', 'what', 'which', 'who', 'where',
                         'wat', 'welke', 'wie', 'waar']
        found_uid = ''

        # If search string denotes an unknown from the list unknown_terms
        # then add unknown to the list of options
        if self.search_string in unknown_terms:
            if self.search_string == '':
                result_string = 'blank'
                return found_uid, options
            else:
                result_string = self.search_string
            if result_string not in self.names_of_unknowns:
                # Create an object for the (list of) unknown(s)
                self.unknown_quid += 1
                unknown = Anything(str(self.unknown_quid), result_string)
                self.unknowns.append(unknown)
                self.names_of_unknowns.append(result_string)
                option_nr = 1
                option.append(option_nr)
                option.append(whetherKnown)
                option.append(self.GUI_lang_pref_uids[1])
                option.append(self.comm_pref_uids[0])
                option.append(result_string)
                option.append(str(self.unknown_quid))
                option.append(is_called_uid)
                option.append(objectTypeKnown)
                option.append(self.unknown_kind[self.GUI_lang_index])

                options.append(option)
                found_uid = str(self.unknown_quid)
            else:
                # Search in earlier collected list of unknowns
                # for object with name search_string
                for unknown in self.unknowns:
                    if unknown.name == self.search_string:
                        found_uid = unknown.uid
                        continue
            if found_uid == '':
                self.user_interface.message_ui(
                    'No uid found.',
                    'Er is geen uid gevonden.')
            return found_uid, options

        # Search for full search_string in GellishDict
        candidates = self.gel_net.Query_network_dict(self.search_string, self.string_commonality)

        # Collect found option in 'options' list for display and selection
        if len(candidates) > 0:
            # Debug print ("nr of candidates:",len(candidates), self.GUI_lang_pref_uids)
            option_nr = 0
            for candidate in candidates:
                # Only add the candidate if uid of language
                # corresponds with uid from GUI_lang_pref_uids
                # because the query is in the GUI_language
                if candidate[0][0] not in self.GUI_lang_pref_uids:
                    continue
                whetherKnown = 'known'
                option = []
                option_nr += +1
                option.append(option_nr)
                option.append(whetherKnown)
                # Add candidate fields to option (in column (2,3,4),(5,6,7)
                for part in candidate:
                    for field in part:
                        option.append(field)
                # Debug print ("option:",len(candidates), option)

                # == option: option_nr, whetherKnown, langUID, commUID, result_string,
                #           resultUID, objectTypeKnown, kind_name (of resultUID).

                # If result_uid is a known uid (being alphanumeric or >= 100) then
                # then find the object and its supertype or classifier
                # and add the object to the list of options

                result_uid, integer = Convert_numeric_to_integer(option[5])
                if integer is False or result_uid >= 100:
                    # UID is of a known object (alpha or in range above unknowns (1-100))
                    # then identify the object.
                    obj = self.gel_net.uid_dict[str(result_uid)]

                    # Find and append the name of the kind
                    # (the supertype or classifier of the option)
                    if len(obj.supertypes) > 0:
                        pref_kind_name = obj.supertypes[0].name
                        # Find the first name in the preferred language
                        # of the first supertype in the GUI_language
                        if len(obj.supertypes[0].names_in_contexts) > 0:
                            lang_name, comm_name_supertype, pref_kind_name, descr_of_super = \
                                self.user_interface.Determine_name_in_context(obj.supertypes[0])
                    elif len(obj.classifiers) > 0:
                        pref_kind_name = obj.classifiers[0].name
                        # Find the first name in the preferred language
                        # of the first classifier in the GUI_language
                        if len(obj.classifiers[0].names_in_contexts) > 0:
                            lang_name, comm_name_supertype, pref_kind_name, descr_of_super = \
                                self.user_interface.Determine_name_in_context(obj.classifiers[0])
                    else:
                        pref_kind_name = obj.category
                    option.append(pref_kind_name)
                else:
                    # option.append('unknown')       # objectType
                    option.append(self.unknown_kind[self.GUI_lang_index])

                # Add the option to the list of options
                options.append(option)
                found_uid = option[5]

        # If not found in vocabulary, return with name of search_string
        # (being the unknown) and next UID.
        else:
            if self.search_string not in self.names_of_unknowns:
                self.unknown_quid += 1
                self.user_interface.message_ui(
                    'String "{}" is not found in the dictionary. New UID = {}. '.
                    format(self.search_string, self.unknown_quid),
                    'Term "{}" is niet gevonden in het woordenboek. Nieuw UID = {}. '.
                    format(self.search_string, self.unknown_quid))
                found_uid = self.unknown_quid
                self.names_of_unknowns.append(self.search_string)
                # Create an option for a new object
                unknown = Anything(str(self.unknown_quid), result_string)
                self.unknowns.append(unknown)
                option_nr = 1
                option.append(option_nr)
                option.append(whetherKnown)
                option.append(self.GUI_lang_pref_uids[1])
                option.append(self.comm_pref_uids[0])
                option.append(self.search_string)
                option.append(str(self.unknown_quid))
                option.append(is_called_uid)
                option.append(objectTypeKnown)
                option.append(self.unknown_kind[self.GUI_lang_index])
                options.append(option)
            else:
                # Search in unknowns for object with name search_string
                for obj in self.unknowns:
                    if obj.name == self.search_string:
                        found_uid = obj.uid
                        break
            if found_uid == '':
                self.user_interface.message_ui(
                    'The found UID is blank, which is incorrect.',
                    'De gevonden UID is blanco, hetgeen niet correct is.')
        return found_uid, options

    def process_selected_option(self, window, row, item):
        """ Put the object that is selected from any_options
            in the query (q_lh_name and q_lh_uid, q_rel, q_rh and q_uom)
            and display its textual definition, name and uid.
            Then determine the kinds of relations
            that relate to that lh_object or its subtypes
            for display their phrases in dropdown listbox and selection.
            And determine the synonyms and translations of lh_object name.
        """
        blank = ''
        # Determine UID and Name of the selected option
        values = list(row.children.values())
        any_uid = values[0].get_text()
        selected_name = values[1].get_text()

        # Delete earlier definition text in query view.
        full_def = ''
        self.full_def_widget.set_text(full_def)

        # Determine the selected object via its uid
        int_any_uid, integer = Convert_numeric_to_integer(any_uid)
        # If object is unknown then display message
        if integer is True and int_any_uid < 100:
            self.user_interface.message_ui(
                'Selected object with name "{}" is unknown'.format(selected_name),
                'Geselecteerd object met naam "{}" is onbekend'.format(selected_name))
            return
        # object is known: Find object
        any_object = self.gel_net.uid_dict[any_uid]
        any_object.name = selected_name

        # Determine the full definition and preferred_name
        # of the selected object in the preferred language
        lang_name, comm_name, preferred_name, full_def = \
            self.user_interface.Determine_name_in_context(any_object)

        # Display full definition
        self.full_def_widget.set_text(full_def)

        # Display selected UID and Name in selection fields
        self.q_lh_uid_widget.set_text(any_uid)
        # selected_name = preferred_name
        if self.search_for == 'subject':
            self.q_lh_name_widget.set_text(selected_name)
            self.query.q_lh_obj = any_object
            self.query.q_lh_uid = any_uid
            self.query.q_lh_name = selected_name
            self.query.q_lh_category = any_object.category
        elif self.search_for == 'kind of relation':
            self.q_rel_name_widget.set_text(selected_name)
            self.query.q_rel_uid = any_uid
            self.query.q_rel_name = selected_name
            self.query.q_rel_category = any_object.category
        elif self.search_for == 'object':
            self.q_rh_name_widget.set_text(selected_name)
            self.query.q_rh_uid = any_uid
            self.query.q_rh_name = selected_name
            self.query.q_rh_category = any_object.category
        elif self.search_for == 'uom':
            self.q_uom_name_widget.set_text(selected_name)
            self.query.q_uom_uid = any_uid
            self.query.q_uom_name = selected_name
            self.query.q_uom_category = any_object.category

        if self.search_for == 'subject':
            lh_object = any_object
            # Determine possible aspects of found lh_object
            self.q_aspects[:] = []

            # Determine the kinds of relations that relate to that lh_object
            # if integer is False or int_q_lh_uid >= 100:
            rel_options = []
            # lh_object = self.gel_net.uid_dict[self.query.q_lh_uid]
            # Determine list of subtypes of the lh_object
            sub_types, sub_type_uids = self.gel_net.Determine_subtypes(lh_object)
            sub_types.append(lh_object)
            for lh_obj_sub in sub_types:
                # Determine rel types and store results in self.lh_obj_relation_types
                self.Determine_rel_types_for_lh_object(lh_obj_sub)

                # Create option list for each found kind of relation
                for rel_type in self.lh_obj_relation_types:
                    if len(rel_type.base_phrases_in_contexts) > 0:
                        for phrase_in_context in rel_type.base_phrases_in_contexts:
                            # If language of phrase is as requested and phrase matches
                            # then add phrase to options (if not yet present)
                            if phrase_in_context[0] == self.GUI_lang_uid:
                                rel_option = phrase_in_context[2]
                                if rel_option not in rel_options:
                                    rel_options.append(rel_option)
                                    # Debug print('Rel type option:', rel_option)
                    elif len(rel_type.inverse_phrases_in_contexts) > 0:
                        # The same for an inverse phrase
                        for phrase_in_context in rel_type.inverse_phrases_in_contexts:
                            if phrase_in_context[0] == self.GUI_lang_uid:
                                rel_option = phrase_in_context[2]
                                if rel_option not in rel_options:
                                    rel_options.append(rel_option)
                                    # Debug print('Rel type option:', rel_option)
                self.Determine_aspect_and_value_options(lh_obj_sub)

            if self.aspects_widget is False:
                self.sixth_line_box.append(self.aspects_frame)
                self.aspects_widget = True
            # Delete previous characteristics, if any
            self.aspects_table.empty()
            self.aspects_table.append_from_list(self.aspects_table_head, fill_title=True)

            # Insert new list of characteristics in aspects_tree
            if len(self.q_aspects) > 0:
                # Sort aspect values by kind of aspect name and by value
                self.q_aspects.sort(key=itemgetter(4, 6))
                for asp in self.q_aspects:
                    # Debug print('Asp:', asp)
                    aspect_name = asp[1]
                    if aspect_name != '':
                        # Display kind of aspect name
                        aspect_row = gui.TableRow()
                        aspect_row_item = gui.TableItem(text=aspect_name,
                                                        style={'text-align': 'left'})
                        aspect_row.append(aspect_row_item)
                        self.aspects_table.append(aspect_row)

                        # Display aspect values
                        for asp_val in self.q_aspects:
                            name_value = asp_val[4]
                            if name_value == aspect_name:
                                equality = asp_val[5]
                                value = asp_val[6]
                                uom = asp_val[7]
                                aspect_row = gui.TableRow()
                                aspect_row_item = gui.TableItem(text=blank,
                                                                style={'text-align': 'left'})
                                aspect_row.append(aspect_row_item, blank)
                                aspect_row_item = gui.TableItem(text=equality,
                                                                style={'text-align': 'left'})
                                aspect_row.append(aspect_row_item, equality)
                                aspect_row_item = gui.TableItem(text=value,
                                                                style={'text-align': 'left'})
                                aspect_row.append(aspect_row_item, value)
                                aspect_row_item = gui.TableItem(text=uom,
                                                                style={'text-align': 'left'})
                                aspect_row.append(aspect_row_item, uom)
                                self.aspects_table.append(aspect_row)
            rel_options.sort()
            self.gel_net.rel_terms = rel_options

        # For any_object:
        # If alias_box not yet filled, the fill it
        if self.aliases_widget is False:
            self.alias_box.append(self.alias_label)
            self.alias_box.append(self.aliases_table_widget)
            self.aliases_widget = True
            self.sixth_line_left_box.append(self.alias_box)
        # Delete previous aliases in aliases_table and add title row
        self.aliases_table_widget.empty()
        self.aliases_table_widget.append_from_list(self.aliases_table_head, fill_title=True)

        # Determine synonyms and translations of lh_object name in various languages
        languages, alias_table = self.Determine_aliases(any_object)
        for language in languages:
            # Add language_row to table
            language_row = gui.TableRow()
            language_item = gui.TableItem(text=language,
                                          style={'text-align': 'left'})
            language_row.append(language_item, language_item)
            self.aliases_table_widget.append(language_row, language)

            # Add aliases rowa per language to the table
            for alias_row in alias_table:
                if alias_row[0] == language:
                    row_widget = gui.TableRow()
                    row_item = gui.TableItem(text='')
                    row_widget.append(row_item, language)
                    for field in alias_row[1:]:
                        row_item = gui.TableItem(text=field,
                                                 style={'text-align': 'left'})
                        row_widget.append(row_item, field)
                    self.aliases_table_widget.append(row_widget, alias_row[1])

    def Determine_aspect_and_value_options(self, lh_obj_sub):
        ''' Determine in a search the characteristics of lh_object and its subtypes
            and determine the available values for those characteristics.
            These are options for conditions that reduce the selection in a query.
        '''
        equality = '='
        for rel_obj in lh_obj_sub.relations:
            expr = rel_obj.expression
            if expr[rel_type_uid_col] in self.gel_net.subConcPossAspUIDs \
               and not expr[rel_type_uid_col] in self.gel_net.conc_playing_uids:
                # An aspect is found
                asp_opt = [expr[rh_uid_col], expr[rh_name_col], '', '', '', '', '', '']
                role_uid = expr[rh_role_uid_col]
                if asp_opt not in self.q_aspects:
                    self.q_aspects.append(asp_opt)
                    # Debug print('Aspect:', asp_opt)

                # Determine the value(s) for a found kind of aspect
                # Therefore, find a rh_role object (intrinsic aspect)
                # of a <can have as aspect a> relation or its subtypes.
                if role_uid != '':
                    role = self.gel_net.uid_dict[role_uid]

                    # Find criterion, constraints or value for intrinsic aspect, if any.
                    for rel_obj2 in role.relations:
                        expr2 = rel_obj2.expression
                        values = []
                        # Find compliancy criterion or constraint (4951)
                        # Find conceptual quantification (1791) value (on a scale)
                        # Find conceptual compliance criterion/qualif (4902)
                        # or def qualification
                        if role_uid == expr2[lh_uid_col] \
                                and (expr2[lh_role_uid_col] in self.gel_net.concComplUIDs
                                     or expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs
                                     or expr2[rel_type_uid_col]
                                     in self.gel_net.subConcComplRelUIDs):
                            values = [expr2[rh_uid_col], '', expr2[rel_type_uid_col],
                                      expr[rh_uid_col], expr[rh_name_col],
                                      equality, expr2[rh_name_col], expr2[uom_name_col]]
                        # Find compliancy criterion or constraint (inverse)
                        # Find conceptual quantification (1791) value (inverse)
                        # Find conceptual compliance criterion (inverse)
                        elif role_uid == expr2[rh_uid_col] \
                                and (expr2[rh_role_uid_col] in self.gel_net.concComplUIDs
                                     or expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs
                                     or expr2[rel_type_uid_col]
                                     in self.gel_net.subConcComplRelUIDs):
                            values = [expr2[lh_uid_col], '', expr2[rel_type_uid_col],
                                      expr[rh_uid_col], expr[rh_name_col],
                                      equality, expr2[lh_name_col], expr2[uom_name_col]]
                        if len(values) > 0:
                            if values not in self.q_aspects:
                                self.q_aspects.append(values)
                                # Debug print('Values:', values)

    def Determine_rel_types_for_lh_object(self, lh_object):
        ''' With given selected lh_object determine which kinds of relations are known
            and store results in self.lh_obj_relation_types
        '''
        self.lh_obj_relation_types = []
        for lh_obj_rel in lh_object.relations:
            expr = lh_obj_rel.expression
            rel_type = self.gel_net.uid_dict[expr[rel_type_uid_col]]
            if rel_type is None:
                self.user_interface.message_ui(
                    'The kind of relation {} is not found.'.format(expr[rel_type_uid_col]),
                    'De soort relatie {} is niet gevonden.'.format(expr[rel_type_uid_col]))
            else:
                if rel_type not in self.lh_obj_relation_types:
                    self.lh_obj_relation_types.append(rel_type)

                    # Determine_subtypes of the relation type
                    sub_rel_types, sub_rel_type_uids = \
                        self.gel_net.Determine_subtypes(rel_type)
                    for sub_rel_type in sub_rel_types:
                        if sub_rel_type not in self.lh_obj_relation_types:
                            self.lh_obj_relation_types.append(sub_rel_type)

    def Determine_aliases(self, obj):
        ''' Collect the names and translation that are known for obj
            in the alias_table for display aliases view.
            name_in_context = (lang_uid, comm_uid, name, naming_uid, description)
            alias_row = (language, term, alias_type)
        '''
        alias_table = []
        languages = []
        for name_in_context in obj.names_in_contexts:
            alias_type = self.gel_net.uid_dict[name_in_context[3]]
            # Determine preferred name of alias_type
            lang_name, comm_name, alias_name, full_def = \
                self.user_interface.Determine_name_in_context(
                    alias_type, base_or_inverse='base')

            language = self.gel_net.lang_uid_dict[name_in_context[0]]
            if language not in languages:
                languages.append(language)

            alias_row = (language, name_in_context[2], alias_name)
            if alias_row not in alias_table:
                alias_table.append(alias_row)
        return languages, alias_table

    def Set_selected_q_rel_term(self, ind):
        """ Put the selected relObject name and uid from relOptions
            in query (self.q_rel_name and self.q_rel_uid).
            Then determine the rh_objects
            that are related to the lh_object by such a relation or its subtypes
        """
        item = self.rel_options_tree.selection()
        ind = self.rel_options_tree.index(item)
        self.query.relSel = self.rel_options[ind]
        # Determine UID and Name of selected option
        self.query.q_rel_uid = self.query.relSel[5]
        self.query.q_rel_name = self.query.relSel[4]
        self.q_rel_uid.set(str(self.query.q_rel_uid))
        self.q_rel_name.set(self.query.q_rel_name)
        if self.query.q_rel_name in self.gel_net.total_base_phrases:
            self.query.q_phrase_type_uid = '6066'

        # Determine the rh_objects in the query
        # that are related by selected rel_object type or its subtypes
        # to the lh_object or its subtypes in the query
        int_q_lh_uid, integer = Convert_numeric_to_integer(self.query.q_lh_uid)
        if integer is False or int_q_lh_uid >= 100:
            rh_options = []
            # Determine list of subtypes of the rel_object
            q_rel_object = self.gel_net.uid_dict[self.query.q_rel_uid]
            q_rel_sub_types, q_rel_sub_type_uids = self.gel_net.Determine_subtypes(q_rel_object)
            q_rel_sub_types.append(q_rel_object)
            # Determine list of subtypes of the lh_object
            q_lh_obj = self.gel_net.uid_dict[self.query.q_lh_uid]
            q_lh_sub_types, q_lh_sub_type_uids = self.gel_net.Determine_subtypes(q_lh_obj)
            q_lh_sub_types.append(q_lh_obj)
            # For each relation of an lh_subtype verify if the relation type (rel_type_uid)
            # corresponds with the relation type of the query or one of its rel_subtypes.
            # If yes, then collect the rh_name in the list of rh_options.
            for lh_sub in q_lh_sub_types:
                for lh_sub_rel in lh_sub.relations:
                    expr = lh_sub_rel.expression
                    for rel_sub in q_rel_sub_types:
                        # Check if the relation types correspond
                        if expr[rel_type_uid_col] == rel_sub.uid:
                            # If the base relation corresponds the collect the rh name,
                            # if not yet present
                            if expr[lh_uid_col] == lh_sub.uid:
                                if expr[rh_name_col] not in rh_options:
                                    rh_options.append(expr[rh_name_col])
                            # If the inverse corresponds
                            elif expr[rh_uid_col] == lh_sub.uid:
                                if expr[lh_name_col] not in rh_options:
                                    rh_options.append(expr[lh_name_col])
                            # Debug print('lh_name, rh_name', expr[lh_name_col], expr[rh_name_col])
            rh_options.sort()
            self.gel_net.rh_terms = rh_options
            self.q_rh_name_widget.config(values=self.gel_net.rh_terms)

    def Set_selected_q_rh_term(self, ind):
        """ Put the selection of rhObject
            in self.q_rh_name and self.q_rh_uid.
        """

        item = self.rh_options_tree.selection()
        ind = self.rh_options_tree.index(item)
        self.query.rhSel = self.rh_options[ind]
        # Determine UID and Name of selected option
        self.query.q_rh_uid = self.query.rhSel[5]
        self.query.q_rh_name = self.query.rhSel[4]
        self.q_rh_uid.set(str(self.query.q_rh_uid))
        self.q_rh_name.set(self.query.q_rh_name)

    def formulate_expression(self, widget):
        """ Formulte one or more expressions
            being a query_spec on the network, based on the selected option(s)
            or new knowledge.
            If a kind of relation is specified
            then it includes a search for it and for its subtypes.
            Store resulting expressions in candids table
            with the same table definition.
        """
        # Make query_spec empty
        self.query.query_spec[:] = []
        self.query.ex_candids[:] = []

        # LH: Get selected option (textString)
        # from the presented list of options (lh_options_tree) in QueryWindow
        if self.query.q_lh_uid == '':
            self.user_interface.message_ui(
                'Left hand option is not yet selected. Please try again.',
                'Linker optie is nog niet geselecteerd. Probeer nogmaals.')
            return

        # Determine UID and Name of selected lh option
        # and formulate query expression (query_expr)
        self.query.query_expr = [self.query.q_lh_uid, self.query.q_lh_name]

        int_q_lh_uid, integer = Convert_numeric_to_integer(self.query.q_lh_uid)

        if self.search_for in ['object', 'kind of relation', 'uom']:
            # Search for related object
            self.views.create_knowledge_expression()
            return

##        # Deleted region for specification of a query as an expression of [lh, rel_type, rh]
##        # (no extended search specification)
##        # Rel: Selected relation type option
##        # Verify whether kind of relation is specified or only lh option is selected.
##        #   If yes then formulate query, else determine rel and rh part of query expression
##
##        if rel_uid_init != '':
##            # There is a kind of relation specified. Identify its uid and name
##            item = self.rel_options_tree.selection()
##            ind = self.rel_options_tree.index(item)
##            print('rel_ind', ind, self.rel_options)
##            self.query.relSel = self.rel_options[ind]
##
##            self.query.q_rel_uid = self.query.relSel[5]
##            self.query.q_rel_name = self.query.relSel[4]
##            self.q_rel_uid.set(str(self.query.q_rel_uid))
##            self.q_rel_name.set(self.query.q_rel_name)
##
##            int_q_rel_uid, integer = Convert_numeric_to_integer(self.query.q_rel_uid)
##            if integer is False or int_q_rel_uid >= 100:
##                self.query.q_rel_obj = self.gel_net.uid_dict[self.query.q_rel_uid]
##
##                # Determine phraseTypeUID of self.query.q_rel_name
##                self.query.q_phrase_type_uid = 0
##                if self.query.q_rel_name in self.gel_net.total_base_phrases:
##                    self.query.q_phrase_type_uid = '6066'   # base phrase
##                else:
##                    self.query.q_phrase_type_uid = '1986'   # inverse phrase
##
##                # Determine role_players_types because of q_rel_type
##                self.query.rolePlayersQTypes = self.query.q_rel_obj.role_players_types
##                self.query.rolePlayerQTypeLH = self.query.q_rel_obj.role_player_type_lh
##                self.query.rolePlayerQTypeRH = self.query.q_rel_obj.role_player_type_rh
##                # 6068 = binary relation between an individual thing and any (kind or individual)
##                if self.query.rolePlayersQTypes == 'individualsOrMixed':  # is related to (a)
##                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
##                        self.query.rolePlayersQTypes = 'individualAndMixed'
##                        self.query.rolePlayerQTypeLH = 'individual'
##                        self.query.rolePlayerQTypeRH = 'mixed'
##                    else:
##                        self.query.rolePlayersQTypes = 'mixedAndIndividual'
##                        self.query.rolePlayerQTypeLH = 'mixed'
##                        self.query.rolePlayerQTypeRH = 'individual'
##                # Binary relation between an individual thing and a kind
##                elif self.query.rolePlayersQTypes == 'mixed':
##                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
##                        self.query.rolePlayersQTypes = 'individualAndKind'
##                        self.query.rolePlayerQTypeLH = 'individual'
##                        self.query.rolePlayerQTypeRH = 'kind'
##                    else:
##                        self.query.rolePlayersQTypes = 'kindAndIndividual'
##                        self.query.rolePlayerQTypeLH = 'kind'
##                        self.query.rolePlayerQTypeRH = 'individual'
##                # 7071 = binary relation between a kind and any (kind or individual)
##                elif self.query.rolePlayersQTypes == 'kindsOrMixed':  # can be related to (a)
##                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
##                        self.query.rolePlayersQTypes = 'kindsAndMixed'  # can be related to (a)
##                        self.query.rolePlayerQTypeLH = 'kind'
##                        self.query.rolePlayerQTypeRH = 'mixed'
##                    else:
##                        self.query.rolePlayersQTypes = 'mixedAndKind'  # is or can be related to a
##                        self.query.rolePlayerQTypeLH = 'mixed'
##                        self.query.rolePlayerQTypeRH = 'kind'
##                else:
##                    pass
##
##            # RH: Selected right hand option
##            # Verify whether a rh name is specified
##            rh_uid_init = self.q_rh_uid_widget.get()
##            if rh_uid_init == '':
##                self.user_interface.message_ui(
##                    'Right hand option ís not (yet) selected.',
##                    'Rechter optie is nog niet geselecteerd.')
##            else:
##                # There is a rh name specified. Determine its name and uid and identity
##                item = self.rh_options_tree.selection()
##                ind = self.rh_options_tree.index(item)
##                self.query.rhSel = self.rh_options[ind]
##
##                self.query.q_rh_uid = self.query.rhSel[5]
##                self.query.q_rh_name = self.query.rhSel[4]
##                self.q_rh_uid.set(str(self.query.q_rh_uid))
##                self.q_rh_name.set(self.query.q_rh_name)
##
##                int_q_rh_uid, integer = Convert_numeric_to_integer(self.query.q_rh_uid)
##                if integer is False or int_q_rh_uid >= 100:
##                    self.query.q_rh_obj = self.gel_net.uid_dict[self.query.q_rh_uid]
##
##                # Report final query
##                queryText = ['Query ', 'Vraag   ']
##                self.views.log_messages.insert(
##                    'end', '\n\n{}: {} ({}) {} ({}) {} ({})'.
##                    format(queryText[self.GUI_lang_index],
##                           self.query.q_lh_name, self.query.q_lh_uid,
##                           self.query.q_rel_name, self.query.q_rel_uid,
##                           self.query.q_rh_name, self.query.q_rh_uid))
##                self.query.query_expr = [self.query.q_lh_uid, self.query.q_lh_name,
##                                         self.query.q_rel_uid, self.query.q_rel_name,
##                                         self.query.q_rh_uid, self.query.q_rh_name,
##                                         self.query.q_phrase_type_uid]

        # Append query expression as first line in query_spec
        # query_expr = lh_uid, lh_name, rel_uid, rel_name, rh_uid_rh_name, phrase_type_uid
        self.query.query_spec.append(self.query.query_expr)

        # Formulate coditions as are specified in the GUI
        self.query.Formulate_conditions_from_gui()

        # Prepare query for execution and execute query
        self.query.Interpret_query_spec()
        # Display query results in notebook sheets
        self.views.Display_notebook_views()
