''' Define and display IDEF0 diagrams of occurrences, being activities,
    processes or events.
    The diagrams have a hierarchy,
    whereby the parts of an occurrence are presented on a next page
'''
import math

import remi.gui as gui

from gellish_communicator.remi_ext import SingleRowSelectionTable


class SvgPolygon(gui.SvgPolyline):
    def __init__(self, _maxlen=None, *args, **kwargs):
        super(SvgPolygon, self).__init__(_maxlen, *args, **kwargs)
        self.type = 'polygon'

    def set_stroke(self, width=1, color='black'):
        """Sets the stroke properties.

        Args:
            width (int): stroke width
            color (str): stroke color
        """
        self.attributes['stroke'] = color
        self.attributes['stroke-width'] = str(width)

    def set_fill(self, color='black'):
        """Sets the fill color.

        Args:
            color (str): stroke color
        """
        self.style['fill'] = color
        self.attributes['fill'] = color

    def add_arrow_coord(self, line, arrow_height, arrow_width, recess):
        """ Determine the coordinates of an arrow head polygon
            with height (h) and width (w) and recess (r)
            pointing from the one but last to the last point of polyline 'line'.
        """
        # arrow = SvgPolygon(line, _maxlen=4)
        if line.type == 'polyline':
            xe = line.coordsX[-1]
            ye = line.coordsY[-1]
            xp = line.coordsX[-2]
            yp = line.coordsY[-2]
        else:
            xe = line.attributes['x2']
            ye = line.attributes['y2']
            xp = line.attributes['x1']
            yp = line.attributes['y1']
        h = arrow_height
        if arrow_width == 0:
            w = arrow_height / 3
        else:
            w = arrow_width
        r = recess
        self.add_coord(xe, ye)
        dx = xe - xp
        dy = ye - yp
        de = math.sqrt(dx**2 + dy**2)
        xh = xe - h * dx / de
        yh = ye - h * dy / de
        x1 = xh + w * dy / de
        y1 = yh - w * dx / de
        self.add_coord(x1, y1)
        x2 = xe - (h - r) * dx / de
        y2 = ye - (h - r) * dy / de
        self.add_coord(x2, y2)
        x3 = xh - w * dy / de
        y3 = yh + w * dx / de
        self.add_coord(x3, y3)


