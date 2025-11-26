from fastapi import FastAPI
from db.database import engine, Base
from api import auth_controller, movie_controller, link_controller, rating_controller, tag_controller

Base.metadata.create_all(bind=engine)
app = FastAPI(title="MovieLens API")

# Include all routers
app.include_router(auth_controller.router)
app.include_router(movie_controller.router)
app.include_router(link_controller.router)
app.include_router(rating_controller.router)
app.include_router(tag_controller.router)


@app.get("/")
def hello() -> dict:
    return {"hello": "world"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)