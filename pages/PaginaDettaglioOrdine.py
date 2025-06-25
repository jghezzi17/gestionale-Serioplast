import flet as ft
from functools import partial
from utils.OrdiniPostgresDB import OrdiniDB
from utils.ClassiOrdini import Ordine
from utils.ClassiProdotti import Prodotto, TabellaProdotti,FormInserimentoProdotto, BoxFiltro

def pagina_dettaglio_ordine(page: ft.Page, ordine: Ordine, ordini_DB : OrdiniDB):

    def on_close(e):
        page.window.close()
        
    #devo mostrare l'ordine
    prodotti = ordini_DB.get_prodotti_per_ordine(ordine.id)

    # Crea callback parziali con ordine.id già "iniettato"
    aggiorna_prodotto_cb = partial(ordini_DB.aggiorna_prodotto_ordine, ordine.id)
    elimina_prodotto_cb = partial(ordini_DB.elimina_prodotto_ordine, ordine.id)

    tabella = TabellaProdotti(
        prodotti,
        on_modifica=aggiorna_prodotto_cb,
        on_elimina_db=elimina_prodotto_cb,
    )
    
    filtro = BoxFiltro(tabella)
    tabella.on_elimina_filtro = filtro.elimina_prodotto

    aggiungi_prodotto = partial(ordini_DB.aggiungi_prodotto_ordine, ordine.id)
   
    form = FormInserimentoProdotto(
      tabella.aggiungi_prodotto,
      aggiungi_prodotto,
      filtro.aggiorna_tabella
      )
    print(f"L'ordine ID è{ordine.id}")
    print("FILTRO WIDGET:", filtro.get_widget())
    print("TABELLA WIDGET:", tabella.get_widget())

    if page.route == f"/ordiniSerio/{ordine.id}":
        page.views.append(
            ft.View(
                f"/ordiniSerio/{ordine.id}",
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"Ordine ID: {ordine.codice_ordine}",
                                            size=50,
                                            color="Blue",
                                            text_align=ft.TextAlign.CENTER,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # centra il contenuto orizzontalmente
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton("Indietro",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/ordSerio")),
                                        ft.ElevatedButton("Aggiungi Prodotto",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: form.mostra_form(page)),
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
                                    ft.ElevatedButton("Esci", on_click=on_close)
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
        page.update()


    elif page.route == f"/ordiniLuma/{ordine.id}":     
        page.views.append(
            ft.View(
                f"/ordiniLuma/{ordine.id}",
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"Ordine ID: {ordine.codice_ordine}",
                                            size=50,
                                            color="Blue",
                                            text_align=ft.TextAlign.CENTER,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # centra il contenuto orizzontalmente
                                ),
                                filtro.get_widget(),
                                ft.Container(
                                    content=tabella.get_widget(),
                                    expand=True,     # 💡 tabella si espande
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton("Indietro",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/ordLuma")),
                                        ft.ElevatedButton("Aggiungi Prodotto",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: form.mostra_form(page)),
                                                                        ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20,
                                ),
                                ft.Row(
                                controls=[
                                    ft.ElevatedButton("Esci", on_click=on_close)
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
        page.update()
