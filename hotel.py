import json
from datetime import datetime, timedelta
import os
import subprocess

def ask_input(prompt, default_value):
    """Solicita una entrada al usuario con un valor por defecto."""
    user_input = input(f"{prompt} [{default_value}]: ")
    return user_input if user_input else default_value

def ask_date(prompt, default_date_str):
    """Solicita una fecha y la valida."""
    while True:
        user_input = input(f"{prompt} [YYYY-MM-DD, default: {default_date_str}]: ")
        date_str = user_input if user_input else default_date_str
        try:
            # Intentar parsear la fecha para validarla
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%a, %d %b %Y"), date_obj # Devuelve formato legible y objeto datetime
        except ValueError:
            print("Fecha inválida. Por favor, usa el formato YYYY-MM-DD.")

def create_pkpass_bundle(json_filename, pkpass_filename, common_images):
    """
    Crea el archivo .pkpass a partir del JSON y las imágenes.
    Requiere que 'zip' esté disponible en el sistema.
    """
    print(f"\nEmpaquetando '{json_filename}' en '{pkpass_filename}'...")
    
    # Crea un directorio temporal para el contenido del pase
    temp_dir = "temp_pkpass_content_hotel" # Nombre único para evitar conflictos
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Mueve el JSON al directorio temporal
        os.rename(json_filename, os.path.join(temp_dir, "pass.json"))
        
        # Copia las imágenes al directorio temporal
        images_to_zip = []
        for img in common_images:
            if os.path.exists(img):
                subprocess.run(["cp", img, temp_dir], check=True)
                images_to_zip.append(img)
            else:
                print(f"Advertencia: La imagen '{img}' no se encontró. El .pkpass podría estar incompleto.")
        
        # Crea el archivo .pkpass (es un zip renombrado)
        current_cwd = os.getcwd() # Guarda el directorio actual
        os.chdir(temp_dir) # Cambia al directorio temporal para zipear solo los contenidos
        
        zip_command = ["zip", "-j", "-r", os.path.join(current_cwd, pkpass_filename), "pass.json"]
        zip_command.extend(images_to_zip) # Añade solo las imágenes que realmente existían y se copiaron
        
        result = subprocess.run(zip_command, capture_output=True, text=True)
        
        os.chdir(current_cwd) # Vuelve al directorio original

        if result.returncode == 0:
            print(f"'{pkpass_filename}' creado exitosamente.")
        else:
            print(f"Error al crear '{pkpass_filename}':")
            print(result.stderr)
            print("Asegúrate de que 'zip' esté instalado en tu sistema.")

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar un archivo necesario para el empaquetado (JSON o imagen).")
    except Exception as e:
        print(f"Ocurrió un error inesperado al empaquetar el .pkpass: {e}")
    finally:
        # Limpia el directorio temporal
        if os.path.exists(os.path.join(temp_dir, "pass.json")):
            os.remove(os.path.join(temp_dir, "pass.json"))
        for img in common_images:
            if os.path.exists(os.path.join(temp_dir, img)):
                os.remove(os.path.join(temp_dir, img))
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

