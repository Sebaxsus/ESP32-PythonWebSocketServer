# En construccion

## Descipción.

## Observaciones.

> [!NOTE]
>
> Probando la duración de bateria y consumo del ESP32 teniendo:
> 1. LED Rojo con una resistencia de 220 Ohms.
> 2. Sensor de GAS MQ-40.
> 3. ESP32 usando el Modulo WIFI Integrado.
>
> Se concluye que con una Bateria de 10000 mAh a 3.7V
> -- Sebaxsus

> [!NOTE]
>
> Especificaciones de la bateria externa
> 
> 10000 mili Amperios hora - mAh
> Power: 37 Watts hora - Wh
> Input: 5 Voltios / 2 Amperios - 5V/2A
> OutPut: 5 Voltios / 2 Amperios - 5/2A
> Letras Chinas: 6800 mili Amperios hora - mAh


## Tabla de contenidos

1. Descripción General.
2. Observaciones.
3. Tabla de contenidos.
4. Instalación.
5. Configuración.
6. Diagramas.
7. Autor.
8. Licencia.

## Instalación.

**Para instalar el Programa se necesita**
- **Arduino:**
    1. [Arduino IDE](https://www.arduino.cc/en/software/).
    2. Instalar en Arduino el Modulo de compatibilidad con el [ESP32 de Expressif](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html#installing-using-arduino-ide)
        - [!IMPORTANT]
        Para hacer esto toca configurar arudino con un link externo arriba esta el Link de la guia de Instalacion y configuracion por ExpressIf, Ademas de esto dentro de Arduino en la Seccion de Boards Manager toca agregar **ESP32 By ExpressIf**.
    3. Instalar la Libreria para manejar los **WebSockets INET y STREAMS** por Protocolo TCP LLamada [WebSockets By Marcus Sattler](https://github.com/Links2004/arduinoWebSockets/tree/master/src).
    4. Instalar la Libreria para manejar el Modulo 7 Segmentos de 4 Llamado [TM1637 By Avishay Orpaz](https://github.com/avishorp/TM1637).
- **Python (Servidor):**
    1. [Python 3.12^](https://www.python.org/downloads/).
    2. **Opcional:**
        - Entorno Virtual: [UV](https://github.com/astral-sh/uv/blob/main/README.md).

## Configuracion.

No es necesario, Lo unico es si se va usar UV Tenerlo Instalado y dentro de el PATH de la Maquina para que la terminal entianda el comando.

```bash
uv -venv Nombre_De_El_Entorno_Virtual
cd Nombre_De_El_Entorno_Virtual
uv pip install -r requiremets.txt
Ó
uv pip sync requiremets.txt
```

## Diagramas

- [ ] Por hacer 👍.

## Autor

[Sebaxsus](https://github.com/Sebaxsus).

## Licencia

[MIT License](./LICENSE)
