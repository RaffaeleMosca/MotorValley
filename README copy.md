# PharmaCenter
Eseguire le seguenti istruzioni per eseguire PharmaCenter:
Windows:
Digitare nel terminale il seguente comando: python -m venv path/to/venv 
Entrare nel path fino ad arrivare al file activate.ps1 ed eseguire il comando: powershell -noprofile -executionpolicy bypass -file "activate.ps1"
Infine installare tutte le dipendenze mediante pip, usando il comando: pip install -r requirements.txt
Eseguire l'applicativo con il comando: python -m flask run

MacOS:
Digitare nel terminale il seguente comando: python -m venv path/to/venv 
Attivare l'evnviroment usando il comando: source path/to/venv/bin/activate
Infine installare tutte le dipendenze mediante pip, usando il comando: pip install -r requirements.txt
Eseguire l'applicativo con il comando: python -m flask run
FLASK_APP=app.py FLASK_ENV=development flask run

In caso di Access to 127.0.0.1 was denied eseguire le seguenti istruzioni:
Se si sta usando Chrome andare al seguente link: chrome://net-internals/#sockets
Cliccare su: [Flush socket pools]