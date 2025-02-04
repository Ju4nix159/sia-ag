import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar
import math


# Datos del problema
productos = [
    {"nombre": "Notebook", "peso": 2.1},
    {"nombre": "Tablet", "peso": 0.6},
    {"nombre": "Parlante Bluetooth", "peso": 3.6},
    {"nombre": "Smart TV", "peso": 5},
    {"nombre": "Smartphone", "peso": 0.25},
    {"nombre": "Impresora laser", "peso": 10},
    {"nombre": "Ventilador 15''", "peso": 6},
    {"nombre": "Cámara GoPro", "peso": 0.16},
    {"nombre": "Router wifi", "peso": 0.55},
    {"nombre": "Aro luz 18''", "peso": 2},
]
peso_maximo = 17  # Peso máximo del dron

# Lista inicial de cantidades de productos
def inicializar_cantidad_productos(max_cantidad=500):
    """Inicializa las cantidades de productos disponibles con un máximo configurable."""
    return {producto["nombre"]: random.randint(0, max_cantidad) for producto in productos}


# Variables globales
cantidades_disponibles = {}
cantidades_iniciales = {}
graficos_datos = []


import math

def predecir_viajes():
    if not cantidades_disponibles:
        messagebox.showinfo("Sin datos", "Primero genere la lista de productos.")
        return

    # Calcular el peso total de los productos en la lista generada
    peso_total = sum(cantidades_disponibles[producto["nombre"]] * producto["peso"] for producto in productos)

    # Calcular el número estimado de viajes
    viajes_estimados = math.ceil(peso_total / peso_maximo)

    # Mostrar la predicción en un cuadro de diálogo
    messagebox.showinfo("Predicción de Viajes", f"Peso total: {peso_total:.2f} kg\n"
                                                f"Viajes estimados: {viajes_estimados}")


def generar_cromosoma_v2(temp_cantidades):
    """Genera un cromosoma sin exceder el peso maximo ni las cantidades disponibles de productos."""
    cromosoma = [0] * len(productos)
    peso_total = 0

    while True:
        indices_disponibles = [
            i for i in range(len(productos))
            if cromosoma[i] < temp_cantidades[productos[i]["nombre"]] and
            peso_total + productos[i]["peso"] <= peso_maximo
        ]
        if not indices_disponibles:
            break

        indice = random.choice(indices_disponibles)
        cromosoma[indice] += 1
        peso_total += productos[indice]["peso"]
        
    
    return cromosoma



def calcular_aptitud(cromosoma):
    """Calcula la aptitud de un cromosoma segun su peso total."""
    peso_total = sum(cromosoma[i] * productos[i]["peso"] for i in range(len(productos)))
    if peso_total > peso_maximo:
        return 0
    return peso_total 

def seleccion_ruleta(poblacion, aptitudes):
    total_aptitud = sum(aptitudes)
    if total_aptitud == 0:
        return random.choice(poblacion)
    probabilidades = [apt / total_aptitud for apt in aptitudes]
    return random.choices(poblacion, weights=probabilidades, k=1)[0]

def seleccion_elitista(poblacion, aptitudes):
    ordenados = sorted(zip(poblacion, aptitudes), key=lambda x: x[1], reverse=True)
    return ordenados[0][0]  # Retorna el mejor cromosoma

def cruzar_simple(padre1, padre2):
    punto = random.randint(1, len(padre1) - 1)
    hijo1 = padre1[:punto] + padre2[punto:]
    hijo2 = padre2[:punto] + padre1[punto:]
    return hijo1, hijo2

def cruzar_multipunto(padre1, padre2):
    puntos = sorted(random.sample(range(1, len(padre1)), 2))
    hijo1, hijo2 = padre1[:], padre2[:]
    for i in range(puntos[0], puntos[1]):
        hijo1[i], hijo2[i] = hijo2[i], hijo1[i]
    return hijo1, hijo2

def mutar_simple(cromosoma, prob_mutacion):
    if random.random() < prob_mutacion:
        indice = random.randint(0, len(cromosoma) - 1)
        if cromosoma[indice] > 0:
            cromosoma[indice] = max(0, cromosoma[indice] + random.choice([-1, 1]))
    return cromosoma

def mutar_adaptativa_convergencia(cromosoma, prob_mutacion, generacion_actual, max_generaciones):
    """Mutación adaptativa donde la probabilidad de mutación disminuye conforme avanza la convergencia."""
    if max_generaciones == 0:  # Manejo de generaciones ilimitadas
        adaptacion = prob_mutacion  # Mantén probabilidad constante en este caso
    else:
        adaptacion = prob_mutacion * (1 - generacion_actual / max_generaciones)

    if random.random() < adaptacion:
        indice = random.randint(0, len(cromosoma) - 1)
        if cromosoma[indice] > 0:
            cromosoma[indice] = max(0, cromosoma[indice] + random.choice([-1, 1]))

    return cromosoma


