
from nicegui import ui
from seccion_fingerprinting import build_seccion_fingerprinting
from seccion_trilateracion import build_seccion_trilateracion

ui.page_title('Bluetooth Indoor Positioning')

with ui.header().classes('items-center justify-between'):
    ui.label('Bluetooth Indoor Positioning').classes('text-2xl font-bold')

with ui.tabs().classes('w-full') as tabs:
    fingerprinting = ui.tab('Fingerprinting')
    trilateracion = ui.tab('Trilateración')

with ui.tab_panels(tabs, value=fingerprinting).classes('w-full'):
    with ui.tab_panel(fingerprinting):
        build_seccion_fingerprinting()


    with ui.tab_panel(trilateracion):
        build_seccion_trilateracion()
ui.run()
