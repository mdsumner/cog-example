library(vaster)
library(sds)
library(terra)

vrtti_from_vrt <- function(x, outname, crs = NULL) {
  ex <- vaster::extent_vrt(gsub("/vsicurl/", "", x))

  info <- vapour::vapour_raster_info(x)
  res <- format(c(vaster::x_res(info$dimension, info$extent), vaster::y_res(info$dimension, info$extent)), digits = 12)
  if (is.null(crs)) crs <- info$projection
  tiles <- tibble::tibble(geom = wk::rct(xmin = ex[, "xmin", drop = TRUE], ymin = ex[, "ymin", drop = TRUE],
                                         xmax = ex[, "xmax", drop = TRUE], ymax = ex[, "ymax", drop = TRUE], crs = crs),
                          location = info$filelist[-1L])
  ## create the dummy VRTTI at the command line
  cmd <- sprintf("gdaltindex %s  %s -tr %s %s -ot %s -te %s ", outname, tiles$location[1L], res[1L], res[2L], info$datatype, paste0(info$extent[c(1, 3, 2, 4)], collapse = " "))
  print(cmd)
  system(cmd)
  system(sprintf("gdalinfo %s | grep Size", outname))
  sf::st_write(sf::st_as_sf(tiles), outname, delete_layer = TRUE, layer_options = c(sprintf("RESX=%s", res[1L]),
                                                                                    sprintf("RESY=%s", res[2L])))
  outname
}

vrtti_from_vrt(cop30(), "vrtti/cop30.vrt.gpkg")
vrtti_from_vrt(cop90(), "vrtti/cop90.vrt.gpkg")




