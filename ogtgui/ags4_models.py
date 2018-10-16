# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""
from Qt import QtGui, QtCore, Qt, pyqtSignal

from img  import Ico


from ogt import ags4

import app_globals as G

import xobjects

class AGS4_TYPE:
    abbrev = "ABBR"
    abbrev_item = "ABBR_ITEM"
    group = "GROUP"
    heading = "HEADING"
    note = "NOTE"


class AGS4_COLORS:
    group = "#286225"
    abbrev = "#496FA3"


SHOW_NONE = "##__NONE__##"
"""Used to filter for nothing"""

def data_type_ico(ags_type):
    """Returns an icon filename for the data type"""
    v = ags_type.upper()

    # Date time
    if v in ["DT"]:
        return Ico.TypeDate

    # decimal places
    if v.endswith("DP"):
        return  Ico.TypeDecimal

    # UID
    # TODO: (is this realy UID in doucment ?? aslks pete)
    if v == "ID":
        return  Ico.TypeID

    # Picklists
    if v in ["PA", "PU", "PT"]:
        return  Ico.TypePicklist

    # Scientific stuff
    if v.endswith("SCI"):
        return  Ico.TypeSci

    # Boolean yes/no, false, true, not false
    if v == "YN":
        return  Ico.TypeCheckBox

    # text and text in general
    if v in ["X"]:
        return  Ico.TypeText

    # oopps
    return Ico.TypeUnknown

def data_type_qicon(ags_type):
    """Return a QIcon for and ags.data_type"""
    return Ico.icon(data_type_ico(ags_type))

##===================================================================
## Main
##===================================================================
class Ags4Object(QtCore.QObject):

    sigLoaded = pyqtSignal()

    def __init__( self, parent=None):
        super(QtCore.QObject, self).__init__(parent)

        self.modelNotes = NotesModel()
        self.modelUnits = UnitsModel(self)
        self.modelTypes = TypesModel(self)

        self.modelClasses = ClassesModel(self)
        self.modelGroups = GroupsModel(self)
        self.modelHeadings = HeadingsModel(self)

        #self.modelAbbrevClasses = ClassesModel(self)
        #self.modelAbbrevs = AbbrevsModel(self)

        self.modelAbbrItems = AbbrevItemsModel(self)

        #self.modelGroups.sigClasses.connect(self.modelClasses.load_classes)

        #self.connect(self.modelAbbrevs, QtCore.SIGNAL("classes"), self.modelAbbrevClasses.load_classes)


    def init_load(self):
        err = ags4.AGS4.initialise()
        if err:
            panicssss


        self.load()

    def load(self):

        #self.modelAbbrItems.load_data(ags4.AGS4.abbrs())

        self.modelClasses.set_ags4dd(ags4.AGS4)
        self.modelGroups.set_ags4dd(ags4.AGS4)

        self.modelUnits.set_ags4dd(ags4.AGS4)
        self.modelTypes.set_ags4dd(ags4.AGS4)

        self.modelNotes.init_words()

        self.sigLoaded.emit()



    def get_group(self, code):
        return self.modelGroups.get_group(code)

    def deadget_abbrev(self, head_code):
        return self.modelAbbrevItems.get_abbrev(head_code)

    def has_abbrev(self, head_code):
        """Check `head_code` exists


        :param head_code:

        """
        return self.modelAbbrevItems.has_abbrev(head_code)
#
    def get_words(self):
        return self.modelNotes.get_words()

    def get_notes(self, group_code):
        return self.modelNotes.get_notes(group_code)

    def get_heading(self, head_code):
        return self.modelHeadings.get_heading(head_code)

    def get_picklist(self, abbrev):

        #print self.modelAbbrevItems.get_picklist(abbrev)
        return self.modelAbbrevItems.get_picklist(abbrev)
        """
        if not abbrev in self._abbrevs:
            return None
        vals = self._abbrevs[abbrev]['vals']
        dic = {}
        for v in vals:
            dic[v['val_code']] = v
        return [ dic[k] for k in sorted( dic.keys() ) ]

        return None
        """
class NotesModel():

    def __init__(self):

        self.d = {}
        self.words = {}

    def remove_rows(self):
        self.d = {}
        self.words = {}

    def append_notes(self, group_code, recs):

        self.d[group_code] = recs


    def add_words(self, rows):

        for rec in rows:
            if rec['code'] in self.words:
                pass #print "panic", rec, self.words[rec['code']]
            else:
                self.words[rec['code']] = rec


    def init_words(self):

        self.words = {}
        #print "TODO words", self
        #self.add_words( G.Ags.modelAbbrevs.get_words() )
        #self.add_words( G.ags.modelGroups.get_words() )
        #self.add_words( G.ags.modelHeadings.get_words() )
        #print self.words

    def get_words(self):
        return self.words

    def get_notes(self, group_code):
        return self.d.get(group_code)

