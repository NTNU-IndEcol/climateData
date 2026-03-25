climateData-app/
├── Dockerfile              
├── docker-compose.yml      
├── data/
│   ├── world_power_region.geojson
│   ├── tcc/
│   │   ├── tcc_1994_dailymean.nc
│   │   ├── tcc_1994_daymax.nc
│   │   └── ...
│   ├── t2m/
│   │   ├── t2m_1994_daymean.nc
│   │   └── ...
│   └── ...
├── download/
├── app/
│   ├── backend/
│   │   ├── processing.py
│   │   ├── routes.py
│   │   └── ...
│   └── frontend/
│       └── ...
├── .dockerignore
├── README.md
├── DATA_SETUP.md
└── .gitignore
