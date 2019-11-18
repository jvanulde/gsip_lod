# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GsipLod
                                 A QGIS plugin
 GSIP linked open data browser
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-11
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Geological Survey of Canada - Laboratoire de cartographie numérique et de photogrammétrie
        email                : eric.boisvert2@canada.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgsMapToolIdentifyFeature
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .gsip_lod_dockwidget import GsipLodDockWidget
from .forms import DatasetForm,InformationForm
from .selfie import getMir,Selfie
import os.path
import tempfile
import urllib
import uuid


'''
code example to use
https://gis.stackexchange.com/a/260214

'''



class GsipLod:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GsipLod_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GSIP')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GsipLod')
        self.toolbar.setObjectName(u'GsipLod')

        #print "** INITIALIZING GsipLod"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GsipLod', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/gsip_lod/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GSIP'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING GsipLod"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False



    def ac_dataset(self):
        ''' dataset button is clicked'''
        self.dockwidget.lblAction.setText("Dataset")
        f = DatasetForm()
        f.exec_()
        if f.result():
            self.downloadSpatialResource("https://geoconnex.ca/gsip/resources/catchment/catchments", "application/vnd.geo+json")

    
    def ac_inspect(self):
        ''' identify button is clicked, set the tool'''
        self.dockwidget.lblAction.setText("Select a linked feature")
        mc=self.iface.mapCanvas()
        lyr=self.iface.activeLayer()
        if lyr is not None:
            self.mapTool = QgsMapToolIdentifyFeature(mc,lyr)
            mc.setMapTool(self.mapTool)
            self.mapTool.featureIdentified.connect(self.ac_identified)
        

    
    def ac_identified(self,feature):
        nir =feature.attribute("uri")
        self.dockwidget.lblAction.setText("")
        if nir is not None:
            s = getMir(nir)
            f = InformationForm(s)
            f.exec_()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD GsipLod"

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&GSIP'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING GsipLod"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GsipLodDockWidget()
                self.bindButtons(self.dockwidget)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
    def bindButtons(self,widget):
        ''' link the buttons on the widget to actions in this class'''
        widget.btnDataset.clicked.connect(self.ac_dataset)
        widget.btnInspect.clicked.connect(self.ac_inspect)
        
    def downloadSpatialResource(self,location,mime_type):
        ''' download a spatial resource from the web and upload it on the map
        location is the URL, ext is the format (extension)
        TODO: For this demo, we assume spatia=geojson, so we just generate a 
        temp name (a guid) an save it in /temp
        '''
        #name = location.rsplit('/', 1)[-1]
        #filename = "f" + str(uuid.uuid1()) + ".geojson"
        #path = tempfile.gettempdir() + "/" + filename
        path = "/home/eric/geo/d.geojson"
        opener = urllib.request.build_opener()
        opener.addheaders = [('Accept', mime_type)]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(location, path)
        # load this file in QGIS
        self.iface.addVectorLayer(path, "catchment", "ogr")
