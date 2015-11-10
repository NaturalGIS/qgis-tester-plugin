import qgis.utils
from qgistester.test import Test
import geoserverexplorer
from geoserverexplorer.geoserver.retry import RetryCatalog
from geoserverexplorer.test.catalogtests import suite as catalogSuite
from geoserverexplorer.gui.gsexploreritems import *
from geoserverexplorer.qgis.catalog import CatalogWrapper
import os
from qgistester.utils import layerFromName



#Tests assume a standard Geoserver at localhost:8080 and default admin/geoserver credentials

#Some common methods

def _loadTestData():
    projectFile = os.path.join(os.path.dirname(os.path.abspath(geoserverexplorer.__file__)), "test", "data", "test.qgs")
    if projectFile != QgsProject.instance().fileName():
        qgis.utils.iface.addProject(projectFile)

def _loadSymbologyTestData():
    projectFile = os.path.join(os.path.dirname(os.path.abspath(geoserverexplorer.__file__)), "test", "data", "symbology", "test.qgs")
    if projectFile != QgsProject.instance().fileName():
        qgis.utils.iface.addProject(projectFile)

def _getCatalog():
    return RetryCatalog("http://localhost:8080/geoserver/rest", "admin", "geoserver")

def _setUpCatalogAndWorkspace():
    cat = _getCatalog()
    try:
        _clean()
    except:
        raise
    cat.create_workspace("test_workspace", "http://test.com")
    return cat

def _setUpCatalogAndExplorer():
    explorer = qgis.utils.plugins["geoserverexplorer"].explorer
    explorer.show()
    gsItem = explorer.explorerTree.gsItem
    cat = _setUpCatalogAndWorkspace()
    geoserverItem = GsCatalogItem(cat, "test_catalog")
    gsItem.addChild(geoserverItem)
    geoserverItem.populate()
    gsItem.setExpanded(True)


#TESTS

def _checkNewLayer():
    cat = _getCatalog()
    stores = cat.get_stores("test_workspace")
    assert len(stores) != 0

def _clean():
    cat = _getCatalog()
    ws = cat.get_workspace("test_workspace")
    if ws:
        cat.delete(ws, recurse = True)

dragdropTest = Test("Verify dragging browser element into workspace")
dragdropTest.addStep("Setting up catalog and explorer", _setUpCatalogAndExplorer)
dragdropTest.addStep("Drag layer from browser into testing workspace of testing catalog")
dragdropTest.addStep("Checking new layer", _checkNewLayer)
dragdropTest.setCleanup(_clean)

def _openAndUpload():
    _loadTestData()
    layer = layerFromName("qgis_plugin_test_pt1")
    cat = _setUpCatalogAndWorkspace()
    catWrapper = CatalogWrapper(cat)
    catWrapper.publishLayer(layer, "test_workspace", True)
    url = 'url=http://localhost:8080/geoserver/wms&format=image/png&layers=test_workspace:qgis_plugin_test_pt1&styles=qgis_plugin_test_pt1&crs=EPSG:4326'
    wmsLayer = QgsRasterLayer(url, "WMS", 'wms')
    QgsMapLayerRegistry.instance().addMapLayer(wmsLayer)


vectorRenderingTest = Test("Verify rendering of uploaded style")
vectorRenderingTest.addStep("Preparing data", _openAndUpload)
vectorRenderingTest.addStep("Check that WMS layer is correctly rendered")
vectorRenderingTest.setCleanup(_clean)

def functionalTests():
    return [dragdropTest, vectorRenderingTest]

def unitTests():
    return catalogSuite()