# Smartkar(poloha)

## Setup

 1. `python -m venv virt`
 2. `. virt/bin/activate`
 3. `pip install -r requirements.txt`
 4. `export FLASK_ENV='development' or 'production'`
 5. `export SECRET_KEY='random bullshit here'`
 6. `export NCZI_TOKEN='....'`
 7. Setup nginx to proxy `/geo/` to `127.0.0.1:7777`
 8. Run `./run.py`
 
## Translations

### Extract
Extracts strings into a POT (template) file.

    pybabel extract -F babel.cfg -o messages.pot . --no-wrap

### Create/Update
Creates/Updates a PO file for a language from a given POT.

    pybabel init -i messages.pot -d smartkar/translations -l en

    pybabel update -i messages.pot -d smartkar/translations -l en   

### Compile
Compiles a PO file into a MO file, for use in the app.

    pybabel compile -d smartkar/translations 