# hello.py: API IoT pentru citiri de la senzori
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
import re
app = FastAPI(title="TPI IoT API")
DEV_PATTERN = r"^[a-z0-9-]{1,32}$"

class Reading(BaseModel):
    dev: str = Field(pattern=DEV_PATTERN) # ID dispozitiv
    seq: int = Field(ge=0) # nr de ordine al citirii pentru dispozitivul respectiv
    ts: int = Field(gt=1_600_000_000) # secunde Unix, UTC
    temp: float = Field(ge=-40, le=85) # temperatura °C
    hum: float | None = Field(default=None, ge=0, le=100) # umiditate %
# "Baza de date" în memorie: dev_id -> {seq: Reading}
DB: dict[str, dict[int, Reading]] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

# TODO 1: endpoint POST /readings
# - primește un obiect Reading în corpul cererii
# - răspunde cu 201 și cu citirea salvată
# - seq deja existent pentru același dev -> 409

@app.post("/readings", status_code=201)
def create_reading(reading: Reading):
    dev_id = reading.dev
    seq = reading.seq

    if not re.match(DEV_PATTERN, dev_id):
        raise HTTPException(status_code=422, detail="ID dispozitiv invalid.")
    # Verificam daca exista o citire cu acelasi nr de ordine pentru dispozitivul respectiv
    if seq in DB.get(dev_id, {}):
        raise HTTPException(status_code=409, detail="Acest seq exista deja pentru dispozitivul specificat.")


    if reading.temp < -40 or reading.temp > 85:
        raise HTTPException(status_code=422, detail="Temperatura invalida. Trebuie sa fie intre -40 si 85 °C.") 

    if reading.hum is not None and (reading.hum < 0 or reading.hum > 100):
        raise HTTPException(status_code=422, detail="Umiditate invalida. Trebuie sa fie intre 0 si 100 %.")

    # Adaugam citirea in baza de date
    if dev_id not in DB:
        DB[dev_id] = {}
    DB[dev_id][seq] = reading
    return reading

@app.get("/devices/{dev_id}/readings", status_code=200)
def readings(
    dev_id: str = Path(pattern=DEV_PATTERN), # TODO 2: validare cu DEV_PATTERN
    since: int = Query(default=0,ge=0), # TODO 3: since >= 0
    limit: int = Query(default=10, ge=1, le=100) # TODO 4: 1 <= limit <= 100
) -> list[Reading]:
    if dev_id not in DB:
        raise HTTPException(status_code=404, detail="Dispozitiv necunoscut.")

    if since < 0:
        raise HTTPException(status_code=422, detail="Parametrul 'since' trebuie sa fie >= 0.")

    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Parametrul 'limit' trebuie sa fie intre 1 si 100.")


    return list(reading for seq, reading in sorted(DB[dev_id].items()) if seq > since)[:limit]
    
    # TODO 5: dispozitiv necunoscut -> 404
    # TODO 6: doar citirile cu seq > since, ordonate crescător după seq 
    # TODO 7: cel mult `limit` citiri
