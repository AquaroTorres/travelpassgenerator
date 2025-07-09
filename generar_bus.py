import json
from datetime import datetime, timedelta
import os
import subprocess

def ask_input(prompt, default_value):
    """Solicita una entrada al usuario con un valor por defecto."""
    user_input = input(f"{prompt} [{default_value}]: ")
    return user_input if user_input else default_value

def ask_date_time(prompt, default_date_time_str):
    """Solicita una fecha y hora y la valida."""
    while True:
        user_input = input(f"{prompt} [DD Mon. YYYY HH:MM, default: {default_date_time_str}]: ")
        dt_str = user_input if user_input else default_date_time_str
        try:
            # Intentar parsear la fecha y hora
            date_obj = datetime.strptime(dt_str, "%d %b %Y %H:%M")
            return date_obj.strftime("%d %b %Y %H:%M") # Devuelve el formato legible
        except ValueError:
            print("Fecha y hora inválidas. Por favor, usa el formato 'DD Mon. YYYY HH:MM' (ej: 21 Sep. 2025 18:15).")

def create_pkpass_bundle(json_filename, pkpass_filename, common_images):
    """
    Crea el archivo .pkpass a partir del JSON y las imágenes.
    Requiere que 'zip' esté disponible en el sistema.
    """
    print(f"Empaquetando '{json_filename}' en '{pkpass_filename}'...")
    
    # Crea un directorio temporal para el contenido del pase
    temp_dir = "temp_pkpass_content"
    os.makedirs(temp_dir, exist_ok=True)

    # Mueve o copia el JSON y las imágenes al directorio temporal
    try:
        os.rename(json_filename, os.path.join(temp_dir, "pass.json"))
        for img in common_images:
            if not os.path.exists(img):
                print(f"Advertencia: La imagen '{img}' no se encontró en el directorio actual. El .pkpass podría estar incompleto.")
                continue
            subprocess.run(["cp", img, temp_dir], check=True) # Usa cp para copiar y no mover
        
        # Crea el archivo .pkpass (es un zip renombrado)
        # Nos movemos al temp_dir para zipear solo los contenidos
        current_cwd = os.getcwd() # Guardar el directorio actual
        os.chdir(temp_dir)
        
        # Comando zip: -r (recursivo), -j (junk paths - no guardar directorios), --exclude para evitar .DS_Store
        zip_command = ["zip", "-r", os.path.join(current_cwd, pkpass_filename)]
        zip_command.extend(["pass.json"] + [img for img in common_images if os.path.exists(os.path.join(current_cwd, img))]) # Asegurarse que solo incluimos las que existen
        
        # Ejecutar el comando zip
        result = subprocess.run(zip_command, capture_output=True, text=True)
        
        os.chdir(current_cwd) # Volver al directorio original

        if result.returncode == 0:
            print(f"'{pkpass_filename}' creado exitosamente.")
        else:
            print(f"Error al crear '{pkpass_filename}':")
            print(result.stderr)

    except FileNotFoundError:
        print(f"Error: Asegúrate de que '{json_filename}' y las imágenes PNG existan en el directorio actual.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al empaquetar el .pkpass: {e}")
    finally:
        # Limpiar el directorio temporal y el JSON original (ya movido o copiado)
        if os.path.exists(os.path.join(temp_dir, "pass.json")):
            os.remove(os.path.join(temp_dir, "pass.json"))
        for img in common_images:
            if os.path.exists(os.path.join(temp_dir, img)):
                os.remove(os.path.join(temp_dir, img))
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        # Si el JSON original se movió, puede que necesitemos recrearlo o copiarlo de vuelta si se usará el mismo nombre
        # En este script, cada JSON tiene un nombre único, así que no es problema.


