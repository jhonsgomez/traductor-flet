import flet as ft
import threading
import time
import mediapipe as mp
import cv2
import numpy as np

from utils import cv_utils, model_utils
from pathlib import Path


def view(page: ft.Page) -> ft.View:
    page.title = "Traductor | Traductor de Señas"

    # Estado compartido
    state = {
        "running": False,
        "thread": None,
        "cap": None,
        "hands": None,
        "last_frame": None,
        "labels": {0: "Hola", 1: "Si", 2: "Te quiero"},
        "model": None,
        "device_index": 0,
    }

    # UI Controls
    title = ft.Text("Traductor de Señas", size=26, weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("Unidades Tecnológicas de Santander", size=14, opacity=0.7)

    img = ft.Image(
        width=850,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(16),
        src="./assets/img/placeholder.jpg",
    )
    prediction_txt = ft.Text("—", size=30, weight=ft.FontWeight.BOLD)
    status_txt = ft.Text("Estado: detenido", size=12, opacity=0.8)
    fps_txt = ft.Text("FPS: —", size=12, opacity=0.8)

    draw_landmarks = ft.Switch(label="Dibujar marcas", value=True)

    # Selector de cámara (0..3 por defecto)
    device_dd = ft.Dropdown(
        width=200,
        label="Cámara",
        options=[ft.dropdown.Option(f"Dispositivo #{str(i)}") for i in range(4)],
        value="0",
    )

    start_btn = ft.ElevatedButton("Iniciar", icon=ft.icons.PLAY_ARROW)
    stop_btn = ft.OutlinedButton("Detener", icon=ft.icons.STOP, disabled=True)

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
        ft.Container(
            ft.Row(
                [device_dd, draw_landmarks, start_btn, stop_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=20, bottom=10),
        ),
        ft.Container(
            ft.Row(
                [
                    ft.Chip(label=ft.Text("Predicción:")),
                    prediction_txt,
                    ft.Container(width=20),
                    status_txt,
                    ft.Container(width=20),
                    fps_txt,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=10, bottom=10),
        ),
        ft.Container(
            ft.Row([img], alignment=ft.MainAxisAlignment.CENTER),
            margin=ft.margin.only(top=10),
        ),
    ]

    # ---------------------------
    # Inicialización de modelo y MediaPipe
    # ---------------------------
    model_path = Path("./modelo/modelo.p")
    if model_path.exists():
        try:
            state["model"] = model_utils.load_model(str(model_path))
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error cargando modelo: {e}"), open=True
            )
    else:
        page.snack_bar = ft.SnackBar(
            ft.Text(
                "No se encontró ./modelo/modelo.p. La app iniciará sin predicción."
            ),
            open=True,
        )

    mp_hands = mp.solutions.hands
    state["hands"] = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1,
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    # ---------------------------
    # Lógica de captura en hilo
    # ---------------------------
    def open_camera(index: int) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(index)
        # Resolución moderada para buen rendimiento
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        return cap

    def predict_from_landmarks(hand_landmarks, W: int, H: int):
        x_, y_, data_aux = [], [], []
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            x_.append(x)
            y_.append(y)
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x - min(x_))
            data_aux.append(y - min(y_))
        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10
        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10
        return np.asarray(data_aux), (x1, y1, x2, y2)

    def capture_loop():
        nonlocal img
        state["running"] = True
        status_txt.value = "Estado: Ejecutando"
        page.update()

        # Abrir cámara
        try:
            state["cap"] = open_camera(state["device_index"])
        except Exception as e:
            status_txt.value = f"Error abriendo cámara: {e}"
            state["running"] = False
            page.update()
            return

        cap = state["cap"]
        if not cap or not cap.isOpened():
            status_txt.value = "No se pudo abrir la cámara (índice no válido)."
            state["running"] = False
            page.update()
            return

        last_sec = time.time()
        frames = 0
        predicted_character = "—"

        while state["running"]:
            ok, frame = cap.read()
            if not ok:
                continue

            # Espejo
            frame = cv2.flip(frame, 1)
            H, W, _ = frame.shape

            # MediaPipe procesa en RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = state["hands"].process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if draw_landmarks.value:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_styles.get_default_hand_landmarks_style(),
                            mp_styles.get_default_hand_connections_style(),
                        )

                # Tomamos la primera mano para predecir
                hand_landmarks = results.multi_hand_landmarks[0]
                data_vec, (x1, y1, x2, y2) = predict_from_landmarks(
                    hand_landmarks, W, H
                )

                if state["model"] is not None:
                    try:
                        pred = state["model"].predict([data_vec])
                        predicted_character = state["labels"].get(
                            int(pred[0]), str(pred[0])
                        )
                    except Exception as e:
                        predicted_character = f"Error pred: {e}"

                # Caja + texto
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 3)
                cv2.putText(
                    frame,
                    predicted_character,
                    (max(x1, 0), max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.1,
                    (0, 0, 0),
                    3,
                    cv2.LINE_AA,
                )

                prediction_txt.value = predicted_character
            else:
                prediction_txt.value = "—"

            # Mostrar en Flet
            img.src_base64 = cv_utils.bgr_frame_to_base64(frame, quality=80)
            page.update()

            # FPS
            frames += 1
            now = time.time()
            if now - last_sec >= 1.0:
                fps_txt.value = f"FPS: {frames}"
                frames = 0
                last_sec = now

        # Al salir del bucle
        if state["cap"] is not None:
            try:
                state["cap"].release()
            except Exception:
                pass
            state["cap"] = None
        status_txt.value = "Estado: detenido"
        fps_txt.value = "FPS: —"
        page.update()

    # ---------------------------
    # Handlers UI
    # ---------------------------
    def start(_):
        if state["running"]:
            return
        # Tomar índice cámara
        try:
            state["device_index"] = int(device_dd.value)
        except Exception:
            state["device_index"] = 0
        start_btn.disabled = True
        stop_btn.disabled = False
        page.update()
        state["thread"] = threading.Thread(target=capture_loop, daemon=True)
        state["thread"].start()

    def stop(_):
        if not state["running"]:
            return
        stop_btn.disabled = True
        state["running"] = False
        page.update()
        # Esperar al hilo
        th = state.get("thread")
        if th and th.is_alive():
            th.join(timeout=2)
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    def on_disconnect(_):
        try:
            state["running"] = False
            if state["cap"] is not None:
                state["cap"].release()
        except Exception:
            pass

    start_btn.on_click = start
    stop_btn.on_click = stop
    page.on_disconnect = on_disconnect

    return ft.View(
        "/translator",
        controls=content,
        padding=0,
        spacing=0,
    )
