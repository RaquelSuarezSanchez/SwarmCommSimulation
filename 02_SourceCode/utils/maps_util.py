import numpy as np
import rasterio
from pyproj import Transformer
from pathlib import Path

# Coordinate transformers
GPS_TO_UTM = Transformer.from_crs("epsg:4326", "epsg:32628", always_xy=True)
UTM_TO_GPS = Transformer.from_crs("epsg:32628", "epsg:4326", always_xy=True)

def load_map(filename): 
    """Process elevation and coordinates"""
    path = Path(__file__).parent.parent / filename
    
    with rasterio.open(path) as src:
        Z = src.read(1) 
        
        # VISUAL - DEGREES
        # 201 puntos que vayan desde la longitud -13.74 (Oeste) hasta -13.70 (Este)
        lon = np.linspace(-13.74, -13.70, 201)  
        
        # 201 puntos desde la latitud 29.03 (Sur) hasta 29.05 (Norte)
        lat = np.linspace(29.03, 29.05, 201)
        lonGrid, latGrid = np.meshgrid(lon, lat)
        lon_flat = lonGrid.flatten()
        lat_flat = latGrid.flatten()
        
        col_flat, row_flat = ~src.transform * (lon_flat, lat_flat)
        col = np.floor(col_flat).astype(int).reshape(lonGrid.shape)
        row = np.floor(row_flat).astype(int).reshape(latGrid.shape)

    row = np.clip(row, 0, Z.shape[0] - 1)
    col = np.clip(col, 0, Z.shape[1] - 1)

    Z_interp = Z[row, col].astype(float)
    nodata_val = src.nodata if src.nodata is not None else -9999
    Z_interp[Z_interp == nodata_val] = np.nan 

    Zmin = np.nanmin(Z_interp) 
    Zmax = np.nanmax(Z_interp) 
    Z_interp[np.isnan(Z_interp)] = Zmin 
    
    xGrid, yGrid = GPS_TO_UTM.transform(lonGrid, latGrid)

    # FISICAL - METERS
    cx_grados, cy_grados = -13.72, 29.04
    cx_metros, cy_metros = GPS_TO_UTM.transform(cx_grados, cy_grados)
    
    return Z_interp, xGrid, yGrid, cx_metros, cy_metros