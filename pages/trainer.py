import flet as ft


def view(page: ft.Page) -> ft.View:
    page.title = "Entrenamiento | Traductor de Señas"
    
    title = ft.Text("Entrenamiento", size=26, weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("Unidades Tecnológicas de Santander", size=14, opacity=0.7)

    content = [
        ft.Container(
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        tooltip="Volver",
                        on_click=lambda _: page.go("/"),
                    ),
                    ft.Image(
                        src="assets/img/favicon.png",
                        width=50,
                        height=50,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Container(width=10),
                    ft.Column(
                        [title, subtitle],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            margin=ft.margin.only(left=30, top=30, bottom=10),
        ),
    ]

    return ft.View(
        "/translator",
        controls=content,
        padding=0,
        spacing=0,
    )