def main():
    print("--- Generador de JSON y PKPASS para Pases de Autobús ---")
    print("")

    # --- Datos Comunes a Todos los Pases ---
    print("--- Datos Generales del Viaje ---")
    origin = ask_input("Origen del viaje (ej: Arica (Chile))", "Arica (Chile)")
    destination = ask_input("Destino del viaje (ej: Tacna (Perú))", "Tacna (Perú)")
    
    # Fecha y hora por defecto: 21 de septiembre de 2025 a las 18:15
    # Usamos datetime.now() para la fecha actual, y ajustamos para el ejemplo
    current_date = datetime.now()
    default_travel_date_time = (current_date + timedelta(days=10)).strftime("%d %b %Y %H:%M") # 10 días en el futuro
    travel_date_time = ask_date_time("Fecha y hora del viaje", default_travel_date_time)
    
    platform = ask_input("Número de Andén/Plataforma", "12")
    confirmation = ask_input("Número de Confirmación General", "4641175213")
    price = ask_input("Precio del pasaje (ej: 20 USD / $18.000 CLP)", "20 USD / $18.000 CLP")

    # --- Cantidad de Pasajeros ---
    while True:
        try:
            num_passengers = int(ask_input("Cantidad de pasajeros", "1"))
            if num_passengers > 0:
                break
            else:
                print("La cantidad de pasajeros debe ser al menos 1.")
        except ValueError:
            print("Por favor, ingresa un número válido para la cantidad de pasajeros.")

    # Lista de imágenes comunes para el PKPASS
    common_images = ["icon.png", "logo.png", "thumbnail.png", "strip.png"]

    # --- Generación de JSON y PKPASS por Pasajero ---
    generated_pkpass_files = []
    for i in range(num_passengers):
        print(f"\n--- Datos del Pasajero {i + 1} ---")
        passenger_name = ask_input(f"Nombre completo del Pasajero {i + 1}", f"Pasajero {i + 1}")
        passenger_id = ask_input(f"Identificación del Pasajero {i + 1} (ej: RUN: 12345678-9)", f"ID: {12345678 + i}-{(i % 9) + 1}")
        seat_number = ask_input(f"Número de Asiento del Pasajero {i + 1}", str(12 + i))
        
        # Serial Number único para cada pase
        serial_number = f"{confirmation}-{i+1}" 

        pass_data = {
          "formatVersion": 1,
          "passTypeIdentifier": "pass.com.ejemplo.bus", 
          "serialNumber": serial_number,
          "teamIdentifier": "ABCDE12345",
          "organizationName": "Empresa de transportes TURBUS SA",
          "logoText": "TURBUS SA",
          "foregroundColor": "rgb(255, 255, 255)",
          "backgroundColor": "rgb(0, 128, 0)", # Color verde para el bus
          "labelColor": "rgb(255, 255, 255)",
          "boardingPass": {
            "transitType": "PKTransitTypeBus",
            "primaryFields": [
              {
                "key": "from",
                "label": "Origin",
                "value": origin
              },
              {
                "key": "to",
                "label": "Destination",
                "value": destination
              }
            ],
            "secondaryFields": [
              {
                "key": "passenger",
                "label": "Passenger / Pasajero",
                "value": passenger_name
              },
              {
                "key": "seat",
                "label": "Seat / Asiento",
                "value": seat_number
              },
              {
                "key": "identification",
                "label": "ID / Identificación",
                "value": passenger_id
              },
              {
                "key": "date",
                "label": "Date / Fecha",
                "value": travel_date_time
              }
            ],
            "auxiliaryFields": [
              {
                "key": "platform",
                "label": "Platform / Andén",
                "value": platform
              },
              {
                "key": "confirmation",
                "label": "Confirmación",
                "value": confirmation
              },
              { 
                "key": "price",
                "label": "Price / Valor",
                "value": price
              }
            ]
          },
          "barcode": {
            "format": "PKBarcodeFormatQR",
            "message": f"TURBUS SA - {travel_date_time} - {origin.split(' ')[0].upper()}-{destination.split(' ')[0].upper()} - {passenger_name} ({passenger_id}) - Asiento {seat_number}",
            "messageEncoding": "iso-8859-1"
          }
        }

        json_output_filename = f"pass_bus_{i+1}.json" if num_passengers > 1 else "pass_bus.json"
        pkpass_output_filename = f"pass_bus_{i+1}.pkpass" if num_passengers > 1 else "pass_bus.pkpass"

        with open(json_output_filename, "w", encoding="utf-8") as f:
            json.dump(pass_data, f, indent=2, ensure_ascii=False)
        print(f"Archivo '{json_output_filename}' JSON generado.")
        
        # Ahora creamos el archivo PKPASS
        create_pkpass_bundle(json_output_filename, pkpass_output_filename, common_images)
        generated_pkpass_files.append(pkpass_output_filename)

    print("\n--- Proceso Completado ---")
    print("Se han generado los siguientes archivos PKPASS:")
    for filename in generated_pkpass_files:
        print(f"- {filename}")
    print("\n¡Ya están listos para ser distribuidos!")

if __name__ == "__main__":
    main()