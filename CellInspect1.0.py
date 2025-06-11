import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import sys
import re
import main_sequence
import csv
from datetime import datetime

# Agregar el directorio al sys.path
sys.path.append("c:/scripts/")

# Importar la librería
import odcLib
serial=""
selected_order=""
import qrcode
from PIL import Image, ImageTk

def registrar_log(serial, operador, shop_order, pallet_id, resultado, defecto):
    log_file = "registro_inspeccion.csv"
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila = [fecha_hora, operador, shop_order, pallet_id, serial, resultado, defecto]
    existe = False
    try:
        with open(log_file, "r", newline="", encoding="utf-8") as f:
            existe = True
    except FileNotFoundError:
        pass
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["FechaHora", "Operador", "ShopOrder", "PalletID", "Serial", "Resultado", "Defecto"])
        writer.writerow(fila)

def show_qr_warning(msg, qr_data):
    # Crear ventana personalizada
    qr_win = tk.Toplevel(root)
    qr_win.title("Formato inválido")
    qr_win.geometry("350x400")
    qr_win.grab_set()  # Modal

    # Mensaje
    tk.Label(qr_win, text=msg, font=("Arial", 12), wraplength=320).pack(pady=10)

    # Generar QR
    qr_img = qrcode.make(qr_data)
    qr_img = qr_img.resize((200, 200))
    qr_photo = ImageTk.PhotoImage(qr_img)
    qr_label = tk.Label(qr_win, image=qr_photo)
    qr_label.image = qr_photo  # Mantener referencia
    qr_label.pack(pady=10)

    # Instrucción
    tk.Label(qr_win, text="Escanee el QR para continuar", font=("Arial", 12)).pack(pady=5)

    # Botón OK
    ok_button = tk.Button(qr_win, text="OK", font=("Arial", 12), command=qr_win.destroy)
    ok_button.pack(pady=10)
    ok_button.focus_set()  # El foco inicia en el botón OK

    # Entry oculto para capturar el escaneo del QR
    hidden_entry = tk.Entry(qr_win)
    hidden_entry.place(x=-100, y=-100)  # Fuera de la vista

    def on_qr_scan(event):
        if hidden_entry.get().strip().upper() == qr_data.upper():
            ok_button.invoke()  # Simula el click en OK

    hidden_entry.bind("<Return>", on_qr_scan)

    # Al abrir la ventana, el foco va al entry oculto
    hidden_entry.focus_set()

    # Esperar a que se cierre la ventana
    qr_win.wait_window()

def on_shop_order_selected(event):
    global selected_order  # Declarar selected_order como global
    selected_order = shop_order_menu.get()
    # Buscar la cantidad de unidades asociadas a la Shop Order seleccionada
    shop_orders_raw = odcLib.get_SO_BB(model='10-06527A-I3MS')
    for line in shop_orders_raw.replace("<br>", "\n").strip().split("\n"):
        order, quantity = line.split("|")
        if order == selected_order:
            shop_order_info_label.config(text=f"Shop Order: {selected_order}, Qty: {quantity}")
            break
    print(f"Shop Order seleccionado: {selected_order}")


# Modifica la función on_serial_entered para validar el uniqueId
def on_serial_entered(event):
    global serial, user,password
    serial = serial_entry.get()
    unique_id = uniqueid_value.get()
    print(f"Unique ID capturado: {unique_id}")
    print(f"Serial escaneado: {serial}")

    # Validar Unique ID: solo dígitos y 11 caracteres
    if not re.fullmatch(r"\d{11}", unique_id):
        messagebox.showwarning(
            "Formato inválido",
            "El Unique ID debe contener exactamente 11 dígitos numéricos.\nEjemplo: 10025246569"
        )
        return

    # Validar formato del serial
    if not re.fullmatch(r"K[A-Z0-9]{15}", serial):
        show_qr_warning(
        "El número de serie debe empezar con 'K' y tener 16 caracteres alfanuméricos.\nEjemplo: K1045D22P1002781",
        qr_data="OK"  # Puedes poner aquí el texto que tu lector QR espera
        )
        serial_entry.delete(0, tk.END)
        serial_entry.focus()
        return

    # Deshabilitar solo el entry del serial
    #serial_entry.config(state="disabled")

    # Ejecutar la secuencia principal, pasando unique_id si es necesario
    #user = "MESGATEWAY"
    #password = "02 01 10 14 04 1B 01 14 12 1C"
    result = main_sequence.main(serial, selected_order, user, password, unique_id)
    if result["status"] != "ok":
        messagebox.showerror("Error en secuencia", result["msg"])
        serial_entry.config(state="normal")
        serial_entry.delete(0, tk.END)
        serial_entry.focus()
        return

    messagebox.showinfo("Listo", "OLSU Pallet ID completado. Realice la inspección visual y seleccione PASA o FALLA.")

