# Analog Clock Reader
### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Code
```bash
python main.py
```
Specify the path of the image
```bash
python main.py ./images/clock.jpeg
```

### Run with Docker 🐳
---
1. Build the image
```bash
docker build -t clockreader .
```
2. Run the container
```bash
docker compose up -d
```