#!/bin/bash

# --- Funciones Auxiliares ---

# Función para solicitar entrada al usuario
ask_input() {
    local prompt_text="$1"
    local default_value="$2"
    read -p "$prompt_text [$default_value]: " input_value
    echo "${input_value:-$default_value}"
}

# Función para solicitar fecha en formato YYYY-MM-DD
ask_date() {
    local prompt_text="$1"
    local default_date="$2"
    local date_format="+%a, %d %b %Y" # Ej: Lun, 19 May 2025
    local parsed_date=""

    while true; do
        read -p "$prompt_text [YYYY-MM-DD, default: $default_date]: " input_date
        input_date="${input_date:-$default_date}"

        # Intentar parsear la fecha
        parsed_date=$(date -d "$input_date" "$date_format" 2>/dev/null)

        if [[ -n "$parsed_date" ]]; then
            echo "$parsed_date"
            break
        else
            echo "Fecha inválida. Por favor, usa el formato YYYY-MM-DD."
        fi
    done
}

# Función para calcular días entre dos fechas (en Linux)
calculate_days() {
    local start_date_str="$1" # YYYY-MM-DD
    local end_date_str="$2"   # YYYY-MM-DD

    # Convertir fechas a segundos desde la época
    start_seconds=$(date -d "$start_date_str" +%s)
    end_seconds=$(date -d "$end_date_str" +%s)

    # Calcular la diferencia en segundos y convertir a días
    diff_seconds=$((end_seconds - start_seconds))
    diff_days=$((diff_seconds / 86400)) # 86400 segundos en un día

    echo "$diff_days"
}

# --- Recopilación de Datos ---

echo "--- Generador de JSON para Reserva de Hotel PKPASS ---"
echo ""

# Datos del Huésped
GUEST_NAME=$(ask_input "Nombre del Huésped" "Alvaro Torres F.")
CONFIRMATION_NUMBER=$(ask_input "Número de Confirmación de Reserva" "1234567890")

# Datos del Hotel
HOTEL_NAME=$(ask_input "Nombre del Hotel" "Hotel & Villas 7")
HOTEL_ADDRESS=$(ask_input "Dirección del Hotel" "Calle Siete, 98, Col. Agrícola Pantitlán, Iztacalco, 08100 Ciudad de México, México")
HOTEL_PHONE=$(ask_input "Teléfono de Contacto del Hotel" "+52 55 2235 4752")
HOTEL_EMAIL=$(ask_input "Email de Contacto del Hotel" "contacto@hotelvilllas7.com")

# Fechas
CURRENT_YEAR=$(date +%Y)
DEFAULT_CHECKIN_DATE=$(date -d "+7 days" +%Y-%m-%d) # Default a 7 días en el futuro
DEFAULT_CHECKOUT_DATE=$(date -d "+8 days" +%Y-%m-%d) # Default a 8 días en el futuro

CHECK_IN_DATE_RAW=$(ask_date "Fecha de Check-in" "$DEFAULT_CHECKIN_DATE")
CHECK_OUT_DATE_RAW=$(ask_date "Fecha de Check-out" "$DEFAULT_CHECKOUT_DATE")

# Asegurarse de que la fecha de salida sea posterior a la de entrada
while [[ "$(date -d "$CHECK_OUT_DATE_RAW" +%s)" -le "$(date -d "$CHECK_IN_DATE_RAW" +%s)" ]]; do
    echo "¡La fecha de Check-out debe ser posterior a la fecha de Check-in!"
    CHECK_OUT_DATE_RAW=$(ask_date "Fecha de Check-out" "$DEFAULT_CHECKOUT_DATE")
done

NIGHTS=$(calculate_days "$CHECK_IN_DATE_RAW" "$CHECK_OUT_DATE_RAW")

# Cantidad de Pasajeros
NUM_GUESTS=$(ask_input "Cantidad de Pasajeros" "2 adultos")

