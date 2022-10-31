# Blog API
Lightweight blogging API written in Python and FastAPI.

## Resources:
- Users
- Posts
- Tokens
- Follows

## Deploy methods:
### Local deployment:
1. Install requirements.txt:
```
pip install -r requirements.txt
```
2. Fill in .env file with .env.example file
3. Apply database migrations:
```
alembic upgrade head
```
4. Run local server:
```
uvicorn run:app --reload
```

### Docker-compose deployment:
- Run command:
```
docker-compose up -d
```