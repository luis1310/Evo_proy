import pandas as pd

def generar_carga_horaria_ejemplo():
    """
    Genera un archivo Excel con una carga horaria de ejemplo.
    
    Estructura de cada celda: "id|nombre_curso|profesor|tipo"
    - id: Identificador único del curso
    - nombre_curso: Nombre del curso
    - profesor: Nombre del profesor
    - tipo: Teórico o Práctico
    """
    
    # Definir los cursos disponibles
    cursos = {
        1: {"nombre": "Cálculo I", "profesor": "García", "tipo": "Teórico"},
        2: {"nombre": "Física I", "profesor": "Martínez", "tipo": "Teórico"},
        3: {"nombre": "Programación I", "profesor": "López", "tipo": "Teórico"},
        4: {"nombre": "Programación I Lab", "profesor": "López", "tipo": "Práctico"},
        5: {"nombre": "Álgebra Lineal", "profesor": "Gómez", "tipo": "Teórico"},
        6: {"nombre": "Matemática Discreta", "profesor": "Sánchez", "tipo": "Teórico"},
        7: {"nombre": "Física I Lab", "profesor": "Martínez", "tipo": "Práctico"},
        8: {"nombre": "Estructuras de Datos", "profesor": "Torres", "tipo": "Teórico"},
        9: {"nombre": "Estructuras de Datos Lab", "profesor": "Torres", "tipo": "Práctico"},
        10: {"nombre": "Cálculo II", "profesor": "García", "tipo": "Teórico"},
        11: {"nombre": "Física II", "profesor": "Rodríguez", "tipo": "Teórico"},
        12: {"nombre": "Estadística", "profesor": "Ramírez", "tipo": "Teórico"},
        13: {"nombre": "Probabilidad", "profesor": "Ramírez", "tipo": "Teórico"},
        14: {"nombre": "Algoritmos", "profesor": "Torres", "tipo": "Teórico"},
        15: {"nombre": "Algoritmos Lab", "profesor": "Torres", "tipo": "Práctico"},
    }
    
    # Crear la estructura de la carga horaria
    # 14 bloques por día (7:00 AM a 9:00 PM)
    # 5 días (Lunes a Viernes)
    
    # Columnas (Lunes a Viernes)
    columnas = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Filas (Bloques de 7:00 AM a 9:00 PM)
    horas = []
    for i in range(14):
        hora_inicio = 7 + i
        hora_fin = hora_inicio + 1
        horas.append(f"{hora_inicio}:00 - {hora_fin}:00")
    
    # Crear DataFrame vacío
    df = pd.DataFrame(index=horas, columns=columnas)
    
    # Llenar la carga horaria con algunos cursos
    # Formato: "id|nombre|profesor|tipo"
    
    # Lunes
    df.loc["7:00 - 8:00", "Lunes"] = "1|Cálculo I|García|Teórico"
    df.loc["8:00 - 9:00", "Lunes"] = "1|Cálculo I|García|Teórico"
    df.loc["9:00 - 10:00", "Lunes"] = "2|Física I|Martínez|Teórico"
    df.loc["10:00 - 11:00", "Lunes"] = "2|Física I|Martínez|Teórico"
    df.loc["11:00 - 12:00", "Lunes"] = "5|Álgebra Lineal|Gómez|Teórico"
    df.loc["12:00 - 13:00", "Lunes"] = "5|Álgebra Lineal|Gómez|Teórico"
    df.loc["14:00 - 15:00", "Lunes"] = "8|Estructuras de Datos|Torres|Teórico"
    df.loc["15:00 - 16:00", "Lunes"] = "8|Estructuras de Datos|Torres|Teórico"
    df.loc["16:00 - 17:00", "Lunes"] = "12|Estadística|Ramírez|Teórico"
    df.loc["17:00 - 18:00", "Lunes"] = "12|Estadística|Ramírez|Teórico"
    
    # Martes
    df.loc["7:00 - 8:00", "Martes"] = "3|Programación I|López|Teórico"
    df.loc["8:00 - 9:00", "Martes"] = "3|Programación I|López|Teórico"
    df.loc["9:00 - 10:00", "Martes"] = "6|Matemática Discreta|Sánchez|Teórico"
    df.loc["10:00 - 11:00", "Martes"] = "6|Matemática Discreta|Sánchez|Teórico"
    df.loc["11:00 - 12:00", "Martes"] = "10|Cálculo II|García|Teórico"
    df.loc["12:00 - 13:00", "Martes"] = "10|Cálculo II|García|Teórico"
    df.loc["14:00 - 15:00", "Martes"] = "4|Programación I Lab|López|Práctico"
    df.loc["15:00 - 16:00", "Martes"] = "4|Programación I Lab|López|Práctico"
    df.loc["16:00 - 17:00", "Martes"] = "4|Programación I Lab|López|Práctico"
    df.loc["17:00 - 18:00", "Martes"] = "13|Probabilidad|Ramírez|Teórico"
    df.loc["18:00 - 19:00", "Martes"] = "13|Probabilidad|Ramírez|Teórico"
    
    # Miércoles
    df.loc["7:00 - 8:00", "Miércoles"] = "1|Cálculo I|García|Teórico"
    df.loc["8:00 - 9:00", "Miércoles"] = "1|Cálculo I|García|Teórico"
    df.loc["9:00 - 10:00", "Miércoles"] = "2|Física I|Martínez|Teórico"
    df.loc["10:00 - 11:00", "Miércoles"] = "2|Física I|Martínez|Teórico"
    df.loc["11:00 - 12:00", "Miércoles"] = "14|Algoritmos|Torres|Teórico"
    df.loc["12:00 - 13:00", "Miércoles"] = "14|Algoritmos|Torres|Teórico"
    df.loc["14:00 - 15:00", "Miércoles"] = "7|Física I Lab|Martínez|Práctico"
    df.loc["15:00 - 16:00", "Miércoles"] = "7|Física I Lab|Martínez|Práctico"
    df.loc["16:00 - 17:00", "Miércoles"] = "7|Física I Lab|Martínez|Práctico"
    df.loc["17:00 - 18:00", "Miércoles"] = "11|Física II|Rodríguez|Teórico"
    df.loc["18:00 - 19:00", "Miércoles"] = "11|Física II|Rodríguez|Teórico"
    
    # Jueves
    df.loc["7:00 - 8:00", "Jueves"] = "3|Programación I|López|Teórico"
    df.loc["8:00 - 9:00", "Jueves"] = "3|Programación I|López|Teórico"
    df.loc["9:00 - 10:00", "Jueves"] = "5|Álgebra Lineal|Gómez|Teórico"
    df.loc["10:00 - 11:00", "Jueves"] = "5|Álgebra Lineal|Gómez|Teórico"
    df.loc["11:00 - 12:00", "Jueves"] = "6|Matemática Discreta|Sánchez|Teórico"
    df.loc["12:00 - 13:00", "Jueves"] = "6|Matemática Discreta|Sánchez|Teórico"
    df.loc["14:00 - 15:00", "Jueves"] = "9|Estructuras de Datos Lab|Torres|Práctico"
    df.loc["15:00 - 16:00", "Jueves"] = "9|Estructuras de Datos Lab|Torres|Práctico"
    df.loc["16:00 - 17:00", "Jueves"] = "9|Estructuras de Datos Lab|Torres|Práctico"
    df.loc["17:00 - 18:00", "Jueves"] = "12|Estadística|Ramírez|Teórico"
    df.loc["18:00 - 19:00", "Jueves"] = "12|Estadística|Ramírez|Teórico"
    
    # Viernes
    df.loc["7:00 - 8:00", "Viernes"] = "10|Cálculo II|García|Teórico"
    df.loc["8:00 - 9:00", "Viernes"] = "10|Cálculo II|García|Teórico"
    df.loc["9:00 - 10:00", "Viernes"] = "11|Física II|Rodríguez|Teórico"
    df.loc["10:00 - 11:00", "Viernes"] = "11|Física II|Rodríguez|Teórico"
    df.loc["11:00 - 12:00", "Viernes"] = "14|Algoritmos|Torres|Teórico"
    df.loc["12:00 - 13:00", "Viernes"] = "14|Algoritmos|Torres|Teórico"
    df.loc["14:00 - 15:00", "Viernes"] = "15|Algoritmos Lab|Torres|Práctico"
    df.loc["15:00 - 16:00", "Viernes"] = "15|Algoritmos Lab|Torres|Práctico"
    df.loc["16:00 - 17:00", "Viernes"] = "15|Algoritmos Lab|Torres|Práctico"
    df.loc["17:00 - 18:00", "Viernes"] = "13|Probabilidad|Ramírez|Teórico"
    df.loc["18:00 - 19:00", "Viernes"] = "13|Probabilidad|Ramírez|Teórico"
    
    # Guardar el archivo
    archivo = "carga_horaria_ejemplo.xlsx"
    df.to_excel(archivo)
    print(f"Carga horaria generada y guardada en: {archivo}")
    
    return df

