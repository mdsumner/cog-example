## remotes::install_github("hypertidy/vaster")
e <- vaster::extent_vrt(gsub("/vsicurl/", "", sds::cop30()))

info <-  vapour::vapour_raster_info(sds::cop30())
length(info$filelist)
idx <- c(1, 3, 2, 3, 2, 4, 1, 4, 1, 3)
library(terra)
## too slow
#v <- vect(lapply(split(t(e), rep(1:nrow(e), each = 4)), \(.x) vect(matrix(.x[idx], ncol = 2L, byrow = TRUE), type = "polygon")), crs = "OGC:CRS84")
v <- vect(sf::st_as_sf(wk::rct(e[,1], e[,3], e[, 2], e[,4])))
v <- set.crs(v, "OGC:CRS84")
v$location <-info$filelist[-1]
writeVector(v, "cop30.fgb", filetype = "FlatGeoBuf")

system("gdalinfo GTI:cop30.fgb")
