im <- vapour::gdal_raster_dsn(dsn::wms_bluemarble_s3_tms(), target_dim = c(4096, 4096),
                              out_dsn = "cog/blue_marble.tif")
