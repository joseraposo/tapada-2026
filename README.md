# Run

### Create virtual env
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Compile translations

```bash
pybabel compile -d translations
```

### Run

```bash
flask run
```

### Open locally

Go to `http://127.0.0.1:5000/`
