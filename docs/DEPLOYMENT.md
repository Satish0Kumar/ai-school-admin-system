# Deployment Guide

## Local Deployment
Backend: http://127.0.0.1:5000  
Frontend: http://localhost:8501

## Local Network Deployment
Change API host to 0.0.0.0  
Update frontend API_BASE_URL  
Allow ports 5000 & 8501 in firewall

## Cloud Deployment
Use Gunicorn for backend  
Deploy frontend using Streamlit Cloud

## Security & Performance
- Enable HTTPS
- Add authentication
- Add rate limiting
- Enable logging & monitoring
