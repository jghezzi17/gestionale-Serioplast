"""creazione delle classi che gestiscono i prodotti
ci sarà una classe  Prodotti che contiene le info per
Magliette, Pantaloni, Polo, Felpe

Inoltre è presente anche una classe TabellaProdotti che gestisce la creazione di una tabella su flet"""

import flet as ft

TAGLIE_VALIDE = ["XS","S","M","L","XL","XXL","XXXL","N/A"]
PRODOTTI_VALIDI = ["T-shirt", "Pantaloni Uomo","Pantaloni Donna", "Pile","Felpe","Camice", "Camicie","Giacche","Scaldacollo","Cuffie","N/A"]

class Prodotto:
    def __init__(self,id = None, quantita=0,taglia="N/A",nome="N/A"):
        self.id = id
        self.quantita = quantita
        self.nome = nome
        self.taglia = taglia

    def aggiorna_quantita(self, quantita):
        if quantita > 0:
            self.quantita = quantita
        else:
           raise ValueError("Quantità non valida")
        
    def aggiorna_taglia(self, taglia):
        if taglia in TAGLIE_VALIDE:
            self.taglia = taglia
        else:
            raise ValueError("Taglia non valida")

    def aggiorna_nome(self,nome):
        if nome in PRODOTTI_VALIDI:
                self.nome = nome
        else:
            raise ValueError("Prodotto non valido")
        
class FormModificaProdotto:
    def __init__(self, prodotto: Prodotto, on_prodotto_modificato, page):
        self.prodotto = prodotto
        self.on_prodotto_modificato = on_prodotto_modificato
        self.page = page
        self.dialog = None

    def mostra_form(self):
        tipo_prodotto = ft.Dropdown(
            label="Tipo di Prodotto",
            options=[ft.dropdown.Option(nome) for nome in PRODOTTI_VALIDI],
            width=200,
            value=self.prodotto.nome
        )

        quantita = ft.TextField(
            label="Quantità",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.prodotto.quantita),
            error_text=None
        )

        taglia = ft.Dropdown(
            label="Taglia",
            options=[ft.dropdown.Option(t) for t in TAGLIE_VALIDE],
            width=100,
            value=self.prodotto.taglia
        )

        def salva_modifiche(e):
            quantita.error_text = None

            try:
                self.prodotto.aggiorna_nome(tipo_prodotto.value)
                self.prodotto.aggiorna_quantita(int(quantita.value))
                self.prodotto.aggiorna_taglia(taglia.value)

                if self.on_prodotto_modificato:
                    self.on_prodotto_modificato(self.prodotto)

                self.dialog.open = False
                self.page.update()

            except ValueError as ex:
                err = str(ex).lower()
                if "quantità" in err:
                    quantita.error_text = str(ex)
                elif "taglia" in err:
                    taglia.error_text = str(ex)
                else:
                    tipo_prodotto.error_text = str(ex)

                quantita.update()
                taglia.update()
                tipo_prodotto.update()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Modifica Prodotto"),
            content=ft.Column(
                controls=[tipo_prodotto, quantita, taglia],
                tight=True,
            ),
            actions=[
                ft.TextButton("Annulla", on_click=lambda e: self._chiudi_dialog()),
                ft.ElevatedButton("Salva", on_click=salva_modifiche),
            ],
        )

        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)

        self.dialog.open = True
        self.page.update()

    def _chiudi_dialog(self):
        self.dialog.open = False
        self.page.update()


