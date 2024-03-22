from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from fastapi_helloworld import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends
from fastapi import HTTPException



class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "My Beautiful Test World"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

# Update (PUT /todos/{todo_id}/)
@app.put("/todos/{todo_id}/", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    db_todo = session.get(Todo, todo_id)
    if db_todo:
        db_todo.content = todo.content
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


# Delete (DELETE /todos/{todo_id}/)
@app.delete("/todos/{todo_id}/", response_model=Todo)
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    db_todo = session.get(Todo, todo_id)
    if db_todo:
        session.delete(db_todo)
        session.commit()
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