# NO USADA
def debug_message(message, verbose=True):
    """Muestra un mensaje de depuración si verbose está activado."""
    if verbose:
        print(message)


def algoritmo_genetico_viajes_v2(cantidades_disponibles, generaciones, tamano_poblacion, prob_mutacion, tipo_seleccion, tipo_cruza, tipo_mutacion):
    temp_cantidades = cantidades_disponibles.copy() # Copia de las cantidades
    viajes = []
    generacion_actual = 0
    sin_mejora = 0
    max_sin_mejora = 50
    
    # umbral_aptitud = 0.95 * peso_maximo

    global graficos_datos
    graficos_datos = []

    #Este ciclo se ejecuta mientras quede al menos un producto con cantidad mayor a 0. Cada iteración representa un viaje del dron
    while any(cantidad > 0 for cantidad in temp_cantidades.values()): 
        mejor_aptitud_por_generacion = []
        poblacion = [generar_cromosoma_v2(temp_cantidades) for _ in range(tamano_poblacion)]
        aptitudes = [calcular_aptitud(crom) for crom in poblacion]
        mejor_cromosoma = poblacion[aptitudes.index(max(aptitudes))]
        mejor_aptitud_global = max(aptitudes)
        
        mejora_significativa = True  # Flag para control de cambios significativos

        #Este ciclo representa la evolución de generaciones dentro de un viaje
        while mejora_significativa:
            nueva_poblacion = []
            for _ in range(tamano_poblacion // 2):
                #Selección: Los cromosomas padres son seleccionados según el tipo de selección (Ruleta o Elitista).
                if tipo_seleccion == "Ruleta":
                    padre1 = seleccion_ruleta(poblacion, aptitudes)
                    padre2 = seleccion_ruleta(poblacion, aptitudes)
                elif tipo_seleccion == "Elitista":
                    padre1 = seleccion_elitista(poblacion, aptitudes)
                    padre2 = seleccion_elitista(poblacion, aptitudes)
                else:
                    raise ValueError("Tipo de selección no reconocido.")

                #Cruza: Los padres generan dos hijos con el método indicado (Simple o Multipunto).
                if tipo_cruza == "Simple":
                    hijo1, hijo2 = cruzar_simple(padre1, padre2)
                elif tipo_cruza == "Multipunto":
                    hijo1, hijo2 = cruzar_multipunto(padre1, padre2)
                else:
                    raise ValueError("Tipo de cruza no reconocido.")

                #Mutación: Se aplica mutación según el tipo (Simple o Adaptativa).
                if tipo_mutacion == "Simple":
                    hijo1 = mutar_simple(hijo1, prob_mutacion)
                    hijo2 = mutar_simple(hijo2, prob_mutacion)
                elif tipo_mutacion == "Adaptativa":
                    hijo1 = mutar_adaptativa_convergencia(hijo1, prob_mutacion, generacion_actual, generaciones)
                    hijo2 = mutar_adaptativa_convergencia(hijo2, prob_mutacion, generacion_actual, generaciones)
                else:
                    raise ValueError("Tipo de mutación no reconocido.")

                #Población: Los nuevos cromosomas hijos se añaden a la nueva población.
                nueva_poblacion.extend([hijo1, hijo2])

            #Se evalúa la nueva población calculando las aptitudes de los cromosomas.
            poblacion = nueva_poblacion[:tamano_poblacion]
            aptitudes = [calcular_aptitud(crom) for crom in poblacion]
            mejor_aptitud_actual = max(aptitudes)

            historial_generaciones = []  # Guardará los datos de cada generación, no usado por el momento
    


            mejor_cromosoma_actual = poblacion[aptitudes.index(mejor_aptitud_actual)]
            mejor_aptitud_por_generacion.append(mejor_aptitud_actual)



            if mejor_aptitud_actual > mejor_aptitud_global:
                mejor_aptitud_global = mejor_aptitud_actual
                mejor_cromosoma = mejor_cromosoma_actual
                sin_mejora = 0
            else:
                sin_mejora += 1

            generacion_actual += 1

            # Control de corte por generaciones o mejora
            mejora_significativa = generaciones == 0 or generacion_actual < generaciones

            if not mejora_significativa or sin_mejora >= max_sin_mejora:
                break

        graficos_datos.append(mejor_aptitud_por_generacion)

        #Al final de un viaje, se descuentan las cantidades usadas de cada producto según el mejor cromosoma.
        for i, cantidad in enumerate(mejor_cromosoma):
            temp_cantidades[productos[i]["nombre"]] -= cantidad

        #Se guarda el mejor cromosoma y su aptitud para este viaje en la lista viajes.
        aptitud = calcular_aptitud(mejor_cromosoma)
        viajes.append((mejor_cromosoma, aptitud))

    return viajes, temp_cantidades



def generar_lista_productos():
    global cantidades_disponibles, cantidades_iniciales
    max_cantidad = max_cantidad_var.get()  # Tomar el máximo configurado por el usuario
    cantidades_disponibles = inicializar_cantidad_productos(max_cantidad)
    cantidades_iniciales = cantidades_disponibles.copy()

    lista_productos_texto = "Lista de productos disponibles:\n"
    for nombre, cantidad in cantidades_disponibles.items():
        lista_productos_texto += f"{nombre}: {cantidad} unidad(es)\n"
    lista_productos_label.config(text=lista_productos_texto)

# Interfaz gráfica
def ejecutar_ag_interface():
    tipo_seleccion = seleccion_var.get()
    tipo_cruza = cruza_var.get()
    tipo_mutacion = mutacion_var.get()
    generaciones = num_generaciones_var.get()
    tamano_poblacion = tamano_poblacion_var.get()
    prob_mutacion = prob_mutacion_var.get()

    viajes, cantidades_finales = algoritmo_genetico_viajes_v2(
        cantidades_disponibles, generaciones, tamano_poblacion, prob_mutacion, tipo_seleccion, tipo_cruza, tipo_mutacion
    )

    resultado_list.delete(0, tk.END)
    for i, (viaje, aptitud) in enumerate(viajes):
        resultado_list.insert(tk.END, f"\nViaje {i+1} - Total: {aptitud:.2f} kg")
        for j, cantidad in enumerate(viaje):
            if cantidad > 0:
                resultado_list.insert(tk.END, f"  {productos[j]['nombre']}: {cantidad} unidad(es), {productos[j]['peso'] * cantidad:.2f} kg")

    resumen_final_texto = "Resumen de cantidades finales:\n"
    for nombre, cantidad in cantidades_finales.items():
        inicial = cantidades_iniciales[nombre]
        resumen_final_texto += f"{nombre}: Inicial: {inicial}, Restante: {cantidad}\n"
    messagebox.showinfo("Resumen Final", resumen_final_texto)



def mostrar_grafico_mejor_aptitud_simple():
    if not graficos_datos:
        messagebox.showinfo("Sin datos", "Primero ejecute el AG para ver el gráfico")
        return

    # Calcular la mejor aptitud para cada generación
    mejor_aptitudes = [max(generacion) for generacion in graficos_datos]

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(mejor_aptitudes) + 1), mejor_aptitudes, marker='o', label="Mejor Aptitud", color="blue")
    plt.axhline(y=peso_maximo, color='red', linestyle='--', label="Peso Máximo Permitido")

    plt.xlabel("Generaciones")
    plt.ylabel("Mejor Aptitud")
    plt.title("Evolución de la Mejor Aptitud por Generación")
    plt.legend()
    plt.grid(True)
    plt.show()


