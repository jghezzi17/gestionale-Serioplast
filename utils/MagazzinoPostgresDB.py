import psycopg2
from psycopg2 import sql
from utils.ClassiProdotti import Prodotto

class MagazzinoDB:
    def __init__(self, db_config):
        """
        db_config: dict con parametri di connessione a Postgres, esempio:
        {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'nome_db',
            'user': 'utente',
            'password': 'password'
        }
        """
        self.db_config = db_config
        self._create_table()
        self.on_elimina_prodotto_gui = None
        

    def _connect(self):
        return psycopg2.connect(**self.db_config)

    def set_callbacks(self, on_elimina_prodotto_gui=None):
        self.on_elimina_prodotto_gui = on_elimina_prodotto_gui

    def _create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS magazzino (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            quantita INTEGER,
            taglia TEXT
        )
        '''
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def verifica_disponibilita(self, prodotto: Prodotto) -> bool:
        query = '''
            SELECT quantita FROM magazzino
            WHERE nome = %s AND taglia = %s
        '''
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (prodotto.nome, prodotto.taglia))
                row = cursor.fetchone()
                return row is not None and row[0] >= prodotto.quantita

   

    def aggiungi_o_incrementa(self, prodotto: Prodotto) -> int:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, quantita FROM magazzino
                    WHERE nome = %s AND taglia = %s
                ''', (prodotto.nome, prodotto.taglia))
                esistente = cursor.fetchone()

                if esistente:
                    id_esistente, quantita_attuale = esistente
                    nuova_quantita = quantita_attuale + prodotto.quantita
                    cursor.execute('''
                        UPDATE magazzino
                        SET quantita = %s
                        WHERE id = %s
                    ''', (nuova_quantita, id_esistente))
                    conn.commit()
                    return id_esistente
                else:
                    cursor.execute('''
                        INSERT INTO magazzino (nome, quantita, taglia)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    ''', (prodotto.nome, prodotto.quantita, prodotto.taglia))
                    nuovo_id = cursor.fetchone()[0]
                    conn.commit()
                    return nuovo_id


    
    def scarica_prodotto(self, prodotto: Prodotto) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, quantita FROM magazzino
                    WHERE nome = %s AND taglia = %s
                ''', (prodotto.nome, prodotto.taglia))
                esistente = cursor.fetchone()

                if esistente:
                    id_esistente, quantita_attuale = esistente

                    if quantita_attuale < prodotto.quantita:
                        return False

                    nuova_quantita = quantita_attuale - prodotto.quantita

                    if nuova_quantita == 0:
                        # ✅ Elimina il prodotto dal DB
                        cursor.execute('''
                            DELETE FROM magazzino WHERE id = %s
                        ''', (id_esistente,))
                    else:
                        # Aggiorna la quantità
                        cursor.execute('''
                            UPDATE magazzino SET quantita = %s WHERE id = %s
                        ''', (nuova_quantita, id_esistente))

                    conn.commit()

                    # ✅ Dopo commit: trigger GUI update se necessario
                    if self.on_elimina_prodotto_gui:
                        self.on_elimina_prodotto_gui(prodotto)

                    return True
                else:
                    return False


    def get_tutti_prodotti(self):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, nome, quantita, taglia FROM magazzino')
                righe = cursor.fetchall()
                return [
                    Prodotto(id=r[0], nome=r[1], quantita=r[2], taglia=r[3])
                    for r in righe
                ]

    def aggiorna_prodotto(self, prodotto: Prodotto):
        if prodotto.id is None:
            raise ValueError("Prodotto senza ID non può essere aggiornato")
        query = '''
            UPDATE magazzino SET nome=%s, quantita=%s, taglia=%s
            WHERE id=%s
        '''
        with self._connect() as conn:
            with conn.cursor() as cursor:
                print("DEBUG aggiorna_prodotto:")
                print("nome:", prodotto.nome, type(prodotto.nome))
                print("quantita:", prodotto.quantita, type(prodotto.quantita))
                print("taglia:", prodotto.taglia, type(prodotto.taglia))
                print("id:", prodotto.id, type(prodotto.id))
                cursor.execute(query, (prodotto.nome, prodotto.quantita, prodotto.taglia, prodotto.id))
            conn.commit()

    def elimina_prodotto(self, prodotto: Prodotto):
        if prodotto.id is None:
            raise ValueError("Impossibile eliminare un prodotto senza ID")
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM magazzino WHERE id = %s', (prodotto.id,))
            conn.commit()

    def svuota_tabella(self):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM magazzino')
            conn.commit()
