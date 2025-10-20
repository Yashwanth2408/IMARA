# IMARA Deployment Guide

## Local Development Setup (Already Done!)

You've completed this section. Your system is running locally.

## Docker Deployment

### Create Dockerfile
IMARA Dockerfile
FROM python:3.11-slim

WORKDIR /app

Install system dependencies
RUN apt-get update && apt-get install -y
curl
&& rm -rf /var/lib/apt/lists/*

Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

Expose Streamlit port
EXPOSE 8501

Start Ollama and pull model, then run Streamlit
CMD ollama serve &
sleep 5 &&
ollama pull llama3.2:3b &&
streamlit run ui/app.py --server.address=0.0.0.0

### Build and Run
docker build -t imara .
docker run -p 8501:8501 imara

## Cloud Deployment (AWS EC2)

### Requirements
- EC2 instance (t3.large or larger)
- Ubuntu 22.04
- At least 8GB RAM

### Steps
SSH into EC2
ssh -i key.pem ubuntu@<instance-ip>

Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip git

Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

Clone project
git clone <your-repo-url>
cd IMARA

Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Pull model
ollama pull llama3.2:3b

Run with nohup
nohup streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0 &

### Access
Open `http://<instance-ip>:8501` in browser

## Production Considerations

### Performance
- Use GPU instance for faster LLM inference
- Add Redis for caching
- Implement request queuing

### Security
- Add authentication (Streamlit supports basic auth)
- Use HTTPS with SSL certificates
- Firewall configuration

### Monitoring
- Log agent execution times
- Track error rates
- Monitor memory/CPU usage
