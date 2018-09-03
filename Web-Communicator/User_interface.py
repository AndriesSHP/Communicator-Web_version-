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
        self.user = None
        self.user_interface = None

        self.GUI_lang_name_dict = {"English":'910036', \
                                   "Nederlands":'910037'}
        self.GUI_lang_names = ['English', 'Nederlands']

        self.extended_query = False
        self.obj_without_name_in_context = []

        self.reply_lang_name_dict = {'English':'910036', \
                                     'Nederlands':'910037', \
                                     'American':'911689', \
                                     'Chinese':'911876', \
                                     'Deutsch':'910038', \
                                     'Francais':'910039'}
        self.comm_pref_uids = ['492014', 'any'] # Default: 492014 = 'Gellish'
        
        super(Communicator, self).__init__(*args)

    # Define the main window
    def main(self):
        """ Define a main_window with select options and GUI language choice.
        """
        main_menu = ['Main Menu', 'Hoofdmenu']
        login = ['Login/Register', 'Login/Registreer']
        read_file = ['Read file', 'Lees file']
        search = ['Search', 'Zoek']
        query = ['Query', 'Vraag']
        admin = ['DB Admin', 'DB Admin']
        new_net = ['New network', 'Nieuw netwerk']
        save_as = ['Save net', 'Opslaan']
        manual = ['User manual', 'Handleiding']
        wiki = ['Gellish wiki', 'Gellish wiki']

        # Initialize user_db and start up
        user_db = SU.UserDb()
        self.start_up(user_db)
        self.start_net()
        
        # Set GUI language default = English: GUI_lang_names[0]
        self.Set_GUI_language(self.GUI_lang_names[0])

        # Define main GUI window
        #self.root = Tk()
        self.container = gui.Widget(margin='2px', style='background-color:#eeffdd')
        self.container.set_size('100%', '100%')
        self.container.attributes['title'] = 'Communicator'
##        self.container.title("Gellish Communicator")
##        max_width, max_height = self.container.winfo_screenwidth(), \
##                                self.container.winfo_screenheight()
##        self.container.geometry('1000x600')
##        self.container.minsize(width=600, height=300)
##        self.container.maxsize(width=1000,height=600) #max_width, height=max_height)
##        self.container.myStyle = Style()
##        self.container.myStyle.configure("TFrame", background="#dfd")
##        self.container.configure(background="#ddf")
##        self.container.columnconfigure(0, weight=1)
##        self.container.rowconfigure(0, weight=1)
##        self.container.option_add('*tearOff', False)

        # Menu bar
        self.menubar = gui.MenuBar(height=20, width='100%')
        self.container.append(self.menubar)

##        self.menubar.add_cascade(menu=self.main_menu,
##                                 label=main_menu[self.GUI_lang_index])
##        self.main_menu.add_command(label=login[self.GUI_lang_index],
##                                   command=self.login_reg)
        #login_tag = gui.MenuItem(login[self.GUI_lang_index], width=100, height=20)
        #self.menubar.append(login_tag)
##        self.main_menu.add_command(label=read_file[self.GUI_lang_index],
##                                   command=self.read_file)
        import_text = ['Import one or more Gellish files', 'Lees een of meer Gellish files']
        self.read_file_tag = gui.MenuItem(read_file[self.GUI_lang_index], width=100, height=20)
        self.read_file_tag.attributes['title'] = import_text[self.GUI_lang_index]
        self.read_file_tag.onclick.connect(self.read_verify_and_merge_files)
        self.menubar.append(self.read_file_tag)
        
##        self.main_menu.add_command(label=search[self.GUI_lang_index],
##                                   command=self.search_net)
        self.search_tag = gui.MenuItem(search[self.GUI_lang_index], width=100, height=20)
        self.search_tag.attributes['title'] = 'Open a search window'
        self.search_tag.onclick.connect(self.search_net)
        self.menubar.append(self.search_tag)
##        self.main_menu.add_command(label=query[self.GUI_lang_index],
##                                   command=self.query_net)
##        self.main_menu.add_command(label=manual[self.GUI_lang_index],
##                                   command=self.user_manual)
        self.manual_tag = gui.MenuItem(manual[self.GUI_lang_index], width=100, height=20)
        self.manual_tag.attributes['title'] = 'Open the Communicator user manual'
        self.manual_tag.onclick.connect(self.user_manual)
        self.menubar.append(self.manual_tag)

        self.wiki_tag = gui.MenuItem(wiki[self.GUI_lang_index], width=100, height=20)
        self.wiki_tag.attributes['title'] = 'Open the Gellish languages wiki'
        self.wiki_tag.onclick.connect(self.user_manual)
        self.menubar.append(self.wiki_tag)

        self.admin_tag = gui.MenuItem(admin[self.GUI_lang_index], width=100, height=20)
        self.admin_tag.attributes['title'] = 'Save network on file or delete old and create new network'
        self.menubar.append(self.admin_tag)
