import flet as ft
from datetime import datetime
from utils.ClassiProdotti import Prodotto



class Ordine:
    def __init__(self, codice_ordine: str, prodotti=None, id=None, timestamp=None,applicato=False):
        """
        codice_ordine: identificativo inserito dall’utente (es. "ORD001")
        id: campo gestito dal database, se serve
        timestamp: data e ora della creazione (di default ora)
        prodotti: lista di oggetti Prodotto
        """
        self.id = id  # ID interno del DB (opzionale)
        self.codice_ordine = codice_ordine.strip()
        self.timestamp = timestamp or datetime.now()
        self.prodotti = prodotti or []
        self.applicato = applicato

    def aggiungi_prodotto(self, prodotto: Prodotto):
        self.prodotti.append(prodotto)

    def rimuovi_prodotto(self, prodotto: Prodotto):
        if prodotto in self.prodotti:
            self.prodotti.remove(prodotto)

    def totale_quantita(self):
        return sum(p.quantita for p in self.prodotti)

    def __str__(self):
        prodotti_str = "\n".join(
            f"{p.nome} x{p.quantita} (Taglia: {p.taglia})" for p in self.prodotti
        )
        return (
            f"Ordine {self.codice_ordine} - "
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n{prodotti_str}"
        )
class FormNoteOrdine:
    def __init__(self, ordine, magazzino_db, page):
        self.ordine = ordine
        self.magazzino_db = magazzino_db
        self.page = page
        self.dialog = None

    def mostra_form(self):
        note_iniziali = self.magazzino_db.get_note_ordine(self.ordine.id)

        campo_note = ft.TextField(
            label="Note",
            multiline=True,
            value=note_iniziali or "",
            width=400,
            height=200,
        )

        def salva_note(e):
            self.magazzino_db.salva_note_ordine(self.ordine.id, campo_note.value)
            self.dialog.open = False
            self.page.update()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Note per Ordine"),
            content=campo_note,
            actions=[
                ft.TextButton("Annulla", on_click=lambda e: self._chiudi()),
                ft.ElevatedButton("Salva", on_click=salva_note),
            ]
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _chiudi(self):
        self.dialog.open = False
        self.page.update()

class TabellaOrdini:
    def __init__(
        self,
        ordini: list,
        on_elimina=None,
        on_visualizza_dettagli=None,
        on_elimina_filtro=None,
        magazzino_db=None,
        tipo_operazione="scarica",  # o "carica"
        ordini_db=None,              # 🔄 DB necessario per aggiornare applicato
        page=None
    ):
        self.ordini = ordini
        self.on_elimina = on_elimina
        self.on_visualizza_dettagli = on_visualizza_dettagli
        self.on_elimina_filtro = on_elimina_filtro
        self.magazzino_db = magazzino_db
        self.tipo_operazione = tipo_operazione
        self.ordini_db = ordini_db
        self.page = page
        self.tabella = self._costruisci_tabella()

    def _costruisci_tabella(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Codice Ordine")),
                ft.DataColumn(label=ft.Text("Data e Ora")),
                ft.DataColumn(label=ft.Text("Azioni")),
            ],
            rows=[
                self._crea_riga(index, ordine)
                for index, ordine in enumerate(self.ordini)
            ],
            data_row_min_height=50,
            heading_row_height=60,
        )

    def _mostra_popup(self, messaggio):
        if not self.page:
            print("[⚠️] Errore: self.page non è stato fornito. Messaggio non mostrato.")
            return

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Errore"),
            content=ft.Text(messaggio),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._chiudi_popup(dialog))
            ],
        )

        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)

        dialog.open = True
        self.page.update()

    def _chiudi_popup(self, dialog):
        dialog.open = False
        self.page.update()

    def _crea_riga(self, index, ordine):
        is_applicato = ordine.applicato

        btn_visualizza = ft.ElevatedButton(
            text="Visualizza Prodotti",
            disabled=is_applicato,
            on_click=lambda e: self.on_visualizza_dettagli(ordine) if self.on_visualizza_dettagli else None,
        )
        tooltip = "Ordine già applicato – non eliminabile" if ordine.applicato else "Elimina ordine"


        btn_elimina = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="red",
            tooltip=tooltip,
            disabled=ordine.applicato,
            on_click=lambda e: self._elimina_ordine(ordine)
        )

        btn_applica = ft.ElevatedButton(
            text="Annulla Modifica" if is_applicato else "Applica al Magazzino",
            color="white",
            bgcolor="#4CAF50" if not is_applicato else "#9E9E9E",
            on_click=lambda e: self._applica_o_annulla(ordine)
        )

        btn_note = ft.ElevatedButton(
            text="Note",
            on_click=lambda e: self._apri_finestra_note(e, ordine),
        )


        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(ordine.codice_ordine)),
                ft.DataCell(ft.Text(ordine.timestamp.strftime("%Y-%m-%d %H:%M"))),
                ft.DataCell(ft.Row([btn_visualizza, btn_elimina, btn_applica,btn_note])),
            ],
            color=ft.Colors.GREEN_100 if is_applicato else None  # sfondo verde se applicato
        )

    def _apri_finestra_note(self, e, ordine):
        form = FormNoteOrdine(ordine, self.ordini_db, e.page)
        form.mostra_form()

    def _applica_o_annulla(self, ordine):
        if ordine.applicato:
            # Annulla
            
            for p in ordine.prodotti:
                if self.tipo_operazione == "scarica":
                    self.magazzino_db.aggiungi_o_incrementa(p)
                else:
                    self.magazzino_db.scarica_prodotto(p)
            ordine.applicato = False
            if self.ordini_db:
                self.ordini_db.set_applicato(ordine.id, False)

        else:
            # Applica (scarica o carica in blocco solo se TUTTO va bene)
            success = True
            error_msg = ""

            if self.tipo_operazione == "scarica":
                # Fase 1: verifica
                for p in ordine.prodotti:
                    if not self.magazzino_db.verifica_disponibilita(p):
                        success = False
                        error_msg += f"❌ {p.nome} (taglia {p.taglia}) non disponibile o quantità insufficiente\n"

                if success:
                    # Fase 2: esegui
                    for p in ordine.prodotti:
                        self.magazzino_db.scarica_prodotto(p)  
                    ordine.applicato = True
                    if self.ordini_db:
                        self.ordini_db.set_applicato(ordine.id, True)
                else:
                    error_msg+= "L'ordine non è stato scaricato dal magazzino\n Risolvi i conflitti mostrati sopra"
                    self._mostra_popup(error_msg)
                    return
            else:
                # Caricamento sempre possibile
                for p in ordine.prodotti:
                    self.magazzino_db.aggiungi_o_incrementa(p)
                ordine.applicato = True
                if self.ordini_db:
                    self.ordini_db.set_applicato(ordine.id, True)

        self.aggiorna()


    def _elimina_ordine(self, ordine):
        self.ordini.remove(ordine)
        if self.on_elimina:
            self.on_elimina(ordine)
        if self.on_elimina_filtro:
            self.on_elimina_filtro(ordine)
        self.aggiorna()

    def aggiorna(self):
        self.tabella.rows = [
            self._crea_riga(index, ordine)
            for index, ordine in enumerate(self.ordini)
        ]
        self.tabella.update()

    def aggiungi_ordine(self, ordine):
        self.ordini.append(ordine)
        self.tabella.rows.append(self._crea_riga(len(self.ordini) - 1, ordine))
        self.tabella.update()

    def get_widget(self):
        return ft.Container(
            content=self.tabella,
            padding=20,
            alignment=ft.alignment.center,
            expand=True
        )


