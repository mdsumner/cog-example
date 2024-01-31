from osgeo import gdal
import xml.etree.ElementTree as ET
from osgeo import ogr
from osgeo import osr

from urllib.request import urlopen

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

urldirname = "https://opentopography.s3.sdsc.edu/raster/COP90"
basename = "COP90_hh.vrt"
url = f"{urldirname}/{basename}"
layer_name = "cop90"
drivername = "FlatGeobuf"
fgb_path = f"{layer_name}.gti.fgb"

vrt = gdal.Open(f"/vsicurl/{url}")
gt = vrt.GetGeoTransform()
resxy = [gt[1], -gt[5]]
exxy = [gt[0], gt[0] + vrt.RasterXSize * resxy[0], 
        gt[3] + vrt.RasterYSize * -resxy[1], gt[3]]
con = urlopen(url) 
tree = ET.parse(con)

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
            

sr = osr.SpatialReference()
sr.SetFromUserInput("EPSG:4326")


ds = ogr.GetDriverByName(drivername).CreateDataSource(fgb_path)
layer = ds.CreateLayer(layer_name, geom_type=ogr.wkbPolygon, srs=sr)
layer.SetMetadataItem("RESX", str(resxy[0]))
layer.SetMetadataItem("RESY", str(resxy[1]))
layer.SetMetadataItem("DATA_TYPE", "Float32")
layer.SetMetadataItem("COLOR_INTERPRETATION", "undefined")
layer.SetMetadataItem("MINX", str(exxy[0]))
layer.SetMetadataItem("MAXX", str(exxy[1]))
layer.SetMetadataItem("MINY", str(exxy[2]))
layer.SetMetadataItem("MAXY", str(exxy[3]))
layer.SetMetadataItem("BAND_COUNT", "1")
layer.SetMetadataItem("SRS", "EPSG:4326")
#layer.SetMetadataItem("BLOCKXSIZE", "2048")
#layer.SetMetadataItem("BLOCKYSIZE", "2048")

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
 feature.SetField("location", f'/vsicurl/{urldirname}/{locations[i]}')
 layer.CreateFeature(feature)
 feature = None
 geom = None

layer = None
ds = None
  
    
    
