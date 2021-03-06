import csv
import datetime
import json

from rdflib import Graph, URIRef, RDFS
import remi.gui as gui

from gellish_communicator.Expr_Table_Def import (
    lang_uid_col,
    lang_name_col,
    comm_uid_col,
    comm_name_col,
    intent_uid_col,
    intent_name_col,
    idea_uid_col,
    lh_uid_col,
    lh_name_col,
    rel_type_uid_col,
    rel_type_name_col,
    phrase_type_uid_col,
    rh_role_uid_col,
    rh_role_name_col,
    rh_uid_col,
    rh_name_col,
    full_def_col,
    uom_uid_col,
    uom_name_col,
    status_col,
    expr_col_ids,
    header3,
    default_row,
)
from gellish_communicator.utils import open_file


def Create_gellish_expression(lang_comm, idea_uid, intent_uid_name,
                              lh_uid_name, rel_uid_phrase_type,
                              rh_role_uid_name, rh_uid_name, uom_uid_name, full_description):
    ''' Create a Gellish expression from default_row in Expr_Table_Def'''
    gellish_expr = default_row[:]
    gellish_expr[lang_uid_col] = lang_comm[0]
    gellish_expr[lang_name_col] = lang_comm[1]
    gellish_expr[comm_uid_col] = lang_comm[2]
    gellish_expr[comm_name_col] = lang_comm[3]
    gellish_expr[intent_uid_col] = intent_uid_name[0]
    gellish_expr[intent_name_col] = intent_uid_name[1]
    gellish_expr[idea_uid_col] = idea_uid
    gellish_expr[lh_uid_col] = lh_uid_name[0]
    gellish_expr[lh_name_col] = lh_uid_name[1]
    gellish_expr[rel_type_uid_col] = rel_uid_phrase_type[0]
    gellish_expr[rel_type_name_col] = rel_uid_phrase_type[1]
    gellish_expr[phrase_type_uid_col] = rel_uid_phrase_type[2]
    gellish_expr[rh_role_uid_col] = rh_role_uid_name[0]
    gellish_expr[rh_role_name_col] = rh_role_uid_name[1]
    gellish_expr[rh_uid_col] = rh_uid_name[0]
    gellish_expr[rh_name_col] = rh_uid_name[1]
    gellish_expr[full_def_col] = full_description
    gellish_expr[uom_uid_col] = uom_uid_name[0]
    gellish_expr[uom_name_col] = uom_uid_name[1]
    gellish_expr[status_col] = 'accepted'
    return gellish_expr


def Open_output_file(expressions, subject_name, lang_name, serialization):
    """ Open a file for saving expressions in some format
        such as the CSV in Gellish Expression Format:
        Serialization is either 'csv', 'xml', 'n3' or 'json'.
    """
    date = datetime.date.today()
    # Create header line 1 and an initial file name
    if lang_name == 'Nederlands':
        header1 = ['Gellish', 'Nederlands', 'Versie', '9.0', date, 'Resultaten',
                   'over ' + subject_name]
        res = 'Resultaten-'
    else:
        header1 = ['Gellish', 'English', 'Version', '9.0', date, 'Results',
                   'about ' + subject_name]
        res = 'Query_results-'
    ini_file_name = ''
    if serialization == 'csv':
        ini_file_name = res + subject_name + '.csv.csv'
    if serialization == 'xml':
        ini_file_name = res + subject_name + '.xml.xml'
    if serialization == 'n3':
        ini_file_name = res + subject_name + '.n3.n3'
    if serialization == 'json':
        ini_file_name = res + subject_name + '.json.json'

    # header2 = expr_col_ids  # from Bootstrapping

    # Select file name and directory
    # Ini_out_path from Bootstrapping
    output_file_name = ini_file_name
    if output_file_name == '':
        output_file = 'Results.' + serialization
        if lang_name == 'Nederlands':
            print('***De filenaam voor opslaan is blanco of the file selectie is gecancelled. '
                  'De file met naam ' + output_file + ' is niet opgeslagen')
        else:
            print('***File name for saving is blank or file selection is cancelled. '
                  'The file with name ' + output_file + 'is not saved')
    else:
        Save_expressions_in_file(expressions, output_file_name, header1, serialization)

def fileupload_on_success(widget, filename):
    print('File upload success: ' + filename)

def fileupload_on_failed(widget, filename):
    print('File upload failed: ' + filename)

def Save_expressions_in_file(expressions, output_file, header1, serialization):
    '''Write expressions to an output file in an CSV or RDF serialization'''

    if serialization == 'csv':
        # Save the result_expr expressions in a CSV file, preceeded by three header lines.
        try:
            f = open(output_file, mode='a', newline='', encoding='utf-8')
            file_writer = csv.writer(f, dialect='excel', delimiter=';')

            # Write header rows and expressions
            file_writer.writerow(header1)
            file_writer.writerow(expr_col_ids)
            file_writer.writerow(header3)
            for expression in expressions:
                file_writer.writerow(expression)

            f.close()

            # Open the written file in a CSV viewer (e.g. Excel)
            # open_file(output_file)
        except PermissionError:
            print('File {} cannot be opened. Probably already in use'.format(output_file))
            return

    elif serialization in ['xml', 'n3']:
        g1 = Graph()
        uri = "http://www.formalenglish.net/dictionary"
        # gel = Namespace("http://www.formalenglish.net/dictionary")
        g1.bind('gel', "http://www.formalenglish.net/dictionary")

        # rdfs = {1146: 'subClassOf'}

        for expr in expressions:
            rel_name = str(expr[3]).replace(" ", "_")
            if expr[2] == 1146:
                rel = RDFS.subClassOf
            else:
                rel = URIRef(uri + rel_name)

            lh = URIRef(uri + str(expr[1]))
            rh = URIRef(uri + str(expr[5]))
            g1.add((lh, rel, rh))

        if serialization == 'n3':
            s = g1.serialize(format='n3')
            f = open(output_file, 'w')
            f.write(str(s))
        elif serialization == 'xml':
            s = g1.serialize(format='xml')
            f = open(output_file, 'w')
            f.write(str(s))
    else:
        f = open(output_file, 'w', encoding='utf-8')
        json.dump(expressions, f)

    f.close()
    print('Saved file: {}'.format(output_file))
    # Open written file in a viewer
    open_file(output_file)

    output_file = gui.FileUploader('./', width=200, height=30, margin='10px')
    output_file.onsuccess.connect(fileupload_on_success)
    output_file.onfailed.connect(fileupload_on_failed)


def Convert_numeric_to_integer(numeric_text):
    ''' Convert a numeric string into integer value removing dots(.), commas(,) and spaces( )
        If string is not numeric, return string and integer = False.
    '''
    integer = True
    try:
        int_val = int(numeric_text)
    except ValueError:
        commas_removed = numeric_text.replace(',', '')
        dots_removed = commas_removed.replace('.', '')
        spaces_removed = dots_removed.replace(' ', '')
        if spaces_removed.isdecimal():
            return int(spaces_removed), integer
        else:
            integer = False
            return numeric_text, integer
    return int_val, integer


def Message(GUI_lang_index, mess_text_EN, mess_text_NL):
    if GUI_lang_index == 1:
        print(mess_text_NL)
    else:
        print(mess_text_EN)