def on_capture_clicked():
    selected_status = status_var.get()
    defect_text = defect_entry.get()
    print(f"Estado: {selected_status}, Defecto: {defect_text}")

def on_pass_clicked():
    global user
    serial = serial_entry.get()
    #user = "MESGATEWAY"  # o el usuario que corresponda
    station = "QA_INSP"
    tester = "CMXLUNARPC"  # o el nombre de tester que corresponda

    # 1. Obtener el ticket
    ticket_response = odcLib.getTicket(serial)
    ticket = ticket_response.strip()  # Ajusta si necesitas extraer solo el número

    # 2. Enviar resultado PASS
    sendpass_response = odcLib.sendPass(ticket, serial, station, tester, user)
    if "success" in sendpass_response.lower():
        # 3. Procesar el ticket
        odcLib.processTicket(ticket)
        #messagebox.showinfo("Éxito", "Inspección registrada como PASA y ticket procesado.")
        show_qr_warning("Inspección registrada como PASA y ticket procesado.","OK")
        pallet_id=uniqueid_value.get(),
        registrar_log(serial, user, selected_order, pallet_id, "PASA", "")  # Registrar log
        serial_entry.delete(0, tk.END)
        serial_entry.focus()

    else:
        messagebox.showerror("Error", f"Error al registrar PASA: {sendpass_response}")


def on_fail_clicked():
    global user
    serial = serial_entry.get()
    station = "QA_INSP"
    tester = "CMXLUNARPC"

    # Ventana modal para seleccionar defecto
    def seleccionar_defecto():
        seleccionado = defect_var.get()
        if not seleccionado:
            messagebox.showwarning("Defecto requerido", "Debe seleccionar un defecto para continuar.", parent=defecto_win)
            return
        defecto_win.selected = seleccionado
        defecto_win.destroy()

    defecto_win = tk.Toplevel(root)
    defecto_win.title("Seleccionar Defecto")
    defecto_win.geometry("400x200")
    defecto_win.grab_set()  # Hace la ventana modal

    tk.Label(defecto_win, text="Seleccione el defecto:", font=("Arial", 12)).pack(pady=10)
    defect_var = tk.StringVar()
    defect_combo = ttk.Combobox(defecto_win, font=("Arial", 12), values=defectos, textvariable=defect_var, state="readonly", width=35)
    defect_combo.pack(pady=10)
    defect_combo.focus()

    tk.Button(defecto_win, text="Aceptar", font=("Arial", 12), command=seleccionar_defecto).pack(pady=10)

    defecto_win.selected = None
    defecto_win.wait_window()  # Espera hasta que la ventana se cierre

    failDetails = defecto_win.selected
    if not failDetails:
        return  # El usuario cerró la ventana o no seleccionó

    # Confirmar antes de enviar el resultado de falla
    if not messagebox.askyesno("Confirmar", "¿Está seguro que desea registrar este serial como FALLA?"):
        return

    # 1. Obtener el ticket
    ticket_response = odcLib.getTicket(serial)
    ticket = ticket_response.strip()  # Ajusta si necesitas extraer solo el número

    # 2. Enviar resultado FAIL
    pallet_id=uniqueid_value.get(),
    sendfail_response = odcLib.sendFail(ticket, serial, station, tester, user, failDetails, "INSPFAIL/inspfail")
    if "success" in sendfail_response.lower():
        # 3. Procesar el ticket
        odcLib.processTicket(ticket)
        #messagebox.showinfo("Éxito", "Inspección registrada como FALLA y ticket procesado.")
        show_qr_warning("Inspección registrada como FALLA y ticket procesado.","OK")
        registrar_log(serial, user, selected_order, pallet_id, "FALLA", failDetails)  # Registrar log
        serial_entry.delete(0, tk.END)
        serial_entry.focus()
    else:
        messagebox.showerror("Error", f"Error al registrar FALLA: {sendfail_response}")


def habilitar_botones_inspeccion():
    pasa_button.config(state="normal")
    falla_button.config(state="normal")

def deshabilitar_botones_inspeccion():
    pasa_button.config(state="disabled")
    falla_button.config(state="disabled")

