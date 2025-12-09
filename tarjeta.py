import tkinter as tk  # Importamos la librería Tkinter
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import csv

# --- Variables para almacenar datos ---
ldr_values = []
ntc_values = []
acc_x_vals = []
acc_y_vals = []
acc_z_vals = []

izquierda = False
centro = False
derecha = False

datos = []  


# ---- CONFIGURACIÓN DEL PUERTO SERIE ----
try:
    ser = serial.Serial("COM6", 115200, timeout=1)
    time.sleep(2)
    print("Conectado al microcontrolador")
except Exception as e:
    ser = None
    print(f"No se pudo abrir el puerto serie: {e}")

# ---- FUNCIONES QUE ENVÍAN LOS MENSAJES ----
def enviar_D1():
    ser.write(b"D1")
    print("Enviado: D1")

def enviar_D2():
    ser.write(b"D2")
    print("Enviado: D2")

def enviar_D3():
    ser.write(b"D3")
    print("Enviado: D3")

def enviar_rgb():
    texto = entry_RGB.get().strip()      
    mensaje = f"RGB({texto})"            
    ser.write(mensaje.encode())               
    print("Enviado:", mensaje)

def guardar_csv():
    global datos

    with open("datos.csv", "w", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow(["LDR", "NTC", "AccX", "AccY", "AccZ"])
        for dato in datos:
            writer.writerow(dato)
    print("Datos guardados en datos.csv")

def borrar_csv():
    global datos
    datos = []
    with open("datos.csv", "w", newline="") as archivo_csv:
        archivo_csv.truncate()
    print("Archivo datos.csv borrado")


# Creamos un objeto Tk, que será nuestra ventana principal
root = tk.Tk()

# Definimos título y tamaño de la ventana
root.title("Máster en Microelectronica. Diseño con microcontrolador")
root.geometry("1200x1200")
root.config(bg="#A0A0A0")

label1 = tk.Label(root, text="Conmutar diodo D1", font=("Arial", 14, "bold"), bg="#A0A0A0")
label1.place(x=50, y=50)

font_title = ("Arial", 14, "bold")
font_button = ("Arial", 12)
font_label = ("Arial", 12)

btn_style = {"font": font_button, "fg": "white", "width": 8, "height": 2}


btn1 = tk.Button(
    root,
    text="D1",
    font=("Arial", 16),
    fg="white",
    bg="#388E3C",
    command=enviar_D1)
btn1.place(x=100, y=100)

label2 = tk.Label(root, text="Conmutar diodo D2", font=("Arial", 14, "bold"), bg="#A0A0A0")
label2.place(x=250, y=50)
btn2 = tk.Button(
    root,
    text="D2",
    font=("Arial", 16),
    fg="white",
    bg="#1976D2",
    command=enviar_D2)
btn2.place(x=300, y=100)

label3 = tk.Label(root, text="Conmutar diodo D3", font=("Arial", 14, "bold"), bg="#A0A0A0")
label3.place(x=450, y=50)
btn3 = tk.Button(
    root,
    text="D3",
    font=("Arial", 16),
    fg="white",
    bg="#F57C00",
    command=enviar_D3)
btn3.place(x=500, y=100)


label4 = tk.Label(root, text="RGB (ej: 255,120,0):", font=("Arial", 14, "bold"), bg="#A0A0A0")
label4.place(x=50, y=200)
entry_RGB = tk.Entry(root, width=20, font=("Arial", 14))
entry_RGB.place(x=250, y=200)
tk.Button(root, text="Enviar RGB", font=font_button, bg="#4CAF50", fg="white", command=enviar_rgb).place(x=500, y=200)

label5 = tk.Label(root, text="Exportar Datos CSV", font=font_title, bg="#A0A0A0")
label5.place(x=700, y=200)
tk.Button(root, text="Guardar CSV", font=("Arial", 12), bg="#2196F3", fg="white", command=guardar_csv).place(x=920, y=200)
tk.Button(root, text="Borrar CSV", font=("Arial", 12), bg="#F44336", fg="white", command=borrar_csv).place(x=1040, y=200)

tk.Label(root, text="LEDS CAP1203:", font=("Arial", 14, "bold"), bg="#A0A0A0").place(x=850, y=50)

led1 = tk.Label(root, text="●", font=("Arial", 50), bg="#A0A0A0")
led2 = tk.Label(root, text="●", font=("Arial", 50), bg="#A0A0A0")
led3 = tk.Label(root, text="●", font=("Arial", 50), bg="#A0A0A0")

# Colocar en fila horizontal (derecha)
led1.place(x=850, y=75)
led2.place(x=900, y=75)
led3.place(x=950, y=75)

# Etiquetas pequeñas debajo
tk.Label(root, text="Izq", font=("Segoe UI", 10), fg="#555555", bg="#A0A0A0").place(x=865, y=140)
tk.Label(root, text="Cen", font=("Segoe UI", 10), fg="#555555", bg="#A0A0A0").place(x=915, y=140)
tk.Label(root, text="Der", font=("Segoe UI", 10), fg="#555555", bg="#A0A0A0").place(x=965, y=140)


# Función para actualizar los LEDs
def update_touch_leds(izquierda, centro, derecha):
    led1.config(fg="#FFD700" if izquierda else "#555555")
    led2.config(fg="#4FC3F7" if centro else "#555555")
    led3.config(fg="#FF4500" if derecha else "#555555")

# Agregamos los gráficos de ILUM y NTC
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5,1, figsize=(10,6), sharex=True)
fig.tight_layout(pad=3.0)
ax1.set_title("ILUM [uA]")
ax2.set_title("NTC")
ax3.set_title("Acelerómetro X")
ax4.set_title("Acelerómetro Y")
ax5.set_title("Acelerómetro Z")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().place(x=80, y=250, width=1000, height=800)
axs = [ax1, ax2, ax3, ax4, ax5]

