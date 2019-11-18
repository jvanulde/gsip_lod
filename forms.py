import os
import webbrowser
import rdflib

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtCore import pyqtSignal, Qt

FORM_CLASS_DS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dataset_form.ui'))

FORM_CLASS_INF, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'information.ui'))

SPARQL_LIST = """
PREFIX dct: <http://purl.org/dc/terms/> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
SELECT ?l ?u ?f WHERE {?u rdfs:label ?l;dct:format ?f}
"""

class DatasetForm(QtWidgets.QDialog, FORM_CLASS_DS):

    closingPlugin = pyqtSignal()

    def __init__(self, g, parent=None):
        """Constructor."""
        super(DatasetForm, self).__init__(parent)
        self.setupUi(self)
        # load the form
        self.listWidget.clear()
        # execute sparql and add tuples as data
        for row in g.query(SPARQL_LIST):
            li = QListWidgetItem(str(row['l']))
            li.setData(Qt.UserRole,row)
            self.listWidget.addItem(li)

    def getSelectedResource(self):
        ci = self.listWidget.currentItem()
        if ci is not None:
            d = ci.data(Qt.UserRole)
            return d['u'],d['f']
        else:
            return None,None



    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
        
class InformationForm(QtWidgets.QDialog,FORM_CLASS_INF):
    closingPlugin = pyqtSignal()

    def __init__(self,selfie, parent=None):
        """Constructor."""
        super(InformationForm, self).__init__(parent)
        self.selfie = selfie
        self.setupUi(self)
        self._setup()
        
    def _setup(self):
        self.btnNir.clicked.connect(self.clickNir)
        self.btnNir.setText(self.selfie.context_resource)
        self.lvRepresentations.setModel(self.selfie.representationModel())
        self.tvLinks.setModel(self.selfie.linkModel())
        
    def clickNir(self):
        if self.selfie.context_resource is not None:
            webbrowser.open(self.selfie.context_resource, new = 2)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()