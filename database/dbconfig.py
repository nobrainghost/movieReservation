import os

class Config:
    DATABASE_URL=os.environ.get('DATABASE_URL') or 'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'