class CG:
    code = 0
    description = 1
    cls = 2
    search = 3
    _col_count = 4

##===================================================================
## Groups
##===================================================================
class GroupsModel(QtCore.QAbstractItemModel):

    def __init__( self, parent=None):
        QtCore.QAbstractItemModel.__init__( self, parent)
        self.ags4dd = None

    def set_ags4dd(self, ags4dd):
        self.ags4dd = ags4dd
        self.reset()

    def columnCount(self, midx):
        return CG._col_count

    def rowCount(self, midx):
        if self.ags4dd == None:
            return 0
        return self.ags4dd.groups_count()

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def parent(self, pidx=None):
        return QtCore.QModelIndex()

    def data(self, midxx, role):

        col = midxx.column()

        if role == Qt.DisplayRole:
            # the the ags grp
            grp = self.ags4dd.group_by_row_index(midxx.row())

            if col == 0:
                return grp['group_code']
            if col == 1:
                return grp['group_description']
            if col == 2:
                return grp['class']
            if col == 3:
                return (grp['group_code'] + grp['group_description']).replace(" ", "")

        if role == Qt.DecorationRole:
            if col == 0:
                return Ico.icon(Ico.AgsGroup)

        if role == Qt.FontRole:
            if col == 0:
                f = QtGui.QFont()
                f.setBold(True)
                f.setFamily("monospace")
                return f

        return None

    def rec_from_midx(self, midx):
        #print "get=", midx.row()
        return self.ags4dd.group_by_row_index(midx.row())

    def headerData(self, p_int, orient, role=None):

        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            heads = ["Code", "Description", "Classification", "Search"]
            return heads[p_int]



    def load_dataDEAD(self, groups):

        self.remove_rows()
        G.ags.modelHeadings.remove_rows()
        G.ags.modelNotes.remove_rows()

        classes = []

        for group_code in groups.keys():
            rec = groups[group_code]
            items = self.make_blank_row()

            items[CG.code].set(rec['group_code'], bold=True, ico=Ico.AgsGroup, font="monospace")
            items[CG.description].set(rec['group_description'])
            items[CG.search].set( rec['group_code'] + rec['group_description'] )
            items[CG.cls].set(rec['class'])
            self.appendRow(items)

            if not rec['class'] in classes:
                classes.append(rec['class'])

            G.ags.modelHeadings.append_headings(rec)
            G.ags.modelNotes.append_notes(group_code, rec['notes'])


        self.sigClasses.emit(classes)

    def get_group(self, code):
        items = self.findItems(code, Qt.MatchExactly, CG.code)
        #print "GET+", code
        if len(items) == 0:
            # not in ags data dict
            return None
        ridx = items[0].index().row()
        return dict(	group_code=self.item(ridx, CG.code).s(),
                        group_description=self.item(ridx, CG.description).s(),
                        cls=self.item(ridx, CG.cls).s())

    def get_words(self):

        lst = []
        for ridx in range(0, self.rowCount()):
            lst.append( dict(type=AGS4_TYPE.group, description=self.item(ridx, CG.description).s(),
                            code=self.item(ridx, CG.code).s()))
        return lst


##===================================================================
## Headings
##===================================================================



