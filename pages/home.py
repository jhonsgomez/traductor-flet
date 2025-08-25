import flet as ft


def view(page: ft.Page) -> ft.View:
    page.title = "Inicio | Traductor de Señas"

    title = ft.Text(
        "Bienvenido al Traductor de Señas",
        size=28,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    subtitle = ft.Text(
        "Convierte tus gestos en palabras con inteligencia artificial.",
        size=16,
        opacity=0.8,
        text_align=ft.TextAlign.CENTER,
    )

    logo = ft.Container(
        content=ft.Image(
            src="assets/img/logo.png",
            width=260,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        ),
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        padding=10,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            blur_radius=16,
            color=ft.colors.BLACK26,
            spread_radius=2,
            offset=ft.Offset(0, 4),
        ),
        width=310,
    )

    translator_btn = ft.ElevatedButton(
        content=ft.Column(
            [
                ft.Icon(ft.icons.TRANSLATE, size=32),
                ft.Text("Ir al Traductor"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
        ),
        on_click=lambda _: page.go("/translator"),
    )

    trainer_btn = ft.ElevatedButton(
        content=ft.Column(
            [
                ft.Icon(ft.icons.SCHOOL, size=32),
                ft.Text("Entrenar modelo"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20,
        ),
        on_click=lambda _: page.go("/trainer"),
    )

    return ft.View(
        "/",
        [
            ft.Column(
                [
                    logo,
                    title,
                    subtitle,
                    ft.Container(height=30),
                    ft.Row(
                        [
                            translator_btn,
                            trainer_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            ),
            ft.Container(
                ft.Text(
                    "© 2025 Unidades Tecnológicas de Santander",
                    size=12,
                    opacity=0.6,
                    text_align=ft.TextAlign.CENTER,
                ),
                margin=ft.margin.only(bottom=10),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
