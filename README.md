# ⚡ AI API Chaos Simulator

A FastAPI-based backend system that simulates real-world API behavior including failures, latency, and rate limiting — with built-in observability and request replay.

This project was built to explore how backend systems behave under unpredictable production-like conditions.

---

## 🚀 Features

- 🔁 Retry logic for handling transient failures  
- ❌ Simulated API failures  
- ⏱️ Random latency injection  
- 🚫 Rate limiting per client  
- 📊 Real-time metrics tracking  
- 🔁 Request logging & replay system  
- 🖥️ Live dashboard for observability  

---

## 🧠 Why this project?

Traditional API testing relies on synthetic test cases.

This project explores:
- Capturing real-world behavior
- Simulating unpredictable conditions
- Improving backend reliability and observability

---

## 📡 API Endpoints

| Endpoint     | Description |
|--------------|------------|
| `/data`      | Simulated API with failures, latency, retry logic |
| `/metrics`   | Returns API performance metrics |
| `/replay`    | Returns recent logged requests |
| `/dashboard` | Web UI for live monitoring |

---

## 📊 Dashboard

Access the live dashboard at:


http://127.0.0.1:8000/dashboard


Displays:
- Total requests
- Failures
- Success rate
- Recent request logs

---

## ⚙️ Setup Instructions

### 1. Clone the repo


git clone https://github.com/yourusername/api-chaos-simulator.git

cd api-chaos-simulator


### 2. Install dependencies


pip install fastapi uvicorn jinja2


### 3. Create logs file


mkdir data


Create `data/logs.json`:


[]


### 4. Run the server


uvicorn app.main:app --reload


---

## 🧪 Example Use

Call the API multiple times:


http://127.0.0.1:8000/data


Observe:
- Random failures
- Delays
- Rate limiting

Then check:


/metrics
/dashboard
/replay


---

## 🧩 Tech Stack

- FastAPI
- Python
- Jinja2 Templates
- REST APIs

---

## 🧠 Key Concepts Demonstrated

- Backend reliability engineering  
- API observability  
- Failure simulation (chaos testing)  
- Retry strategies  
- Data logging & replay  
- Real-time monitoring  

---

## 🔮 Future Improvements

- 📈 Graph-based dashboard (Chart.js)
- 🌐 Cloud deployment (Render / Railway)
- 🧪 Automated test generation (Keploy-style)
- 🔐 Authentication & API security layers

---

## 💡 Author

Dave Aashisth 
AI/ML + Backend Systems