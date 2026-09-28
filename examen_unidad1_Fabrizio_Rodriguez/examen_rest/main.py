import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from database import Base, engine, get_db
from models import Laptop

def esperar_y_cargar_datos():
    # Intenta conectarse a MySQL con reintentos
    max_retries = 15
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

    # Crea las tablas si no existen
    Base.metadata.create_all(bind=engine)

    # Carga inicial si la tabla está vacía
    db = next(get_db())
    try:
        if db.query(Laptop).count() == 0:
            laptops_iniciales = [
                Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
                Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
                Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True)
            ]
            db.add_all(laptops_iniciales)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ocurre al arrancar el contenedor
    esperar_y_cargar_datos()
    yield

app = FastAPI(title="API Laboratorio de Cómputo", lifespan=lifespan)

# Esquemas Pydantic
class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int

class LaptopResponse(BaseModel):
    id: int
    marca: str
    modelo: str
    ram_gb: int
    disponible: bool

    class Config:
        from_attributes = True

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"mensaje": "API del laboratorio de cómputo"}

@app.get("/laptops", response_model=list[LaptopResponse])
def get_laptops(db: Session = Depends(get_db)):
    return db.query(Laptop).order_by(Laptop.id.asc()).all()

@app.get("/laptops/disponibles", response_model=list[LaptopResponse])
def get_laptops_disponibles(db: Session = Depends(get_db)):
    return db.query(Laptop).filter(Laptop.disponible == True).order_by(Laptop.id.asc()).all()

@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def get_laptop_by_id(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if not laptop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop no encontrada"
        )
    return laptop

@app.post("/laptops", response_model=LaptopResponse, status_code=status.HTTP_201_CREATED)
def create_laptop(laptop: LaptopCreate, db: Session = Depends(get_db)):
    nueva_laptop = Laptop(
        marca=laptop.marca,
        modelo=laptop.modelo,
        ram_gb=laptop.ram_gb,
        disponible=True
    )
    db.add(nueva_laptop)
    db.commit()
    db.refresh(nueva_laptop)
    return nueva_laptop