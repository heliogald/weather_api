from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, weather
from app.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API de Clima Ativa!"}

@app.post("/weather/", response_model=schemas.WeatherResponse)
def get_and_store_weather(data: schemas.WeatherBase, db: Session = Depends(get_db)):
    try:
        weather_data = weather.fetch_weather(data.city)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao buscar clima.")

    db_weather = models.Weather(
        city=data.city,
        temperature=weather_data["temperature"],
        description=weather_data["description"]
    )
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

@app.get("/weather/", response_model=list[schemas.WeatherResponse])
def list_weather(city: str = None, db: Session = Depends(get_db)):
    if city:
        return db.query(models.Weather).filter(models.Weather.city == city).all()
    return db.query(models.Weather).all()

@app.delete("/weather/{weather_id}")
def delete_weather(weather_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Weather).get(weather_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    db.delete(record)
    db.commit()
    return {"detail": "Registro deletado com sucesso"}
