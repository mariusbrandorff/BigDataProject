# Testing tools
These testing tools are just a consumer and a producer.

## Setup
```bash
python -m venv venv
```

### Then active the venv
(you should know how, but in case you don't)
```bash
# Powershell
venv\Scripts\Activate.ps1
```
```bash
# Bash
source venv/Scripts/activate
```
```bash
# Fish
source venv/Scripts/activate.fish
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Start Kafka
```bash
docker compose up -d
```

### Run
```bash
python ./main.py -i ${IN_TOPIC} -o ${OUT_TOPIC}
```

### Enjoy
???