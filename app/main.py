from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, weather
from app.database import SessionLocal, engine, Base
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from app.weather import fetch_weather, transform_weather_data
from datetime import datetime
import requests

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
        transformed_weather_data = weather.transform_weather_data(weather_data)  # Transformação dos dados
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao buscar clima.")

    # Armazenar os dados transformados no banco
    db_weather = models.Weather(
        city=data.city,
        temperature=transformed_weather_data["temperature"],
        description=transformed_weather_data["description"]
    )
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)

    # Enviar dados para WebHook
    send_webhook_notification({
        "city": db_weather.city,
        "temperature": db_weather.temperature,
        "description": db_weather.description
    })

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

# Função de agendamento
def fetch_and_store_weather_periodically():
    city = "São Paulo"  # Você pode definir um conjunto de cidades
    try:
        weather_data = fetch_weather(city)
        transformed_data = transform_weather_data(weather_data)

        # Armazenar os dados no banco de dados
        db = SessionLocal()  # Criando uma nova sessão para o banco de dados
        db_weather = models.Weather(
            city=city,
            temperature=transformed_data["temperature"],
            description=transformed_data["description"]
        )
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)

        # Enviar dados para WebHook
        send_webhook_notification({
            "city": db_weather.city,
            "temperature": db_weather.temperature,
            "description": db_weather.description
        })
    except Exception as e:
        print(f"Erro ao processar dados climáticos: {e}")

# Função para enviar dados para WebHook
def send_webhook_notification(weather_data):
    WEBHOOK_URL = "http://outrosistema.com/webhook"  # Defina a URL do WebHook
    try:
        response = requests.post(WEBHOOK_URL, json=weather_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar dados para o WebHook: {e}")

# Inicializa o agendador
scheduler = BackgroundScheduler()

# Agende a execução da função a cada 1 hora (pode ajustar o intervalo)
scheduler.add_job(fetch_and_store_weather_periodically, 'interval', hours=1)

# Inicia o agendador
scheduler.start()