def actualizar():
    global datos
    if ser and ser.in_waiting:
        linea = ser.readline().decode("utf-8", errors="ignore").strip()
        m = re.match(
            r"ILUM:\s*([+-]?\d+\.?\d*).*NTC:\s*([+-]?\d+).*"
            r"AccelerometroX:\s*([+-]?\d+\.?\d*).*"
            r"AccelerometroY:\s*([+-]?\d+\.?\d*).*"
            r"AccelerometroZ:\s*([+-]?\d+\.?\d*).*"
            r"izquierda:\s*(\d).*centro:\s*(\d).*derecha:\s*(\d)",
            linea
        )
        if m:
            try:
                ldr = float(m.group(1))
                ntc = float(m.group(2))
                acc_x = float(m.group(3))
                acc_y = float(m.group(4))
                acc_z = float(m.group(5))
                izq = bool(int(m.group(6)))
                cen = bool(int(m.group(7)))
                der = bool(int(m.group(8)))
                
                update_touch_leds(izq, cen, der)
                datos.append([ldr, ntc, acc_x, acc_y, acc_z])
                
                ldr_values.append(ldr)
                ntc_values.append(ntc)
                acc_x_vals.append(acc_x)
                acc_y_vals.append(acc_y)
                acc_z_vals.append(acc_z)
                
                for lst in [ldr_values, ntc_values, acc_x_vals, acc_y_vals, acc_z_vals]:
                    if len(lst) > 100:
                        lst.pop(0)
                if len(datos) > 100:
                    datos.pop(0)
                
                x_vals = list(range(len(ldr_values)))
                for ax in axs:
                    ax.clear()
                    ax.set_facecolor("#1E1E1E")
                    ax.grid(True, color="#555555", linestyle="--", linewidth=0.5)
                    ax.tick_params(colors="#CCCCCC")
                
                axs[0].plot(x_vals, ldr_values, color="#4FC3F7", linewidth=2)
                axs[1].plot(x_vals, ntc_values, color="#FF7043", linewidth=2)
                axs[2].plot(x_vals, acc_x_vals, color="#81C784", linewidth=2)
                axs[3].plot(x_vals, acc_y_vals, color="#FFD54F", linewidth=2)
                axs[4].plot(x_vals, acc_z_vals, color="#BA68C8", linewidth=2)
                
                axs[0].set_title("ILUM [µA]", color="#4FC3F7")
                axs[1].set_title("NTC", color="#FF7043")
                axs[2].set_title("Acelerómetro X", color="#81C784")
                axs[3].set_title("Acelerómetro Y", color="#FFD54F")
                axs[4].set_title("Acelerómetro Z", color="#BA68C8")
                
                canvas.draw()
            except Exception as e:
                print(f"Error procesando datos: {e}")
    
    root.after(50, actualizar)

def on_closing():
    if ser:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
actualizar()
root.mainloop()