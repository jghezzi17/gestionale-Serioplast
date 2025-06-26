# Gestionale Serioplast

Gestionale per la gestione del magazzino Serioplast, sviluppato in Python con interfaccia grafica tramite [Flet](https://flet.dev/) e database PostgreSQL.

## Funzionalità

- Visualizzazione prodotti in magazzino
- Inserimento e modifica prodotti (nome, quantità, taglia)
- Filtro per tipo prodotto e taglia
- Eliminazione prodotti
- Aggiornamento diretto del database PostgreSQL

## Requisiti

- Python 3.10+
- PostgreSQL
- Ambiente virtuale consigliato (venv)

## Setup

### 1. Clona il progetto

```bash
git clone https://github.com/tuo-username/gestionaleSerioplast.git
cd gestionaleSerioplast
’’’
### 2. Crea e attiva il venv
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
’’’

## 3. Installa le dipendenze
```bash
pip install -r requirements.txt
’’’

## Configurazione Database PostgreSQL

Per far funzionare correttamente l’app, è necessario installare e configurare PostgreSQL con i database richiesti.

### 1. Installazione PostgreSQL

- Scarica PostgreSQL dal sito ufficiale:  
  [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

- Segui le istruzioni di installazione per il tuo sistema operativo (Windows, macOS, Linux).

### 2. Creazione utente e accesso

- Durante l’installazione ti verrà chiesto di creare una password per l’utente `postgres` (superuser).
- Puoi gestire utenti e permessi anche tramite pgAdmin (interfaccia grafica) o da terminale con `psql`.

### 3. Creazione dei database

Una volta installato e configurato PostgreSQL, crea i database necessari aprendo il terminale (o pgAdmin) ed eseguendo i seguenti comandi:

```sql
CREATE DATABASE ordiniserioplast;
CREATE DATABASE ordinilumachina;
CREATE DATABASE magazzino_db;
’’’

## Configurazione Database per Accesso da Altri PC (Server/Host)

Se stai eseguendo il database PostgreSQL su un PC che funge da server/host, e vuoi che altri computer in rete vi si connettano, segui queste istruzioni:

### 1. Configurazione Connessione Locale (Server)

- Sul PC server dove gira PostgreSQL, nel file di configurazione del database (`db_config.py` o simile), il parametro di connessione deve essere impostato così:

```python
DB_HOST = 'localhost'   # connessione locale
DB_PORT = 5432          # porta di default PostgreSQL
’’’
## Configurazione per Connessione da Altri PC

Per consentire l'accesso al database PostgreSQL da altri computer della rete locale:

1. **Configura PostgreSQL per connessioni remote:**

- Modifica `postgresql.conf` (es. `C:\Program Files\PostgreSQL\<versione>\data` o `/etc/postgresql/<versione>/main/`):

  ```ini
  listen_addresses = '*'
’’’
- **Modifica `pg_hba.conf` aggiungendo** (sostituisci con la tua subnet):

```conf
host    all    all    192.168.1.0/24    md5
’’’
## Configurazione firewall e rete per accesso remoto al database

### Configura il firewall sul PC server:

- Permetti il traffico in entrata sulla porta TCP 5432.

- Su **Windows**: crea una regola firewall per la porta 5432.

- Su **Linux**:

  ```bash
  sudo ufw allow 5432/tcp
’’’
## Imposta IP fisso al PC server (consigliato)

- Trova l’IP con `ipconfig` (Windows) o `ifconfig` / `ip a` (Linux/macOS).

- Configura IP statico tramite impostazioni di rete o prenotazione DHCP nel router.



## Configura i client

Nel file di configurazione client (`db_config.py`), imposta:

```python
DB_HOST = '<IP-del-server>'  # es. '192.168.1.100'
DB_PORT = 5432
’’’
