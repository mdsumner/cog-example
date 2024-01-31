from osgeo import gdal
import xml.etree.ElementTree as ET
from osgeo import ogr
from osgeo import osr


def create_poly(extent):
  # Create a Polygon from the extent list
  ring = ogr.Geometry(ogr.wkbLinearRing)
  ring.AddPoint_2D(extent[0],extent[2])
  ring.AddPoint_2D(extent[1], extent[2])
  ring.AddPoint_2D(extent[1], extent[3])
  ring.AddPoint_2D(extent[0], extent[3])
  ring.AddPoint_2D(extent[0],extent[2])
  poly = ogr.Geometry(ogr.wkbPolygon)
  poly.AddGeometry(ring)
  return poly

gdal.UseExceptions()
#!wget https://opentopography.s3.sdsc.edu/raster/COP90/COP90_hh.vrt
url = "https://opentopography.s3.sdsc.edu/raster/COP90/COP90_hh.vrt"
vrt = gdal.Open(f"/vsicurl/{url}")
gt = vrt.GetGeoTransform()
tree = ET.parse("COP90_hh.vrt")
root = tree.getroot()
locations = []
xmin = [0.0 for x in range(0, len(vrt.GetFileList()) - 1)]
xmax = [0.0 for x in range(0, len(vrt.GetFileList()) - 1)]
ymin = [0.0 for x in range(0, len(vrt.GetFileList()) - 1)]
ymax = [0.0 for x in range(0, len(vrt.GetFileList()) - 1)]

i = 0

for child in root: 
  if child.tag == "VRTRasterBand": 
    for element in child: 
      if element.tag == "SimpleSource":
        for source in element: 
          if source.tag == "DstRect": 
            xOff = float(source.get("xOff"))
            yOff = float(source.get("yOff"))
            xSize = float(source.get("xSize"))
            ySize = float(source.get("ySize"))
            xmin[i] = gt[0] + xOff * gt[1]
            xmax[i] = gt[0] + gt[1] * (xSize + xOff)
            ymax[i] = gt[3] + yOff * gt[5]
            ymin[i] = gt[3] + gt[5] * (ySize + yOff)
            i = i + 1
          if source.tag == "SourceFilename": 
            locations.append(source.text)
            
layer_name = "cop90"
fgb_path = f"{layer_name}.gti.fgb"

sr = osr.SpatialReference()
sr.SetFromUserInput("OGC:CRS84")

ds = ogr.GetDriverByName("GPKG").CreateDataSource(fgb_path)
layer = ds.CreateLayer(layer_name, geom_type=ogr.wkbPolygon, srs=sr)
layer.SetMetadataItem("XRES", "0.000833333333333")
layer.SetMetadataItem("YRES", "0.000833333333333")
layer.SetMetadataItem("DATA_TYPE", "Float32")
layer.SetMetadataItem("COLOR_INTERPRETATION", "undefined")
layer.SetMetadataItem("MINX", "-180.0")
layer.SetMetadataItem("MAXX", "180.0")
layer.SetMetadataItem("MINY", "-90.0")
layer.SetMetadataItem("MAXY", "90.0")
layer.SetMetadataItem("BAND_COUNT", "1")
layer.SetMetadataItem("SRS", "OGC:CRS84")
layer.SetMetadataItem("BLOCKXSIZE", "2048")
layer.SetMetadataItem("BLOCKYSIZE", "2048")






# Add an ID field
idField = ogr.FieldDefn("id", ogr.OFTInteger)
layer.CreateField(idField)
locField = ogr.FieldDefn("location", ogr.OFTString)
layer.CreateField(locField)

# Create the feature and set values
featureDefn = layer.GetLayerDefn()

for i in range(0, len(xmin)) : 
 extent = [xmin[i], xmax[i], ymin[i], ymax[i]]
 feature = ogr.Feature(featureDefn)
 geom = create_poly(extent)
 feature.SetGeometry(geom)
 feature.SetField("id", i)
 feature.SetField("location", f'/vsicurl/https://opentopography.s3.sdsc.edu/raster/COP90/{locations[i]}')
 layer.CreateFeature(feature)
 feature = None
 geom = None

layer = None
ds = None
  
    
    
