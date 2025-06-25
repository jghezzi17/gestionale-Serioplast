import flet as ft
from utils.ClassiProdotti import Prodotto, TabellaProdotti,FormInserimentoProdotto, BoxFiltro
from utils.MagazzinoPostgresDB import MagazzinoDB

def pagina_magazzino(page: ft.Page):
   
   def on_close(e):
        page.window.close()

   db_config = {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'magazzino_db',
        'user': 'jacopoghezzi',
        'password': 'Atalanta123.'
    }
     
   
   magazzino_db = MagazzinoDB(db_config)
   
   prodotti = magazzino_db.get_tutti_prodotti()
   
   tabella = TabellaProdotti(
      prodotti,
      on_modifica = magazzino_db.aggiorna_prodotto,
      on_elimina_db = magazzino_db.elimina_prodotto,
      
      )
   
   filtro = BoxFiltro(tabella)
   tabella.on_elimina_filtro = filtro.elimina_prodotto
   
   form = FormInserimentoProdotto(
      tabella.aggiungi_prodotto, #da sistemare, da cambiare in aggiungi_o_incrementa
      magazzino_db.aggiungi_o_incrementa,
      filtro.aggiorna_tabella
      )
   
   magazzino_db.set_callbacks(
    on_elimina_prodotto_gui=tabella.elimina_prodotto,
    on_elimina_filtro=filtro.elimina_prodotto
   )
  
   """
   page.views.append(
                ft.View(
                    "/magazzino",
                    [
                        ft.Text("Benvenuto nel Magazzino",
                            size= 50,
                            color = "Blue",
                            text_align = ft.TextAlign.CENTER),
                        filtro.get_widget(),
                        tabella.get_widget(),
                        ft.ElevatedButton("Torna alla Home ", on_click=lambda e: page.go("/")),
                        ft.ElevatedButton("Aggiungi Prodotto", on_click=lambda e: form.mostra_form(page)),
                        ft.ElevatedButton("Azzera database", on_click=lambda e: magazzino_db.svuota_tabella())
                    ]
                     )
                )"""

   page.views.append(
    ft.View(
        "/magazzino",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Magazzino",
                                    size=50,
                                    color="Blue",
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER  # centra il contenuto orizzontalmente
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton("Torna alla Home",on_click=lambda e: page.go("/")),
                                ft.ElevatedButton("Aggiungi Prodotto", on_click=lambda e: form.mostra_form(page)),
                                ft.ElevatedButton("Aggiungi Ordine Serioplast", on_click=lambda e: page.go("/ordSerio")),
                                ft.ElevatedButton("Aggiungi Ordine Lumachina", on_click=lambda e: page.go("/ordLuma")),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        ft.Container(
                            content=tabella.get_widget(),
                            expand=True,     # 💡 tabella si espande
                        ),
                        
                        filtro.get_widget(),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton("Esci",bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE, on_click=on_close)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        
                    ],
                    expand=True,  # 💡 importante per propagare l'espansione
                    spacing=20,
                ),
                expand=True,
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
)




