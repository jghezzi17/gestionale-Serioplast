import flet as ft
from utils.ClassiProdotti import Prodotto, TabellaProdotti,FormInserimentoProdotto, BoxFiltro
from utils.MagazzinoPostgresDB import MagazzinoDB
from pages.utilsPagine import pagina_prodotti_quasi_zero, pagina_prodotti_a_zero

def pagina_magazzino(page: ft.Page):
   
   def on_close(e):
        page.window.close()
      
   def apri_pagina_prodotti_a_zero(e):
         print ("sto aprendo pagina dei prodotti a zero")
         page.go("/magazzino/proZero")
         print (page.route)
         if page.route == "/magazzino/proZero":
            pagina_prodotti_a_zero(page,magazzino_db)
            
   def apri_pagina_prodotti_quasi_zero(e):
         print ("sto aprendo pagina dei prodotti prossimi allo zero")
         page.go("/magazzino/proQuasiZero")
         print (page.route)
         if page.route == "/magazzino/proQuasiZero":
            pagina_prodotti_quasi_zero(page,magazzino_db,15)

   db_config = {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'magazzino_db',
        'user': 'jacopoghezzi',
        'password': 'Atalanta123.'
    }

   def aggiungi_prodotto_con_id(prodotto: Prodotto):
       print("sto aggiungendo un prodotto")
       prodotto.id = magazzino_db.aggiungi_o_incrementa(prodotto)
       print("il prodotto aggiunto è")
       print(prodotto.nome)
       print(prodotto.taglia)
       print(f"il prodotto id è: {prodotto.id}")
       # Verifica se prodotto già esiste nella tabella
       for p in tabella.prodotti:
           if p.nome == prodotto.nome and p.taglia == prodotto.taglia:
               p.quantita += prodotto.quantita
               tabella.aggiorna()
               return

       # Se è nuovo
       tabella.prodotti.append(prodotto)
       tabella.aggiorna()
   
   magazzino_db = MagazzinoDB(db_config)
   
   prodotti = magazzino_db.get_tutti_prodotti()
   
   tabella = TabellaProdotti(
      prodotti,
      on_modifica = magazzino_db.aggiorna_prodotto,
      on_elimina_db = magazzino_db.elimina_prodotto,
      )
   
   filtro = BoxFiltro(tabella)
   
   form = FormInserimentoProdotto(aggiungi_prodotto_con_id)     
   
   magazzino_db.set_callbacks(
    on_elimina_prodotto_gui=tabella.elimina_prodotto
   )

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
                                ft.ElevatedButton("Torna alla Home",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE,on_click=lambda e: page.go("/")),
                                ft.ElevatedButton("Aggiungi Prodotto",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: form.mostra_form(page)),
                                ft.ElevatedButton("Aggiungi Ordine Serioplast",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/ordSerio")),
                                ft.ElevatedButton("Aggiungi Ordine Lumachina",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/ordLuma")),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                            ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton("Prodotti quasi finiti",on_click= apri_pagina_prodotti_quasi_zero),
                                ft.ElevatedButton("Prodotti non in Magazzino", on_click= apri_pagina_prodotti_a_zero),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        filtro.get_widget(),
                        ft.Container(
                            content=tabella.get_widget(),
                            expand=True,     # 💡 tabella si espande
                        ),
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




