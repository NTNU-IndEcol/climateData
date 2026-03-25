# Data Setup Instructions

## Required Data Files

Place the following files in the `data/` directory:

### 1. Shapefile
- **File**: `world_power_region.geojson`
- **Description**: Geographic boundaries for countries and subregions
- **Required columns**: `countryName`, `zoneName`, `geometry`

### 2. NetCDF Climate Data Files

Format: `data/{variable}/{variable}_{year}_{method}.nc`

**Available Variables:**
- `t2m` - 2-meter air temperature
- `ws10` - 10-meter wind speed  
- `ws100` - 100-meter wind speed
- `ro` - Surface runoff
- `tcc` - Total cloud cover
- `ssrd` - Surface solar radiation

**Available Methods:**
- `daymean` - Daily mean
- `daymax` - Daily maximum
- `daymin` - Daily minimum  
- `daysum` - Daily accumulation

For daily mean files, both `{variable}_{year}_daymean.nc` and `{variable}_{year}_dailymean.nc` are accepted.

**Example directory layout:**

```text
data/
  world_power_region.geojson
  tcc/
    tcc_1994_dailymean.nc
    tcc_1994_daymax.nc
    tcc_1994_daymin.nc
    tcc_2000_dailymean.nc
    tcc_2000_daymax.nc
    tcc_2000_daymin.nc
  t2m/
    t2m_1994_daymean.nc
    t2m_1995_daymean.nc
    ...
```

The app automatically loads all files in the selected variable folder that match the requested aggregation method, sorts them by year, and concatenates them into one time series before extraction.