##        self.menubar.add_cascade(menu=self.db_menu,
##                                 label=admin[self.GUI_lang_index])
##        self.db_menu.add_command(label=save_as[self.GUI_lang_index],
##                                 command=self.gel_net.save_pickle_db)
        self.save_as_tag = gui.MenuItem(save_as[self.GUI_lang_index], width=100, height=20)
        self.save_as_tag.attributes['title'] = 'Save semantic network on binary file'
        self.save_as_tag.onclick.connect(self.gel_net.save_pickle_db)
        self.admin_tag.append(self.save_as_tag)

##        self.db_menu.add_command(label=new_net[self.GUI_lang_index],
##                                 command=self.gel_net.reset_and_build_network)
        self.new_net_tag = gui.MenuItem(new_net[self.GUI_lang_index], width=100, height=20)
        self.new_net_tag.attributes['title'] = 'Delete old and create new semantic network'
        self.new_net_tag.onclick.connect(self.gel_net.reset_and_build_network)
        self.admin_tag.append(self.new_net_tag)

        # Define language selector 
        self.lang_container = gui.HBox(width=180, height=20)
        self.container.append(self.lang_container)
        
        lang_text = ['Language:', 'Taal:']
        self.lang_label = gui.Label(lang_text[self.GUI_lang_index], width=80, height=20)
        self.lang_label.attributes['title'] = 'Select a language for specification of a search'
        self.lang_container.append(self.lang_label) #self.main_frame, width=10)
        # Set default language: GUI_lang_names[0] = English, [1] = Nederlands
        self.lang_default = self.GUI_lang_names[0]
        self.lang_select = gui.DropDown(self.GUI_lang_names, width=100, height=20) #margin='10px'
        self.lang_select.attributes['title'] = 'The language used for specification of a search'
        self.lang_container.append(self.lang_select)
##        self.lang_label.grid(column=0, row=0, sticky=NW)
##        self.lang_box.grid(column=1, row=0, sticky=NW)
        # Binding GUI language choice
##        self.lang_box.bind("<<ComboboxSelected>>", self.Determine_GUI_language)
        self.lang_select.onchange.connect(self.Determine_GUI_language)

        # Main Frame
        self.main_frame = gui.VBox(width='100%', height='100%')
        self.container.append(self.main_frame)
        self.main_frame.attributes['color'] = 'green'
        
##        self.main_frame.grid(column=0, row=0, sticky=NSEW)
##        self.main_frame.columnconfigure(0, weight=0)
##        self.main_frame.columnconfigure(1, weight=1)
##        self.main_frame.rowconfigure(0, weight=0)
##        self.main_frame.rowconfigure(1, weight=1)

##        event = 'Button-1'
##        self.Determine_GUI_language(event)
##
        self.query = None
        self.unknown = ['unknown', 'onbekend']
        self.unknown_quid = 0   # start UID for unknowns in queries

        # Create display views object
        self.views = Display_views(self.gel_net, self)
        
        # Define a notebook in window
        self.Define_notebook()

        return self.container
    
    def Define_notebook(self):
        """ Defines a Notebook with various view layouts and displays view contents.
            Starting in grid on row 1.
        """
        # Define the overall views_notebook
        self.views_noteb = gui.TabBox(height='100%', width='100%')
        self.main_frame.append(self.views_noteb)
##        self.views_noteb.grid(column=0, row=1,sticky=NSEW, columnspan=2)
##        self.views_noteb.columnconfigure(0,weight=1)
##        self.views_noteb.rowconfigure(0,weight=1)

        self.Define_log_sheet()
    
    def Define_log_sheet(self):
        ''' Define a tab and frame for errors and warnings'''
        log_head = ['Messages and warnings','Berichten en foutmeldingen']
        self.log_frame = gui.ListView(width='100%', height='100%')
        self.log_frame.attributes['title'] = 'Display messages and warnings'
        self.views_noteb.add_tab(self.log_frame, log_head[self.GUI_lang_index], self.tab_cb)
##        self.log_frame.grid (column=0, row=0,sticky=NSEW)
##        self.log_frame.columnconfigure(0, weight=1)
##        self.log_frame.rowconfigure(0, weight=1)
        
