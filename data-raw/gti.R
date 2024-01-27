create_gti_vect <- function(vrtfile, gtifilename = NULL, driver = "FlatGeoBuf") {
  if (is.null(gtifilename)) stop("gtifilename must be set, to create the vector file")
  e <- vaster::extent_vrt(gsub("/vsicurl/", "", vrtfile))
  info <-  vapour::vapour_raster_info(vrtfile)

  idx <- c(1, 3, 2, 3, 2, 4, 1, 4, 1, 3)
  ## too slow
  #v <- vect(lapply(split(t(e), rep(1:nrow(e), each = 4)), \(.x) vect(matrix(.x[idx], ncol = 2L, byrow = TRUE), type = "polygon")), crs = "OGC:CRS84")
  v <- terra::vect(sf::st_as_sf(wk::rct(e[,1], e[,3], e[, 2], e[,4])))
  v <- terra::set.crs(v, "OGC:CRS84")
  v$location <-info$filelist[-1]
  terra::writeVector(v, gtifilename, filetype = driver)
  v
}
usgstiles <- create_gti_vect(sds::usgs_seamless(), "gti/usgs_seamless.fgb")
cop30 <-     create_gti_vect(sds::cop30(), "gti/cop30.fgb")
#system("gdalinfo GTI:gti/usgs_seamless.fgb")



#
# library(vapour)
# bm <- gdal_raster_dsn(sds::wms_bluemarble_s3_tms(), target_ext = c(-180, 180, -90, 90), target_crs = "OGC:CRS84", target_res = 2, out_dsn = "vrtti/bm_longlat.tif")
#
# img0 <- "WMTS:https://services.ga.gov.au/gis/rest/services/Topographic_Base_Map/MapServer/WMTS/1.0.0/WMTSCapabilities.xml"
# img <- vapour::vapour_sds_names(img0)[1L]
#
# ga <- gdal_raster_dsn(img, target_crs = "EPSG:9473", target_dim = c(256, 0), out_dsn = "vrtti/ga_albers.tif")
#
#
# system("gdaltindex vrtti/global_first.vrt.gpkg vrtti/bm_longlat.tif vrtti/ga_albers.tif -t_srs OGC:CRS84 -write_absolute_path")
# system("gdaltindex vrtti/global_last.vrt.gpkg  vrtti/ga_albers.tif vrtti/bm_longlat.tif -t_srs OGC:CRS84 -write_absolute_path")
#
#
# gdal_raster_dsn(sprintf("vrt://%s?ovr=8&outsize=30,15", sds::gebco()), out_dsn = "vrtti/gebco_tiny.tif")
#
# system(sprintf("gdaltindex vrtti/dem_global_first.vrt.gpkg vrtti/gebco_tiny.tif %s -t_srs OGC:CRS84 -tr 1 1 -write_absolute_path", sds::ibcso()))
# system(sprintf("gdaltindex vrtti/dem_global_last.vrt.gpkg  %s vrtti/gebco_tiny.tif -t_srs OGC:CRS84 -tr 1 1 -write_absolute_path", sds::ibcso()))
#
#
# library(ximage)
# ximage(gdal_raster_data("vrtti/dem_global_first.vrt.gpkg"))
# ximage(gdal_raster_data("vrtti/dem_global_last.vrt.gpkg"))
#
#
# system("gdaltindex vrtti/global_ibcso.vrt.gpkg vrtti/bm_longlat.tif /vsicurl/https://github.com/mdsumner/ibcso-cog/raw/main/IBCSO_v2_digital_chart.tif -t_srs OGC:CRS84 -tr .05 .05 -write_absolute_path")

