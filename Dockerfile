FROM python:latest 

COPY requirements.txt ./
RUN pip install -r requirements.txt 
RUN pip install psycopg2

COPY api api 
COPY migrations migrations
COPY config.py run.py alembic.ini boot.sh ./

EXPOSE 8000 

CMD ./boot.sh