##        self.views_noteb.add(self.log_frame, text=log_head[self.GUI_lang_index], sticky=NSEW)
##        self.views_noteb.insert("end", self.log_frame, sticky=NSEW)

        # Messages area - text widget definition
##        self.log_message = Text(self.log_frame, width = 40, background='#efc') # height = 10,
##        log_mess_scroll  = ttk.Scrollbar(self.log_frame,orient=VERTICAL,\
##                                         command=self.log_message.yview)
##        self.log_message.config(yscrollcommand=log_mess_scroll.set)
##
##        self.log_message.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=NSEW)
##        log_mess_scroll.grid(column=0, row=0, sticky=NS+E)
    
    def tab_cb(self):
        return

    def start_up(self, user_db):
        party = 'Andries'   #input("User name: ")
        self.user = SU.User(party)
        sesam = self.user.Providing_Access(party, user_db)
        if sesam is False:
            print('You are not registered as having access rights.')
            sys.exit(0)

    def start_net(self):
        ''' Start user interaction and
            Import gel_net semantic network from Pickle
            or create new network from files
        '''
        # Load the semantic network from pickle, if available
        self.load_net()
        if self.gel_net is None:
            # Create a Semantic Network with a given name
            # from bootstrapping and from files
            self.gel_net = Semantic_Network(self.net_name)
            # Build the semantic network
            self.gel_net.build_network()
        # Create and open a user interface
