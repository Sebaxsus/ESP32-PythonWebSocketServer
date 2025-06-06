#include <Arduino.h>
#include <TM1637.h>
#include <WebSocketsClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "Credentials.h"

#define CLK 18
#define DIO 19
#define pinSensor 34
#define pinLed 5

const char* websocket_server = "192.168.20.173"; // La direccion IPV4 de Mi pc
const uint16_t websocket_port = 5000;

static unsigned long lastSend = 0;
static unsigned long lastDisplayed = 0;
static unsigned long DangerSend = 0;

// Instancias
WebSocketsClient webSocket;
TM1637 display(CLK, DIO);

void SendData(int valorSensor) {
  StaticJsonDocument<200> doc;
  doc["event"] = "sensor_data";
  JsonObject data = doc.createNestedObject("data");
  data["valor"] = valorSensor;

  String mensaje;
  serializeJson(doc, mensaje);
  webSocket.sendTXT(mensaje);
  Serial.println("📤 Enviado: " + mensaje);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("❌ Desconectado del servidor");
      break;
    case WStype_CONNECTED:
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
  display.set(1); // Brillo de 0 a 7
  display.clearDisplay(); // Limpia el display

  // Iniciando la Conexion a WiFi
  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);

  Serial.println("Conectando a Wi-Fi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
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

  // Configurando y Inicializando el Led
  pinMode(pinLed, OUTPUT);
}

void loop() {

  webSocket.loop(); // Obligatorio para mantener la conexión

  unsigned long now = millis();

  int valorSensor = analogRead(pinSensor); // lee el valor del sensor

  if (valorSensor >= 600) {
    digitalWrite(pinLed, HIGH);

    if (now - DangerSend > 1000) {
      DangerSend = now;
      display.displayNum(valorSensor);
      SendData(valorSensor);
    }

  } else {
    // Apagar LED suavemente
    digitalWrite(pinLed, LOW);
  }
  // Cada segundo entra aqui
  if (now - lastDisplayed > 500) {
    lastDisplayed = now;
    // Mostrar en el display
    display.displayNum(valorSensor);

    // Cada 60 segundos desde el anterior envio entra aqui
    if (now - lastSend > 60000) {
      lastSend = now;
      SendData(valorSensor);
    }

  }

  delay(50); // Ajusta si quieres lectura más suave
}