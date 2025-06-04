#include <TM1637.h>
#include <WebSocketsClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "Credentials.h"

#define CLK 18
#define DIO 19
#define pinSensor 34

const char* websocket_server = "192.168.20.173"; // La direccion IPV4 de Mi pc
const uint16_t websocket_port = 5000;

// Instancias
WebSocketsClient webSocket;
TM1637 display(CLK, DIO);

unsigned long lastSendTime = 0;
const unsigned long interval = 2000;  // cada minuto

// Bandera para saber si Socket.IO está realmente conectado (después del sIOEvent::Connect)
bool isSocketIOConnected = false;

void mostrarNumero(int numero) {
  numero = constrain(numero, 0, 9999);
  display.display(0, numero / 1000);
  display.display(1, (numero / 100) % 10);
  display.display(2, (numero / 10) % 10);
  display.display(3, numero % 10);
}
// Los eventos de la Lib WebSockets padre de WebSocketsClient
// typedef enum {
//     WSC_NOT_CONNECTED,
//     WSC_HEADER,
//     WSC_BODY,
//     WSC_CONNECTED
// } WSclientsStatus_t;

// typedef enum {
//     WStype_ERROR,
//     WStype_DISCONNECTED,
//     WStype_CONNECTED,
//     WStype_TEXT,
//     WStype_BIN,
//     WStype_FRAGMENT_TEXT_START,
//     WStype_FRAGMENT_BIN_START,
//     WStype_FRAGMENT,
//     WStype_FRAGMENT_FIN,
//     WStype_PING,
//     WStype_PONG,
// } WStype_t;

// typedef enum {
//     WSop_continuation = 0x00,    ///< %x0 denotes a continuation frame
//     WSop_text         = 0x01,    ///< %x1 denotes a text frame
//     WSop_binary       = 0x02,    ///< %x2 denotes a binary frame
//                                  ///< %x3-7 are reserved for further non-control frames
//     WSop_close = 0x08,           ///< %x8 denotes a connection close
//     WSop_ping  = 0x09,           ///< %x9 denotes a ping
//     WSop_pong  = 0x0A            ///< %xA denotes a pong
//                                  ///< %xB-F are reserved for further control frames
// } WSopcode_t;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("❌ Desconectado del servidor");
      isSocketIOConnected = false; // Actualizamos la bandera
      break;
    case WStype_CONNECTED:
      Serial.println("🔌 Conectado al servidor Socket.IO");
      isSocketIOConnected = true; // Actualizamos la bandera

      Serial.printf("🔌 Conectado a: %s\n", payload);
      webSocket.sendTXT("ESP32 conectado!");
      
      break;
    case WStype_TEXT: {
      Serial.printf("📩 Mensaje recibido: %.*s\n", length, payload);
      break;
    }
    case WStype_PING:
      Serial.println("📡 Ping recibido del servidor");
      break;
    default:
      Serial.printf("❓ Tipo de evento desconocido: %d\n", type);
      break;
  }
}

void setup() {
  Serial.begin(115200);
  Serial.print("WebSockets Library Version: ");
  Serial.println(WEBSOCKETS_VERSION_INT);

  // Inicializando el Display
  display.set(2); // Brillo de 0 a 7
  display.clearDisplay(); // Limpia el display

  // Iniciando la Conexion a WiFi
  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);

  Serial.println("Conectando a Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando.");
    Serial.print(".");
  }
  delay(5000);
  Serial.println();
  Serial.println("Conectado a Wi-Fi!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());

  // Socket.IO
  // String url = "/socket.io/?EIO=4&t=" + String(millis());
  webSocket.begin(websocket_server, websocket_port, "/sensor");
  String ip = WiFi.localIP().toString();
  webSocket.onEvent(webSocketEvent);

  webSocket.setReconnectInterval(5000);
}

void loop() {

  webSocket.loop(); // Obligatorio para mantener la conexión

  static unsigned long lastSend = 0;
  static unsigned long lastDisplayed = 0;
  // Cada segundo entra aqui
  if (millis() - lastDisplayed > 1000) {
    lastDisplayed = millis();

    int valorSensor = analogRead(pinSensor); // lee el valor del sensor
    // Mostrar en el display
    display.displayNum(valorSensor);

    // Cada 60 segundos desde el anterior envio entra aqui
    if (millis() - lastSend > 60000) {
      lastSend = millis();
      StaticJsonDocument<200> doc;
      doc["event"] = "sensor_data";
      JsonObject data = doc.createNestedObject("data");
      data["valor"] = valorSensor;

      String mensaje;
      serializeJson(doc, mensaje);
      webSocket.sendTXT(mensaje);
      Serial.println("📤 Enviado: " + mensaje);
    }

  }

  delay(50); // Ajusta si quieres lectura más suave
}

// if (!err) {
//   const char* evt = doc["event"];
//   if (strcmp(evt, "sensor_data") == 0) {
//     int valor = doc["data"]["valor"];
//     Serial.println("Valor recibido del sensor: %d\n", valor);
//   }
// }