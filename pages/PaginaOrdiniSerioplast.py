import flet as ft
from utils.OrdiniPostgresDB import OrdiniDB
from utils.ClassiOrdini import Ordine, TabellaOrdini, BoxFiltroOrdini, FormInserimentoOrdine
from utils.ClassiProdotti import Prodotto, TabellaProdotti,FormInserimentoProdotto, BoxFiltro
from pages.PaginaDettaglioOrdine import pagina_dettaglio_ordine
from utils.MagazzinoPostgresDB import MagazzinoDB




def pagina_ordiniSerioplast(page: ft.Page):

     def on_close(e):
        page.window.close()

     def apri_dettaglio_ordine(ordine: Ordine):
          #il cambio pagina è gestito sempre nel main
         print ("l'ordine id è", ordine.id)
         page.go(f"/ordiniSerio/{ordine.id}")
         print (page.route)
         if page.route == f"/ordiniSerio/{ordine.id}":
            pagina_dettaglio_ordine(page, ordine, ordini_serio_DB)

     # Configurazione per la connessione PostgreSQL
     db_config_serioplast = {
         'host': 'localhost',
         'port': 5432,
         'dbname': 'ordiniserioplast',
         'user': 'postgres',
         'password': 'serioplast'
     }

     db_config_magazzino = {
         'host': 'localhost',
         'port': 5432,
         'dbname': 'magazzino_db',
         'user': 'postgres',
         'password': 'serioplast'
     }

     magazzino_db = MagazzinoDB(db_config_magazzino)# recupera magazzino DB
     ordini_serio_DB = OrdiniDB(db_config_serioplast) #crea DB per ordini Serioplast
     ordini = ordini_serio_DB.get_tutti_ordini() # recupera gli ordini dal database
     tabella_ordini_serio = TabellaOrdini(
          ordini,
          on_elimina = ordini_serio_DB.elimina_ordine, #elima prodotto dal DB qunado si preme il tasto elimina
          on_visualizza_dettagli = apri_dettaglio_ordine,
          magazzino_db=magazzino_db,
          tipo_operazione="scarica",  # oppure "carica" per Lumachina
          ordini_db = ordini_serio_DB,
          page = page
          )
     filtro = BoxFiltroOrdini(tabella_ordini_serio) # creazione del filtro passando gli ordini della tabella
     tabella_ordini_serio.on_elimina_filtro = filtro.elimina_ordine # da aggiungere per aggiornare il filtro quando si aggiunge qualcosa

     form = FormInserimentoOrdine(
           tabella_ordini_serio.aggiungi_ordine,
           ordini_serio_DB.aggiungi_ordine,
           filtro.aggiorna_tabella
           )
     
     page.views.append(
                ft.View(
                    "/ordSerio",
                    controls = [
                         ft.Container(
                              content = ft.Column(
                                   controls = [
                                        ft.Row(
                                             controls = [
                                                  ft.Text(
                                                       "Ordini Serioplast",
                                                       size= 50,
                                                       color = "Blue",
                                                       text_align = ft.TextAlign.CENTER,
                                                       )
                                                  ],
                                             alignment = ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Row(
                                             controls = [
                                                  ft.ElevatedButton("Torna alla Home",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/")),
                                                  ft.ElevatedButton("Magazzino",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/magazzino")),
                                                  ft.ElevatedButton("Aggiungi Ordine",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: form.mostra_form(page)),
                                                  
                                             ],
                                             alignment = ft.MainAxisAlignment.CENTER,
                                             spacing = 20,
                                        ),
                                        filtro.get_widget(),
                                        ft.Container(
                                           content=tabella_ordini_serio.get_widget(),
                                           expand=True,     # 💡 tabella si espande
                                        ),
                                        ft.Row(
                                           controls=[
                                               ft.ElevatedButton("Esci",bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE, on_click=on_close)
                                           ],
                                           alignment=ft.MainAxisAlignment.START,
                                       ),
                                   ],
                                   expand = True,
                                   spacing = 20,
                              ),
                              expand = True,
                              padding = 20,
                         ),
                    ],
                    scroll = ft.ScrollMode.AUTO,
                    
               )
          )
                              
                    
                     
             