def visualizar_carga_horaria(df):
    """Visualiza la carga horaria generada"""
    print("\nCarga Horaria Generada:")
    print("="*50)
    
    # Para cada día
    for dia in df.columns:
        print(f"\n{dia}:")
        print("-"*20)
        
        # Para cada hora del día
        for hora in df.index:
            celda = df.loc[hora, dia]
            if pd.notna(celda):
                partes = celda.split('|')
                if len(partes) >= 3:
                    print(f"{hora}: {partes[1]} - Prof. {partes[2]}")
            else:
                print(f"{hora}: -")

if __name__ == "__main__":
    # Generar la carga horaria
    df = generar_carga_horaria_ejemplo()
    
    # Visualizar la carga horaria generada
    visualizar_carga_horaria(df)
    
    # Mostrar los cursos disponibles
    print("\nCursos disponibles en la carga horaria:")
    cursos_unicos = set()
    
    for dia in df.columns:
        for hora in df.index:
            celda = df.loc[hora, dia]
            if pd.notna(celda):
                partes = celda.split('|')
                if len(partes) >= 4:
                    curso_id = partes[0]
                    curso_nombre = partes[1]
                    profesor = partes[2]
                    tipo = partes[3]
                    cursos_unicos.add((curso_id, curso_nombre, profesor, tipo))
    
    for curso in sorted(cursos_unicos, key=lambda x: int(x[0])):
        print(f"ID: {curso[0]}, Nombre: {curso[1]}, Profesor: {curso[2]}, Tipo: {curso[3]}")