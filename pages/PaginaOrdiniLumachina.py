import flet as ft
from utils.OrdiniPostgresDB import OrdiniDB
from utils.ClassiOrdini import Ordine, TabellaOrdini, BoxFiltroOrdini, FormInserimentoOrdine
from utils.ClassiProdotti import Prodotto, TabellaProdotti,FormInserimentoProdotto, BoxFiltro
from pages.PaginaDettaglioOrdine import pagina_dettaglio_ordine
from utils.MagazzinoPostgresDB import MagazzinoDB


def pagina_ordiniLumachina(page: ft.Page):

     def on_close(e):
        page.window.close()

     def apri_dettaglio_ordine(ordine: Ordine):
          #il cambio pagina è gestito sempre nel main
         print ("l'ordine id è", ordine.id)
         page.go(f"/ordiniLuma/{ordine.id}")
         print (page.route)
         if page.route == f"/ordiniLuma/{ordine.id}":
            pagina_dettaglio_ordine(page, ordine, ordini_luma_DB)
            
     db_config_lumachina = {
         'host': '192.168.2.104',
         'port': 5432,
         'dbname': 'ordinilumachina',
         'user': 'postgres',
         'password': 'serioplast'
     }
     db_config_magazzino = {
         'host': '192.168.2.104',
         'port': 5432,
         'dbname': 'magazzino_db',
         'user': 'postgres',
         'password': 'serioplast'
     }

     magazzino_db = MagazzinoDB(db_config_magazzino)
     ordini_luma_DB = OrdiniDB(db_config_lumachina) #crea DB per ordini Serioplast
     ordini = ordini_luma_DB.get_tutti_ordini() # recupera gli ordini dal database
     tabella_ordini_luma = TabellaOrdini(
          ordini,
          on_elimina = ordini_luma_DB.elimina_ordine, #elima prodotto dal DB qunado si preme il tasto elimina
          on_visualizza_dettagli = apri_dettaglio_ordine,
          magazzino_db=magazzino_db,
          tipo_operazione="carica",
          ordini_db=ordini_luma_DB,
          page=page
          )
     filtro = BoxFiltroOrdini(tabella_ordini_luma) # creazione del filtro passando gli ordini della tabella
    # tabella.on_elimina_filtro = filtro.elimina_prodotto da aggiungere per aggiornare il filtro quando si aggiunge qualcosa

     form = FormInserimentoOrdine(
           tabella_ordini_luma.aggiungi_ordine,
           ordini_luma_DB.aggiungi_ordine,
           filtro.aggiorna_tabella
           )
     
     page.views.append(
                ft.View(
                    "/ordLuma",
                    controls = [
                         ft.Container(
                              content = ft.Column(
                                   controls = [
                                        ft.Row(
                                             controls = [
                                                  ft.Text(
                                                       "Ordini Lumachina",
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
                                           content=tabella_ordini_luma.get_widget(),
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
                              
                    
                     
             
