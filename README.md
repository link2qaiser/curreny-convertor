# PingHub

**PingHub** is a lightweight FastAPI backend service for performing geo-distributed ping measurements using the [Globalping API](https://api.globalping.io). This is ideal for measuring network latency from multiple countries around the world.

---

## 🚀 Features

- 🔐 Secure HMAC-protected endpoint  
- 🌍 Global ping measurement using `https://api.globalping.io`  
- 🧱 Simple modular structure (routes, services, schemas, utils)  
- 📜 Clean logging setup with rotating file handler  

---

## 📁 Project Structure

```
pinghub/
├── app/
│   ├── geoping/
│   │   ├── routes.py          # API endpoint for geo-ping
│   │   ├── service.py         # Business logic for calling Globalping
│   │   └── schema.py          # Request schema
│   ├── utils/
│   │   ├── logging_config.py  # Centralized logging config
│   │   ├── security.py        # HMAC validation logic
│   │   └── main.py            # FastAPI app definition
├── logs/                      # Log directory
├── .env                       # Environment variables
├── .env.example               # Example env file
├── Dockerfile
├── docker-compose.yml
├── docker-compose.local.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 📦 Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)

---

### 🧪 Local Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/pinghub.git
   cd pinghub
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your HMAC_SECRET and Globalping token
   ```

3. **Create a virtual environment & install dependencies:**

   ```bash
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the server:**

   ```bash
   uvicorn app.utils.main:app --reload
   ```

---

### 🐳 Docker Development

To run the app with Docker:

```bash
docker-compose -f docker-compose.local.yml up --build
```

Then access it at:

```
http://localhost:8000/docs
```

---

## 🔐 Security

The `/network/geo-ping` endpoint is protected via **HMAC authentication**.

### 🔐 Headers Required:

- `X-Timestamp`: Current UNIX timestamp
- `X-Signature`: HMAC-SHA256 of `target + timestamp` using your shared secret

---

## 🌐 Environment Variables

Create a `.env` file based on `.env.example` with values like:

```
HMAC_SECRET=your_super_secret_key
GLOBALPING_BEARER_TOKEN=your_globalping_token
```

---

## 🧪 Example cURL Request

```bash
curl -X POST http://localhost:8000/network/geo-ping \
  -H "Content-Type: application/json" \
  -H "X-Timestamp: 1719071013" \
  -H "X-Signature: <your_signature>" \
  -d '{"target": "dixeam.com"}'
```

Generate signature using:
```
HMAC_SHA256(secret, target + timestamp)
```

---

## 📝 Logging

All logs are written to both console and file:  
`logs/app.log`

To configure log format or rotation, see `app/utils/logging_config.py`.

---

## 📚 Future Plans

- Add GET `/geo-ping/{measurement_id}` to fetch results
- Integrate caching to avoid duplicate requests
- Add rate limiting for public use

---

## 🤝 License

MIT License © 2025 — PingHub by [YourName or Org]
