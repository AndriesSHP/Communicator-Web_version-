import os
import remi.gui as gui
from operator import itemgetter

from Bootstrapping import ini_out_path, is_called_uid
from Expr_Table_Def import *
from Query import Query
from Anything import Anything
from Create_output_file import Create_gellish_expression, \
     Convert_numeric_to_integer, Open_output_file

class MyTable(gui.Table):
    ''' A subclass of gui.Table that has the feature
        that the last selected row is highlighted.
    '''
    @gui.decorate_event
    def on_table_row_click(self, row, item):
        if hasattr(self, "last_clicked_row"):
            del self.last_clicked_row.style['outline']
        self.last_clicked_row = row
        self.last_clicked_row.style['outline'] = "2px dotted blue"
        return (row, item)

class Query_view():
    ''' Defines a query window
        for specification of searched/queries in the semantic network
        of dictionary, knowledge and information,
        including the display of a textual definition, synonyms and translations.
    '''
    def __init__(self, gel_net, user_interface):
        self.gel_net = gel_net
        self.user_interface = user_interface
        self.views = user_interface.views
        self.query = user_interface.query
        self.unknown_quid = user_interface.unknown_quid
        self.root = user_interface.root
        self.GUI_lang_pref_uids = user_interface.GUI_lang_pref_uids
        self.comm_pref_uids = user_interface.comm_pref_uids

        self.GUI_lang_name = self.user_interface.GUI_lang_name
        self.GUI_lang_uid = self.user_interface.GUI_lang_uid
        self.GUI_lang_index = self.user_interface.GUI_lang_index

        self.cs = 'cs'  # case sensitive - to search string
        self.fe = 'fi'  # front end identical

        self.lh_options = []
        self.rh_options = []
        self.rel_options = []
        self.unknowns = [] # List of unkown objects that are denoted by an unknown in a query
        self.names_of_unknowns = []
        self.unknown_kind = ['unknown kind' ,'onbekende soort']

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
        #self.rh_terms.sort() # copy of lh_terms that are already sorted
        self.uoms = ['m', 'mm', 'bar', 'deg C']
        self.uoms.sort()

        self.reply_lang_names = ("English", "Nederlands",  "American",  "Chinese")
        self.reply_language = ['The reply language is', 'De antwoordtaal is']

        self.q_aspects = []
        self.options_widget = False
        self.aliases_widget = False
        self.aspects_widget = False

    def Query_window(self):
        """ Specify a Search term or UID
            or a Query expression with unknowns and possible multiline conditions.
            Display options for found objects that satisfy the search or query.
            Display definition and aliases and translations of selected option.
            Initiate seach for information about selected option
            by selecting confirmation button.
        """
        query_text = ["Search","Zoek"]
        self.query_widget = gui.Widget(height='100%', width='100%',
                                       style={'display':'block', 'background-color':'#eeffdd'})
        search_title = ['A table for searching and selecting objects '
                        'from the semantic network (dictionary)',
                        'Een tabel voor het zoeken en selecteren van objecten '
                        'uit het semantische netwerk (woordenboek)']
        self.query_widget.attributes['title'] = search_title[self.GUI_lang_index]
        self.user_interface.views_noteb.add_tab(self.query_widget,
                                                query_text[self.GUI_lang_index],
                                                self.user_interface.tab_cb)

        self.first_line_widget = gui.HBox(height=20, width=730, margin='5px',
                                          style='position:relative; background-color:#eeffdd')

        # Define reply language with language selector
        lang_text = ['Reply language:', 'Antwoordtaal:']
        reply_text = ['Select the language used for display of search results',
                      'Kies de taal waarin zoekresultaten weergegeven worden']
        self.reply_lang_label = gui.Label(lang_text[self.GUI_lang_index], width=100, height=20,
                                          style={'margin-left':'110px'})
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
        case_sensitive_text = gui.Label(case_text[self.GUI_lang_index], width=150, height=20)
        case_sensitive_text.attributes['title'] = 'Tick when search string is case sensitive'

        front_end_box = gui.CheckBox(checked=True, width=10, height=20)
        front_end_box.attributes['title'] = \
            'Tick when search string shall match with first character(s) of found string'
        front_end_box.onchange.connect(self.set_front_end)
        front_end_text = gui.Label(front_end[self.GUI_lang_index], width=150, height=20)
        front_end_text.attributes['title'] = \
            'Tick when search string shall match with first character(s) of found string'

        # Buttons definition
        confirm = ['Confirm','Bevestig']
        close = ['Close'  ,'Sluit']
        confirm_button = gui.Button(confirm[self.GUI_lang_index], width=100, height=20)
        confirm_button.attributes['title'] = 'Confirm that selected option is searched for'
        confirm_button.onclick.connect(self.Formulate_query_spec)

        close_button = gui.Button(close[self.GUI_lang_index], width=100, height=20)
        close_button.attributes['title'] = 'Close the search window'
        close_button.onclick.connect(self.Close_query,
                                     self.user_interface.views_noteb,
                                     self.query_widget)

        # Widget locations in grid
        self.first_line_widget.append(case_sensitive_box)
        self.first_line_widget.append(case_sensitive_text)
        self.first_line_widget.append(self.reply_lang_label)
        self.first_line_widget.append(self.reply_lang_box)
        self.first_line_widget.append(confirm_button)
        self.first_line_widget.append(close_button)
        self.query_widget.append(self.first_line_widget)

        self.second_line_widget = gui.HBox(height=20, width=190, margin='5px',
                                           style='background-color:#eeffdd')
        self.second_line_widget.append(front_end_box)
        self.second_line_widget.append(front_end_text)
        self.query_widget.append(self.second_line_widget)

        # Define English and Dutch example values (initial options) for query
        lhTermListEN = ['?', 'Paris', 'Eiffel tower', 'France']
        relTermListEN = ['?', 'is related to (a)', 'is related to', 'is classified as a',
                         'is located in', 'has as part']
        rhTermListEN = ['?', 'city', 'tower', 'country']
        uomTermListEN = ['', 'inch', 'mi', 's', 'degC', 'psi']

        lhTermListNL = ['?', 'N51', 'Groningen', 'Parijs', 'Eiffeltoren', 'Frankrijk']
        relTermListNL = ['?', 'is een soort', 'is gerelateerd aan (een)', 'is gerelateerd aan',
                         'is geclassificeerd als een', 'bevindt zich in', 'heeft als deel']
        rhTermListNL = ['?', 'isolatieplaat', 'weg', 'dorp', 'stad', 'toren', 'land']
        uomTermListNL = ['', 'mm', 'm', 's', '°C', 'bar']

        if self.GUI_lang_name == 'Nederlands' or 'Dutch':
            lhTermListD = lhTermListNL
            relTermListD = relTermListNL
            rhTermListD = rhTermListNL
            uomTermListD = uomTermListNL
        else:
            lhTermListD = lhTermListEN
            relTermListD = relTermListEN
            rhTermListD = rhTermListEN
            uomTermListD = uomTermListEN

        # Set default values in StringVar's
        self.q_lh_name_str = lhTermListD[0]
        self.q_rel_name_str = relTermListD[0]
        self.q_rh_name_str = rhTermListD[0]
        self.q_uom_name_str = uomTermListD[0]
        self.q_lh_uid_str = ''
        self.q_rel_uid_str = ''
        self.q_rh_uid_str = ''
        self.q_uom_uid_str = ''

        lhCondQStr = []
        relCondQStr = []
        rhCondQStr = []
        uomCondQStr = []
        for i in range(0,3):
            lhCondQStr.append ('')
            relCondQStr.append('')
            rhCondQStr.append ('')
            uomCondQStr.append('')

        lh_term = ["Search term", "Zoekterm"]
        rel_term = ["Relation type phrase", "Relatietype frase"]
        rh_term = ["Right hand term", "Rechter term"]
        uom_term = ["Unit of measure", "Meeteenheid"]

        # Query variables widgets definition
        self.third_line_widget = gui.HBox(height=20, width='100%',
                                          style='background-color:#eeffdd')
        self.label_frame = gui.HBox(height=20, width=300,
                                    style='background-color:#eeffdd')
        lhNameLbl = gui.Label(lh_term[self.GUI_lang_index], height=20, width=160,
                              style='background-color:#eeffdd')
        lhNameLbl.attributes['title'] = 'Specify a text string as part of the name '\
                                        'of an object to be searched'
        lhUIDLbl = gui.Label('UID:', height=20, width=40,
                             style='background-color:#eeffdd')
        lhUIDLbl.attributes['title'] = 'A unique identifier of the searched object '\
                                       '(specified or found)'

        self.q_lh_uid_widget = gui.TextInput(self.q_lh_uid_str, height=20, width=100,
                                             style={'background-color':'#ffffc0',
                                                    "border-width":"1px","border-style":"solid"})
        self.q_lh_uid_widget.attributes['title'] = 'A unique identifier of the searched object '\
                                                   '(specified or found'
        self.q_lh_uid_widget.onkeyup.connect(self.Lh_uid_command)
        self.label_frame.append(lhNameLbl)
        self.label_frame.append(lhUIDLbl)
        self.label_frame.append(self.q_lh_uid_widget)
        self.third_line_widget.append(self.label_frame)
        self.query_widget.append(self.third_line_widget)

        self.fourth_line_widget = gui.HBox(height=60, width='100%',
                                           style={'background-color':'#eeffdd',
                                                  'justify-content':'flex-start',
                                                  'align-items':'flex-start'})
        self.query_widget.append(self.fourth_line_widget)
        self.name_frame = gui.VBox(height=60, width=300,
                                   style={'background-color':'#eeffdd',
                                          'justify-content':'flex-start',
                                          'align-items':'flex-start'})
        self.q_lh_name_widget = gui.TextInput(height=20, width=300,
                                              style={'background-color':'#ffffb0',
                                                     'border-width':'2px', 'border-style':'solid',
                                                     'justify-content':'flex-start',
                                                     'align-items':'flex-start'})
        self.dummy_widget = gui.TextInput(height=40, width=300,
                                          style={'background-color':'#eeffdd'})

        self.q_lh_name_widget.attributes['title'] = 'Enter a text string that is (part of) '\
                                                    'a name of the searched object'
        self.q_lh_name_widget.onkeyup.connect(self.Lh_search_cmd)
        self.name_frame.append(self.q_lh_name_widget)
        self.name_frame.append(self.dummy_widget)
        self.fourth_line_widget.append(self.name_frame)

        # Definition display widget
        #self.fifth_line_widget = gui.HBox(height=60, width='100%')
        def_text = ['Definition of the selected object:',
                    'Definitie van het geselecteerde object:']
        def_label = gui.Label(def_text[self.GUI_lang_index], height=20, width='100%',
                              style={'background-color':'#eeffdd', 'margin-left':'5px'})
        def_label.attributes['title'] = 'First select an object below, '\
                                        'then its definition will appear'
        fullDefQStr = ''
        self.full_def_widget = gui.TextInput(single_line=False, width='100%', height=60,
                                             style={'justify-content':'flex-start',
                                                    'align-items':'flex-start',
                                                    'margin-left':'5px',
                                                    'border-width':'1px',
                                                    'border-style':'solid'})
        self.third_line_widget.append(def_label)
        self.fourth_line_widget.append(self.full_def_widget)

        # Aliases, options and aspects boxes on sixth line
        self.sixth_line_box = gui.HBox(height=600, width='100%',
                                       style={'background-color':'#eeffdd'})
        self.sixth_line_box.style['justify-content'] = 'flex-start'

        self.query_widget.append(self.sixth_line_box)

        # Aliases and options in sixth_line_left_box
        self.sixth_line_left_box = gui.VBox(height='99%', width='60%',
                                            style={'background-color':'#eeffdd',
                                                   "border-width":"3px",
                                                   "border-style":"solid"})
        self.sixth_line_left_box.style['justify-content'] = 'flex-start'
        self.sixth_line_left_box.style['align-items'] = 'flex-start'
        #self.sixth_line_box.append(self.sixth_line_left_box)

        # Aliases display label
        aliasText = ['Aliases for the name of the selected object:',
                     'Aliases voor de naam van het geselecteerde object:']
        self.alias_label = gui.Label(aliasText[self.GUI_lang_index], height=20, width='100%')
        self.alias_label.attributes['title'] = 'A table with synonyms, abbreviations and ' \
                                               'translations of the name of the selected object'
        #self.sixth_line_left_box.append(self.alias_label)

        lang_text = ('Language', 'Taal')
        term_text = ('Term', 'Term')
        alias_text = ('Alias type', 'Aliastype')

        self.aliases_table_widget = gui.Table(width='100%',
                                              style={"overflow":"auto",
                                                     "background-color":"#eeffdd",
                                                     "border-width":"2px",
                                                     "border-style":"solid",
                                                     "font-size":"12px",
                                                     'table-layout':'auto'})
        self.aliases_table_head = [(lang_text[self.GUI_lang_index],
                                    term_text[self.GUI_lang_index],
                                    alias_text[self.GUI_lang_index])]
        self.aliases_table_widget.append_from_list(self.aliases_table_head, fill_title=True)
        #self.sixth_line_left_box.append(self.aliases_table_widget)
        self.aliases_widget == False

        # Options for selection widgets definition
        select_term = ["Select one of the following options:",
                       "Kies één van de volgende opties:"]
        self.options_heading = gui.Label(select_term[self.GUI_lang_index], height=20, width=300)
        #self.sixth_line_left_box.append(self.options_heading)

        uid_col = ['UID', 'UID']
        name_col = ['Name', 'Naam']
        kind_col = ['Kind', 'Soort']
        comm_col = ['Community', 'Taalgemeenschap']
        lang_col = ['Language', 'Taal']
        rela_col = ['Relation UID', 'Relatie UID']
        right_col = ['Right UID', 'Rechter UID']

        self.options_table = MyTable(width='100%',
                                     style={"overflow":"auto", "background-color":"#eeffdd",
                                            "border-width":"2px", "border-style":"solid",
                                            "font-size":"12px", 'table-layout':'auto'})
        self.options_table_head = [(uid_col[self.GUI_lang_index],
                                    name_col[self.GUI_lang_index],
                                    kind_col[self.GUI_lang_index],
                                    comm_col[self.GUI_lang_index],
                                    lang_col[self.GUI_lang_index])]
        self.options_table.append_from_list(self.options_table_head, fill_title=True)

        self.options_table.on_table_row_click.connect(self.Set_selected_q_lh_term)
        #self.sixth_line_left_box.append(self.options_table)
        self.options_widget = False

        # Aspect frame widget
        self.aspects_frame = gui.VBox(height='99%', width='39%',
                                     style={'background-color':'#eeffdd',
                                            "border-width":"2px","border-style":"solid"})
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

        self.aspects_table = MyTable(width='100%',
                                     style={"overflow":"auto", "background-color":"#eeffdd",
                                            "border-width":"2px", "border-style":"solid",
                                            "font-size":"12px", 'table-layout':'auto'})
        self.aspects_table_head = [(aspect_col[self.GUI_lang_index],
                                    eq_col[self.GUI_lang_index],
                                    value_col[self.GUI_lang_index],
                                    uom_col[self.GUI_lang_index])]
        self.aspects_table.append_from_list(self.aspects_table_head, fill_title=True)

        self.aspects_table.on_table_row_click.connect(self.Determine_selected_aspects)
        self.aspects_frame.append(self.aspects_table)
        #self.sixth_line_box.append(self.aspects_frame)

        # Set the reply language initially identical to the GUI language
        self.user_interface.Set_reply_language(self.GUI_lang_name)
        self.views.Display_message(
                'The reply language is {}'.format(self.user_interface.reply_lang_name),
                'De antwoordtaal is {}'.format(self.user_interface.reply_lang_name))

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
        self.lh_options[:] = []
        # Remove possible earlier options by making the options_table empty
        if self.options_widget == False:
            self.sixth_line_box.append(self.sixth_line_left_box)
            self.sixth_line_left_box.append(self.options_heading)
            self.sixth_line_left_box.append(self.options_table)
            self.options_widget = True

        self.options_table.empty()
        self.options_table.append_from_list(self.options_table_head, fill_title=True)

        # Determine lh_options for lh uid in query
        lh_uid = new_value #self.q_lh_uid_widget.get()
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
                                             style={'text-align':'left'})
                    row_widget.append(row_item, field)
                    self.options_table.append(row_widget, opt[1])

                # Display lh_object uid
                self.query.q_lh_uid = lh_uid

            # Delete earlier definition text and replace by new full definition text
            self.full_def_widget.set_text(full_def)
        except KeyError:
            pass

    def set_case(self, widget, new_value):
        ''' Depending on user input determine whether the search string is case sensitive'''
        case_sens = new_value #self.case_sensitive_var.get()
        if case_sens:
            self.cs = 'cs'   # case sensitive
        else:
            self.cs = 'ci'   # case insensitive

    def set_front_end(self, widget, new_value):
        ''' Depending on user input determine whether the front end part of the found name
            should comply with the front end part of the search string.''' 
        front_end = self.front_end_match_var.get()
        if front_end:
            self.fe = 'fi'   # front end identical
        else:
            self.fe = 'pi'   # part identical

    def Lh_search_cmd(self, widget, new_value):
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

            == OptionsTable: option_nr, whetherKnown, langUIDres, commUIDres,
                             result_string, resultUID, is_called_uid, kindKnown,kind
        """
        # Tkinter options to be done: if event.keysym not in ['Shift_L', 'Shift_R']:
        self.string_commonality = self.cs + self.fe

        self.query.q_lh_uid = 0
        self.lh_options[:] = []
        # If no options_table yet, then add options_table to sixth_line_left_box
        if self.options_widget == False:
            self.sixth_line_box.append(self.sixth_line_left_box)
            self.sixth_line_left_box.append(self.options_heading)
            self.sixth_line_left_box.append(self.options_table)
            self.options_widget = True
        # Remove possible earlier options by making the options_table empty
        self.options_table.empty()
        self.options_table.append_from_list(self.options_table_head, fill_title=True)

        # Determine lh_options for lh term in query
        self.search_string = new_value #self.q_lh_name_widget.get()
        self.found_lh_uid, self.lh_options = \
                           self.Solve_unknown()
        # Debug print("  Found lh: ", self.lh_string, self.unknown_quid,
        #      self.lh_options[0:3])

        # => lh_options: option_nr, whetherKnown, langUIDres, commUIDres, result_string,
        #                resultUID, is_called_uid, kindKnown, kind
        # Sort the list of options alphabetically by name,
        # and determine lang_names and display options
        if len(self.lh_options) > 0:
            if len(self.lh_options) > 1:
                # Sort options by name
                self.lh_options.sort(key=itemgetter(4))
            # Find lang_name and comm_name from uids for option display
            for option in self.lh_options:
                if option[2] == '':
                    lang_name = 'unknown'
                else:
                    if self.GUI_lang_index == 1:
                        lang_name = self.gel_net.lang_dict_NL[option[2]]
                    else:
                        lang_name = self.gel_net.lang_dict_EN[option[2]]
                if option[3] == '':
                    comm_name = 'unknown'
                else:
                    comm_name = self.gel_net.community_dict[option[3]]

                # Display option in lh_options table
                uid = option[5]
                name = option[4]
                kind_name = option[8]
                opt = [uid, name, kind_name, comm_name, lang_name]

                row_widget = gui.TableRow()
                for field in opt:
                    row_item = gui.TableItem(text=field,
                                             style={'text-align':'left'})
                    row_widget.append(row_item, field)
                    self.options_table.append(row_widget, opt[1])

            # Display lh_object uid
            self.query.q_lh_uid = self.lh_options[0][5]

        # Delete earlier definition text. Then replace by new definition text
        full_def = ''
        int_q_lh_uid, integer = Convert_numeric_to_integer(self.query.q_lh_uid)
        if integer is False or int_q_lh_uid >= 100:
            # If lh_object is known then determine and display full definition
            self.query.q_lh_category = self.lh_options[0][8]
            obj = self.gel_net.uid_dict[self.query.q_lh_uid]
            # Determine the full definition of the obj in the preferred language
            lang_name, comm_name, preferred_name, full_def = \
                       self.user_interface.Determine_name_in_context(obj)
        # Display full definition
        self.full_def_widget.set_text(full_def)

    def Rel_search_cmd(self, widget):
        """ Search or Query in Ontology and Model
            Entry in QueryWindow is a question with possible condition expressions
            (lh_string, rel_string, rh_string):

            lhCommonality = 'csfi'
            lhCommonality = input('Lh-commonality
                                  (default: csfi-case sensitive, front-end identical): ')

            Search in vocabulary for left hand, relation type and right hand terms 
            and build a question

            == Options: option_nr, whetherKnown, langUIDres, commUIDres,
                        result_string, resultUID, is_called_uid, kindKnown,kind
        """

        # Debug print('Rel Entry:',event.char)
        if event.keysym not in ['Shift_L', 'Shift_R']:

            front_end = self.front_end_match_var.get()
            case_sens = self.case_sensitive_var.get()

            # Delete previous list of rel_options in tree
            self.rel_options[:] = []
            x = self.rel_options_tree.get_children()
            for item in x: self.rel_options_tree.delete(item)

            # Get relation type name (rel_string) from user interface
            #if event != '': rel_string = rel_string # + event.char
            if rel_string == 'any':
                if self.GUI_lang_index == 1:
                    rel_string = 'binaire relatie'
                else:
                    rel_string = 'binary relation'
            if rel_string == '':
                rel_string = 'binary relation'
            self.string_commonality = 'csfi'
            self.search_string = rel_string
            self.foundRel, self.rel_options = \
                           self.Solve_unknown()
            # Debug print('  OptRel:',self.rel_options)

            # == rel_opions: option_nr,whetherKnown, langUIDres, commUIDres,
            #                result_string, resultUID, is_called_uid, kindKnown,kind 
            # If rel_options are available, then sort the list and display in rel_options tree
            if len(self.rel_options) > 0:
                self.query.q_rel_uid = self.rel_options[0][5]
                int_q_rel_uid, integer = Convert_numeric_to_integer(self.query.q_rel_uid)
                if integer is False or int_q_rel_uid > 100:
                    obj = self.gel_net.uid_dict[self.query.q_rel_uid]
                    self.q_rel_uid_str.set(str(self.query.q_rel_uid))
                if len(self.rel_options) > 1:
                    # Sort the list of options alphabetically by name
                    self.rel_options.sort(key=itemgetter(4))
                for option in self.rel_options:
                    if option[2] == 0:
                        lang_name = 'unknown'
                    else:
                        lang_name = self.gel_net.lang_uid_dict[option[2]]
                    if option[3] == 0:
                        comm_name = 'unknown'
                    else:
                        comm_name = self.gel_net.community_dict[option[3]]
                    opt = [option[5], option[4], option[8], comm_name, lang_name]
                    self.rel_options_tree.insert('', index='end', values=opt)        

    def Rh_search_cmd(self, widget):
        """ Search or Query in Ontology and Model
            An entry in QueryWindow (lh_string, rel_string, rh_string)
            is a question with possible condition expressions:

            rhCommonality = input('Rh-commonality
                                  (default: csfi-case sensitive, front-end identical): ')

            Search for string in vocabulary for candidates for right hand term 
            and build a question

            == Options: option_nr, whetherKnown, langUIDres, commUIDres,
                        result_string, resultUID, is_called_uid, kindKnown,kind
        """
        # Debug print('Rh Entry:',event.char)
        if event.keysym not in ['Shift_L', 'Shift_R']:

            # Delete previous items in the rh_options in tree
            self.rh_options[:]  = []
            x = self.rh_options_tree.get_children()
            for item in x: self.rh_options_tree.delete(item)

            # Get the rh_string and search for options in the dictionary
            rh_string = self.q_rh_name_widget.get()
            self.search_string = rh_string
            self.foundRh, self.rh_options = \
                          self.Solve_unknown()
            # Debug print('  OptRh:',self.rh_options);

            # == rh_options: option_nr, whetherKnown, langUIDres, commUIDres,
            #                result_string, resultUID, is_called_uid, kindKnown,kind
            # If rh_options are available,
            # then sort the list and display them in the rh_options tree
            if len(self.rh_options) > 0:
                self.query.q_rh_uid = self.rh_options[0][5]
                #obj = self.gel_net.uid_dict[self.query.q_rh_uid]
                self.q_rh_uid_str.set(str(self.query.q_rh_uid))            
                self.query.q_rh_category = self.rh_options[0][8]
                if len(self.rh_options) > 1:
                    # Sort the list of options alphabetically by name
                    self.rh_options.sort(key=itemgetter(4))
                for option in self.rh_options:
                    if option[2] == 0:
                        lang_name = 'unknown'
                    else:
                        lang_name = self.gel_net.lang_uid_dict[option[2]]
                    if option[3] == 0:
                        comm_name = 'unknown'
                    else:
                        comm_name = self.gel_net.community_dict[option[3]]
                    opt = [option[5], option[4], option[8] ,comm_name, lang_name]
                    self.rh_options_tree.insert('', index='end', values=opt)

    def Determine_selected_aspects(self, widget, row, item):
        ''' Determine one or more selected aspects and their values
            and add them to the query.
            Note: values for the same aspects are alternative options (or)
                  values for different aspects are additional requirements (and).
        '''
        aspect_value = []
        self.query.aspect_values = []
        for val in row.children.values():
            # Debug print('Aspect value:', val.get_text())
            aspect_value.append(val.get_text())
        # Debug print('Query aspects:', aspect_value)
        self.query.aspect_values.append(aspect_value)

    def Solve_unknown(self):
        """ Determine the available options (UIDs and names) in the dictionary
            that match the search_string.
            Collect options in lh, rel and rh optionsTables for display and selection.
            - search_string = the string to be found in Gel_dict
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

            Process: Determine whether search_string equals 'what' etc. or whether it occurs one or more times in vocabulary Gel_dict.
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
##        is_called_uid = '5117'

        # If search string denotes an unknown from the list unknown_terms
        # then add unknown to the list of options
        if self.search_string in unknown_terms:
            if self.search_string == '':
                result_string = 'blank';
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

                #== option: option_nr, whetherKnown, langUID, commUID, result_string,
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
                    #option.append('unknown')       # objectType
                    option.append(self.unknown_kind[self.GUI_lang_index])

                # Add the option to the list of options 
                options.append(option)
                found_uid = option[5]

        # If not found in vocabulary, return with name of search_string
        # (being the unknown) and next UID.
        else:
            if self.search_string not in self.names_of_unknowns:
##                # Create an object for the (list of) unknown(s)
##                self.unknown_quid += 1
##                unknown = Anything(str(self.unknown_quid), self.search_string)
##                self.unknowns.append(unknown)
##                whetherKnown = 'unknown'
##                self.names_of_unknowns.append(self.search_string)
##                option_nr = 1
##                option.append(option_nr)
##                option.append(whetherKnown)
##                option.append(self.GUI_lang_pref_uids[1])
##                option.append(self.comm_pref_uids[0])
##                option.append(self.search_string)
##                option.append(str(self.unknown_quid))
##                option.append(is_called_uid)
##                option.append(objectTypeKnown)
##                option.append(self.unknown_kind[self.GUI_lang_index])
##
##                options.append(option)

                self.user_interface.message_ui(
                    'String "{}" is not found in the dictionary. UID = {}. '.
                    format(self.search_string, self.unknown_quid),
                    'Term "{}" is niet gevonden in het woordenboek. UID = {}. '.
                    format(self.search_string, self.unknown_quid))
                found_uid = self.unknown_quid
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

    def Set_selected_q_lh_term(self, window, row, item):
        """ Put the lh_object that is selected from lh_options
            in the query (q_lh_name_str and q_lh_uid_str)
            and display its textual definition, name and uid.
            Then determine the kinds of relations
            that relate to that lh_object or its subtypes
            for display their phrases in dropdown listbox and selection.
            And determine the synonyms and translations of lh_object name.
        """
        blank = ''
        # Determine UID and Name of selected option
        values = list(row.children.values())
        self.query.q_lh_uid = values[0].get_text()
        # Debug print('LH_uid', self.query.q_lh_uid)

        self.full_def_widget.set_text('')
        full_def = ''
        # Determine the selected object via its uid
        int_q_lh_uid, integer = Convert_numeric_to_integer(self.query.q_lh_uid)
        # If object is unknown then display message
        if integer is True and int_q_lh_uid < 100:
            search_string = values[1].get_text()
            self.user_interface.message_ui(
                'Selected object with name "{}" is unknown'.format(search_string),
                'Geselecteerd object met naam "{}" is onbekend'.format(search_string))
            return
        # Find object
        obj = self.gel_net.uid_dict[self.query.q_lh_uid]
        # Determine the full definition and preferred_name
        # of the selected object in the preferred language
        lang_name, comm_name, preferred_name, full_def = \
                   self.user_interface.Determine_name_in_context(obj)
        # Debug print('FullDef:',self.query.q_lh_uid, self.query.q_lh_name,
        #      self.query.q_lh_category,full_def)
        
        # Display full definition
        self.full_def_widget.set_text(full_def)

        # Display selected UID and Name in selection fields
        self.q_lh_uid_widget.set_text(self.query.q_lh_uid)
        selected_name = preferred_name
        self.q_lh_name_widget.set_text(selected_name)

        self.q_aspects[:] = []
        # If the lh_object is known,
        # then determine the kinds of relations that relate to that lh_object
        #is_called_uid = '5117'
        if integer is False or int_q_lh_uid >= 100:
            rel_options = []
            #opt_nr = 0
            lh_object = self.gel_net.uid_dict[self.query.q_lh_uid]
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

            if self.aspects_widget == False:
                self.sixth_line_box.append(self.aspects_frame)
                self.aspects_widget = True
            # Delete previous characteristics, if any
            self.aspects_table.empty()
            self.aspects_table.append_from_list(self.aspects_table_head, fill_title=True)

            # Insert new list of characteristics in aspects_tree
            if len(self.q_aspects) > 0:
                # Sort aspect values by kind of aspect name and by value
                self.q_aspects.sort(key=itemgetter(4,6))
                for asp in self.q_aspects:
                    # Debug print('Asp:', asp)
                    aspect_name = asp[1]
                    if aspect_name != '':
                        # Display kind of aspect name
                        aspect_row = gui.TableRow()
                        aspect_row_item = gui.TableItem(text=aspect_name,
                                                        style={'text-align':'left'})
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
                                                                style={'text-align':'left'})
                                aspect_row.append(aspect_row_item, blank)
                                aspect_row_item = gui.TableItem(text=equality,
                                                                style={'text-align':'left'})
                                aspect_row.append(aspect_row_item, equality)
                                aspect_row_item = gui.TableItem(text=value,
                                                                style={'text-align':'left'})
                                aspect_row.append(aspect_row_item, value)
                                aspect_row_item = gui.TableItem(text=uom,
                                                                style={'text-align':'left'})
                                aspect_row.append(aspect_row_item, uom)
                                self.aspects_table.append(aspect_row)
            rel_options.sort()
            self.gel_net.rel_terms = rel_options

            # Delete previous aliases in alias_tree
            if self.aliases_widget == False:
                self.sixth_line_left_box.append(self.alias_label)
                self.sixth_line_left_box.append(self.aliases_table_widget)
                self.aliases_widget == True
            self.aliases_table_widget.empty()
            self.aliases_table_widget.append_from_list(self.aliases_table_head, fill_title=True)

            # Determine synonyms and translations of lh_object name in various languages        
            languages, alias_table = self.Determine_aliases(lh_object)
            for language in languages:
                # Add language_row to table
                language_row = gui.TableRow()
                language_item = gui.TableItem(text=language,
                                              style={'text-align':'left'})
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
                                                     style={'text-align':'left'})
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
                             and (expr2[lh_role_uid_col] in self.gel_net.concComplUIDs \
                                  or expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs \
                                  or expr2[rel_type_uid_col] in self.gel_net.subConcComplRelUIDs):
                            values = [expr2[rh_uid_col], '', expr2[rel_type_uid_col],
                                      expr[rh_uid_col], expr[rh_name_col],
                                      equality, expr2[rh_name_col], expr2[uom_name_col]]
                        # Find compliancy criterion or constraint (inverse)
                        # Find conceptual quantification (1791) value (inverse)
                        # Find conceptual compliance criterion (inverse)
                        elif role_uid == expr2[rh_uid_col] \
                             and (expr2[rh_role_uid_col] in self.gel_net.concComplUIDs \
                                  or expr2[rel_type_uid_col] in self.gel_net.concQuantUIDs \
                                  or expr2[rel_type_uid_col] in self.gel_net.subConcComplRelUIDs):
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
                if rel_type == None:
                    self.user_interface.message_ui(
                        'The kind of relation {} is not found.'.format(rel_type_uid),
                        'De soort relatie {} is niet gevonden.'.format(rel_type_uid))
                else:
                    if rel_type not in self.lh_obj_relation_types:
                        self.lh_obj_relation_types.append(rel_type)

                        # Determine_subtypes of the relation type
                        sub_rel_types, sub_rel_type_uids = self.gel_net.Determine_subtypes(rel_type)
                        for sub_rel_type in sub_rel_types:
                            if sub_rel_type not in self.lh_obj_relation_types:
                                self.lh_obj_relation_types.append(sub_rel_type)

    def Determine_aliases(self, obj):
        ''' Collect the names and translation that are known for obj
            in the alias_table for display in alias_tree treeview.
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
                           alias_type, base_or_inverse = 'base')

            language = self.gel_net.lang_uid_dict[name_in_context[0]]
            if language not in languages:
                languages.append(language)

            alias_row = (language, name_in_context[2], alias_name)
            if alias_row not in alias_table:
                alias_table.append(alias_row)
        return languages, alias_table

    def Set_selected_q_rel_term(self, ind):
        """ Put the selected relObject name and uid from relOptions
            in query (self.q_rel_name_str and self.q_rel_uid_str).
            Then determine the rh_objects
            that are related to the lh_object by such a relation or its subtypes
        """
        item   = self.rel_options_tree.selection()
        ind    = self.rel_options_tree.index(item)
        self.query.relSel = self.rel_options[ind]
        # Determine UID and Name of selected option
        self.query.q_rel_uid  = self.query.relSel[5]
        self.query.q_rel_name = self.query.relSel[4]
        self.q_rel_uid_str.set(str(self.query.q_rel_uid))
        self.q_rel_name_str.set(self.query.q_rel_name)
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
        """Put the selection of rhObject in self.q_rh_name_str and self.q_rh_uid_str"""

        item  = self.rh_options_tree.selection()
        ind   = self.rh_options_tree.index(item)
        self.query.rhSel = self.rh_options[ind]
        # Determine UID and Name of selected option
        self.query.q_rh_uid  = self.query.rhSel[5]
        self.query.q_rh_name = self.query.rhSel[4]
        self.q_rh_uid_str.set(str(self.query.q_rh_uid))
        self.q_rh_name_str.set(self.query.q_rh_name)

    def Formulate_query_spec(self, widget):
        """Formulte a query_spec on the network for the relation type and its subtypes.
           Store resulting query expressions in candids table with the same table definition.
        """
        # Make query_spec empty
        self.query.query_spec[:] = []
        self.query.ex_candids[:] = []

        # LH: Get selected option (textString)
        # from the presented list of options (lh_options_tree) in QueryWindow
        lh_uid_init = self.q_lh_uid_widget.get_text()
        if lh_uid_init == '':
            self.user_interface.message_ui(
                'Left hand option is not yet selected. Please try again.',
                'Linker optie is nog niet geselecteerd. Probeer nogmaals.')
            return

        # Determine UID and Name of selected lh option
        # and formulate query expression (query_expr)
        self.query.q_lh_uid = lh_uid_init
        self.query.q_lh_name = self.q_lh_name_widget.get_text()
        self.query.query_expr = [self.query.q_lh_uid, self.query.q_lh_name]

        # Delete earlier definition text in query_window.
        self.full_def_widget.set_text('')

        # If lh_object is known then determine and display its full definition
        int_q_lh_uid, integer = Convert_numeric_to_integer(self.query.q_lh_uid)
        if integer is False or int_q_lh_uid >= 100:
            self.query.q_lh_obj = self.gel_net.uid_dict[self.query.q_lh_uid]
            self.query.q_lh_category = self.lh_options[0][8]

            # Determine the full definition of the selected object in the preferred language
            lang_name, comm_name, preferred_name, full_def = \
                       self.user_interface.Determine_name_in_context(self.query.q_lh_obj)
            # Debug print('Full def:', self.query.q_lh_uid, self.lh_string,
            #             self.query.q_lh_category, full_def)
            # Display full definition
            self.full_def_widget.set_text(full_def)

        # Rel: Selected relation type option
        # Verify whether kind of relation is specified or only lh option is selected.
        #   If yes then formulate query, else determine rel and rh part of query expression 

        # Initial rel_uid_init set to blank ('') to indicate the no query expression is specified
        # (no extended search specification)
        rel_uid_init = ''
        if rel_uid_init != '':
            # There is a kind of relation specified. Identify its uid and name
            item = self.rel_options_tree.selection()
            ind = self.rel_options_tree.index(item)
            print('rel_ind', ind, self.rel_options)
            self.query.relSel = self.rel_options[ind]

            self.query.q_rel_uid = self.query.relSel[5]
            self.query.q_rel_name = self.query.relSel[4]
            self.q_rel_uid_str.set(str(self.query.q_rel_uid))
            self.q_rel_name_str.set(self.query.q_rel_name)

            int_q_rel_uid, integer = Convert_numeric_to_integer(self.query.q_rel_uid)
            if integer is False or int_q_rel_uid >= 100:
                self.query.q_rel_obj = self.gel_net.uid_dict[self.query.q_rel_uid]

                # Determine phraseTypeUID of self.query.q_rel_name
                self.query.q_phrase_type_uid = 0
                if self.query.q_rel_name in self.gel_net.total_base_phrases:
                    self.query.q_phrase_type_uid = '6066'   # base phrase
                else:
                    self.query.q_phrase_type_uid = '1986'   # inverse phrase

                # Determine role_players_types because of q_rel_type
                self.query.rolePlayersQTypes = self.query.q_rel_obj.role_players_types
                self.query.rolePlayerQTypeLH = self.query.q_rel_obj.role_player_type_lh
                self.query.rolePlayerQTypeRH = self.query.q_rel_obj.role_player_type_rh
                # 6068 = binary relation between an individual thing and any (kind or individual)
                if self.query.rolePlayersQTypes == 'individualsOrMixed':  # is related to (a)
                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
                        self.query.rolePlayersQTypes = 'individualAndMixed'
                        self.query.rolePlayerQTypeLH = 'individual'
                        self.query.rolePlayerQTypeRH = 'mixed'
                    else:
                        self.query.rolePlayersQTypes = 'mixedAndIndividual'
                        self.query.rolePlayerQTypeLH = 'mixed'
                        self.query.rolePlayerQTypeRH = 'individual'
                # Binary relation between an individual thing and a kind
                elif self.query.rolePlayersQTypes == 'mixed':
                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
                        self.query.rolePlayersQTypes = 'individualAndKind'
                        self.query.rolePlayerQTypeLH = 'individual'
                        self.query.rolePlayerQTypeRH = 'kind'
                    else:
                        self.query.rolePlayersQTypes = 'kindAndIndividual'
                        self.query.rolePlayerQTypeLH = 'kind'
                        self.query.rolePlayerQTypeRH = 'individual'
                # 7071 = binary relation between a kind and any (kind or individual)
                elif self.query.rolePlayersQTypes == 'kindsOrMixed':  # can be related to (a)
                    if self.query.q_rel_name in self.gel_net.total_base_phrases:
                        self.query.rolePlayersQTypes = 'kindsAndMixed' # can be related to (a)
                        self.query.rolePlayerQTypeLH = 'kind'
                        self.query.rolePlayerQTypeRH = 'mixed'
                    else:
                        self.query.rolePlayersQTypes = 'mixedAndKind' # is or can be related to a
                        self.query.rolePlayerQTypeLH = 'mixed'
                        self.query.rolePlayerQTypeRH = 'kind'
                else:
                    pass

            # RH: Selected right hand option
            # Verify whether a rh name is specified
            rh_uid_init = self.q_rh_uid_widget.get()
            if rh_uid_init == '':
                self.user_interface.message_ui(
                    'Right hand option ís not (yet) selected.',
                    'Rechter optie is nog niet geselecteerd.')
            else:
                # There is a rh name specified. Determine its name and uid and identity
                item = self.rh_options_tree.selection()
                ind = self.rh_options_tree.index(item)
                self.query.rhSel = self.rh_options[ind]

                self.query.q_rh_uid = self.query.rhSel[5]
                self.query.q_rh_name = self.query.rhSel[4]
                self.q_rh_uid_str.set(str(self.query.q_rh_uid))
                self.q_rh_name_str.set(self.query.q_rh_name)

                int_q_rh_uid, integer = Convert_numeric_to_integer(self.query.q_rh_uid)
                if integer is False or int_q_rh_uid >= 100:
                    self.query.q_rh_obj = self.gel_net.uid_dict[self.query.q_rh_uid]

                # Report final query
                queryText = ['Query ','Vraag   ']
                self.views.log_messages.insert('end','\n\n{}: {} ({}) {} ({}) {} ({})'.
                    format(queryText[self.GUI_lang_index],
                           self.query.q_lh_name, self.query.q_lh_uid,
                           self.query.q_rel_name, self.query.q_rel_uid,
                           self.query.q_rh_name, self.query.q_rh_uid))
                self.query.query_expr = [self.query.q_lh_uid, self.query.q_lh_name,
                                         self.query.q_rel_uid, self.query.q_rel_name,
                                         self.query.q_rh_uid, self.query.q_rh_name,
                                         self.query.q_phrase_type_uid]

        # Append query expression as first line in query_spec
        # query_expr = lh_uid, lh_name, rel_uid, rel_name, rh_uid_rh_name, phrase_type_uid
        self.query.query_spec.append(self.query.query_expr)

        # Formulate coditions as are specified in the GUI 
        self.query.Formulate_conditions_from_gui()

        # Prepare query for execution and execute query
        self.query.Interpret_query_spec()
        # Display query results in notebook sheets
        self.views.Display_notebook_views()

    def Close_query(self, widget, tabbox, refWidgetTab):
        ''' Close the tab about the Search'''
        query_text = ["Search", "Zoek"]
        tabbox.select_by_widget(refWidgetTab)
        tabbox.remove_tab_by_name(query_text[self.GUI_lang_index])


class User_interface():
    def __init__(self):
        self.root = Tk()
        
if __name__ == "__main__":
    
    main = Main()
    user_interface = User_interface()
    gel_net = Semantic_network()
    main_view = Query_views(gel_net, user_interface)
    
    root.mainloop()