#class HeadingsModel(xobjects.XStandardItemModel):
class HeadingsModel(QtCore.QAbstractItemModel):

    class CH:
        """Columns NO's for the ;class:`~ogtgui.ags_models.HeadingsModel`"""
        head_code = 0
        description = 1
        unit = 2
        data_type = 3
        example = 4
        status = 5
        sort_order = 6
        _col_count = 7

    def __init__( self, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        self.grpDD = None

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def set_group(self, grpdd):
        self.grpDD = grpdd
        self.reset()

    def columnCount(self, midx):
        return self.CH._col_count

    def rowCount(self, midx):
        if self.grpDD == None:
            return 0
        return len(self.grpDD.get("headings"))

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def parent(self, pidx=None):
        return QtCore.QModelIndex()

    def data(self, midxx, role):

        col = midxx.column()

        if role == Qt.DisplayRole:
            rec = self.grpDD["headings"][midxx.row()]

            if col == self.CH.head_code:
                return rec['head_code']

            if col == self.CH.description:
                return rec['head_description']

            if col == self.CH.data_type:
                return rec['data_type']

            if col == self.CH.unit:
                return rec['unit']

            if col == self.CH.status:
                return rec['head_status']

            if col == self.CH.example:
                return rec['example']

            if col == self.CH.sort_order:
                return rec['sort_order']



        if role == Qt.DecorationRole:
            if col == self.CH.head_code:
                return data_type_qicon( self.grpDD["headings"][midxx.row()]['data_type'] )

        if role == Qt.FontRole:
            if col == self.CH.head_code:
                f = QtGui.QFont()
                f.setBold(True)
                f.setFamily("monospace")
                return f

        return None



    def rec_from_midx(self, midx):
        return self.grpDD.get("headings")[midx.row()]

    def headerData(self, p_int, orient, role=None):

        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            heads = ["Heading", "Description", "Unit", "Type",  "Example", "Stat", "Srt"]
            return heads[p_int]


    def append_headingsDEAD(self, grp):

        for rec in grp['headings']:
            #print rec.keys()
            # print rec
            ico = type_ico(rec['type'])

            items = self.make_blank_row()
            items[CH.head_code].set(rec['head_code'], ico=ico, bold=True, font="monospace")

            items[CH.data_type].set(rec['type'])
            items[CH.unit].set( rec['unit'])
            items[CH.description].set( rec['head_description'])
            items[CH.sort].set(rec['sort_order'])
            items[CH.example].set(rec['example'])

            items[CH.group_code].set(grp['group_code'])
            items[CH.group_descr].set(grp['group_description'])
            items[CH.class_].set(grp['class'])

            self.appendRow(items)


    def get_words(self):

        lst = []
        for ridx in range(0, self.rowCount()):
            lst.append( dict(type=AGS4_TYPE.heading, description=self.item(ridx, CH.description).s(),
                            code=self.item(ridx, CH.head_code).s()))
        return lst

    def get_heading(self, code):
        items = self.findItems(code, Qt.MatchExactly, CH.head_code)
        if len(items) == 0:
            return None
        #print "GET+", code, items
        ridx = items[0].index().row()
        return dict(	head_code=self.item(ridx, CH.head_code).s(),
                        head_description=self.item(ridx, CH.description).s(),
                        group_code=self.item(ridx, CH.group_code).s(),
                        #group_code=self.item(ridx, CH.group_code).s(),
                        data_type=self.item(ridx, CH.data_type).s())

##===================================================================
## Abbrev Values
##===================================================================




class AbbrevItemsModel(QtCore.QAbstractItemModel):

    class CA:
        """Columns no's for the :class:`~ogtgui.ags4_models.AbbrevItemsModel` """
        code = 0
        description = 1
        _col_count = 2

    def __init__( self, parent=None):
        #super(xobjects.XStandardItemModel, self).__init__(parent)
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        self.abbrDD = None

    def set_heading(self, heading):


        # self.proxy.setFilterFixedString(SHOW_NONE if head_code == None else head_code)
        self.abbrDD = None
        if heading == None:
            return
        print heading.keys(), self


        dic = ags4.AGS4.abbrs(heading['head_code'])
        if dic:
            self.abbrDD = dic.get("abbrs")

        self.reset()
        #if self.abbrDD == None:
        #    return


        #return

        #self.ags4dd = ags4dd
        #self.reset()

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def parent(self, pidx=None):
        return QtCore.QModelIndex()

    def columnCount(self, midx=None):
        return self.CA._col_count

    def rowCount(self, midx=None):
        if self.abbrDD == None:
            return 0
        return len(self.abbrDD)

    def headerData(self, p_int, orient, role=None):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            heads = ["Type", "Description"]
            return heads[p_int]

    def data(self, midxx, role):

        col = midxx.column()

        if role == Qt.DisplayRole:
            # the the ags grp
            rec = self.abbrDD[midxx.row()]
            # print rec
            if col == self.CA.code:
                return rec['code']
            if col == self.CA.description:
                return rec['description']

        if role == Qt.FontRole:
            if col == self.CA.code:
                f = QtGui.QFont()
                f.setBold(True)
                f.setFamily("monospace")
                return f

        return None


    def deadload_data(self, data):
        self.remove_rows()
        for head_code, recs in data.iteritems():
            self.append_abbrv_items(head_code, data[head_code]['abbrs'])

    def deadappend_abbrv_items(self, head_code, recs):

        for rec in recs:
            items = self.make_blank_row()
            items[CA.code].set(rec['code'], ico=Ico.AgsAbbrevItem, bold=True, font="monospace")
            items[CA.description].set(rec['description'])
            items[CA.head_code].set(head_code)
            self.appendRow(items)

    def deadhas_abbrev(self, head_code):
        return len(  self.findItems(head_code, Qt.MatchExactly, CA.head_code) ) > 0

    def deadget_picklist(self, abbrev_code):
        lst = []
        items = self.findItems(abbrev_code, Qt.MatchExactly, CA.code)
        for item in items:
            row = self.get_items_from_item(item)

            lst.append( dict(	item_code = row[CA.item_code].s(),
                                item_description = row[CA.item_description].s()
                                ))

        return lst

    def deadget_row(self, item):
        return self.get_row_from_item(item)

##===================================================================
## Classes
##===================================================================
class ClassesModel(xobjects.XStandardItemModel):

    #sigLoaded = pyqtSignal()

    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        self.ags4dd = None

        self.set_header(0, "Class")

        ## make root node
        items = self.make_blank_row()
        items[0].set("All", ico=Ico.Folder)
        self.appendRow(items)

    def set_ags4dd(self, ags4dd):
        self.ags4dd = ags4dd

        ## get unique list of classes by walking groups
        classes = []
        for g in self.ags4dd.groups_list():
            if not g['class'] in classes:
                classes.append(g['class'])
        classes.sort()

        rootItem = self.item(0, 0)  # 'All' parent

        ## remove existing nodes
        while rootItem.hasChildren():
            rootItem.removeRow(0)

        ## add items
        for r in classes:
            citems = self.make_blank_row()
            citems[0].set(r)
            rootItem.appendRow(citems)

        #self.sigLoaded.emit()

    # def deadcolumnCount(self, midx):
    #     return 1
    #
    # def rowCount(self, midx):
    #     if self.ags4dd == None:
    #         return 0
    #     return len(self.classes)
    #
    # def index(self, row, col, parent=None):
    #     return self.createIndex(row, col)
    #
    # def parent(self, child=None):
    #     print "p=", child.row(), child.column() #, pidx.parent()
    #     return QtCore.QModelIndex()
    #
    # def data(self, midxx, role):
    #
    #     col = midxx.column()
    #
    #     if role == Qt.DisplayRole:
    #         # the the ags grp
    #         print "<<", midxx.row(), midxx.column(), midxx.parent()
    #         return "XXX %s" % midxx.row()

##===================================================================
## Units + Types
##===================================================================



class UnitsModel(QtCore.QAbstractItemModel):

    class CU:
        unit = 0
        description = 1

    def __init__( self, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        self.ags4dd = None

    def set_ags4dd(self, ags4dd):

        self.ags4dd = ags4dd
        self.reset()

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def parent(self, pidx=None):
        return QtCore.QModelIndex()

    def columnCount(self, midx=None):
        return 2

    def rowCount(self, midx=None):
        if self.ags4dd == None:
            return 0
        return len(self.ags4dd.units_list())

    def headerData(self, p_int, orient, role=None):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            heads = ["Type", "Description"]
            return heads[p_int]

    def data(self, midxx, role):

        col = midxx.column()

        if role == Qt.DisplayRole:
            # the the ags grp
            rec = self.ags4dd.units_list()[midxx.row()]
            #print rec
            if col == self.CU.unit:
                return rec['unit']
            if col == self.CU.description:
                return rec['description']

        if role == Qt.FontRole:
            if col == self.CU.unit:
                f = QtGui.QFont()
                f.setBold(True)
                f.setFamily("monospace")
                return f

        return None




class TypesModel(QtCore.QAbstractItemModel):

    class CT:
        data_type = 0
        description = 1

    def __init__( self, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)

        self.ags4dd = None

    def set_ags4dd(self, ags4dd):
        self.ags4dd = ags4dd
        self.reset()

    def index(self, row, col, parent=None):
        return self.createIndex(row, col)

    def parent(self, pidx=None):
        return QtCore.QModelIndex()

    def columnCount(self, midx=None):
        return 2

    def rowCount(self, midx=None):
        if self.ags4dd == None:
            return 0
        return len(self.ags4dd.types_list())

    def headerData(self, p_int, orient, role=None):

        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            heads = ["Type", "Description"]
            return heads[p_int]


    def data(self, midxx, role):

        col = midxx.column()

        if role == Qt.DisplayRole:
            rec = self.ags4dd.types_list()[midxx.row()]
            if col == self.CT.data_type:
                return rec['data_type']
            if col == self.CT.description:
                return rec['description']

        # if role == Qt.DecorationRole:
        #     if col == 0:
        #         return Ico.icon(Ico.AgsHeading)

        if role == Qt.FontRole:
            if col == 0:
                f = QtGui.QFont()
                f.setBold(True)
                f.setFamily("monospace")
                return f

        return None


    def load_datadead(self, recs):

        #recs = data['units']

        for rec in recs:
            items = self.make_blank_row()
            items[CT.type].set(rec['type'], bold=True, font="monospace")
            items[CT.description].set(rec['description'])
            self.appendRow(items)

        self.sigLoaded.emit()
