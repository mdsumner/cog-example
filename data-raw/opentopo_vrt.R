library(vaster)
library(sds)
library(terra)

vrtti_from_vrt <- function(x, outname, crs = NULL) {
  ex <- vaster::extent_vrt(gsub("/vsicurl/", "", x))

  info <- vapour::vapour_raster_info(x)
  if (is.null(crs)) crs <- info$projection
  tiles <- tibble::tibble(geom = wk::rct(xmin = ex[, "xmin", drop = TRUE], ymin = ex[, "ymin", drop = TRUE],
                                         xmax = ex[, "xmax", drop = TRUE], ymax = ex[, "ymax", drop = TRUE], crs = crs),
                          location = info$filelist[-1L])
  ## create the dummy VRTTI at the command line
  system(sprintf("gdaltindex %s  %s ", outname, tiles$location[1L]))
  sf::st_write(sf::st_as_sf(tiles), outname, delete_layer = TRUE)
  outname
}

vrtti_from_vrt(cop90(), "vrtti/cop90.vrt.gpkg")
vrtti_from_vrt(cop30(), "vrtti/cop30.vrt.gpkg")



## now we have an index of the COP90 and a valid raster index in VRTTI format
plot(vect("cop90.vrt.gpkg"))
r <- crop(rast("cop90.vrt.gpkg"), ext(147, 147.5, -43.2, -42.6))
plot(r)
plot(vect("cop90.vrt.gpkg"), add = TRUE)


## don't use crop (or project without by_util) for larger extents
r <- project(rast("cop90.vrt.gpkg"), rast(ext(147, 147.5, -43.2, -42.6) + 2, res = 0.1), by_util = TRUE)
plot(r)
plot(vect("cop90.vrt.gpkg"), add = TRUE)