# Obtener las opciones de Shop Order desde odcLib
shop_orders_raw = odcLib.get_SO_BB(model='10-06527A-I3MS')  # Suponiendo que devuelve una lista de órdenes
shop_orders = [line.split("|")[0] for line in shop_orders_raw.replace("<br>", "\n").strip().split("\n")]

# Crear la ventana principal
root = tk.Tk()
root.title("QA INSPEC")
root.geometry("500x500")  # Ajustar el tamaño para acomodar los nuevos elementos
root.resizable(False, False)

# Centrar la ventana en la pantalla
window_width = 500
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

# Cargar y mostrar el logo de Celestica (parte superior izquierda)
celestica_logo = Image.open("c:/scripts/CelLogo.png")  # Reemplaza con la ruta de tu logo
celestica_logo = celestica_logo.resize((100, 50), Image.Resampling.LANCZOS)
celestica_logo = ImageTk.PhotoImage(celestica_logo)
celestica_label = tk.Label(root, image=celestica_logo)
celestica_label.place(x=10, y=10)

# Cargar y mostrar el logo de Lunar (parte superior derecha)
lunar_logo = Image.open("c:/scripts/lunar.png")  # Reemplaza con la ruta de tu logo
lunar_logo = lunar_logo.resize((100, 50), Image.Resampling.LANCZOS)
lunar_logo = ImageTk.PhotoImage(lunar_logo)
lunar_label = tk.Label(root, image=lunar_logo)
lunar_label.place(x=390, y=10)

# Título centrado
title_label = tk.Label(root, text="QA INSPECTION", font=("Arial", 18, "bold"))
title_label.pack(pady=20)

# Frame para Shop Order label y combobox en la misma línea
shop_order_frame = tk.Frame(root)
shop_order_frame.pack(pady=10)

shop_order_label = tk.Label(shop_order_frame, text="Shop Order:", font=("Arial", 14))
shop_order_label.pack(side="left")

shop_order_menu = ttk.Combobox(shop_order_frame, font=("Arial", 14), state="readonly", width=17)
shop_order_menu["values"] = shop_orders  # Asignar las opciones obtenidas de odcLib
shop_order_menu.pack(side="left", padx=5)
shop_order_menu.bind("<<ComboboxSelected>>", on_shop_order_selected)

# Crear una etiqueta para mostrar la Shop Order seleccionada y la cantidad de unidades
shop_order_info_label = tk.Label(root, text="", font=("Arial", 10))
shop_order_info_label.pack(pady=5)

# Variable para almacenar el Unique ID
uniqueid_value = tk.StringVar(value="")

# Frame para colocar la etiqueta y el botón en la misma línea
uniqueid_frame = tk.Frame(root)
uniqueid_frame.pack(pady=10)

uniqueid_label = tk.Label(uniqueid_frame, text="Unique Id:", font=("Arial", 14))
uniqueid_label.pack(side="left")

uniqueid_display = tk.Label(uniqueid_frame, textvariable=uniqueid_value, font=("Arial", 14), width=18, relief="sunken", anchor="w")
uniqueid_display.pack(side="left", padx=5)

def pedir_pallet_id():
    new_id = simpledialog.askstring("Unique ID", "Ingrese el Unique ID (11 dígitos):", parent=root)
    if new_id is not None:
        # Tomar solo los últimos 11 dígitos numéricos
        digits = re.sub(r"\D", "", new_id)[-11:]
        if re.fullmatch(r"\d{11}", digits):
            uniqueid_value.set(digits)
            update_pallet_btn_label()
        else:
            messagebox.showwarning("Formato inválido", "El Unique ID debe contener al menos 11 dígitos numéricos.\nEjemplo: 10025246569")
            # Si quieres volver a pedirlo automáticamente, puedes llamar recursivamente:
            # pedir_pallet_id()

cambiar_pallet_btn = tk.Button(uniqueid_frame, text="Ingrese Unique ID", font=("Arial", 10), command=pedir_pallet_id)
cambiar_pallet_btn.pack(side="left", padx=5)

def update_pallet_btn_label(*args):
    if uniqueid_value.get().strip() == "":
        cambiar_pallet_btn.config(text="Ingrese Unique ID")
    else:
        cambiar_pallet_btn.config(text="Cambiar Unique ID")

uniqueid_value.trace_add("write", update_pallet_btn_label)

# Caja de texto para escanear el número de serie
serial_label = tk.Label(root, text="Serial:", font=("Arial", 14))
serial_label.pack(pady=10)