class Occurrences_diagram():
    ''' Diagrams that display occurrences and their sequence, composition
        and connetions between them. Typically according to the IDEF0 method.
    '''
    def __init__(self, user_interface, gel_net):
        self.user_interface = user_interface
        self.gel_net = gel_net
        self.GUI_lang_index = user_interface.GUI_lang_index
        self.seq_table = user_interface.views.seq_table
        self.involv_table = user_interface.views.involv_table
        self.part_whole_occs = user_interface.views.part_whole_occs

        self.drawings = []
        self.sheets = []
        self.left_str_frames = []
        self.right_str_frames = []
        self.left_str_tables = []
        self.right_str_tables = []
        self.boxes = []
        self.lines = []
        self.part = []

        self.close_button_text = ['Close', 'Sluiten']

    def Create_occurrences_diagram(self, top_occs, object_in_focus):
        """ Prepare for the drawing of one or more IDEF0 sheets
            about one hierarchy of occurrences
            in the product model.
            nrOfOccs: length of chain of sequence occurrences.
            occ_table: same columns as exprTable with all relations
                       that deal with occurrences in the product model.
            seq_table: previusUID, previusName, nextUID, nextName
            involv_table: occur_obj, involved_obj, role_obj (of invObj), invKindName.
            part_whole_occs: whole, part, kind_of_part
        """
        self.object_in_focus = object_in_focus
        self.sheet_nr = -1

        if len(top_occs) == 0:
            # Debug print('*** No top occurrence identified')
            pass
        else:
            # Debug print('*** Number top occurrence {}:'.format(len(top_occs)))
            pass

        # Initialize drawing
        self.Define_notebook_tab_for_drawings()
        # Draw top occurrences on one or more sheet(s)
        parent_id = 0
        self.Draw_multiple_sheets(parent_id, top_occs)

        # Determine parts per top occurrence for drawing on sheet(s)
        self.Draw_part_occurrences(parent_id, top_occs)

    def Define_notebook_tab_for_drawings(self):
        """ Define a Notebook for tabs for multiple drawings
            and call partRelList function.
        """
        occ_text = ['Occurrences involving ', 'Gebeurtenissen betreffende ']
        self.occ_name = occ_text[self.GUI_lang_index] + self.object_in_focus.name
        self.occ_frame = gui.VBox(width='100%', height='80%',
                                  style={'overflow': 'auto',
                                         'background-color': '#eeffdd'})
        self.user_interface.views_noteb.add_tab(self.occ_frame,
                                                self.occ_name,
                                                self.tab_cb(self.occ_name))
        self.screen_width = 1000  # pixels of canvas
        self.screen_height = 800  # pixels of canvas

    def tab_cb(self, tab_name):
        self.user_interface.views_noteb.select_by_name(tab_name)

    def Draw_multiple_sheets(self, parent_id, occs):
        """ Determine nr of sheets for one drawing and call DrawingOfOneSheet
            totalNrOfBoxes to be drawn on one drawing
            may require more than one drawing sheet.
        """
        totalNrOfBoxes = len(occs)
        maxBoxesPerSheet = 7
        firstBox = 0

        nrOfSheets = (totalNrOfBoxes - 1) / maxBoxesPerSheet + 1
        intSheet = int(nrOfSheets)
        rest = totalNrOfBoxes - (intSheet - 1) * maxBoxesPerSheet
        shText = str(parent_id)
        # Debug print('nrOfSheets on level, totalNrOfBoxes, rest:',
        #      intSheet, totalNrOfBoxes, occs[0].name, rest, shText)
        for sh_nr in range(1, intSheet + 1):
            if sh_nr == intSheet:
                nrBoxesPerSheet = rest
            else:
                nrBoxesPerSheet = maxBoxesPerSheet
            self.sheet_nr += + 1
            schema = ['Sheet-' + shText, 'Blad-' + shText]
            sheet_name = schema[self.GUI_lang_index]
            # Initialize drawing for one sheet.
            self.Define_a_drawing_of_one_sheet(sheet_name)
            # Draw one sheet
            self.Draw_a_drawing_of_one_sheet(nrBoxesPerSheet, occs[firstBox:], parent_id)
            firstBox = firstBox + maxBoxesPerSheet
            shText = shText + '-' + str(sh_nr)

    def Draw_part_occurrences(self, parent_id, occs):
        ''' Draw the diagram(s) of the parts of the occurrences occs
            self.part_whole_occs: whole, part, kind_of_part
        '''
        parts = []
        parts_present = False
        seq = 0
        for topOcc in occs:
            seq = seq + 1
            childID = str(parent_id) + '.' + str(seq)
            for whole, part, kind_of_part in self.part_whole_occs:
                # If the whole appears on previous sheet, then there is a part:
                if whole == topOcc:
                    parts_present = True
                    parts.append(part)
            # Draw part occurrences on sheet(s)
            if parts_present is True:
                self.Draw_multiple_sheets(childID, parts)

        if parts_present is True:
            self.Draw_part_occurrences(childID, parts)

    def RightMouseButton(self, event):
        ''' Handle right mouse button click events in occurModel (actTree):
            Determine mid_point coordinates in box_type_1
        '''
        # x,y = Nr of pixels
        print('Activity details: x = %d, y = %d' % (event.x, event.y))
        name = ''
        midPts = self.box_type_1(event.x, event.y, name)
        return midPts

    def Define_a_drawing_of_one_sheet(self, sheet_name):
        """ Create a Notebook page
            and draw one sheet on that page
            and draw boxes by calling box_type_1
            and draw lines between them by calling CreateLine.
        """
        # Occurrences drawing frame tab
