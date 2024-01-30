## remotes::install_github(c("hypertidy/vaster", "hypertidy/sds"))
## sds has a bunch of DSN in functions, vaster has raster/cell logic, and this VRT parser to get the extent of every source
e <- vaster::extent_vrt(gsub("/vsicurl/", "", sds::cop30()))

## gdalinfo
info <-  vapour::vapour_raster_info(sds::cop30())

## polygon index from xmin,xmax,ymin,ymax (1-based in R)
idx <- c(1, 3, 2, 3, 2, 4, 1, 4, 1, 3)
library(terra)
## too slow
#v <- vect(lapply(split(t(e), rep(1:nrow(e), each = 4)), \(.x) vect(matrix(.x[idx], ncol = 2L, byrow = TRUE), type = "polygon")), crs = "OGC:CRS84")
## create efficient rct, then convert SF and use terra
v <- vect(sf::st_as_sf(wk::rct(e[,1], e[,3], e[, 2], e[,4])))
v <- set.crs(v, "OGC:CRS84")

## put on the GTI field "location" (DSN of each TIF)
v$location <-info$filelist[-1]

writeVector(v, "cop30.fgb", filetype = "FlatGeoBuf")
system("gdalinfo GTI:cop30.fgb")
