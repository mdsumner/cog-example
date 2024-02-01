import xml.etree.ElementTree as ET
from urllib.request import urlopen

from osgeo import gdal, ogr, osr


def create_poly(extent):
    # Create a Polygon from the extent list
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint_2D(extent[0], extent[2])
    ring.AddPoint_2D(extent[1], extent[2])
    ring.AddPoint_2D(extent[1], extent[3])
    ring.AddPoint_2D(extent[0], extent[3])
    ring.AddPoint_2D(extent[0], extent[2])

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

file_extents = {}

# Get all the SimpleSource items from the XML tree
for item in tree.findall(".//SimpleSource"):
    # Get the DstRect item
    dstrect = item.find("DstRect")
    # Get the SourceFilename item
    srcfilename = item.find("SourceFilename")

    # Get the xOff, yOff, xSize, ySize from the DstRect item
    xOff = float(dstrect.get("xOff"))
    yOff = float(dstrect.get("yOff"))
    xSize = float(dstrect.get("xSize"))
    ySize = float(dstrect.get("ySize"))

    extent = [
        gt[0] + xOff * gt[1],
        gt[0] + gt[1] * (xSize + xOff),
        gt[3] + yOff * gt[5],
        gt[3] + gt[5] * (ySize + yOff)
    ]

    file_extents[srcfilename.text] = extent

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

# Add an ID field
idField = ogr.FieldDefn("id", ogr.OFTInteger)
layer.CreateField(idField)
locField = ogr.FieldDefn("location", ogr.OFTString)
layer.CreateField(locField)

# Create the feature and set values
featureDefn = layer.GetLayerDefn()

for n, (file, extent) in enumerate(file_extents.items()):
    feature = ogr.Feature(featureDefn)
    geom = create_poly(extent)
    feature.SetGeometry(geom)
    feature.SetField("id", n)
    feature.SetField("location", f'/vsicurl/{urldirname}/{file}')
    layer.CreateFeature(feature)