##        draw_text = ['Drawing of ', 'Tekening van ']
##        drawing_name = draw_text[self.GUI_lang_index] + sheet_name
##        self.drawing_frame = gui.VBox(width='100%', height='100%',
##                                      style='background-color:#eeffdd')
##        self.drawings.append(self.drawing_frame)
##        self.user_interface.views_noteb.add_tab(self.drawing_frame,
##                                                self.sheet_nr,
##                                                self.tab_cb(drawing_name))
        self.draw_button_row = gui.HBox(height=20, width='100%')

        draw_button_text = ['View', 'Toon']
        self.draw_but = gui.Button(draw_button_text[self.GUI_lang_index],
                                   width='15%', height=20)
        self.draw_but.attributes['title'] = 'Press button to view selected box'
        self.draw_but.onclick.connect(self.RightMouseButton)
        self.draw_button_row.append(self.draw_but)

        self.close_sheet = gui.Button(self.close_button_text[self.GUI_lang_index],
                                      width='15%', height=20)
        self.close_sheet.attributes['title'] = 'Press button when you want to remove this tag'
        self.close_sheet.onclick.connect(
            self.user_interface.Close_tag,
            self.user_interface.views_noteb,
            self.occ_name)
        self.draw_button_row.append(self.close_sheet)
        self.occ_frame.append(self.draw_button_row)

        # Define drawing space widget
        sheet = gui.Svg(width='100%', height='100%')
        sheet.set_viewbox(0, 0, self.screen_width, self.screen_height)
        self.occ_frame.append(sheet)
        self.sheets.append(sheet)

        # Add stream frames - left and right - to occ_frame
        str_frames = gui.HBox(width='100%', height=200,
                              style='background-color:#eeffdd')
        self.left_str_frames.append(gui.VBox(width='50%', height='100%',
                                             style='background-color:#eeffdd'))
        self.right_str_frames.append(gui.VBox(width='50%', height='100%',
                                              style='background-color:#eeffdd'))
        str_frames.append(self.left_str_frames[self.sheet_nr])
        str_frames.append(self.right_str_frames[self.sheet_nr])
        self.occ_frame.append(str_frames)

        # Create left and right stream tables on the sheet
        self.left_str_tables.append(SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'}))
        # Specify and create header row
        str_nr_text = ['Number', 'Nummer']
        str_text = ['Stream Name', 'Stroomnaam']
        uid_text = ['UID', 'UID']
        kind_text = ['Kind', 'Soort']
        columns = [(str_nr_text[self.GUI_lang_index],
                    str_text[self.GUI_lang_index],
                    uid_text[self.GUI_lang_index],
                    kind_text[self.GUI_lang_index])]
        self.left_str_tables[self.sheet_nr].append_from_list(columns, fill_title=True)
        self.left_str_frames[self.sheet_nr].append(self.left_str_tables[self.sheet_nr])

        self.right_str_tables.append(SingleRowSelectionTable(
            width='100%',
            style={'overflow': 'auto', 'background-color': '#eeffaa',
                   'border-width': '2px', 'border-style': 'solid',
                   'font-size': '12px', 'table-layout': 'auto',
                   'text-align': 'left'}))
        self.right_str_tables[self.sheet_nr].append_from_list(columns, fill_title=True)
        self.right_str_frames[self.sheet_nr].append(self.right_str_tables[self.sheet_nr])

        self.uom_color = '#ccf'
        self.occ_color = '#cfc'

    def Draw_a_drawing_of_one_sheet(self, nrOfOccs, occs, parent_id):
        ''' - parent_id: the ID of the whole occurrence(box)
            of which the occNames(occurrences) are parts.
        '''
        outputUID = '640019'     # output role
        inputUID = '640016'      # input role
        actorUID = '5036'        # actor role (supertype of mechanism)
        subOutputs, subOutputUIDs = self.gel_net.Determine_subtype_list(outputUID)
        subInputs, subInputUIDs = self.gel_net.Determine_subtype_list(inputUID)
        subActors, subActorUIDs = self.gel_net.Determine_subtype_list(actorUID)

        thickness = 2
        centerX = []            # X-Center of box[i] on canvas
        centerY = []            # Y-Center of box[i] on canvas
        midPts = []
        boxes_on_sheet = []
        lines_on_sheet = []

        box_width = 120          # pixels
        box_height = 80          # pixels
        self.boxW2 = box_width / 2   # 1/2Width of boxes
        self.boxH2 = box_height / 2   # 1/2Height of boxes

        deltaX = self.screen_width / (nrOfOccs + 1)
        deltaY = self.screen_height / (nrOfOccs + 1)
        dxC = 8                 # corner rounding
        dyC = 8
        # dx = 8                 # shifted start point for line on box
        dy = 8

        # Initialize inputs, outputs, controls and mechanisms according to IDEF0.
        # occCon, occMech, occConUp and 0ccMechUp not yet used, but later exprected
        occIn = []
        occOut = []
        # occCon = []
        # occMech = []
        occInUp = []
        occOutUp = []
        # occConUp = []
        # occMechUp = []
        # Draw boxes (occurrences), return midpts[i] = N(x,y), S(x,y), E(x,y), W(x,y)
        for boxNr in range(0, nrOfOccs):
            centerX.append(deltaX + boxNr * deltaX)     # X of center of box[i] on canvas
            centerY.append(deltaY + boxNr * deltaY)     # Y of center of box[i] on canvas
            self.boxID = str(parent_id) + '.' + str(boxNr + 1)

            midPts.append(self.box_type_1(centerX[boxNr], centerY[boxNr],
                                          occs[boxNr].name))

            # Debug print('NSEWPts:',boxNr,midPts[boxNr])
        self.boxes.append(boxes_on_sheet)

        # Initialize number of I/O/C/M down and upwards for each occurrence on sheet
        occIn = [0 for i in range(0, nrOfOccs)]  # input stream nr of deltas downward
        occOut = [0 for i in range(0, nrOfOccs)]
        # occCon = [0 for i in range(0, nrOfOccs)]  # control stream nr of deltas right
        # occMech = [0 for i in range(0, nrOfOccs)]
        occInUp = [0 for i in range(0, nrOfOccs)]  # input stream nr of deltas upward
        occOutUp = [0 for i in range(0, nrOfOccs)]
        # occConUp = [0 for i in range(0, nrOfOccs)]  # control stream nr of deltas left
        # occMechUp = [0 for i in range(0, nrOfOccs)]

        # Draw lines (streams)
        strNr = 0
        hor_size = 15   # horizontal half size of the rhombus polygon
        vert_size = 25  # vertical half size of the rhombus polygon
        left = True     # indicator for left or right streamTree.
        border = 5

        # Search for lines that have no begin/source occurrence (box),
        # but only a destination occurrence.
        for occur, involved, inv_role_kind, inv_kind_name in self.involv_table:
            # Debug print('ioRow[0]:', occur.uid, occur.name, involved.name, inv_role_kind.name)
            occUIDFrom = '0'
            # If inputStream to occurrence on this sheet, then
            if occur in occs and inv_role_kind.uid in subInputUIDs:
                # IndexTo is the nr of the occ that has stream as input.
                indexTo = occs.index(occur)

                # Verify whether found stream is an output of any box on sheet,
                # then set out = True
                origin = 'external'
                for occur_2, involved_2, inv_role_kind_2, inv_kind_name_2 in self.involv_table:
                    if involved == involved_2 and occur_2 in occs \
                       and inv_role_kind_2.uid in subOutputUIDs:
                        origin = 'box'
                        break

                if origin == 'external':
                    # Input comes from outside the sheet
                    streamUID = involved.uid
                    streamName = involved.name
                    streamKind = inv_kind_name
                    occIn[indexTo] += 1
                    occInUp[indexTo] += 1
                    strNr = strNr + 1
                    strID = str(strNr)
                    endPt = midPts[indexTo][3]
                    beginPt = [border, midPts[indexTo][3][1]]

                    # Draw rhombus at x,y and determine its end points
                    x = (beginPt[0] + endPt[0]) / 2
                    y = beginPt[1]
                    rhombus = self.RhombusPolygon(x, y, strID, hor_size, vert_size)

                    # Draw two straight lines from the left hand side to the rhombus
                    # and from the rhombus to the box
                    lConnPt = rhombus[3]
                    rConnPt = rhombus[2]
                    line1Pts = [beginPt, lConnPt]
                    line2Pts = [rConnPt, endPt]
                    line1 = gui.SvgLine(line1Pts[0][0], line1Pts[0][1],
                                        line1Pts[1][0], line1Pts[1][1])
                    line1.set_stroke(width=thickness, color='black')
                    self.sheets[self.sheet_nr].append(line1)

                    line2 = gui.SvgLine(line2Pts[0][0], line2Pts[0][1],
                                        line2Pts[1][0], line2Pts[1][1])
                    line2.set_stroke(width=thickness, color='black')
                    self.sheets[self.sheet_nr].append(line2)
                    lines_on_sheet.append(line1)
                    lines_on_sheet.append(line2)

                    # Add an arrow head to line2
                    head = SvgPolygon(4)
                    arrow_height = 20
                    arrow_width = arrow_height / 3
                    recess = arrow_height / 5
                    head.add_arrow_coord(line2, arrow_height, arrow_width, recess)
                    head.set_stroke(width=thickness, color='black')
                    head.set_fill(color='blue')
                    self.sheets[self.sheet_nr].append(head)
                    # lines_on_sheet.append(head)

                    # Record stream in left or right stream table
                    values = [strID, streamName, streamUID, streamKind]
                    table_row = gui.TableRow(style={'text-align': 'left'})
                    for field in values:
                        item = gui.TableItem(text=field,
                                             style={'text-align': 'left',
                                                    'background-color': self.occ_color})
                        table_row.append(item)
                    if left is True:
                        # Debug print('Sheet nr:', self.sheet_nr)
                        self.left_str_tables[self.sheet_nr].append(table_row)
                        left = False
                    else:
                        self.right_str_tables[self.sheet_nr].append(table_row)
                        left = True
        # Find streams per occurrence (box) on this sheet in involv_table
        # involv_table: occur_obj, involved_obj, role_obj (of invObj), invKindName.
        # Debug print('subI/O-UIDs:',occs[0].name, subInputUIDs, subOutputUIDs)
        for occ, involved, inv_role_kind, inv_kind_name in self.involv_table:
            # Debug print(' ioRow2:', occs[0].name, occ.name, involved.name, inv_role_kind.uid)
            occUIDTo = '0'
            # If outputStream from occurrence on this sheet, then
            if occ in occs and inv_role_kind.uid in subOutputUIDs:
                # Debug print('**outputStream:', involved.name, inv_role_kind.name)
                strNr = strNr + 1
                strID = str(strNr)
                occUIDFrom = occ.uid
                streamUID = involved.uid
                streamName = involved.name
                streamKind = inv_kind_name
                # Verify if found streamUID is input in box on sheet.
                # If yes, then occUIDTo is known.
                for occ_2, involved_2, inv_role_kind_2, inv_kind_name_2 in self.involv_table:
                    if streamUID == involved_2.uid and occ_2 in occs \
                       and inv_role_kind_2.uid in subInputUIDs:
                        # Debug print('** inputStream:', occ_2.name,
                        #             inv_role_kind_2.name, inv_role_kind_2.name)
                        occUIDTo = occ_2.uid
                        # else occUIDTo remains '0'
                        break
                # Determine index (in list of occs) of boxFrom and boxTo
                indexFrom = -1
                indexTo = -1
                for index in range(0, len(occs)):
                    if occUIDFrom == occs[index].uid:
                        indexFrom = index
                    if occUIDTo == occs[index].uid:
                        indexTo = index

                # Determine the sequenceNr of the input and output of the occurrence box
                # and adjust Yin and Yout accordingly.
                # Draw the stream line from box occUIDFrom to occUIDTo or to edge of sheet.
                if indexTo == -1:
                    # No destination box, thus endPt is on rh side of the sheet.
                    ddyFrom = (occOut[indexFrom]) * dy
                    ddyTo = (occIn[indexTo]) * dy
                    if occOut[indexFrom] == 0:
                        # if not yet started downward, then middle becomes occupied.
                        occOutUp[indexFrom] += 1
                    occOut[indexFrom] += 1
                    # occOut[indexTo] += 1         # indexTo == -1
                    # midPts(occNr, East, x / y)
                    beginPt = [midPts[indexFrom][2][0], midPts[indexFrom][2][1] + ddyFrom]
                    endPt = [self.screen_width - border, beginPt[1]]
                    x = (beginPt[0] + endPt[0]) / 2
                    y = beginPt[1]
                    # Rhombus on vertical line
                    rhombus = self.RhombusPolygon(x, y, strID, hor_size, vert_size)
                    lConnPt = rhombus[3]
                    rConnPt = rhombus[2]
                    line1Pts = [beginPt, lConnPt]
                    line2Pts = [rConnPt, endPt]

                elif indexFrom + 1 < indexTo:
                    # Destination box is behind next box.
                    ddyFrom = (occOut[indexFrom]) * dy
                    ddyTo = (occIn[indexTo]) * dy
                    occOut[indexFrom] += 1
                    occOut[indexTo] += 1
                    beginPt = [midPts[indexFrom][2][0], midPts[indexFrom][2][1] + ddyFrom]
                    endPt = [midPts[indexTo][3][0], midPts[indexTo][3][1] + ddyTo]
                    mid1Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2 - dxC, beginPt[1]]
                    mid2Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2, beginPt[1] + dyC]
                    mid3Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2, endPt[1] - dyC]
                    mid4Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2 + dxC, endPt[1]]
                    x = mid2Pt[0]
                    y = (mid2Pt[1] + mid3Pt[1]) / 2
                    rhombus = self.RhombusPolygon(x, y, strID, hor_size, vert_size)
                    uConnPt = rhombus[0]
                    lConnPt = rhombus[1]
                    line1Pts = [beginPt, mid1Pt, mid2Pt, uConnPt]
                    line2Pts = [lConnPt, mid3Pt, mid4Pt, endPt]

                elif indexFrom + 1 > indexTo:
                    # Destination box id before source box (or the box itself).
                    ddyUpFrom = (occOutUp[indexFrom]) * dy
                    ddyUpTo = (occInUp[indexTo]) * dy
                    occOutUp[indexFrom] += 1
                    occOutUp[indexTo] += 1
                    beginPt = [midPts[indexFrom][2][0], midPts[indexFrom][2][1] - ddyUpFrom]
                    endPt = [midPts[indexTo][3][0], midPts[indexTo][3][1] - ddyUpTo]
                    mid1Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2 - dxC, beginPt[1]]
                    mid2Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2, beginPt[1] - dyC]
                    mid3Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2,
                              endPt[1] - box_height + dyC]
                    mid4Pt = [(beginPt[0] + midPts[indexFrom + 1][3][0]) / 2 - dxC,
                              endPt[1] - box_height]
                    mid5Pt = [(endPt[0] - box_width / 2) + dxC, endPt[1] - box_height]
                    mid6Pt = [(endPt[0] - box_width / 2), endPt[1] - box_height + dyC]
                    mid7Pt = [(endPt[0] - box_width / 2), endPt[1] - dyC]
                    mid8Pt = [(endPt[0] - box_width / 2) + dxC, endPt[1]]
                    x = mid2Pt[0]
                    y = (mid2Pt[1] + mid3Pt[1]) / 2
                    rhombus = self.RhombusPolygon(x, y, strID, hor_size, vert_size)
                    uConnPt = rhombus[0]
                    lConnPt = rhombus[1]
                    line1Pts = [beginPt, mid1Pt, mid2Pt, lConnPt]
                    line2Pts = [uConnPt, mid3Pt, mid4Pt, mid5Pt,
                                mid6Pt, mid7Pt, mid8Pt, endPt]

