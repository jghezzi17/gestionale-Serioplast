import flet as ft
from pages import PaginaMagazzino, PaginaOrdiniLumachina, PaginaOrdiniSerioplast
from pages.PaginaDettaglioOrdine import pagina_dettaglio_ordine



def main(page: ft.Page):         
     
    page.title = "Gestionale Serioplast"

    def on_close(e):
        page.window.close()
        
    def route_change(e):
        page.views.clear()#pulisce la lista di oggetti View
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Column(
                            controls =[ ft.Text("Gestionale Serioplast",
                                        size= 80,
                                        color = "green",
                                        text_align = ft.TextAlign.CENTER),
                                        ft.Row(
                                            controls= [ ft.ElevatedButton("Magazzino ", on_click=lambda e: page.go("/magazzino"),width=180,height=60),
                                                        ft.ElevatedButton("Ordini Serioplast ", on_click=lambda e: page.go("/ordSerio"),width=180,height=60),
                                                        ft.ElevatedButton("Ordini Lumachina ", on_click=lambda e: page.go("/ordLuma"),width=180,height=60),
                                                      ],
                                            alignment=ft.MainAxisAlignment.CENTER

                                        )
                                        
                                       ],
                            alignment=ft.MainAxisAlignment.CENTER,  # allineamento verticale
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # allineamento orizzontale
                            expand = True
                            ),
                        ft.ElevatedButton("Esci",bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=lambda e: on_close(e))

                    ]
                     )
                )
                
        elif page.route == "/magazzino":
            PaginaMagazzino.pagina_magazzino(page)
            
        elif page.route == "/ordLuma":
            PaginaOrdiniLumachina.pagina_ordiniLumachina(page)
            
        elif page.route == "/ordSerio":
            PaginaOrdiniSerioplast.pagina_ordiniSerioplast(page)
            

            
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

    
ft.app(target=main)  # Avvia l'app desktop