def mostrar_tabla_ejecuciones_interfaz():
    if not graficos_datos:
        messagebox.showinfo("Sin datos", "Primero ejecute el AG para ver la tabla")
        return

    # Limpiar el widget antes de mostrar datos nuevos
    tabla_text.delete(1.0, tk.END)

    # Encabezado de la tabla
    tabla_text.insert(tk.END, "{:<15} {:<15} {:<20} {:<10}\n".format("Generación", "Mejor Aptitud", "Promedio Aptitudes", "Diversidad"))
    tabla_text.insert(tk.END, "=" * 60 + "\n")

    # Filas de la tabla
    for i, generacion in enumerate(graficos_datos):
        mejor = max(generacion)
        peor = min(generacion)
        promedio = sum(generacion) / len(generacion)
        diversidad = mejor - peor
        
        tabla_text.insert(tk.END, "{:<15} {:<15.2f} {:<20.2f} {:<10.2f}\n".format(i + 1, mejor, promedio, diversidad))

    tabla_text.insert(tk.END, "\nTabla completada: Se alcanzó el óptimo.")




# Interfaz gráfica mejorada con botón reposicionado y soporte para scroll con rueda del mouse
root = tk.Tk()
root.title("Optimización de Viajes con AG")

# Dividir la ventana principal en dos paneles: Izquierdo (opciones) y Derecho (resultados)
frame_left = ttk.Frame(root)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

frame_right = ttk.Frame(root, padding="10")
frame_right.pack(side=tk.RIGHT, fill=tk.Y)

# Scrollbar para el panel izquierdo
canvas_left = tk.Canvas(frame_left)
scrollbar_left = Scrollbar(frame_left, orient=tk.VERTICAL, command=canvas_left.yview)
canvas_left.configure(yscrollcommand=scrollbar_left.set)

