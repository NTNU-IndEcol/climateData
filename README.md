# Climate Data Extraction Tool

A Dockerized web application for extracting climate data from NetCDF files based on country boundaries.

## Features

- Extract climate data for European countries
- Support for multiple variables (t2m, ws10, ro, tcc, ssrd)
- Multiple aggregation methods (daymean, daymax, daymin, daysum)
- Whole country or power sub-region extraction
- Percentile calculations and masking
- CSV export with zip compression for sub-regions

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone this repository:
```bash
git clone <your-repository-url>
cd climate-data-app
```
2. Set up data files (see DATA_SETUP.md):
```bash
mkdir -p data
mkdir -p download
```
upload the dat files to the data/ directory. 

3. Run with Docker
```bash
docker-compose up --build
```