##        self.user_interface = User_interface(self.gel_net)

    def load_net(self):
        # Load semantic network from pickle binary file.
        self.load_pickle_db(self.pickle_file_name)
        if self.gel_net is None:
            print("Network '{}' is not loaded. File is not found".\
                  format(self.pickle_file_name))
        else:
            print("Network '{}' is loaded "
                  "and is composed of the following files:".\
                  format(self.pickle_file_name))
            for file in self.gel_net.Gellish_files:
                print('- {}'.format(file.path_and_name))

    def load_pickle_db(self, fname):
        try:
            infile = open(fname, "br")
        except FileNotFoundError:
            print("Input pickle file could not be found: {}". \
                  format(fname))
            return()
        try:
            self.gel_net = pickle.load(infile)
            #self = pickle.load(f)
        except EOFError:
            print("Input pickle file could not be read: {}". \
                  format(fname))
        else:
            infile.close()

    def Set_GUI_language(self, GUI_lang_name):
        ''' Set the GUI language (name, uid, index and lang_prefs) of the user.
            The preferences defines a list of language uids in a preference sequence.
        '''
        if GUI_lang_name in self.GUI_lang_name_dict:
            self.GUI_lang_name = GUI_lang_name
            self.GUI_lang_uid  = self.GUI_lang_name_dict[GUI_lang_name]
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
            self.Message_UI(
                'The GUI language {} is unknown. Default = English.'.format(GUI_lang_name),\
                'De GUI taal {} is onbekend. Default = English.'.format(GUI_lang_name))
            GUI_set = False
        return GUI_set

    def Determine_GUI_language(self, event, selection):
        ''' Determine which language for the user interface and query specification
            is spacified by the user.
        '''
        GUI_lang_name = selection #self.lang_box.get()
        self.Set_GUI_language(GUI_lang_name)

        self.Message_UI(
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
        """ Select one or more Gellish files in a dialog
            and import the files,
            after syntactic verification.
            The merge the file content in the semantic network
        """
        # Select one or more files to be imported
##        file_path_names = filedialog.askopenfilenames(
##            filetypes=[("CSV files","*.csv"),("JSON files","*.json"), ("All files","*.*")], \
##            title="Select file")
        dialog = gui.FileSelectionDialog(title='File selection dialog',
                                         message='Select one or more files',
                                         multiple_selection=True, selection_folder='.',
                                         allow_file_selection=True, allow_folder_selection=False)
        dialog.confirm_value.connect(self.on_fileselection_dialog_confirm)

        file_path_names = ''
        print('Selected file(s):',file_path_names)
        if file_path_names == '':
            self.Message_UI(
                'The file name is blank or the inclusion is cancelled. There is no file read.',\
                'De file naam is blanco of het inlezen is gecancelled. Er is geen file ingelezen.')
            return

        # Read file(s)
        for file_path_and_name in file_path_names:
            # Split file_path_and_name in file path and file name
            path_name = file_path_and_name.rsplit('/', maxsplit=1)
            if len(path_name) == 2:
                self.Message_UI(
                    'Reading file <{}> from directory {}.'.format(path_name[1], path_name[0]),\
                    'Lees file <{}> van directory {}.'.format(path_name[1], path_name[0]))
                file_name = path_name[1]
                file_path = path_name[0]
            else:
                self.Message_UI(
                    'Reading file <{}> from current directory.'.format(file_path_and_name),\
                    'Lees file <{}> van actuele directory.'.format(file_path_and_name))
                file_name = file_path_and_name
                file_path = ''

            # Create file object
            self.current_file = Gellish_file(file_path_and_name, self)
            self.gel_net.Gellish_files.append(self.current_file)

            # Import expressions from file
            self.current_file.Import_Gellish_from_file()

    def on_fileselection_dialog_confirm(self, widget, filelist):
        # a list() of filenames and folders is returned
        self.lbl.set_text('Selected files: %s' % ','.join(filelist))
        if len(filelist):
            f = filelist[0]
            # replace the last download link
            fdownloader = gui.FileDownloader("download selected", f, width=200, height=30)
            self.subContainerRight.append(fdownloader, key='file_downloader') 

    def Message_UI(self, mess_text_EN, mess_text_NL):
        if self.GUI_lang_index == 1:
            print(mess_text_NL)
            self.log_frame.append(mess_text_NL)
        else:
            print(mess_text_EN)
            self.log_frame.append(mess_text_EN)

    def user_manual(self, widget):
        ''' Open the user manual wiki. '''

        url = 'http://usermanual.gellish.net/'
        # Open URL in a new tab, if a browser window is already open.
        webbrowser.open_new_tab(url)

    def wiki(self, widget):
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

            # Enter and Interpret a query
            q_view = Query_view(self.gel_net, self)
            # Specify a query via GUI
            q_view.Query_window()

    def Set_reply_language(self, reply_lang_name):
        ''' Set the reply language (name, uid, reply_lang_pref_uids)
            for display of the user views.
        '''
        if reply_lang_name in self.reply_lang_name_dict:
            self.reply_lang_name = reply_lang_name
            self.reply_lang_uid  = self.reply_lang_name_dict[reply_lang_name]
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
            self.Message_UI(
                'The reply language {} is unknown. Default = English is used.'.\
                format(reply_lang_name),\
                'De antwoordtaal {} is onbekend. Default = English wordt gebruikt.'.\
                format(reply_lang_name))
            self.reply_lang_name = 'English'
            self.reply_lang_uid  = '910037'

    def Determine_name_in_context(self, obj, base_or_inverse = 'normal'):
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
                            comm_name = self.gel_net.community_dict[name_in_context[1]] # community uid
##                            # base and inverse phrases have no description (name_in_context[4])
##                            if len(name_in_context) < 5:
##                                part_def = ''
##                            else:
##                                part_def = name_in_context[4]
##                            name_known = True
                            break
                            #return lang_name, comm_name, obj_name, part_def
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
                           and name_in_context[3] == '5117':
                            part_def = name_in_context[4]
                            break
                    if part_def:
                        break
                if not part_def:
                    # No definition found,
                    # then search for def in any name in context in pref_languages
                    for lang_uid in self.reply_lang_pref_uids:
                       for name_in_context in obj.names_in_contexts:
                           if name_in_context[0] == lang_uid \
                              and name_in_context[4] != '':
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
                    self.Message_UI(
                        'There is no name in context known for {}'.format(obj.name),\
                        'Er is geen naam in context bekend voor {}'.format(obj.name))
            obj_name = obj.name
            lang_name = self.unknown[self.GUI_lang_index]
            comm_name = self.unknown[self.GUI_lang_index]
            part_def = ''

        # Determine full_def by determining supertype name in the preferred language
        # and concatenate with part_def
        super_name = None
        if len(obj.supertypes) > 0 and len(obj.supertypes[0].names_in_contexts) > 0:
            for lang_uid in self.reply_lang_pref_uids:
                for name_in_context in obj.supertypes[0].names_in_contexts:
                    # Verify if language uid corresponds with required reply language uid
                    if name_in_context[0] == lang_uid \
                       and name_in_context[3] == '5117':
                        super_name = name_in_context[2]
                        break
                if super_name:
                    break
        if super_name:
            full_def = super_name + ' ' + part_def
        else:
            full_def = part_def

        return lang_name, comm_name, obj_name, full_def

#------------------------------------------------
class Semantic_network():
    def __init__(self):
        self.GUI_lang_index = 0
        self.GUI_lang_name = 'English'
        self.uid_dict = {} # key = uid; value = obj (an instance of Anything)

    def reset_and_build_network(self):
        pass

    def save_pickle_db(self):
        pass

class Network():
    def __init__(self):
        self.gel_net = Semantic_network()

    def build_network(self):
        print('Build network')

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    
    net = Network()
    start(Communicator, title="Gellish Communicator")
