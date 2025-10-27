import os
import geopandas as gpd # type: ignore
import xarray as xr
#import rasterio
#from rasterio.features import geometry_mask
import numpy as np
import pandas as pd
import regionmask # type: ignore
import zipfile
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_data(country_name: str, variable: str, method: str, subregions: bool = False) -> str:
    """Extract and mask data based on country name and variable."""
    try:
        # Normalize the country name to be case-insensitive
        country_name = country_name.lower()
        logger.info(f"Processing data for {country_name}, variable: {variable}, method: {method}, subregions: {subregions}")

        # Get absolute path to data directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data')
        download_dir = os.path.join(project_root, 'download')

        # Load the world shapefile
        shapefile_path = os.path.join(data_dir, "world_power_region.geojson")
        gdf = gpd.read_file(shapefile_path, engine="pyogrio")

        # Find the country polygon by case-insensitive match
        country_gdf = gdf[gdf["countryName"].str.lower() == country_name]

        if country_gdf.empty:
            raise ValueError(f"Country '{country_name}' not found in the shapefile.")

        # Load the appropriate NetCDF dataset based on the variable
        dataset_path = os.path.join(data_dir, f"{variable}_{method}.nc")

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
        # Open dataset with proper error handling
        ds = xr.open_dataset(dataset_path)
        logger.info(f"Loaded dataset with dimensions: {dict(ds.dims)}")

        if subregions:
            return _process_subregions(country_name, variable, method, country_gdf, ds, download_dir)
        else:
            return _process_whole_country(country_name, variable, method, country_gdf, ds, download_dir)

    except Exception as e:
        logger.error(f"Error in extract_data: {str(e)}")
        raise

def _process_subregions(country_name: str, variable: str, method: str, country_gdf: gpd.GeoDataFrame, ds: xr.Dataset, download_dir: str) -> str:
    """Process data for subregions."""
    output_files = []
    
    for zone in country_gdf['zoneName'].unique():
        try:
            # Extract sub-region geometry
            subregion_gdf = country_gdf[country_gdf['zoneName'] == zone]
            if len(subregion_gdf) == 0:
                logger.warning(f"No geometry found for zone: {zone}")
                continue
                
            subregion_shape = subregion_gdf.geometry.values[0]
            subregion_mask = regionmask.Regions([subregion_shape])

            # Apply mask to the data
            mask_region = subregion_mask.mask(ds)
            data_in_subregion = ds[variable].where(mask_region == 0)

            # Check if the data contains valid values
            if data_in_subregion.isnull().all():
                logger.warning(f"Data for subregion '{zone}' contains only NaN values. Skipping...")
                continue

            # Process the data
            df = _create_dataframe(data_in_subregion, variable, country_name, zone)
            
            # Save results to CSV
            output_directory = os.path.join(download_dir, country_name)
            os.makedirs(output_directory, exist_ok=True)
            output_file = f"{country_name}_{zone}_{variable}_{method}.csv"
            output_path = os.path.join(output_directory, output_file)

            df.to_csv(output_path)
            output_files.append(output_path)
            logger.info(f"Saved sub-region data to {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing subregion {zone}: {str(e)}")
            continue

    if not output_files:
        raise ValueError("No valid subregions were processed successfully.")

    # Create zip file
    zip_file_path = os.path.join(download_dir, f"{country_name}_{variable}_{method}.zip")
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)

    logger.info(f"Zipped all files into {zip_file_path}")
    
    return zip_file_path

def _process_whole_country(country_name: str, variable: str, method: str, country_gdf: gpd.GeoDataFrame, ds: xr.Dataset, download_dir: str) -> str:
    """Process data for whole country."""
    # Apply the mask to the dataset
    country_shape = country_gdf.geometry.values[0]
    country_mask = regionmask.Regions([country_shape])

    # Apply mask to the data
    mask_region = country_mask.mask(ds)
    data_in_country = ds[variable].where(mask_region == 0)

    # Check if the masked data contains valid values
    if data_in_country.isnull().all():
        raise ValueError("Masked data contains only NaN values. Check the geometry and dataset alignment.")

    # Process the data
    df = _create_dataframe(data_in_country, variable, country_name)

    # Save results to CSV
    output_directory = download_dir
    os.makedirs(output_directory, exist_ok=True)
    output_file = f"{country_name}_{variable}_{method}.csv"
    output_path = os.path.join(output_directory, output_file)

    df.to_csv(output_path)
    logger.info(f"Saved country data to {output_path}")

    return output_path

def _create_dataframe(data: xr.DataArray, variable: str, country_name: str, zone: Optional[str] = None) -> pd.DataFrame:
    """Create DataFrame with daily mean and percentiles."""
    # Calculate the regional mean
    daily_mean_data = data.mean(dim=["lat", "lon"], skipna=True)

    # Calculate percentiles
    percentiles = daily_mean_data.quantile([0.01, 0.02, 0.03, 0.04, 0.05, 0.95, 0.96, 0.97, 0.98, 0.99], dim='time')
    
    # Create dictionary for DataFrame
    if zone:
        df_dict = {f'{country_name}_{zone}_{variable}': daily_mean_data.values}
    else:
        df_dict = {f'{country_name}_{variable}': daily_mean_data.values}

    # Add percentiles and masks
    percentile_list = [0.01, 0.02, 0.03, 0.04, 0.05, 0.95, 0.96, 0.97, 0.98, 0.99]

    for pct in percentile_list:
        percentile_values = percentiles.sel(quantile=pct)
        mask = np.where(
            (daily_mean_data < percentile_values) if pct < 0.5 else (daily_mean_data > percentile_values), 
            1, 0
        )

        # Add percentile values and masks to the dictionary
        df_dict[f'{int(pct * 100)}th_percentile'] = percentile_values.values
        df_dict[f'{int(pct * 100)}th_percentile_mask'] = mask

    # Create DataFrame
    df = pd.DataFrame(df_dict, index=daily_mean_data['time'].values)
    df.index.name = 'Time'
    
    return df