class TabellaProdotti:
    def __init__(self, prodotti: list[Prodotto], on_modifica=None, on_elimina_db=None,on_elimina_filtro=None ):
        self.prodotti = prodotti
        self.on_modifica = on_modifica  # callback per aggiornare il db
        self.on_elimina_db = on_elimina_db #callback per eliminare un prodotto dal db
        self.tabella = self._costruisci_tabella()

    def elimina_prodotto(self, prodotto: Prodotto):
        self.prodotti = [p for p in self.prodotti if not (
            p.nome == prodotto.nome and p.taglia == prodotto.taglia)]
        self.aggiorna()

    def _costruisci_tabella(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Prodotto")),
                ft.DataColumn(label=ft.Text("Quantità")),
                
                ft.DataColumn(label=ft.Text("Taglia")),
                
                ft.DataColumn(label=ft.Text("Azioni")),
            ],
            rows=[
                self._crea_riga(index, prodotto)
                for index, prodotto in enumerate(self.prodotti)
            ],
            data_row_min_height=50,     # più spazio tra le righe
            heading_row_height=60,       # intestazioni più alte
            
        )

    def _crea_riga(self, index, prodotto: Prodotto):
        # Crea TextField separati così possiamo aggiornarli in caso di errore
        def elimina_prodotto(e):
            self.prodotti.remove(prodotto)
            if self.on_elimina_db:
                self.on_elimina_db(prodotto)
            self.aggiorna()            # Ricostruisce le righe
            self.tabella.update()

        def modifica_prodotto(e):
            form_modifica = FormModificaProdotto(
                prodotto,
                on_prodotto_modificato=self._on_prodotto_modificato,
                page=e.page
            )
            form_modifica.mostra_form()
            
            
        bottone_elimina = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="red",
            tooltip="Elimina prodotto",
            on_click=elimina_prodotto
        )

        bottone_modifica = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color="grey",
            tooltip="modifica prodotto",
            on_click=modifica_prodotto
        )
        
        tf_nome = ft.Text(prodotto.nome)
        tf_quantita = ft.Text(str(prodotto.quantita))
        tf_taglia = ft.Text(prodotto.taglia)

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Container(content=tf_nome, width=150)),
                ft.DataCell(ft.Container(content=tf_quantita, width=150)),
                
                ft.DataCell(ft.Container(content=tf_taglia, width=150)),
                
                ft.DataCell(ft.Row([bottone_modifica, bottone_elimina], spacing=10)),
            ]
        )
        
    def aggiungi_prodotto(self, prodotto: Prodotto):
        for i, p in enumerate(self.prodotti):
            
            if p.nome == prodotto.nome and p.taglia == prodotto.taglia:
                print("il prodotto esiste gia, aggiungo al prodtto esistente")
                # Incrementa quantità
                p.quantita += prodotto.quantita
                
                # Recupera la riga e il TextField quantità
                riga = self.tabella.rows[i]
                tf_quantita = riga.cells[1].content.content  # il TextField è dentro Container -> content
                
                # Aggiorna il valore del TextField
                tf_quantita.value = str(p.quantita)
                tf_quantita.update()
                
                # Aggiorna la tabella e la pagina
                self.tabella.update()
                return
            
        print("il prodotto non esiste, lo aggiungo")
        # Prodotto nuovo, aggiungilo come prima
        self.prodotti.append(prodotto)
        nuova_riga = self._crea_riga(len(self.prodotti) - 1, prodotto)
        self.tabella.rows.append(nuova_riga)
        self.tabella.update()



    def get_widget(self):
        return ft.Container(
            content=self.tabella,
            padding=20,
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _on_prodotto_modificato(self, prodotto_modificato: Prodotto):
        # Cerca se esiste già un altro prodotto con lo stesso nome e taglia
        for i, p in enumerate(self.prodotti):
            if p.id != prodotto_modificato.id and p.nome == prodotto_modificato.nome and p.taglia == prodotto_modificato.taglia:
                # Trovato un duplicato → somma quantità
                print("Unisco i prodotti con la stessa combinazione nome-taglia")

                # Somma le quantità
                p.quantita += prodotto_modificato.quantita

                # Elimina il vecchio prodotto dalla lista e tabella
                index_vecchio = next((i for i, pr in enumerate(self.prodotti) if pr.id == prodotto_modificato.id), None)
                if index_vecchio is not None:
                    del self.prodotti[index_vecchio]
                    del self.tabella.rows[index_vecchio]

                # Aggiorna il TextField della riga del prodotto esistente
                riga = self.tabella.rows[i]
                tf_quantita = riga.cells[1].content.content
                tf_quantita.value = str(p.quantita)
                tf_quantita.update()

                # Aggiorna nel database
                self.on_elimina_db(prodotto_modificato)  # elimina il vecchio record
                self.on_modifica(p)  # aggiorna la quantità del prodotto esistente

                self.aggiorna()
                self.tabella.update()
                return

        # Altrimenti, modifica normale
        if self.on_modifica:
            self.on_modifica(prodotto_modificato)

        self.aggiorna()
        self.tabella.update()


    def aggiorna(self,prodotti_filtrati=None):
        """Ricostruisce tutte le righe nel caso i dati siano stati aggiornati fuori o filtrati."""
        lista = prodotti_filtrati if prodotti_filtrati is not None else self.prodotti
        self.tabella.rows = [
            self._crea_riga(index, prodotto)
            for index, prodotto in enumerate(lista)
        ]
        print("Tabella aggiornata con", len(lista), "prodotti")
        self.tabella.update()
         
         

class FormInserimentoProdotto:
    def __init__(self, on_prodotto_creato):
        self.on_prodotto_creato = on_prodotto_creato
        self.dialog = None

    def mostra_form(self, page):
        print("sto mostrando la form di aggiunta prodotti")
        
        tipo_prodotto = ft.Dropdown(
            label="Tipo di Prodotto",
            options=[ft.dropdown.Option(nome) for nome in PRODOTTI_VALIDI],
            width=200,
            value=PRODOTTI_VALIDI[0]
        )

        quantita = ft.TextField(
            label="Quantità",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            error_text=None
        )
        taglia = ft.Dropdown(
            label="Taglia",
            options=[ft.dropdown.Option(t) for t in TAGLIE_VALIDE],
            width=100,
            value=TAGLIE_VALIDE[0]
        )

        def crea_prodotto(e):
            # Reset errori
            quantita.error_text = None
           

            p = Prodotto()
            try:
                p.aggiorna_nome(tipo_prodotto.value)
                p.aggiorna_quantita(int(quantita.value))
                p.aggiorna_taglia(taglia.value)
                """queste tre callback sono gestite in paginaMgazzino da un'unica callback"""
                if self.on_prodotto_creato:#salva su db
                    self.on_prodotto_creato(p)

                self.dialog.open = False
                page.update()

            except ValueError as ex:
                # Gestione errori e assegnazione messaggi sotto i campi
                err = str(ex).lower()
                if "quantità" in err:
                    quantita.error_text = str(ex)
                elif "taglia" in err:
                    taglia.error_text = str(ex)
                else:
                    colore.error_text = str(ex)
                # Aggiorna il dialog per mostrare errori
                quantita.update()
                taglia.update()
                tipo_prodotto.update()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Inserisci Nuovo Prodotto"),
            content=ft.Column(
                controls=[tipo_prodotto, quantita,  taglia, ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Annulla", on_click=lambda e: self._chiudi_dialog(page)),
                ft.ElevatedButton("Crea", on_click=crea_prodotto),
            ],
        )
        if self.dialog not in page.overlay:
            page.overlay.append(self.dialog)

        self.dialog.open = True
        page.update()

    def _chiudi_dialog(self, page):
        self.dialog.open = False
        page.update()

class BoxFiltro:
    def __init__(self, tabella_prodotti: TabellaProdotti):
        self.tabella_prodotti = tabella_prodotti

        self.filtro_nome = ft.Dropdown(
            label="Tipo Prodotto",
            options=[ft.dropdown.Option(p) for p in ["Tutti"] + PRODOTTI_VALIDI],
            value="Tutti",
            width=150
        )
        self.filtro_taglia = ft.Dropdown(
            label="Taglia Prodotto",
            options=[ft.dropdown.Option(t) for t in ["Tutte"] + TAGLIE_VALIDE],
            value="Tutte",
            width=150
        )

        self.bottone_filtra = ft.ElevatedButton("Applica", bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, on_click=self._applica_filtro)
        self.bottone_reset = ft.TextButton("Reset", on_click=self._reset_filtro)
        self.titolo = ft.Text("Filtro", size=30, color=ft.Colors.BLUE_900)

        self.container = ft.Row(
            controls=[self.titolo, self.filtro_nome, self.filtro_taglia, self.bottone_filtra, self.bottone_reset],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _applica_filtro(self, e):
        nome = self.filtro_nome.value
        taglia = self.filtro_taglia.value

        filtrati = [
            p for p in self.tabella_prodotti.prodotti
            if (nome == "Tutti" or p.nome == nome) and
               (taglia == "Tutte" or p.taglia == taglia)
        ]
        print("sono dentro _applica_filtro")
        

        self.tabella_prodotti.aggiorna(filtrati)
        self.tabella_prodotti.tabella.update()

    def _reset_filtro(self, e):
        self.filtro_nome.value = "Tutti"
        self.filtro_taglia.value = "Tutte"

        self.filtro_nome.update()
        self.filtro_taglia.update()

        # Mostra tutti i prodotti presenti
        self.tabella_prodotti.aggiorna()
        self.tabella_prodotti.tabella.update()

    def get_widget(self):
        return self.container


