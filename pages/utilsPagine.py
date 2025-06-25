import flet as ft
from utils.MagazzinoPostgresDB import MagazzinoDB
from typing import Optional


def pagina_prodotti_quasi_zero(page: ft.Page, magazzino_db: MagazzinoDB, soglia: int = 15):
    def on_close(e):
        page.window.close()
        
    page.views.append(
            ft.View(
                "/magazzino/proZero",
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"Prodotti con meno di {soglia} unità in Magazzino ",
                                            size=50,
                                            color="Blue",
                                            text_align=ft.TextAlign.CENTER,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # centra il contenuto orizzontalmente
                                ),
                                
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=crea_tabella_prodotti_esauriti(magazzino_db,soglia),
                                            padding=20,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton("Indietro",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/magazzino")),                                                                        ],
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
        

def pagina_prodotti_a_zero(page: ft.Page, magazzino_db: MagazzinoDB):
    def on_close(e):
        page.window.close()
        
    page.views.append(
            ft.View(
                "/magazzino/proZero",
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Prodotti non presenti in Magazino",
                                            size=50,
                                            color="Blue",
                                            text_align=ft.TextAlign.CENTER,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # centra il contenuto orizzontalmente
                                ),
                                
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=crea_tabella_prodotti_finiti(magazzino_db),
                                            padding=20,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton("Indietro",bgcolor=ft.Colors.BLUE_900,color=ft.Colors.WHITE, on_click=lambda e: page.go("/magazzino")),                                                                        ],
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

def crea_tabella_prodotti_esauriti(magazzino_db,soglia) -> Optional[ft.Control]:
    prodotti = magazzino_db.get_tutti_prodotti()
    critici = [p for p in prodotti if p.quantita < soglia]

    if not critici:
        # Nessun prodotto esaurito
        return ft.Text(f"✅ Nessun prodotto ha quantità minore di {soglia}", color="green")

    # Creazione delle righe della tabella
    righe = [
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(p.nome)),
            ft.DataCell(ft.Text(p.taglia)),
            ft.DataCell(ft.Text(str(p.quantita))),
        ])
        for p in critici
    ]

    # Creazione della tabella
    tabella = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nome")),
            ft.DataColumn(label=ft.Text("Taglia")),
            ft.DataColumn(label=ft.Text("Quantità")),
        ],
        rows=righe
    )

    return tabella



def crea_tabella_prodotti_finiti(magazzino_db) -> Optional[ft.Control]:
    TAGLIE_VALIDE = ["XS","S","M","L","XL","XXL","XXXL"]
    PRODOTTI_VALIDI = ["T-shirt", "Pantaloni Uomo","Pantaloni Donna", "Pile","Felpe","Camice", "Camicie","Giacche","Scaldacollo","Cuffie"]

    # Recupera tutti i prodotti presenti in magazzino
    presenti = magazzino_db.get_tutti_prodotti()

    # Crea un dizionario per accesso rapido
    mappa_presenti = {
        (p.nome, p.taglia): p.quantita for p in presenti
    }

    # Trova combinazioni assenti o con quantità 0
    esauriti = []
    for nome in PRODOTTI_VALIDI:
        for taglia in TAGLIE_VALIDE:
            quantita = mappa_presenti.get((nome, taglia))
            if quantita is None or quantita == 0:
                esauriti.append((nome, taglia, quantita if quantita is not None else 0))

    if not esauriti:
        return ft.Text("✅ Nessun prodotto è esaurito o mancante.", color="green")

    # Ordina alfabeticamente
    esauriti.sort(key=lambda x: (x[0], x[1]))

    # Crea righe della tabella
    righe = [
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(nome)),
            ft.DataCell(ft.Text(taglia)),
            ft.DataCell(ft.Text(str(quantita))),
        ])
        for nome, taglia, quantita in esauriti
    ]

    return ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nome")),
            ft.DataColumn(label=ft.Text("Taglia")),
            ft.DataColumn(label=ft.Text("Quantità")),
        ],
        rows=righe
    )