serial_entry = ttk.Entry(root, font=("Arial", 14))
serial_entry.pack(pady=10)
serial_entry.bind("<Return>", on_serial_entered)  # Detectar cuando se presiona Enter


# Crear un contenedor para los botones "PASA" y "FALLA"
status_frame = tk.Frame(root)
status_frame.pack(pady=10)

# Botón "PASA"
pasa_button = tk.Button(
    status_frame,
    text="PASA",
    font=("Arial", 12),
    width=20,
    height=2,
    command=on_pass_clicked,
    bg="#28a745",      # Verde
    fg="white",        # Texto blanco
    activebackground="#218838",  # Verde más oscuro al presionar
    activeforeground="white",
    state="active"
)
pasa_button.pack(side="left", padx=5)

# Botón "FALLA"
falla_button = tk.Button(
    status_frame,
    text="FALLA",
    font=("Arial", 12),
    width=20,
    height=2,
    command=on_fail_clicked,
    bg="#dc3545",      # Rojo
    fg="white",        # Texto blanco
    activebackground="#c82333",  # Rojo más oscuro al presionar
    activeforeground="white",
    state="active"
)
falla_button.pack(side="left", padx=5)

# Lista de defectos con código y nombre
defectos = [
    "L10 - Dent - Tab",
    "L20 - Dent - Cell",
    "L30 - Single Particle - Cell",
    "L40 - Multiple Particles - Cell",
    "L50 - Gouge - Cell",
    "L60 - Scratch - Cell",
    "L70 - Scratch - Tab",
    "L80 - White Residue - Cell",
    "L90 - Bent - Tab",
    "L100 - Bent - Cell Pouch",
    "L110 - Contamination - Cell",
    "L120 - Contamination - Tab",
    "L130 - QR Code Error",
    "L140 - Puncture - Cell",
    "L150 - Gasket Damage - Cell",
    "L160 - Other / New Defect",
    "L170 - Swollen - Cell",
    "L180 - Ripples - Cell",
    "L190 - Missing kapton tape",
    "L200 - Dropped cell - Cell",
    "L1200 - Malleable",
    "L1210 - Tool Marks",

]

# Caja de texto para el defecto (convertida a Combobox y deshabilitada)
defect_label = tk.Label(root, text="Defecto:", font=("Arial", 14))
defect_label.pack(pady=10)

defect_entry = ttk.Combobox(root, font=("Arial", 14), values=defectos, state="disabled")
defect_entry.pack(pady=10)

# Función para manejar la selección del estado
def on_status_selected(status):
    global selected_status
    selected_status = status
    print(f"Estado seleccionado: {status}")
    if status == "FALLA":
        defect_entry.config(state="readonly")  # Habilita el combobox
        defect_entry.set("")  # Limpia selección previa
    else:
        defect_entry.config(state="disabled")  # Deshabilita el combobox
        defect_entry.set("")  # Limpia selección previa


#22T10025246073

# Botón de captura
capture_button = tk.Button(root, text="Capturar", font=("Arial", 14), command=on_capture_clicked)
#capture_button.pack(pady=20)

def configurar_usuario_password():
    global user, password
    new_user = simpledialog.askstring("Configurar Usuario", "Ingrese el usuario:", parent=root)
    new_password = simpledialog.askstring("Configurar Password", "Ingrese el password:", parent=root, show="*")
    if new_user and new_password:
        user = new_user
        password = odcLib.encrypt(new_password)
        user_top_label.config(text=f"Usuario: {user}")

def ingresar_shop_order_manual():
    manual_so = simpledialog.askstring("Shop Order Manual", "Ingrese el número de Shop Order:", parent=root)
    if manual_so:
        # Puedes agregar la shop order manualmente a la lista y seleccionarla
        shop_orders.append(manual_so)
        shop_order_menu["values"] = shop_orders
        shop_order_menu.set(manual_so)
        shop_order_info_label.config(text=f"Shop Order: {manual_so}")

# Crear barra de menú
menu_bar = tk.Menu(root)
config_menu = tk.Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Configurar Usuario/Password", command=configurar_usuario_password)
config_menu.add_command(label="Ingresar Shop Order Manual", command=ingresar_shop_order_manual)
menu_bar.add_cascade(label="Configuración", menu=config_menu)
root.config(menu=menu_bar)

user = "32009417"
password = "32009417"
user_top_label = tk.Label(root, text=f"Usuario: {user}", font=("Arial", 12, "bold"), fg="#007bff")
user_top_label.pack(pady=(5, 0))

# Iniciar el loop principal
root.mainloop()