##                    if mid5Pt[1] < 0:
##                        self.sheets[self.sheet_nr].yview_scroll(int(-mid5Pt[1]) + 20, 'units')
                else:
                    # Destination box is next box
                    ddyFrom = (occOut[indexFrom]) * dy
                    ddyUpTo = (occIn[indexTo]) * dy
                    occOut[indexFrom] += 1
                    occOutUp[indexTo] += 1
                    beginPt = [midPts[indexFrom][2][0], midPts[indexFrom][2][1] + ddyFrom]
                    endPt = [midPts[indexTo][3][0], midPts[indexTo][3][1] - ddyUpTo]
                    mid1Pt = [(beginPt[0] + endPt[0]) / 2 - dxC, beginPt[1]]
                    mid2Pt = [(beginPt[0] + endPt[0]) / 2, beginPt[1] + dyC]
                    mid3Pt = [(beginPt[0] + endPt[0]) / 2, endPt[1] - dyC]
                    mid4Pt = [(beginPt[0] + endPt[0]) / 2 + dxC, endPt[1]]
                    x = mid2Pt[0]
                    y = (mid2Pt[1] + mid3Pt[1]) / 2
                    rhombus = self.RhombusPolygon(x, y, strID, hor_size, vert_size)
                    uConnPt = rhombus[0]
                    lConnPt = rhombus[1]
                    line1Pts = [beginPt, mid1Pt, mid2Pt, uConnPt]
                    line2Pts = [lConnPt, mid3Pt, mid4Pt, endPt]

                # Draw polyline 1 from box to rhombus and polyline 2 from rhombus to box
                # Debug print('  Stream:', indexFrom, indexTo, line1Pts)
                line1 = gui.SvgPolyline(_maxlen=4)
                for pt in line1Pts:
                    line1.add_coord(pt[0], pt[1])
                line1.set_stroke(width=thickness, color='black')
                self.sheets[self.sheet_nr].append(line1)

                line2 = gui.SvgPolyline(_maxlen=8)
                for pt in line2Pts:
                    line2.add_coord(pt[0], pt[1])
                line2.set_stroke(width=thickness, color='black')
                self.sheets[self.sheet_nr].append(line2)
                lines_on_sheet.append(line1)
                lines_on_sheet.append(line2)

                # Add an arrow head to line2
                head2 = SvgPolygon(4)
                arrow_height = 20
                arrow_width = arrow_height / 3
                recess = arrow_height / 5
                head2.add_arrow_coord(line2, arrow_height, arrow_width, recess)
                head2.set_stroke(width=thickness, color='black')
                head2.set_fill(color='blue')
                self.sheets[self.sheet_nr].append(head2)

                # Record stream in self.left_str_tables
                # or in self.right_str_tables[self.sheet_nr](s)
                values = [strID, streamName, streamUID, streamKind]
                table_row = gui.TableRow(style={'text-align': 'left'})
                for field in values:
                    item = gui.TableItem(text=field,
                                         style={'text-align': 'left',
                                                'background-color': self.occ_color})
                    table_row.append(item)
                if left is True:
                    self.left_str_tables[self.sheet_nr].append(table_row)
                    left = False
                else:
                    self.right_str_tables[self.sheet_nr].append(table_row)
                    left = True

        self.lines.append(lines_on_sheet)

    def box_type_1(self, X, Y, name):
        """ Draw a box with name on sheet around (X,Y) = Xcenter and Ycenter
            Return midpts = N(x,y), S(x,y), E(x,y), W(x,y)
            (X,Y) = center of box on canvas
        """
        x0, y0 = X - self.boxW2, Y - self.boxH2        # TopLeft of box
        x1, y1 = X + self.boxW2, Y + self.boxH2        # BottomRight of box
        width = x1 - x0
        height = y1 - y0

        box = gui.SvgRectangle(x0, y0, width, height)
        box.set_stroke(width=2, color='black')
        box.set_fill(color='yellow')
        box_name = gui.SvgText(X, Y, name)
        box_name.attributes['text-anchor'] = 'middle'
        box_id = gui.SvgText(X, Y + 15, str(self.boxID))
        box_id.attributes['text-anchor'] = 'middle'
        self.sheets[self.sheet_nr].append([box, box_name, box_id])

        mid_north = [X, Y - self.boxH2]
        mid_south = [X, Y + self.boxH2]
        mid_east = [X + self.boxW2, Y]
        mid_west = [X - self.boxW2, Y]

        return mid_north, mid_south, mid_east, mid_west

    def RhombusPolygon(self, X, Y, strID, hor_size, vert_size):
        """ Draw a rhombus polygon with its center on position X,Y
            with its strID as text in the middle on sheet.
        """
        x0, y0 = X - hor_size, Y    # mid_west
        x1, y1 = X, Y - vert_size   # mid_north
        x2, y2 = X + hor_size, Y    # mid_east
        x3, y3 = X, Y + vert_size   # mid_south

##        sheet.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3,
##                             fill='#dfd', smooth=0, outline='black')
##        sheet.create_text(X, Y, justify=CENTER, text=strID)
        polygon = SvgPolygon(4)
        polygon.set_stroke(width=2, color='black')
        poly_name = gui.SvgText(X, Y + 5, strID)
        poly_name.attributes['text-anchor'] = 'middle'
        self.sheets[self.sheet_nr].append([polygon, poly_name])

        mid_north = [x1, y1]
        mid_south = [x3, y3]
        mid_east = [x2, y2]
        mid_west = [x0, y0]

        polygon.add_coord(*mid_north)
        polygon.add_coord(*mid_east)
        polygon.add_coord(*mid_south)
        polygon.add_coord(*mid_west)

        return mid_north, mid_south, mid_east, mid_west