def main():
    print("--- Generador de PKPASS para Reservas de Hotel ---")
    print("")

    # --- Recopilación de Datos ---

    # Datos Primarios
    hotel_name = ask_input("Nombre del Hotel", "Hotel Colonial")
    
    # Usamos la fecha actual como base para los valores por defecto
    today = datetime.now()
    default_checkin_date_obj = today + timedelta(days=7)
    default_checkout_date_obj = today + timedelta(days=8)

    default_checkin_str = default_checkin_date_obj.strftime("%Y-%m-%d")
    default_checkout_str = default_checkout_date_obj.strftime("%Y-%m-%d")

    check_in_display, check_in_dt_obj = ask_date("Fecha de Check-in", default_checkin_str)
    check_out_display, check_out_dt_obj = ask_date("Fecha de Check-out", default_checkout_str)

    # Validar que la fecha de check-out sea posterior a la de check-in
    while check_out_dt_obj <= check_in_dt_obj:
        print("¡La fecha de Check-out debe ser posterior a la fecha de Check-in!")
        check_out_display, check_out_dt_obj = ask_date("Fecha de Check-out", default_checkout_str)

    nights = (check_out_dt_obj - check_in_dt_obj).days
    nights_text = "noche" if nights == 1 else "noches"

    # Datos Secundarios
    confirmation_number = ask_input("Número de Confirmación de Reserva", "4641175213")
    guest_name = ask_input("Reserva a nombre de:", "Alvaro Torres")
    
    print("\n--- Tipo de Habitación ---")
    room_options = {
        "1": "Habitación Matrimonial",
        "2": "Habitación Single",
        "3": "Habitación Doble - 2 camas",
        "4": "Suite Ejecutiva",
        "5": "Otro (especificar)"
    }
    for key, value in room_options.items():
        print(f"{key}) {value}")
    
    room_choice_key = ask_input("Elige una opción para el tipo de habitación", "3")
    if room_choice_key == "5":
        room_type = ask_input("Especifica el tipo de habitación", "Habitación Familiar")
    else:
        room_type = room_options.get(room_choice_key, "Habitación Doble - 2 camas")
        if room_choice_key not in room_options:
            print("Opción no válida, usando valor por defecto.")

    num_guests = ask_input("Cantidad de Pasajeros (ej: 2 adultos)", "2 adultos")

    # Datos Auxiliares
    hotel_address = ask_input("Dirección del Hotel", "Calle Siete, 98, Col. Agrícola Pantitlán, Iztacalco, 08100 Ciudad de México, México")

    # Datos de los Campos Traseros (BackFields)
    total_price = ask_input("Precio Total (ej: USD 68.30, CLP 32.000)", "USD 68.30")

    print("\n--- Régimen de Comidas ---")
    meal_plan_options = {
        "1": "El precio de esta habitación no incluye desayuno ni servicio de comidas.",
        "2": "Incluye Desayuno.",
        "3": "Incluye Desayuno y Cena."
    }
    for key, value in meal_plan_options.items():
        print(f"{key}) {value}")

    meal_plan_choice_key = ask_input("Elige una opción para el régimen de comidas", "1")
    meal_plan = meal_plan_options.get(meal_plan_choice_key, "El precio de esta habitación no incluye desayuno ni servicio de comidas.")
    if meal_plan_choice_key not in meal_plan_options:
        print("Opción no válida, usando valor por defecto.")

    # --- Estructura del JSON basada en tu plantilla ---
    pass_data = {
      "formatVersion": 1,
      "passTypeIdentifier": "pass.com.tudominio.reservahotel",
      "teamIdentifier": "ABCDEFGHIJ",
      "webServiceURL": "https://example.com/passes/",
      "authenticationToken": "vxwxd7J8AlNNFPS8k0a0FfLPtAecvmprwruOQCrpF4uSMsmiK6qxSDFs",
      "organizationName": "Booking.com",
      "localizedDescription": "Reserva de Hotel",
      "logoText": "Booking.com",
      "foregroundColor": "rgb(255, 255, 255)",
      "backgroundColor": "rgb(0, 75, 150)",
      "labelColor": "rgb(200, 230, 255)",
      "generic": {
        "primaryFields": [
          {
            "key": "hotelName",
            "label": "Hotel",
            "value": hotel_name
          },
          {
            "key": "checkInDate",
            "label": "Check-in",
            "value": check_in_display
          },
          {
            "key": "checkOutDate",
            "label": "Check-out",
            "value": check_out_display
          }
        ],
        "secondaryFields": [
          {
            "key": "confirmation",
            "label": "Confirmación",
            "value": confirmation_number
          },
          {
            "key": "guestName",
            "label": "Huésped",
            "value": guest_name
          },
          {
            "key": "roomType",
            "label": "Tu Reserva",
            "value": f"{nights} {nights_text}, {room_type}"
          },
          {
            "key": "guests",
            "label": "Reservaste para",
            "value": num_guests
          }
        ],
        "auxiliaryFields": [
          {
            "key": "address",
            "label": "Ubicación",
            "value": hotel_address
          }
        ],
        "backFields": [
          {
            "key": "cancellationPolicyTitle",
            "label": "Política de Cancelación",
            "value": "Ten en cuenta que si cancelas, haces algún cambio o no te presentas, se te cobrará el precio total de la reserva."
          },
          {
            "key": "cancellationCharges",
            "label": "Cargos de Cancelación",
            "value": "Esta reserva no es reembolsable. No se pueden cambiar las fechas de estancia."
          },
          {
            "key": "totalPrice",
            "label": "Precio Total",
            "value": total_price
          },
          {
            "key": "breakfast",
            "label": "Régimen de comidas",
            "value": meal_plan
          }
        ]
      },
      "barcode": {
        "format": "PKBarcodeFormatQR",
        "message": confirmation_number,
        "messageEncoding": "iso-8859-1"
      }
    }

    # --- Generación del Archivo JSON ---
    json_output_filename = "pass.json"
    pkpass_output_filename = "reserva_hotel.pkpass"
    common_images = ["icon.png", "logo.png", "thumbnail.png", "strip.png"] # Imágenes estándar para el pase

    with open(json_output_filename, "w", encoding="utf-8") as f:
        json.dump(pass_data, f, indent=2, ensure_ascii=False)

    print(f"\n--- JSON '{json_output_filename}' generado exitosamente ---")
    
    # Crea el PKPASS
    create_pkpass_bundle(json_output_filename, pkpass_output_filename, common_images)

    print("\n--- Proceso Completado ---")
    print(f"El archivo PKPASS '{pkpass_output_filename}' ha sido creado.")
    print("¡Ya está listo para ser distribuido!")

if __name__ == "__main__":
    main()