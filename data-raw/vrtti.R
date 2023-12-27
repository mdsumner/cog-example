library(vapour)
bm <- gdal_raster_dsn(sds::wms_bluemarble_s3_tms(), target_ext = c(-180, 180, -90, 90), target_crs = "OGC:CRS84", target_res = 2, out_dsn = "vrtti/bm_longlat.tif")

img0 <- "WMTS:https://services.ga.gov.au/gis/rest/services/Topographic_Base_Map/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"
img <- vapour::vapour_sds_names(img0)[1L]

ga <- gdal_raster_dsn(img, target_crs = "EPSG:9473", target_dim = c(256, 0), out_dsn = "vrtti/ga_albers.tif")


system("gdaltindex vrtti/global_first.vrt.gpkg vrtti/bm_longlat.tif vrtti/ga_albers.tif -t_srs OGC:CRS84 -write_absolute_path")
system("gdaltindex vrtti/global_last.vrt.gpkg  vrtti/ga_albers.tif vrtti/bm_longlat.tif -t_srs OGC:CRS84 -write_absolute_path")


gdal_raster_dsn(sprintf("vrt://%s?ovr=8&outsize=30,15", sds::gebco()), out_dsn = "vrtti/gebco_tiny.tif")

system(sprintf("gdaltindex vrtti/dem_global_first.vrt.gpkg vrtti/gebco_tiny.tif %s -t_srs OGC:CRS84 -tr 1 1 -write_absolute_path", sds::ibcso()))
system(sprintf("gdaltindex vrtti/dem_global_last.vrt.gpkg  %s vrtti/gebco_tiny.tif -t_srs OGC:CRS84 -tr 1 1 -write_absolute_path", sds::ibcso()))


library(ximage)
ximage(gdal_raster_data("vrtti/dem_global_first.vrt.gpkg"))
ximage(gdal_raster_data("vrtti/dem_global_last.vrt.gpkg"))


system("gdaltindex vrtti/global_ibcso.vrt.gpkg vrtti/bm_longlat.tif /vsicurl/https://github.com/mdsumner/ibcso-cog/raw/main/IBCSO_v2_digital_chart.tif -t_srs OGC:CRS84 -tr .05 .05 -write_absolute_path")