# Frame interno para el contenido del panel izquierdo
frame_content_left = ttk.Frame(canvas_left)

# Empaquetar el scrollbar y el canvas
scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)
canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas_left.create_window((0, 0), window=frame_content_left, anchor="nw")

# Configurar el scrollbar para redimensionarse automáticamente
def configure_scroll_region(event):
    canvas_left.configure(scrollregion=canvas_left.bbox("all"))

frame_content_left.bind("<Configure>", configure_scroll_region)

# Soporte para la rueda del mouse en el panel izquierdo
def on_mousewheel(event):
    canvas_left.yview_scroll(-1 * int(event.delta / 120), "units")

canvas_left.bind_all("<MouseWheel>", on_mousewheel)

# Widgets del panel izquierdo (formulario de configuración)
max_cantidad_var = tk.IntVar(value=10)
ttk.Label(frame_content_left, text="Máximo de cantidad por producto:").pack(pady=5)
ttk.Entry(frame_content_left, textvariable=max_cantidad_var).pack(pady=5)

# Botón "Generar Lista de Productos" colocado justo debajo del input de cantidad
btn_generar_productos = ttk.Button(frame_content_left, text="Generar Lista de Productos", command=generar_lista_productos)
btn_generar_productos.pack(pady=10)

btn_prediccion_viajes = ttk.Button(frame_content_left, text="Predecir Viajes", command=predecir_viajes)
btn_prediccion_viajes.pack(pady=10)


# Mostrar lista de productos iniciales
lista_productos_label = ttk.Label(frame_content_left, text="", justify=tk.LEFT)
lista_productos_label.pack(padx=10, pady=10)

ttk.Label(frame_content_left, text="Seleccione el tipo de Selección:").pack(pady=5)
seleccion_var = tk.StringVar(value="Ruleta")
seleccion_menu = ttk.Combobox(frame_content_left, textvariable=seleccion_var, values=["Ruleta", "Elitista"])
seleccion_menu.pack(pady=5)

ttk.Label(frame_content_left, text="Seleccione el tipo de Cruzamiento:").pack(pady=5)
cruza_var = tk.StringVar(value="Simple")
cruza_menu = ttk.Combobox(frame_content_left, textvariable=cruza_var, values=["Simple", "Multipunto"])
cruza_menu.pack(pady=5)

ttk.Label(frame_content_left, text="Seleccione el tipo de Mutación:").pack(pady=5)
mutacion_var = tk.StringVar(value="Simple")
mutacion_menu = ttk.Combobox(frame_content_left, textvariable=mutacion_var, values=["Simple", "Adaptativa"])
mutacion_menu.pack(pady=5)

ttk.Label(frame_content_left, text="Número de generaciones (0 para ilimitado):").pack(pady=5)
num_generaciones_var = tk.IntVar(value=50)
ttk.Entry(frame_content_left, textvariable=num_generaciones_var).pack(pady=5)

ttk.Label(frame_content_left, text="Tamaño de población:").pack(pady=5)
tamano_poblacion_var = tk.IntVar(value=20)
ttk.Entry(frame_content_left, textvariable=tamano_poblacion_var).pack(pady=5)

ttk.Label(frame_content_left, text="Probabilidad de mutación:").pack(pady=5)
prob_mutacion_var = tk.DoubleVar(value=0.1)
ttk.Entry(frame_content_left, textvariable=prob_mutacion_var).pack(pady=5)

# Botones de ejecución y gráficos
btn_ejecutar = ttk.Button(frame_content_left, text="Ejecutar AG", command=ejecutar_ag_interface)
btn_ejecutar.pack(pady=10)
btn_grafico_mejor_aptitud = ttk.Button(frame_content_left, text="Gráfico Mejor Aptitud", command=mostrar_grafico_mejor_aptitud_simple)
btn_grafico_mejor_aptitud.pack(pady=10)
btn_tabla_ejecuciones_interfaz = ttk.Button(frame_content_left, text="Mostrar Tabla de Ejecuciones", command=mostrar_tabla_ejecuciones_interfaz)
btn_tabla_ejecuciones_interfaz.pack(pady=10)



# Panel derecho para los resultados de los viajes
scrollbar_right = Scrollbar(frame_right)
resultado_list = tk.Listbox(frame_right, height=20, width=50, yscrollcommand=scrollbar_right.set)
scrollbar_right.config(command=resultado_list.yview)

# Empaquetar la lista y el scrollbar
scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)
resultado_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Widget de texto para la tabla
tabla_text = tk.Text(frame_right, wrap=tk.NONE, height=20, width=60)
tabla_text.pack(padx=10, pady=10)


root.mainloop()


