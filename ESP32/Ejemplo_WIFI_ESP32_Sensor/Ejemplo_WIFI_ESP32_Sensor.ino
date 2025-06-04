#include <TM1637.h>
#include <WebSocketsClient.h>
#include <WiFi.h>
#include "Credentials.h"

#define CLK 18
#define DIO 19
#define pinSensor 34

const char* websocket_server = "192.168.20.173"; // La direccion IPV4 de Mi pc
const uint16_t websocket_port = 5000;

// Instancias
WebSocketsClient socket;
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

void webSocketEvent(socketIOmessageType_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case sIOtype_CONNECT:
      Serial.println("🔌 Conectado al servidor Socket.IO");
      isSocketIOConnected = true; // Actualizamos la bandera
      break;
    case sIOtype_DISCONNECT:
      Serial.println("❌ Desconectado del servidor");
      isSocketIOConnected = false; // Actualizamos la bandera
      break;
    case sIOtype_EVENT:
      Serial.printf("📩 Evento recibido: %.*s\n", length, payload);
      break;
    case sIOtype_ACK:
      Serial.printf("✅ ACK recibido: %s\n", payload);
      break;
    case sIOtype_ERROR:
      Serial.printf("🚨 Error de Socket.IO: %s\n", payload);
      break;
    case sIOtype_BINARY_EVENT:
      Serial.printf("📦 Evento binario recibido: %s\n", payload);
      break;
    case sIOtype_BINARY_ACK:
      Serial.printf("📦 ACK binario recibido: %s\n", payload);
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
  String url = "/socket.io/?EIO=4&t=" + String(millis());
  socket.begin(websocket_server, websocket_port, url.c_str());
  String ip = WiFi.localIP().toString();
  socket.onEvent(socketEvent);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.println();
  // Serial.println("Conectado a Wi-Fi!");
  // Serial.print("IP local: ");
  // Serial.println(WiFi.localIP());

  socket.loop(); // Obligatorio para mantener la conexión

  // Lógica de reconexión mejorada
  // Solo intenta reconectar si NO estamos ya conectados AHORA
  // Y si la librería NO está ya en proceso de conexión (isConnected puede ser true aunque no haya llegado el sIOEvent::Connect aun)
  // Añadimos un temporizador para no spamear begins
  static unsigned long lastReconnectAttempt = 0;
  const unsigned long reconnectInterval = 5000; // Intentar reconectar cada 5 segundos

  // Verificar si la conexión Socket.IO está activa por el evento de conexión
  if (!isSocketIOConnected) { // Si el evento CONNECT aún no se ha disparado
      if (!socket.isConnected()) { // Y si la conexión de Engine.IO no está activa
          // Permitir reintentos solo después de un intervalo de tiempo
          if (millis() - lastReconnectAttempt > reconnectInterval) {
              Serial.println("Estado: Conexión Engine.IO no activa o Socket.IO no conectada. Reintentando...");
              String url = "/socket.io/?EIO=4&t=" + String(millis());
              socket.begin(websocket_server, websocket_port, url.c_str());
              lastReconnectAttempt = millis(); // Actualizar el temporizador de reintento

              // *** PRUEBA DE BLOQUEO TEMPORAL (Solo para depuración, si es necesario) ***
              // Si aún no ves el POST/Upgrade en Wireshark, podrías activar esto
              // Pero úsalo con precaución, solo para esta prueba
              Serial.println("DEBUG: Pausando 100ms para permitir el handshake...");
              delay(100); // Dar un poco de tiempo para que la librería procese el OPEN/CONNECT
              Serial.println("DEBUG: Reanudando loop.");
          }
      }
  } else {
      // Si isSocketIOConnected es true, la conexión está establecida,
      // la lógica de desconexión la manejará socketIOEvent
      // y establecerá isSocketIOConnected a false si se desconecta.
  }

  int valorSensor = analogRead(pinSensor); // lee el valor del sensor
  Serial.print("Valor leído del sensor: ");
  Serial.println(valorSensor);

  // Mostrar en el display
  display.displayNum(valorSensor);

  static unsigned long lastTime = 0;
  if (isSocketIOConnected && (millis() - lastSendTime > interval)) {
    lastTime = millis();

    // Preparar y enviar el JSON
    String dataJson = "{\"valor\":" + String(valorSensor) + "}";
    String Payload = "[\"sensor_data\"," + dataJson + "]";

    
    socket.sendEVENT(Payload.c_str());
    Serial.println("Enviado: " + Payload);
  }

  delay(100); // Ajusta si quieres lectura más suave
}

// // Callback de eventos del servidor
// void socketEvent(socketIOmessageType_t type, uint8_t* payload, size_t length) {
//   switch (type) {
//     case sIO_CONNECTED:
//       Serial.println("🔌 Conectado al servidor Socket.IO");
//       break;
//     case sIO_DISCONNECTED:
//       Serial.println("❌ Desconectado del servidor");
//       break;
//     case sIO_EVENT:
//       Serial.printf("📩 Evento recibido: %.*s\n", length, payload);
//       break;
//     case sIO_PING:
//       // Pong automático
//       break;
//     case sIO_PONG:
//       Serial.println("📶 PONG recibido");
//       break;
//   }
// }

