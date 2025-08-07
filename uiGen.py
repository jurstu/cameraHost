from nicegui import ui, app
from fastapi.responses import Response
import time
import threading
import numpy as np
import cv2

from camera import Camera

class UiGen:
    def __init__(self):
        self.controls = {}
        self.resolution = [1280, 720]
        self.lastImage = np.empty((self.resolution[1], self.resolution[0], 3))
        self.lastImage[:] = 255
        self.spawnGui()
        
    def run(self):
        self.t = threading.Thread(target=self.host, daemon=True)
        self.t.start()

    def host(self):
        ui.run(reload=False, show=False)

    def newFrame(self, image):
        self.lastImage = image

    def spawnGui(self):
        dark = ui.dark_mode()
        dark.enable()        
        
        with ui.card() as card:
            with ui.row():
                style = f"width: {self.resolution[0]}px; height: {self.resolution[1]}px; object-fit: contain;"
                self.controls["image"] = ui.interactive_image().classes("border").style(style)  # , size=(self.resolution[0], self.resolution[1]))#.classes('w-full h-full')
            with ui.row().classes("w-full"):
                pass
        ui.timer(interval=0.03, callback=lambda: self.controls["image"].set_source(f'/video/frame?{time.time()}'))

        @app.get("/video/frame", response_class=Response)
        def grabVideoFrame() -> Response:
            _, raw = cv2.imencode(".jpg", self.lastImage)
            return Response(content=raw.tobytes(), media_type="image/jpg")


if __name__ == "__main__":
    ug = UiGen()
    ug.run()

    cam = Camera(0, [1280, 720, 30], 0, 0)
    cam.register_observer(ug.newFrame)


    i = 0
    while(1):
        time.sleep(1)
        i+=1