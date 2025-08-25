import flet as ft
from pages import home, translator, trainer


def main(page: ft.Page):
    page.title = "Inicio | Traductor de Señas"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 750

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        if page.route == "/":
            page.views.append(home.view(page))
        elif page.route == "/translator":
            page.views.append(translator.view(page))
        elif page.route == "/trainer":
            page.views.append(trainer.view(page))
        else:
            page.views.append(ft.View("/404", [ft.Text("Página no encontrada")]))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