class FormInserimentoOrdine:
    def __init__(self, on_ordine_creato_gui, on_ordine_creato_db,on_ordine_creato_filtro):
        self.on_ordine_creato_gui = on_ordine_creato_gui
        self.on_ordine_creato_db = on_ordine_creato_db
        self.on_ordine_creato_filtro = on_ordine_creato_filtro
        self.dialog = None

    def mostra_form(self, page):
        codice = ft.TextField(label="Codice Ordine", width=200)
        data_ora = ft.TextField(
            label="Data e Ora (YYYY-MM-DD HH:MM)", width=200,
            hint_text="Lascia vuoto per ora automatica"
        )

        def crea_ordine(e):
            codice_val = codice.value.strip()
            ora_val = data_ora.value.strip()
            if not codice_val:
                codice.error_text = "Codice obbligatorio"
                codice.update()
                return

            from datetime import datetime
            try:
                timestamp = datetime.strptime(ora_val, "%Y-%m-%d %H:%M") if ora_val else datetime.now()
                ordine = Ordine(codice_ordine=codice_val, timestamp=timestamp, prodotti=[])

                if self.on_ordine_creato_db: #ordine salvato su db
                    self.on_ordine_creato_db(ordine)
                if self.on_ordine_creato_gui: #crea la riga sungui
                    self.on_ordine_creato_gui(ordine)
                if self.on_ordine_creato_filtro: #aggiorna tabella filtro
                    self.on_ordine_creato_filtro(ordine)

                self.dialog.open = False
                page.update()

            except Exception as ex:
                print(ex)
                data_ora.error_text = f"Data non valida: {ex}"
                data_ora.update()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Inserisci Nuovo Ordine"),
            content=ft.Column(controls=[codice, data_ora], tight=True),
            actions=[
                ft.TextButton("Annulla", on_click=lambda e: self._chiudi_dialog(page)),
                ft.ElevatedButton("Crea", on_click=crea_ordine),
            ]
        )
        if self.dialog not in page.overlay:
            page.overlay.append(self.dialog)

        self.dialog.open = True
        page.update()

    def _chiudi_dialog(self, page):
        self.dialog.open = False
        page.update()

class BoxFiltroOrdini:
    def __init__(self, tabella_ordini: TabellaOrdini):
        self.tabella_ordini = tabella_ordini
        self.ordini_originali = list(tabella_ordini.ordini)

        self.filtro_codice = ft.TextField(label="Codice contiene", width=150)
        self.bottone_filtra = ft.ElevatedButton("Applica",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=self._applica_filtro)
        self.bottone_reset = ft.TextButton("Reset", on_click=self._reset_filtro)
        self.titolo = ft.Text("Filtro",size = 30,  color=ft.Colors.BLUE_900)

        self.container = ft.Row(
            controls=[
                self.titolo,
                self.filtro_codice,
                self.bottone_filtra,
                self.bottone_reset
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _applica_filtro(self, e):
        codice = self.filtro_codice.value.strip().lower()
        print(list(self.ordini_originali))
        filtrati = [
            o for o in self.ordini_originali
            if codice in o.codice_ordine.lower()
        ]
        self.tabella_ordini.ordini = filtrati
        self.tabella_ordini.aggiorna()
        self.tabella_ordini.tabella.update()

    def _reset_filtro(self, e):
        self.filtro_codice.value = ""
        self.tabella_ordini.ordini = list(self.ordini_originali)
        self.tabella_ordini.aggiorna()
        self.filtro_codice.update()

    def aggiorna_tabella(self, ordine: Ordine):
        self.ordini_originali.append(ordine)

    def elimina_ordine(self, ordine: Ordine):
        if ordine in self.ordini_originali:
            self.ordini_originali.remove(ordine)

    def get_widget(self):
        return self.container


