# Data Setup Instructions

## Required Data Files

Place the following files in the `data/` directory:

### 1. Shapefile
- **File**: `world_power_region.geojson`
- **Description**: Geographic boundaries for countries and subregions
- **Required columns**: `countryName`, `zoneName`, `geometry`

### 2. NetCDF Climate Data Files

Format: `{variable}_{method}.nc`

**Available Variables:**
- `t2m` - 2-meter air temperature
- `ws10` - 10-meter wind speed  
- `ro` - Surface runoff
- `tcc` - Total cloud cover
- `ssrd` - Surface solar radiation

**Available Methods:**
- `daymean` - Daily mean
- `daymax` - Daily maximum
- `daymin` - Daily minimum  
- `daysum` - Daily accumulation

**Example files needed:**