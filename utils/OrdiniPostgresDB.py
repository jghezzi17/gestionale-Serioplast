import psycopg2
from datetime import datetime
from utils.ClassiOrdini import Ordine
from utils.ClassiProdotti import Prodotto

class OrdiniDB:
    def __init__(self, db_config):
        self.db_config = db_config
        self._create_tables()

    def _connect(self):
        return psycopg2.connect(**self.db_config)

    def _create_tables(self):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ordini (
                        id SERIAL PRIMARY KEY,
                        codice_ordine TEXT UNIQUE,
                        timestamp TEXT,
                        applicato INTEGER DEFAULT 0
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS prodotti_ordine (
                        id SERIAL PRIMARY KEY,
                        ordine_id INTEGER REFERENCES ordini(id) ON DELETE CASCADE,
                        nome TEXT,
                        quantita INTEGER,
                        taglia TEXT
                    )
                ''')
            conn.commit()

    def aggiungi_ordine(self, ordine: Ordine):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO ordini (codice_ordine, timestamp, applicato)
                    VALUES (%s, %s, %s)
                    RETURNING id
                ''', (ordine.codice_ordine, ordine.timestamp.isoformat(), 0))
                ordine.id = cursor.fetchone()[0]

                for prodotto in ordine.prodotti:
                    cursor.execute('''
                        INSERT INTO prodotti_ordine (ordine_id, nome, quantita, taglia)
                        VALUES (%s, %s, %s, %s)
                    ''', (ordine.id, prodotto.nome, prodotto.quantita, prodotto.taglia))
            conn.commit()

    def get_tutti_ordini(self):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, codice_ordine, timestamp, applicato FROM ordini')
                ordini_raw = cursor.fetchall()

                ordini = []
                for ordine_row in ordini_raw:
                    ordine_id, codice_ordine, timestamp, applicato = ordine_row
                    cursor.execute('''
                        SELECT id, nome, quantita, taglia FROM prodotti_ordine
                        WHERE ordine_id = %s
                    ''', (ordine_id,))
                    prodotti_raw = cursor.fetchall()
                    prodotti = [
                        Prodotto(id=p[0], nome=p[1], quantita=p[2], taglia=p[3])
                        for p in prodotti_raw
                    ]
                    ordini.append(Ordine(
                        id=ordine_id,
                        codice_ordine=codice_ordine,
                        timestamp=datetime.fromisoformat(timestamp),
                        prodotti=prodotti,
                        applicato=bool(applicato)
                    ))
                return ordini

    def get_ordine_by_id(self, ordine_id: int) -> Ordine | None:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, codice_ordine, timestamp, applicato FROM ordini
                    WHERE id = %s
                ''', (ordine_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                id_, codice_ordine, timestamp, applicato = row

                cursor.execute('''
                    SELECT id, nome, quantita, taglia FROM prodotti_ordine
                    WHERE ordine_id = %s
                ''', (id_,))
                prodotti_raw = cursor.fetchall()

                prodotti = [
                    Prodotto(id=p[0], nome=p[1], quantita=p[2], taglia=p[3])
                    for p in prodotti_raw
                ]

                return Ordine(
                    id=id_,
                    codice_ordine=codice_ordine,
                    timestamp=datetime.fromisoformat(timestamp),
                    prodotti=prodotti,
                    applicato=bool(applicato)
                )

    def set_applicato(self, ordine_id: int, valore: bool):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE ordini SET applicato = %s
                    WHERE id = %s
                ''', (1 if valore else 0, ordine_id))
            conn.commit()

    def get_prodotti_per_ordine(self, ordine_id: int):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, nome, quantita, taglia FROM prodotti_ordine
                    WHERE ordine_id = %s
                ''', (ordine_id,))
                righe = cursor.fetchall()
                return [
                    Prodotto(id=r[0], nome=r[1], quantita=r[2], taglia=r[3])
                    for r in righe
                ]

    def aggiorna_prodotto_ordine(self, ordine_id: int, prodotto: Prodotto):
        if not hasattr(prodotto, "id") or prodotto.id is None:
            raise ValueError("Prodotto senza ID non può essere aggiornato")
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE prodotti_ordine
                    SET nome = %s, quantita = %s, taglia = %s
                    WHERE id = %s AND ordine_id = %s
                ''', (prodotto.nome, prodotto.quantita, prodotto.taglia, prodotto.id, ordine_id))
            conn.commit()

    def aggiungi_prodotto_ordine(self, ordine_id: int, prodotto: Prodotto):
        if not ordine_id:
            raise ValueError("Ordine ID mancante per l'aggiunta del prodotto")
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO prodotti_ordine (ordine_id, nome, quantita, taglia)
                    VALUES (%s, %s, %s, %s)
                ''', (ordine_id, prodotto.nome, prodotto.quantita, prodotto.taglia))
            conn.commit()

    def elimina_prodotto_ordine(self, ordine_id: int, prodotto: Prodotto):
        if not hasattr(prodotto, "id") or prodotto.id is None:
            raise ValueError("Prodotto senza ID non può essere eliminato")
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    DELETE FROM prodotti_ordine
                    WHERE id = %s AND ordine_id = %s
                    ''',
                    (prodotto.id, ordine_id)
                )
            conn.commit()

    def elimina_ordine(self, ordine: Ordine):
        if ordine.id is None:
            raise ValueError("Impossibile eliminare un ordine senza ID")
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM prodotti_ordine WHERE ordine_id = %s', (ordine.id,))
                cursor.execute('DELETE FROM ordini WHERE id = %s', (ordine.id,))
            conn.commit()

    def svuota_tabella(self):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM prodotti_ordine')
                cursor.execute('DELETE FROM ordini')
            conn.commit()