# Tipo de Habitación
echo ""
echo "--- Tipo de Habitación ---"
echo "1) Habitación Matrimonial"
echo "2) Habitación Single"
echo "3) Habitación Doble - 2 camas"
echo "4) Suite Ejecutiva"
echo "5) Otro (especificar)"
ROOM_CHOICE=$(ask_input "Elige una opción para el tipo de habitación" "3")

case $ROOM_CHOICE in
    1) ROOM_TYPE="Habitación Matrimonial";;
    2) ROOM_TYPE="Habitación Single";;
    3) ROOM_TYPE="Habitación Doble - 2 camas";;
    4) ROOM_TYPE="Suite Ejecutiva";;
    5) ROOM_TYPE=$(ask_input "Especifica el tipo de habitación" "Habitación Familiar");;
    *) ROOM_TYPE="Habitación Doble - 2 camas" && echo "Opción no válida, usando valor por defecto.";;
esac

# Régimen de comidas
echo ""
echo "--- Régimen de Comidas ---"
echo "1) El precio de esta habitación no incluye servicio de comidas."
echo "2) Incluye Desayuno."
echo "3) Incluye Desayuno y Cena."
MEAL_PLAN_CHOICE=$(ask_input "Elige una opción para el régimen de comidas" "1")

case $MEAL_PLAN_CHOICE in
    1) MEAL_PLAN="El precio de esta habitación no incluye servicio de comidas.";;
    2) MEAL_PLAN="Incluye Desayuno.";;
    3) MEAL_PLAN="Incluye Desayuno y Cena.";;
    *) MEAL_PLAN="El precio de esta habitación no incluye servicio de comidas." && echo "Opción no válida, usando valor por defecto.";;
esac

# Precios y Términos
TOTAL_PRICE=$(ask_input "Precio Total (ej: MXN 468.30)" "MXN 468.30")
IVA_AMOUNT=$(ask_input "Monto de IVA (ej: MXN 62.70)" "MXN 62.70")
CITY_TAX_AMOUNT=$(ask_input "Monto de Impuesto Municipal (ej: MXN 13.72)" "MXN 13.72")
CANCELLATION_POLICY=$(ask_input "Política de Cancelación Breve" "Esta reserva no es reembolsable. No se pueden cambiar las fechas de estancia.")
PIN_NUMBER=$(ask_input "Número PIN (opcional, para modificaciones)" "XXXX")

# Hora de Check-in/Check-out
CHECKIN_TIME=$(ask_input "Hora de Check-in (ej: de 15:00 a 22:00)" "de 15:00 a 22:00")
CHECKOUT_TIME=$(ask_input "Hora de Check-out (ej: de 11:00 a 12:00)" "de 11:00 a 12:00")

# -- Generación del JSON --

JSON_OUTPUT="pass.json"

