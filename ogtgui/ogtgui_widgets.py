# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os
import collections

from Qt import QtGui, QtCore, Qt, pyqtSignal

import xwidgets
from img import Ico
from ogt import ags4
from ogt import ERR_COLORS

import app_globals as G

def bg_color(descr):
    if descr == ags4.AGS4.GROUP:
        return "#D4C557"

    if descr == ags4.AGS4.HEADING:
        return "#FCF66D"

    if descr in [ags4.AGS4.UNIT, ags4.AGS4.TYPE]:
        return "#FFE8B9"

    if descr == ags4.AGS4.DATA:
        return "#DFD1FF"

    return "#ffffff"

class FILTER_ROLE:
    warn = Qt.UserRole + 3
    err = Qt.UserRole + 5
class OGTSourceViewWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """



    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("OGTSourceViewWidget")

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)

        # Source View
        self.sourceView = xwidgets.LNTextEdit()
        self.tabWidget.addTab(self.sourceView, "Raw Text")

        # Grid view
        widget = QtGui.QWidget()
        gridLay = xwidgets.vlayout()
        widget.setLayout(gridLay)
        self.tabWidget.addTab(widget, "Grid View")

        self.splitter = QtGui.QSplitter()
        self.splitter.setObjectName(self.objectName() + "grid_splitter")
        gridLay.addWidget(self.splitter)

        sty = "QTableView {gridline-color: #dddddd;}"
        self.tableWidget = QtGui.QTableWidget()
        self.splitter.addWidget(self.tableWidget)

        self.tableWidget.setStyleSheet(sty)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.itemSelectionChanged.connect(self.on_select_changed)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.on_row_clicked)

        self.errorsWidget = OGTErrorsWidget()
        self.errorsWidget.setMinimumWidth(300)
        self.splitter.addWidget(self.errorsWidget)
        self.errorsWidget.sigGotoSource.connect(self.select_cell)
        self.errorsWidget.sigErrorsFilter.connect(self.update_colours)

        G.settings.restore_splitter(self.splitter)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        self.tabWidget.setCurrentIndex(1)

    def clear(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.sourceView.setText("")
        self.errorsWidget.clear()

    def on_splitter_moved(self, i, pos):
        G.settings.save_splitter(self.splitter)

    def load_document(self, doco):

        self.sourceView.setText(doco.source)

        show_warn, show_err = self.errorsWidget.get_error_filters()
        #print "filters=", show_warn, show_err
        #print doco.cells()
        self.tableWidget.setRowCount(len(doco.csv_rows))

        for ridx, row in enumerate(doco.csv_rows):

            # each csv_row is not the same, so extend here
            if self.tableWidget.columnCount() < len(row):
                self.tableWidget.setColumnCount(len(row))


            #errs = doco.error_cells.get(ridx)
            #print ridx, errs
            bg = None
            for cidx, cell in enumerate(row):
                #print ridx, cidx
                #if cidx == 0:
                #    bg = bg_color(cell)
                item = xwidgets.XTableWidgetItem()
                item.setText( cell )
                item.set_bg("#EAFFE0")
                self.tableWidget.setItem(ridx, cidx, item)


                errs = doco.get_errors(lidx=ridx, cidx=cidx)
                if errs != None:
                    #print ridx, cidx, errs
                    for er in errs:
                        #print ridx, cidx, er.error
                        if er.type:
                            item.setData(FILTER_ROLE.err, "1")
                        else:
                            item.setData(FILTER_ROLE.warn, "1")
                        """    
                        if er.cidx == cidx:
                            item.set_bg(er.bg)
                        """
                    self.set_item_bg(item, show_warn, show_err)
                ## color the row
                #item.setBackgroundColor(QtGui.QColor(bg))
            self.tableWidget.setRowHeight(ridx, 20)


        self.errorsWidget.load_document(doco)

    def set_item_bg(self, item, show_warn, show_err):
        has_warn = item.data(FILTER_ROLE.warn).toBool()
        has_err = item.data(FILTER_ROLE.err).toBool()
        item.set_bg("white")
        if show_warn and has_warn:
            item.set_bg(ERR_COLORS.warn_bg)
        if show_err and has_err:
            item.set_bg(ERR_COLORS.err_bg)


    def update_colours(self, show_warn, show_err):
        self.tableWidget.setUpdatesEnabled(False)
        for ridx in range(0, self.tableWidget.rowCount()):
            for cidx in range(0, self.tableWidget.columnCount()):
                item = self.tableWidget.item(ridx, cidx)
                if item:
                    self.set_item_bg(item, show_warn, show_err)
        self.tableWidget.setUpdatesEnabled(True)

    def select_cell(self, lidx, cidx):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tableWidget))
        self.tableWidget.setCurrentCell(lidx, cidx)
        item = self.tableWidget.currentItem()
        self.tableWidget.scrollToItem(item, QtGui.QAbstractItemView.PositionAtCenter)


    def on_select_changed(self):
        item = self.tableWidget.currentItem()
        if item == None:
            self.errorsWidget.select_items(None, None)
            return

        self.errorsWidget.select_items(item.row(), item.column())


    def on_row_clicked(self, ridx):
        print ridx

class OGTScheduleWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        # spread view
        self.tableWidget = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.tableWidget)


    def clear(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)


    def load_document(self, doco):


        samples = doco.group("SAMP")
        sched_group = doco.group("LBST")

        if samples == None or sched_group == None:
            return

        sched = {}
        locs = {}
        for row in sched_group.data:
            #print row
            tst = row.get('LBST_TEST')
            if not tst in sched:
                sched[tst] = dict(test=tst, samp_refs={})
                #tests.append(tst)
            loc = row.get('LOCA_ID') # + "~~" + row.get("SAMP_REF")
            if not loc in locs:
                locs[loc] = collections.OrderedDict()

            samp_ref = row.get("SAMP_REF")
            if not samp_ref in locs[loc]:
                locs[loc][samp_ref] = {}

            locs[loc][samp_ref][tst] = dict(loca_id=loc,
                                            samp_ref=samp_ref,
                                            params = row.get('LBST_METH') )

        #print sched
        tests = sorted(sched.keys())
        self.tableWidget.setColumnCount(len(tests) + 2)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("LOCA_ID", bold=True)

        self.tableWidget.setHorizontalHeaderItem(0, hitem)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("SAMP_REF", bold=True)
        f = hitem.font()
        f.setBold(True)
        hitem.setFont(f)
        self.tableWidget.setHorizontalHeaderItem(1, hitem)

        for cidx, ki in enumerate(tests):
            tst = sched[ki]
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(ki, bold=True)
            self.tableWidget.setHorizontalHeaderItem(cidx + 2, hitem)

        #print locs
        for loca in sorted(locs.keys()):

            for samp_ref in locs[loca].keys():

                row_idx = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row_idx  + 1)

                bg = "#dddddd"

                #print loca, locs[loca]
                item = xwidgets.XTableWidgetItem()
                item.set(loca, bold=True, bg=bg)
                self.tableWidget.setItem(row_idx, 0, item)

                item = xwidgets.XTableWidgetItem()
                item.set(samp_ref, bold=True, bg=bg, align=Qt.AlignCenter)
                self.tableWidget.setItem(row_idx, 1, item)

                #print locs[loca][samp_ref]
                for cidx, tst_ki in enumerate(tests):

                    item = xwidgets.XTableWidgetItem()

                    if tst_ki in locs[loca][samp_ref]:

                        tst = locs[loca][samp_ref][tst_ki]


                        item.set(tst['params'], bg="yellow", check=Qt.Checked)


                    else:
                        item.setCheckState(Qt.Unchecked)

                    self.tableWidget.setItem(row_idx, cidx + 2, item)

        # resize columns, with max_width
        col_width = 200

        self.tableWidget.resizeColumnsToContents()
        for cidx in range(0, self.tableWidget.columnCount()):
            if self.tableWidget.columnWidth(cidx) > col_width:
                self.tableWidget.setColumnWidth(cidx, col_width)


class C_EG:
    """Columns for examples"""
    file_name = 0

class ExamplesWidget( QtGui.QWidget ):

    sigFileSelected = pyqtSignal(object)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.setMinimumWidth(300)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeWidget()
        self.mainLayout.addWidget(self.tree, 30)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().hide()

        hi = self.tree.headerItem()
        hi.setText(C_EG.file_name, "Example")


        self.tree.itemClicked.connect(self.on_tree_item_clicked)

        self.load_files_list()



    def load_files_list(self, sub_dir=None):

        files_list, err = ags4.examples_list()
        if err:
            pass #TODO
        self.tree.clear()

        for fd in files_list:
            file_name = fd["file_name"]
            item = QtGui.QTreeWidgetItem()
            item.setText(C_EG.file_name, file_name)
            item.setIcon(C_EG.file_name, Ico.icon(Ico.Ags4))
            f = item.font(C_EG.file_name)
            f.setBold(True)
            item.setFont(C_EG.file_name, f)
            self.tree.addTopLevelItem(item)



    def on_tree_item_clicked(self, item, col):

        file_name = str(item.text(C_EG.file_name))
        self.sigFileSelected.emit(file_name)



class ErrorsListModel(QtCore.QAbstractTableModel):

    class C:
        err = 0
        lidx = 1
        cidx = 2
        rule = 3
        highlight = 4
        description = 5
        search = 6

    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)

        self.ogtDoc = None
        self._col_labels = ["Type", "Line", "Col", "Rule", "High", "Description", "search"]

    def load_document(self, ogtDoc):
        self.ogtDoc = ogtDoc
        self.modelReset.emit()
        #print self.ogtDoc, self

    def columnCount(self, foo):
        return len(self._col_labels)

    def rowCount(self, midx):
        if self.ogtDoc == None:
            return 0
        return self.ogtDoc.errors_count()

    def data(self, midx, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        row = midx.row()
        col = midx.column()
        errors = self.ogtDoc.errors_list()


        if role == Qt.DisplayRole or role == Qt.EditRole:
            grp = self.ogtDoc.group_by_index(row)
            #print "grp=", grp
            if midx.column() == self.C.err:
                return "1"
            if midx.column() == self.C.group_description:
                return grp.group_description
            if midx.column() == self.C.data_count:
                return grp.data_rows_count()
            return "?"

        if role == Qt.DecorationRole:
            if col == self.C.group_code:
                return Ico.icon(Ico.Group)

        if role == Qt.FontRole:
            if col == self.C.group_code:
                f = QtGui.QFont()
                f.setBold(True)
                return f

        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight if col == 0 else Qt.AlignLeft

        if False and role == Qt.BackgroundColorRole:
            #print self.ogtGroup.data_cell(index.row(), index.column())
            cell = self.ogtDoc.group_by_index(row)[col]
            #bg = cell.get_bg()
            if len(self.ogtGroup.data_cell(row, col).errors) > 0:
                print bg, self.ogtGroup.data_cell(row, col).errors
            return QtGui.QColor(bg)


        return QtCore.QVariant()


    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return QtCore.QVariant(self._col_labels[idx])

        if role == Qt.TextAlignmentRole and orient == Qt.Horizontal:
            return Qt.AlignRight if idx == 0 else Qt.AlignLeft

        return QtCore.QVariant()


class C_ERR:
    """Columns for examples"""
    err = 0
    lidx = 1
    cidx = 2
    rule = 3
    highlight = 4
    descr = 5
    search = 6

class OGTErrorsWidget( QtGui.QWidget ):

    sigGotoSource = pyqtSignal(int, int)
    sigErrorsFilter = pyqtSignal(bool, bool)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.toolBar = QtGui.QToolBar()
        self.mainLayout.addWidget(self.toolBar)

        self.buttGroupFilters = QtGui.QButtonGroup(self)
        self.buttGroupFilters.setExclusive(False)

        self.buttWarnings = xwidgets.XToolButton(text="Show Warnings", checkable=True, checked=True)
        self.buttGroupFilters.addButton(self.buttWarnings)

        self.buttErrors = xwidgets.XToolButton(text="Show Errors", checkable=True, checked=True)
        self.buttGroupFilters.addButton(self.buttErrors)

        self.buttGroupFilters.buttonClicked.connect(self.on_update_filter)

        self.toolBar.addWidget(self.buttWarnings)
        self.toolBar.addWidget(self.buttErrors)

        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree, 30)

        self.model = ErrorsListModel()
        self.tree.setModel(self.model)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        #self.tree.setSortingEnabled(True)

        """
        hi = self.tree.headerItem()
        hi.setText(C_ERR.err, "Type")
        hi.setText(C_ERR.lidx, "Line")
        hi.setText(C_ERR.cidx, "Col")
        hi.setText(C_ERR.rule, "Rule")
        hi.setText(C_ERR.highlight, "Rule")
        hi.setText(C_ERR.descr, "Description")
        hi.setText(C_ERR.search, "search")
        """

        self.tree.setColumnHidden(C_ERR.err, True)
        self.tree.setColumnHidden(C_ERR.search, True)
        self.tree.setColumnWidth(C_ERR.lidx, 30)
        self.tree.setColumnWidth(C_ERR.cidx, 30)
        self.tree.setColumnWidth(C_ERR.rule, 50)
        self.tree.setColumnWidth(C_ERR.highlight, 8)

        #self.tree.itemClicked.connect(self.on_tree_item_clicked)

    def clear(self):
        print "clear", self #self.tree.clear()

    def load_document(self, ogtDoc):

        self.model.load_document(ogtDoc)
        return

        errrs = ogtDoc.get_errors_list()
        if len(errrs) == 0:
            item = xwidgets.XTreeWidgetItem()
            item.set(C_ERR.descr, "Yipee! no errors :-)", bg="#D5FF71")
            item.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(item)
            return

        for er in errrs:

            item = xwidgets.XTreeWidgetItem()
            item.set(C_ERR.err, "1" if er.type else "0")
            item.set(C_ERR.descr, er.message, bg=er.bg )
            item.set(C_ERR.lidx, er.line_no, align=Qt.AlignCenter)
            item.set(C_ERR.cidx, er.column_no, align=Qt.AlignCenter)
            item.set(C_ERR.rule, "-" if er.rule == None else er.rule, align=Qt.AlignCenter)
            item.set(C_ERR.search, "%s-%s" % (er.lidx, er.cidx) )
            self.tree.addTopLevelItem(item)

        self.on_show_warnings(sig=False)
        self.on_show_errors(sig=False)


    def on_tree_item_clicked(self, item, col):
        lidx = item.i(C_ERR.lidx) - 1
        cidx = item.i(C_ERR.cidx) - 1
        if lidx == None and cidx == None:
            return
        self.sigGotoSource.emit(lidx, cidx)


    def select_items(self, ridx, cidx):
        #print "select_items", ridx, cidx
        self.tree.blockSignals(True)

        # clear selection and  hightlight colors
        self.tree.clearSelection()
        root = self.tree.invisibleRootItem()
        for i in range(0, root.childCount()):
            root.child(i).set_bg(C_ERR.highlight, "white")

        if ridx != None and cidx != None:
            # search and hightlight row/col if any
            search = "%s-%s" % (ridx, cidx)
            items = self.tree.findItems(search, Qt.MatchExactly, C_ERR.search)
            if len(items) > 0:
                for item in items:
                    item.set_bg(C_ERR.highlight, "purple")
        self.tree.blockSignals(False)

    def on_update_filter(self):
        self.on_show_warnings()
        self.on_show_errors()
        self.emit_filters_sig()

    def on_show_warnings(self, sig=True):
        hidden = self.buttWarnings.isChecked() == False
        root = self.tree.invisibleRootItem()
        self.tree.setUpdatesEnabled(False)
        for ridx in range(0, root.childCount()):
            if str(root.child(ridx).text(C_ERR.err)) == "0":
                root.child(ridx).setHidden(hidden)
        self.tree.setUpdatesEnabled(True)
        if sig:
            self.emit_filters_sig()

    def on_show_errors(self, sig=True):
        hidden = self.buttErrors.isChecked() == False
        root = self.tree.invisibleRootItem()
        self.tree.setUpdatesEnabled(False)
        for ridx in range(0, root.childCount()):
            if str(root.child(ridx).text(C_ERR.err)) == "1":
                root.child(ridx).setHidden(hidden)
        self.tree.setUpdatesEnabled(True)
        if sig:
            self.emit_filters_sig()

    def emit_filters_sig(self):
        self.sigErrorsFilter.emit(self.buttWarnings.isChecked(), self.buttErrors.isChecked())

    def get_error_filters(self):
        return self.buttWarnings.isChecked(), self.buttErrors.isChecked()


