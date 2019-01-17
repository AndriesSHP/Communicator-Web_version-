import remi.gui as gui
from remi import start, App

import sys
import pickle
import webbrowser

import SystemUsers as SU
from Gellish_file import Gellish_file
from SemanticNetwork import Semantic_Network
from Query import Query
from QueryViews import Query_view
from Display_views import Display_views
from Create_output_file import Convert_numeric_to_integer
from Bootstrapping import is_called_uid


class MyTabBox(gui.TabBox):
    ''' Sub-class of TabBox that enables to remove a tab that is identified by its name.'''
    def remove_tab_by_name(self, name):
        ''' Removes a tab that is identified by its name.'''
        identifier = None
        for a, li, holder in self._tabs.values():
            if a.children['text'] == name:
                a.get_parent().remove_child(a)
                li.get_parent().remove_child(li)
                holder.get_parent().remove_child(holder)
                self._tab_cbs.pop(holder.identifier)
                identifier = holder.identifier
        if identifier is not None:
            self._tabs.pop(holder.identifier)

    def _fix_tab_widths(self):
        tab_w = 100.0 / len(self._tabs)
        for a, li, holder in self._tabs.values():
            li.style['float'] = "left"
            # Specify the size percentage
            li.style['width'] = "%.0f%%" % (tab_w - 1)

            # Specify the text height
            a.style['height'] = "20px"
            a.style['line-height'] = "10px"


