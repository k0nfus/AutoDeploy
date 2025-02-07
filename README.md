# AutoDeploy
Pythonskript für automatisches Deployment des Repositories auf einen VPS mit gunicorn und Nginx.

## Einrichtung

Folgende Schritte habe ich unternommen, um das Projekt einzurichten:

```bash
mkdir Deployment
cd Deployment
python3 -m venv venv
source venv/bin/activate
pip3 install paramiko
touch deploy.py
```
