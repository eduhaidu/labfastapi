# API pentru citiri de la senzori

Aplicația din `hello.py` este un API construit cu FastAPI pentru înregistrarea și consultarea citirilor trimise de senzori.

## Pornirea aplicației

Din directorul proiectului:

```bash
uvicorn hello:app --reload
```

Serverul pornește implicit la `http://127.0.0.1:8000`. Documentația interactivă este disponibilă la `/docs`.

## Endpoint-uri

- `GET /health` — verifică dacă API-ul funcționează; răspunde cu `{"status": "ok"}`.
- `POST /readings` — primește o citire JSON și o salvează; răspunde cu `201 Created`. Nu permite același `seq` de două ori pentru același dispozitiv (`409 Conflict`).
- `GET /devices/{dev_id}/readings` — returnează citirile dispozitivului, ordonate după numărul de secvență.

Exemplu de corp pentru `POST /readings`:

```json
{
  "dev": "senzor-1",
  "seq": 1,
  "ts": 1762096000,
  "temp": 21.5,
  "hum": 40
}
```

`dev` poate conține litere mici, cifre și cratime (maximum 32 de caractere). `seq` trebuie să fie cel puțin `0`, `ts` trebuie să fie mai mare de `1600000000`, temperatura trebuie să fie între `-40` și `85`, iar umiditatea, dacă este furnizată, între `0` și `100`.

Pentru citiri, parametrii opționali sunt `since` (implicit `0`) și `limit` (implicit `10`, între `1` și `100`). `since` este exclusiv: `since=1` returnează doar citirile cu `seq > 1`.

Citirile sunt păstrate într-un dicționar în memoria procesului. Ele se pierd când aplicația se oprește sau repornește. Un dispozitiv fără citiri cunoscute produce răspunsul `404 Not Found`.