class Communicator(App):
    ''' The opening window of the Communicator program
        that presents options for execution.
        The options start queries that are executed
        and the resulting models are displayed in model views.
    '''
    def __init__(self, *args):
        self.net_name = "Gellish semantic network"
        self.pickle_file_name = "Gellish_net_db"

        self.gel_net = None
        self.net_built = False
        self.user = None

        self.GUI_lang_name_dict = {"English": '910036',
                                   "Nederlands": '910037'}
        self.GUI_lang_names = ['English', 'Nederlands']
        self.GUI_lang_index = 0

        self.extended_query = False
        self.obj_without_name_in_context = []

        self.reply_lang_name_dict = {'English': '910036',
                                     'Nederlands': '910037',
                                     'American': '911689',
                                     'Chinese': '911876',
                                     'Deutsch': '910038',
                                     'Francais': '910039'}
        self.comm_pref_uids = ['492014', 'any']  # Default: 492014 = 'Gellish'
        self.file_path_names = []
        self.q_view = None

        super(Communicator, self).__init__(*args)

    # Define the main window
    def main(self):
        ''' Define a main_window with select options and GUI language choice.'''
        # main_menu = ['Main Menu', 'Hoofdmenu']
        # login = ['Login/Register', 'Login/Registreer']
        read_file = ['Read file', 'Lees file']
        search = ['Search', 'Zoek']
        # query = ['Query', 'Vraag']
        admin = ['DB Admin', 'DB Admin']
        new_net = ['New network', 'Nieuw netwerk']
        save_as = ['Save net', 'Opslaan']
        manual = ['User manual', 'Handleiding']
        wiki = ['Gellish wiki', 'Gellish wiki']

        # Initialize user_db
        user_db = SU.UserDb()
        self.start_up(user_db)

        # Set GUI language default = English: GUI_lang_names[0]
        self.Set_GUI_language(self.GUI_lang_names[0])

        # Define main GUI window conform the REMI gui
        self.container = gui.Widget(margin='2px', style='background-color:#eeffdd')
        # self.container.set_size('100%', '100%')
        self.container.attributes['title'] = 'Communicator'

        # Menu bar
        self.menubar = gui.MenuBar(height=20, width='100%')
        self.container.append(self.menubar)

        import_text = ['Import one or more Gellish files', 'Lees een of meer Gellish files']
        self.read_file_tag = gui.MenuItem(read_file[self.GUI_lang_index], width=100, height=20)
        self.read_file_tag.attributes['title'] = import_text[self.GUI_lang_index]
        self.read_file_tag.onclick.connect(self.read_verify_and_merge_files)
        self.menubar.append(self.read_file_tag)

        self.search_tag = gui.MenuItem(search[self.GUI_lang_index], width=100, height=20)
        self.search_tag.attributes['title'] = 'Open a search window'
        self.search_tag.onclick.connect(self.search_net)
        self.menubar.append(self.search_tag)

        self.manual_tag = gui.MenuItem(manual[self.GUI_lang_index], width=100, height=20)
        self.manual_tag.attributes['title'] = 'Open the Communicator user manual'
        self.manual_tag.onclick.connect(self.user_manual)
        self.menubar.append(self.manual_tag)

        self.wiki_tag = gui.MenuItem(wiki[self.GUI_lang_index], width=100, height=20)
        self.wiki_tag.attributes['title'] = 'Open the Gellish languages wiki'
        self.wiki_tag.onclick.connect(self.open_wiki)
        self.menubar.append(self.wiki_tag)

        self.admin_tag = gui.MenuItem(admin[self.GUI_lang_index], width=100, height=20)
        self.admin_tag.attributes['title'] = 'Save network on file '\
                                             'or delete old and create new network'
        self.menubar.append(self.admin_tag)

        self.save_as_tag = gui.MenuItem(save_as[self.GUI_lang_index], width=100, height=20)
        self.save_as_tag.attributes['title'] = 'Save semantic network on binary file'

        self.admin_tag.append(self.save_as_tag)

        self.new_net_tag = gui.MenuItem(new_net[self.GUI_lang_index], width=100, height=20)
        self.new_net_tag.attributes['title'] = 'Delete old and create new semantic network'

        self.admin_tag.append(self.new_net_tag)

        # Define language selector
        self.lang_container = gui.HBox(width=180, height=20, style='margin-left:200px')

        lang_text = ['Language:', 'Taal:']
        self.lang_label = gui.Label(lang_text[self.GUI_lang_index], width=80, height=20,
                                    style='background-color:#eeffdd')
        self.lang_label.attributes['title'] = 'Select a language for specification of a search'

        self.lang_container.append(self.lang_label)
        # Set default language: GUI_lang_names[0] = English, [1] = Nederlands
        self.lang_default = self.GUI_lang_names[0]
        self.lang_select = gui.DropDown(self.GUI_lang_names, width=100, height=20,
                                        style='background-color:#ffffc0')
        self.lang_select.attributes['title'] = 'The language used for specification of a search'
        self.lang_container.append(self.lang_select)
        self.menubar.append(self.lang_container)

        # Binding GUI language choice
        self.lang_select.onchange.connect(self.Determine_GUI_language)

        # Main Frame
        self.main_frame = gui.VBox(width='100%', height='100%')
        self.container.append(self.main_frame)
        self.main_frame.attributes['color'] = 'green'

        self.query = None
        self.unknown = ['unknown', 'onbekend']
        self.unknown_quid = 0   # initial value of UID for unknowns in queries

        # Define a notebook in window
        self.Define_notebook()
        self.Define_log_sheet()

        # Start up semantic network
        self.start_net()
        # Create display views object
        self.views = Display_views(self.gel_net, self)
        self.save_as_tag.onclick.connect(self.gel_net.save_pickle_db)
        self.new_net_tag.onclick.connect(self.gel_net.reset_and_build_network)
        # If new network is only initialized and not built from files yet,
        # then build a semantic network from Gellish files.
        if self.net_built is False:
            self.gel_net.build_network()
            self.net_built = True

        # The REMI gui requires the return of the container root widget in main
        return self.container

    def Define_notebook(self):
        ''' Defines a Notebook with various view layouts and displays view contents.'''
        # Define the overall views_notebook
        self.views_noteb = MyTabBox(width='100%', height='100%',
                                    style='background-color:#eeffdd')
        self.main_frame.append(self.views_noteb)

    def Define_log_sheet(self):
        ''' Define a mess_frame for errors and warnings'''
        log_head_text = ['Messages and warnings', 'Berichten en foutmeldingen']
        self.mess_frame = gui.VBox(width='100%', height=120,
                                   style={'overflow': 'auto'})
        self.mess_frame.attributes['title'] = 'Display area for messages and warnings'

        self.log_label = gui.Label(log_head_text[self.GUI_lang_index],
                                   width='100%', height=20,
                                   style='background-color:#bbffff')
        self.log_messages = gui.ListView(width='100%', height='100%',
                                         style='background-color:#ddffff')
        self.mess_frame.append(self.log_label)
        self.mess_frame.append(self.log_messages)

        self.main_frame.append(self.mess_frame)

    def tab_cb(self):
        return

    def start_up(self, user_db):
        ''' Intended for authentication, providing or preventing unauthorized access.'''
        party = 'Andries'   # input("User name: ")
        self.user = SU.User(party)
        sesam = self.user.Providing_Access(party, user_db)
        if sesam is False:
            print('You are not registered as having access rights.')
            sys.exit(0)

    def start_net(self):
        ''' Import gel_net semantic network from Pickle
            or create new network from files
        '''
        # Load the semantic network from pickle, if available
        self.load_net()
        if self.gel_net is None:
            # Create a Semantic Network with a given name
            # from bootstrapping and from files
            self.gel_net = Semantic_Network(self.GUI_lang_index, self.net_name)
        else:
            self.net_built = True

    def load_net(self):
        ''' Load semantic network from pickle binary file.'''
        self.load_pickle_db(self.pickle_file_name)
        if self.gel_net is None:
            print("Network '{}' is not loaded. File is not found".
                  format(self.pickle_file_name))
        else:
            print("Network '{}' is loaded "
                  "and is composed of the following files:".
                  format(self.pickle_file_name))
            for file in self.gel_net.Gellish_files:
                print('- {}'.format(file.path_and_name))

    def load_pickle_db(self, fname):
        ''' Load a semantic network from a pickle file. '''
        try:
            infile = open(fname, "br")
        except FileNotFoundError:
            print("Input pickle file could not be found: {}".
                  format(fname))
            return()
        try:
            self.gel_net = pickle.load(infile)
        except EOFError:
            print("Input pickle file could not be read: {}".
                  format(fname))
        else:
            infile.close()

    def Set_GUI_language(self, GUI_lang_name):
        ''' Set the GUI language (name, uid, index and lang_prefs) of the user.
            The preferences defines a list of language uids in a preference sequence.
        '''
        if GUI_lang_name in self.GUI_lang_name_dict:
            self.GUI_lang_name = GUI_lang_name
            self.GUI_lang_uid = self.GUI_lang_name_dict[GUI_lang_name]
            if GUI_lang_name == 'Nederlands':
                self.GUI_lang_index = 1
            else:
                self.GUI_lang_index = 0
            GUI_set = True
            if self.GUI_lang_uid == '910036':
                # Set default GUI_preferences at international, English, American
                self.GUI_lang_pref_uids = ['589211', '910036', '911689']
            elif self.GUI_lang_uid == '910037':
                # Set default preferences at international, Dutch, English
                self.GUI_lang_pref_uids = ['589211', '910037', '910036']
            else:
                # Set default preferences at international, user_language, English
                self.GUI_lang_pref_uids = ['589211', self.GUI_lang_uid, '910036']
        else:
            self.message_ui(
                'The GUI language {} is unknown. Default = English.'.
                format(GUI_lang_name),
                'De GUI taal {} is onbekend. Default = English.'.
                format(GUI_lang_name))
            GUI_set = False
        return GUI_set

    def Determine_GUI_language(self, event, selection):
        ''' Determine which language for the user interface and query specification
            is spacified by the user.
        '''
        GUI_lang_name = selection  # self.lang_box.get()
        self.Set_GUI_language(GUI_lang_name)

        self.message_ui(
            'The user interface language is {}.'.format(self.GUI_lang_name),
            'De GUI taal is {}.'.format(self.GUI_lang_name))

    def read_verify_and_merge_files(self, widget):
        ''' Read one or more files, verify their content
            and combine them with the semantic network
        '''
        self.combine_files_with_network()
        addition = 'n'  # 'y' means option for importing more input files
        while addition == 'y':
            addition = input("More import files? (y/n):")
            if addition == 'y':
                self.combine_files_with_network()

    def combine_files_with_network(self):
        ''' Select one or more Gellish files in a dialog
            and import the files,
            after syntactic verification.
            The merge the file content in the semantic network.
        '''
        self.read_file_container = gui.Widget(style={'width': '220px', 'display': 'block',
                                                     'overflow': 'auto', 'text-align': 'center'})
        self.container.append(self.read_file_container)
        # Select one or more files to be imported
        self.dialog = gui.FileSelectionDialog('File selection dialog',
                                              'Select one or more CSV or JSON files',
                                              False, '.',
                                              style='background-color:#eeffdd')
        self.dialog.confirm_value.connect(self.on_fileselection_dialog_confirm)
        self.dialog.cancel_dialog.connect(self.on_dialog_cancel)

        self.dialog.show(self)

    def read_files(self):
        ''' Read the file(s) that are selected in the file selection dialog.'''
        # Debug print('Selected file(s):',self.file_path_names)
        if self.file_path_names == []:
            self.message_ui(
                'The file name is blank or the inclusion is cancelled. There is no file read.',
                'De file naam is blanco of het inlezen is gecancelled. Er is geen file ingelezen.')
            return

        # Read file(s)
        for file_path_and_name in self.file_path_names:
            # Split file_path_and_name in file path and file name
            path_name = file_path_and_name.rsplit('/', maxsplit=1)
            if len(path_name) == 2:
                self.message_ui(
                    'Reading file <{}> from directory {}.'.format(path_name[1], path_name[0]),
                    'Lees file <{}> van directory {}.'.format(path_name[1], path_name[0]))
                # file_name = path_name[1]
                # file_path = path_name[0]
            else:
                self.message_ui(
                    'Reading file <{}> from current directory.'.format(file_path_and_name),
                    'Lees file <{}> van actuele directory.'.format(file_path_and_name))
                # file_name = file_path_and_name
                # file_path = ''

            # Create file object
            self.current_file = Gellish_file(file_path_and_name, self.gel_net)
            self.gel_net.Gellish_files.append(self.current_file)

            # Import expressions from file
            self.current_file.Import_Gellish_from_file()

    def on_fileselection_dialog_confirm(self, widget, filelist):
        ''' A list() of filenames and folders is returned'''
        # Debug print('File list: {}'.format(filelist))
        self.file_path_names = filelist
        if len(filelist):
            self.read_files()

    def on_dialog_cancel(self, widget):
        self.set_root_widget(self.container)

    def message_ui(self, mess_text_EN, mess_text_NL):
        ''' Display a message in the log_messages in any of the languages'''
        if self.GUI_lang_index == 1:
            self.log_messages.append(mess_text_NL)
        else:
            self.log_messages.append(mess_text_EN)

    def user_manual(self, widget):
        ''' Open the user manual wiki. '''

        url = 'http://usermanual.gellish.net/'
        # Open URL in a new tab, if a browser window is already open.
        webbrowser.open_new_tab(url)

    def open_wiki(self, widget):
        ''' Open the Gellish wiki. '''

        url = 'http://wiki.gellish.net/'
        # Open URL in a new tab, if a browser window is already open.
        webbrowser.open_new_tab(url)

    def login_reg(self, widget):
        ''' Enable a user to log in after being recognized as registered
            or register a new user and enable to login after authentication.
        '''
        pass

    def search_net(self, widget):
        ''' Initiate the execution of a simple query as a search for an object.'''
        self.extended_query = False
        self.query_the_network()

    def query_net(self, widget):
        ''' Initiate the execution of a complex query
            with a spec as expression(s) that may include conditions.
        '''
        self.extended_query = True
        self.query_the_network()

    def query_the_network(self):
        ''' Query the semantic network '''
        if self.gel_net is None:
            print('First create a semantic network. Then query again.')
        else:
            # Create a query object
            self.query = Query(self.gel_net, self)

            if self.q_view is None:
                # Create a query view object
                self.q_view = Query_view(self.gel_net, self)
                # Specify a query window and enable spefiying a query via GUI
                self.q_view.Define_query_window()
            else:
                self.views_noteb.select_by_name('Search')

    def Set_reply_language(self, reply_lang_name):
        ''' Set the reply language (name, uid, reply_lang_pref_uids)
            for display of the user views.
        '''
        if reply_lang_name in self.reply_lang_name_dict:
            self.reply_lang_name = reply_lang_name
            self.reply_lang_uid = self.reply_lang_name_dict[reply_lang_name]
            if self.reply_lang_uid == '910036':
                # Set default preferences at international, English, American
                self.reply_lang_pref_uids = ['589211', '910036', '911689']
            elif self.reply_lang_uid == '910037':
                # Set default preferences at international, Dutch, English
                self.reply_lang_pref_uids = ['589211', '910037', '910036']
            else:
                # Set default preferences at international, user_language, English
                self.reply_lang_pref_uids = ['589211', self.reply_lang_uid, '910036']
        else:
            self.message_ui(
                'The reply language {} is unknown. Default = English is used.'.
                format(reply_lang_name),
                'De antwoordtaal {} is onbekend. Default = English wordt gebruikt.'.
                format(reply_lang_name))
            self.reply_lang_name = 'English'
            self.reply_lang_uid = '910037'

    def Determine_name_in_context(self, obj, base_or_inverse='normal'):
        ''' Given an object and preferred language sequence uids and community sequence uids,
            determine lang_name, comm_name, preferred obj_name for user interface.
            base_or_inverse denotes whether the preferred name should be found
            in the attribute list
            names_in_contexts, base_phrases_in_contexts or inverse_phrases_in_contexts
            name_in_context = (lang_uid, comm_uid, name, naming_uid, description)
        '''
        if base_or_inverse == 'base':
            names_in_contexts = obj.base_phrases_in_contexts
        elif base_or_inverse == 'inverse':
            names_in_contexts = obj.inverse_phrases_in_contexts
        else:
            names_in_contexts = obj.names_in_contexts

        obj_name = None
        if len(names_in_contexts) > 0:
            # For language_prefs and community preferences search for name
            for lang_uid in self.reply_lang_pref_uids:
                for comm_pref_uid in self.comm_pref_uids:
                    for name_in_context in names_in_contexts:
                        # Verify if language uid corresponds with required reply language uid
                        if name_in_context[0] == lang_uid \
                           and (name_in_context[1] == comm_pref_uid or comm_pref_uid == 'any'):
                            obj_name = name_in_context[2]
                            lang_name = self.gel_net.lang_uid_dict[name_in_context[0]]
                            comm_name = self.gel_net.community_dict[name_in_context[1]]
                            break
                    if obj_name:
                        break
                if obj_name:
                    break

            # Search for partial definition in specialization relation in pref_languages
            # thus in a name_in_context[3] where 'is called' (5117) is used
            if obj_name:
                part_def = None
                for lang_uid in self.reply_lang_pref_uids:
                    for name_in_context in obj.names_in_contexts:
                        if name_in_context[0] == lang_uid \
                           and name_in_context[3] == is_called_uid:
                            part_def = name_in_context[4]
                            break
                    if part_def:
                        break
                if not part_def:
                    # No definition found,
                    # then search for def in any name in context in pref_languages
                    for lang_uid in self.reply_lang_pref_uids:
                        for name_in_context in obj.names_in_contexts:
                            if name_in_context[0] == lang_uid and name_in_context[4] != '':
                                part_def = name_in_context[4]
                                break
                        if part_def:
                            break
            else:
                # No name is available in the preferred language,
                # then use the first available name and its definition
                obj_name = names_in_contexts[0][2]
                lang_name = self.gel_net.lang_uid_dict[names_in_contexts[0][0]]
                comm_name = self.gel_net.community_dict[names_in_contexts[0][1]]
                if base_or_inverse == 'normal':
                    part_def = names_in_contexts[0][4]
                else:
                    part_def = ''
        # No names in contexts available for obj
        else:
            if obj not in self.obj_without_name_in_context:
                self.obj_without_name_in_context.append(obj)
                numeric_uid, integer = Convert_numeric_to_integer(obj.uid)
                if integer is False or numeric_uid not in range(1000000000, 3000000000):
                    self.message_ui(
                        'There is no name in context known for {}'.format(obj.name),
                        'Er is geen naam in context bekend voor {}'.format(obj.name))
            obj_name = obj.name
            lang_name = self.unknown[self.GUI_lang_index]
            comm_name = self.unknown[self.GUI_lang_index]
            part_def = ''

        # Determine full_def by determining supertype or classifier name
        # in the preferred language and concatenate with part_def
        super_name = None
        if len(obj.supertypes) > 0 and len(obj.supertypes[0].names_in_contexts) > 0:
            for lang_uid in self.reply_lang_pref_uids:
                for name_in_context in obj.supertypes[0].names_in_contexts:
                    # Verify if language uid corresponds with required reply language uid
                    if name_in_context[0] == lang_uid \
                       and name_in_context[3] == is_called_uid:  # '5117'
                        super_name = name_in_context[2]
                        break
                if super_name:
                    break
        elif len(obj.classifiers) > 0 and len(obj.classifiers[0].names_in_contexts) > 0:
            for lang_uid in self.reply_lang_pref_uids:
                for name_in_context in obj.classifiers[0].names_in_contexts:
                    # Verify if language uid corresponds with required reply language uid
                    if name_in_context[0] == lang_uid \
                       and name_in_context[3] == is_called_uid:  # '5117'
                        super_name = name_in_context[2]
                        break
                if super_name:
                    break
        if super_name:
            is_a = ['is a ', 'is een ']
            full_def = is_a[self.GUI_lang_index] + super_name + ' ' + part_def
        else:
            full_def = part_def

        return lang_name, comm_name, obj_name, full_def

    def Close_tag(self, widget, tabbox, ref_widget_tab_name):
        ''' Close the tab in tabbox in widget with the specified tab_name'''
        # tabbox.select_by_name(ref_widget_tab_name)
        tabbox.remove_tab_by_name(ref_widget_tab_name)
        if ref_widget_tab_name == 'Search':
            self.q_view = None


class Semantic_network():
    ''' Dummy class for testing only.'''
    def __init__(self, GUI_lang_index, net_name):
        self.GUI_lang_index = GUI_lang_index
        self.GUI_lang_name = 'English'
        self.uid_dict = {}  # key = uid; value = obj (an instance of Anything)

    def reset_and_build_network(self):
        pass

    def save_pickle_db(self, widget):
        pass


class Network():
    ''' Dummy class for testing only.'''
    def __init__(self):
        GUI_lang_index = 0
        net_name = 'Sementic Newtork'
        self.gel_net = Semantic_network(GUI_lang_index, net_name)

    def build_network(self):
        print('Build network')


if __name__ == "__main__":
    sys.setrecursionlimit(100000)

    net = Network()
    start(Communicator, title="Gellish Communicator")