cat << EOF > "$JSON_OUTPUT"
{
  "formatVersion": 1,
  "passTypeIdentifier": "pass.com.tudominio.reservahotel",
  "teamIdentifier": "ABCDEFGHIJ",
  "webServiceURL": "https://example.com/passes/",
  "authenticationToken": "vxwxd7J8AlNNFPS8k0a0FfLPtAecvmprwruOQCrpF4uSMsmiK6qxSDFs",
  "organizationName": "Booking.com",
  "localizedDescription": "Reserva de Hotel",
  "logoText": "${HOTEL_NAME}",
  "foregroundColor": "rgb(255, 255, 255)",
  "backgroundColor": "rgb(0, 75, 150)",
  "labelColor": "rgb(200, 230, 255)",
  "generic": {
    "headerFields": [
      {
        "key": "confirmation",
        "label": "Confirmación",
        "value": "${CONFIRMATION_NUMBER}"
      }
    ],
    "primaryFields": [
      {
        "key": "hotelName",
        "label": "Hotel",
        "value": "${HOTEL_NAME}"
      },
      {
        "key": "checkInDate",
        "label": "Check-in",
        "value": "${CHECK_IN_DATE_RAW}",
        "changeMessage": "Check-in: %@ (${CHECKIN_TIME})"
      },
      {
        "key": "checkOutDate",
        "label": "Check-out",
        "value": "${CHECK_OUT_DATE_RAW}",
        "changeMessage": "Check-out: %@ (${CHECKOUT_TIME})"
      }
    ],
    "secondaryFields": [
      {
        "key": "guestName",
        "label": "Huésped",
        "value": "${GUEST_NAME}"
      },
      {
        "key": "roomType",
        "label": "Tu Reserva",
        "value": "${NIGHTS} ${NIGHTS_TEXT}, ${ROOM_TYPE}"
      },
      {
        "key": "guests",
        "label": "Reservaste para",
        "value": "${NUM_GUESTS}"
      }
    ],
    "auxiliaryFields": [
      {
        "key": "address",
        "label": "Ubicación",
        "value": "${HOTEL_ADDRESS}"
      }
    ],
    "backFields": [
      {
        "key": "pinNumber",
        "label": "Número PIN",
        "value": "Mantén confidencial este número: ${PIN_NUMBER}. Puede usarse para modificar o cancelar tu reserva."
      },
      {
        "key": "hotelPhone",
        "label": "Teléfono Hotel",
        "value": "${HOTEL_PHONE}"
      },
      {
        "key": "hotelEmail",
        "label": "Contacto",
        "value": "${HOTEL_EMAIL}"
      },
      {
        "key": "cancellationPolicyTitle",
        "label": "Política de Cancelación",
        "value": "Ten en cuenta que si cancelas, haces algún cambio o no te presentas, se te cobrará el precio total de la reserva."
      },
      {
        "key": "cancellationCharges",
        "label": "Cargos de Cancelación",
        "value": "${CANCELLATION_POLICY}"
      },
      {
        "key": "totalPrice",
        "label": "Precio Total",
        "value": "${TOTAL_PRICE} (IVA: ${IVA_AMOUNT}, Impuesto municipal: ${CITY_TAX_AMOUNT})"
      },
      {
        "key": "breakfast",
        "label": "Régimen de comidas",
        "value": "${MEAL_PLAN}"
      },
      {
        "key": "instructions",
        "label": "Instrucciones",
        "value": "Por favor, presente este pase en la recepción al llegar. Para cualquier cambio o cancelación, contacte directamente al hotel o a Booking.com."
      }
    ]
  },
  "barcode": {
    "format": "PKBarcodeFormatQR",
    "message": "${CONFIRMATION_NUMBER}",
    "messageEncoding": "iso-8859-1"
  }
}
EOF

# Ajustar el texto de "noches" singular/plural
if [[ "$NIGHTS" -eq 1 ]]; then
    NIGHTS_TEXT="noche"
else
    NIGHTS_TEXT="noches"
fi

# Reemplazar en el JSON la parte de las noches (se hace después porque necesitamos NIGHTS_TEXT)
sed -i "s|${NIGHTS} ${NIGHTS_TEXT}|${NIGHTS} ${NIGHTS_TEXT}|g" "$JSON_OUTPUT"


echo ""
echo "--- JSON generado exitosamente ---"
echo "El archivo 'pass.json' ha sido creado en el directorio actual."
echo "Ahora puedes usar este archivo junto con tus imágenes PNG para crear el .pkpass."
echo ""
echo "Recuerda: Si vas a usarlo en Google Wallet, asegúrate de tener las imágenes 'logo.png', 'icon.png', 'thumbnail.png' y 'strip.png' en la misma carpeta."
echo "Luego, comprime todos los archivos (solo los archivos, no la carpeta) y renombra el .zip a .pkpass."
echo "$ zip -r reserva.pkpass pass.json icon.png logo.png"
