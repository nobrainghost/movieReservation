import os

class Config:
    ##below credentials are local and therefore not a security risk
    DATABASE_URL=os.environ.get('DATABASE_URL') or 'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'