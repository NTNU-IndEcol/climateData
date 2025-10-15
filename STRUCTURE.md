climate-data-app/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
├── README.md
├── app/
│    ├── __init__.py
│    ├── processing.py
│    ├── routes.py
|    ├── static/
│    |    ├── css/
│    |    │   └── style.css
│    |    └── js/
│    |       └── main.js
|    ├── templates/
│    └── index.html
├── data/ (will be mounted as volume)
└── download/ (will be mounted as volume)
