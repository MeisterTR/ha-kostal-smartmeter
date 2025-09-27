# Ksem API Dokumentation

> Diese Doku enthält alle HTTP-/WebSocket-Endpunkte der Ksem-Komponente
---

## Authentifizierung & Benutzer

### Login

- **Methode:** POST
- **Pfad:** `/api/login`
- **Request:**
    ```json
    {
      "user": "admin",
      "password": "geheim"
    }
    ```
- **Response:**
    ```json
    {
      "access_token": "abcdefg1234567",
      "token_type": "Bearer",
      "expires_in": 3600
    }
    ```
- **Hinweis:**  
  Der Token ist im Header `Authorization: Bearer <token>` anzugeben.

---



## Api Abfragen

## Geräteeinstellungen
- Kurzbeschreibung: Abfrage der aktuellen Geräteeinstellungen inklusive Netzwerk- und Firmware-Informationen.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "Mac": "AA:BB:CC:DD:EE:FF",
      "Serial": "XXXXXXXX",
      "ProductName": "KOSTAL Smart Energy Meter",
      "DeviceType": "hw0100",
      "FirmwareVersion": "2.6.2",
      "hostname": "DEVICE_HOST",
      "network": {
        "ip": "XXX.XXX.XXX.XXX",
        "mask": "255.255.255.0",
        "gateway": "XXX.XXX.XXX.XXX",
        "dns": [
          "XXX.XXX.XXX.XXX"
        ]
      }
    }
    ```

## Geräteeinstellungen Gerätestatus
- Kurzbeschreibung: Abfrage des aktuellen Gerätestatus innerhalb der Geräteeinstellungen.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/devicestatus`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "status": "idle"
    }
    ```


## Geräteeinstellungen Geräteauslastung
- Kurzbeschreibung: Abfrage der aktuellen Systemauslastungs- und Speicherstatistiken des Geräts.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/deviceusage`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "CpuLoad": 59,             // in %
      "CpuTemp": 73,             // in °C
      "RamFree": 138064,         // in KB
      "RamTotal": 248432,        // in KB
      "FlashAppFree": 231806976, // in Bytes
      "FlashAppTotal": 249469952,// in Bytes
      "FlashDataFree": 1207975936,// in Bytes
      "FlashDataTotal": 1300037632// in Bytes
    }
    ```  

## Geräteeinstellungen Lokale Zeit
- Kurzbeschreibung: Abfrage der aktuellen lokalen Zeit des Geräts und NTP-Synchronisationsstatus.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/local-time`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "time": 1752270150.8175027, // in Sekunden seit Unix-Epoche
      "ntp_synced": true          // boolean, NTP-Synchronisation erfolgreich
    }
    ```

## Geräteeinstellungen Netzwerk
- Kurzbeschreibung: Abfrage des Netzwerkmodus, Hostnamen und UPnP-Status des Geräts.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/network`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "mode": "dhcp",
      "hostname": "DEVICE_HOSTNAME",
      "upnpavailable": true,
      "upnpstatus": true
    }
    ```  


## Geräteeinstellungen Serielle Schnittstellen
- Kurzbeschreibung: Abfrage der konfigurierten seriellen Schnittstellen und zugewiesenen Anwendungen.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/serial-interfaces`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    [
      {
        "name": "APP2",
        "app": "evse-kostal"
      },
      {
        "name": "APP1",
        "app": "modbus"
      }
    ]
    ```  

## Geräteeinstellungen SMTP Konfiguration
- Kurzbeschreibung: Abfrage der aktuellen SMTP-Einstellungen des Geräts.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/smtp/config`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "recipient": "",
      "server": "",
      "port": 0,
      "tls": false,
      "authentication": false,
      "username": "",
      "password": ""
    }
    ```  

## Geräteeinstellungen Zeitkonfiguration
- Kurzbeschreibung: Abfrage der aktuellen Zeit-, NTP- und Zeitzoneneinstellungen des Geräts.  
- **Methode:** GET  
- **Pfad:** `/api/device-settings/time/config`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "time": null,
      "ntp": {
        "enable": true
      },
      "timezone": "Europe/Berlin",
      "invalid": false
    }
    ```

## Health-Check Benachrichtigungen – API Anfrage
- **Kurzbeschreibung:** Liefert eine Liste von System-/Update-Benachrichtigungen (z. B. Firmware-Erfolg/Fehlschlag) des Geräts.  
- **Methode:** GET  
- **Pfad:** `/api/health-check/notifications`  
- **Header:**  
  `Authorization: Bearer <token>`

- **Response:**
```json
[
  {
    "app": "updater",
    "category": "info",
    "message": "device-settings.notifications.fwupgradesuccess",
    "msgtext": "<KSEM_FIRMWARE_DATEI_XYZ>.raucb",
    "timestamp": 1725597542,
    "read": true
  },
  {
    "app": "evse-kostal",
    "category": "error",
    "message": "device-settings.notifications.fwupgradesuccess",
    "msgtext": "<KSEM_FIRMWARE_DATEI_2_7_0>.raucb",
    "timestamp": 1758860113,
    "read": false
  }
]
```
## Health-Check Benachrichtigungen – Gelesen markieren
- **Kurzbeschreibung:** Markiert alle ungelesenen Benachrichtigungen als gelesen.  
- **Methode:** POST  
- **Pfad:** `/api/health-check/notifications/unread`  
- **Header:**  
  `Authorization: Bearer <token>`

- **Response:**  
  **Status Code:** `204 No Content`  
  (Es wird kein Response-Body zurückgegeben)

  
## E-Mobility Lade-Modus Konfiguration
- Kurzbeschreibung: Konfiguration des Lade-Modus und zugehöriger Quotenparameter für das E-Mobility-System.  
- **Methode:** PUT  
- **Pfad:** `/api/e-mobility/config/chargemode`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Request Body:**  
    ```json
    {
      "mode": "hybrid",                      // "grid" | "pv" | "hybrid" | "lock"
      "mincharginpowerquota": 100,           // in %, minimale Ladeleistung (Hybrid-Modus)
      "minpvpowerquota": 30,                 // in %, minimale PV-Leistung (Hybrid-Modus)
      "lastminchargingpowerquota": 100,      // in %, zuletzt verwendete Ladeleistung
      "lastminpvpowerquota": 30,             // in %, zuletzt verwendete PV-Leistung
      "controlledby": 0                      // 0 = intern gesteuert, 1 = extern gesteuert
    }
    ```  
- **Response:**  
    HTTP 204 No Content  

## E-Mobility Überlastschutz Konfiguration
- Kurzbeschreibung: Abfrage der aktuellen Überlastschutz-Konfiguration des E-Mobility-Systems.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/config/overloadprotection`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "grid_type": 3,                  // 1 = Einphasen-Netz, 3 = Dreiphasen-Netz
      "main_fuse": [
        63000,                         // in mA pro Phase
        63000,
        63000
      ],
      "deactivate_frontend_cfg": true, // boolean, Frontend-Konfiguration deaktiviert
      "inconsistent_cfg": false        // boolean, Konfigurationskonsistenz in Ordnung
    }
    ```
## E-Mobility Phasenumschaltung
- Kurzbeschreibung: Abfrage und Konfiguration des Phasenumschaltungsmodus im E-Mobility-System.  
- **Pfad:** `/api/e-mobility/config/phaseswitching`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Methoden:**
  - **GET**
    - **Response:**
      ```json
      {
        "phase_usage": 0 // 0 = Standard 3 Phasen, 1 = Eine Phase, 2 = Automatisch
      }
      ```
  - **PUT**
    - **Request Body:**
      ```json
      {
        "phase_usage": 2 // 0 = Standard 3 Phasen, 1 = Eine Phase, 2 = Automatisch
      }
      ```
    - **Response:**  
      HTTP 200 OK  

## E-Mobility Probing-Parameter
- Kurzbeschreibung: Abfrage der minimalen Step-Index-Konfiguration für die Probing-Parameter des E-Mobility-Systems.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/config/probingparameters`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "min_step_index": 0  // integer, minimaler Schrittindex für Probing-Parameter
    }
    ```  

## E-Mobility EV-Parameterliste
- Kurzbeschreibung: Abfrage der aktuellen Parameter für alle angeschlossenen E-Fahrzeuge (Strombegrenzung, Phasennutzung, Probing-Status).  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/evparameterlist`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "<ev_connection_id>": {
        "min_current": 0,            // minimaler Stromwert in mA
        "max_current": 0,            // maximaler Stromwertin mA
        "phases_used": {
          "total": false,            // alle Phasen genutzt
          "l1": false,               // Phase L1 genutzt
          "l2": false,               // Phase L2 genutzt
          "l3": false                // Phase L3 genutzt
        },
        "probing_successful": false  // Probing erfolgreich
      }
    }
    ```  
## E-Mobility EVSE-Limit
- Kurzbeschreibung: Abfrage des aktuellen Limits für die Anzahl aktiver EVSE-Anschlüsse.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/evselimit`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "limit": 1  // integer, maximales Limit an gleichzeitig aktiven EVSE-Anschlüssen
    }
    ```  

## E-Mobility Phasenutzung
- Kurzbeschreibung: Konfiguration des Phasenumschaltungsmodus im E-Mobility-System.  
- **Methode:** PUT  
- **Pfad:** `/api/e-mobility/phaseusage`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Request Body:**  
    ```json
    {
      "phase_usage": 2 // 0 = Standard 3 Phasen, 1 = Eine Phase, 2 = Automatisch
    }
    ```  
- **Response:**  
    HTTP 200 OK  
## E-Mobility EVSE-Liste
- Kurzbeschreibung: Abfrage der registrierten EVSE-Anschlüsse mit deren Konfiguration und Status.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/evselist`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    [
      {
        "label": "Wallbox",
        "uuid": "<WALLBOX_ID>",      // anonymisiert
        "parent_uuid": "<WALLBOX_ID>", // anonymisiert, identisch zur uuid
        "topic": "gdr/local/config/kostal/evse",
        "ip": "",
        "manufacturer": "kostal",
        "slave_addr": "100",
        "modbus_interface": "APP2",
        "product": "",
        "number_of_outlets": "1",
        "outlet": "0",
        "state": "stateConnected",
        "model": "ac-3_7_11",
        "updateable": true,
        "supports_phase_switching": true,
        "phase_usage_state": 3,
        "phase_usage_result": 0,
        "eebus": {
          "i_max": 0,
          "i_min": 0,
          "phases_used": 0
        }
      }
    ]
    ```  

## E-Mobility Probing Aktuelle Stromschritte
- Kurzbeschreibung: Abfrage der verfügbaren Strom-Schritte für das Probing-Verfahren.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/probing/currentsteps`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    [
      6000,   // in mA
      8000,   // in mA
      10000,  // in mA
      13000,  // in mA
      16000   // in mA
    ]
    ```  

## E-Mobility Zustand
- Kurzbeschreibung: Abfrage des aktuellen Betriebszustands des E-Mobility-Systems.  
- **Methode:** GET  
- **Pfad:** `/api/e-mobility/state`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "EvChargingPower": {
        "total": 0,  // in mW
        "l1": 0,     // in mW
        "l2": 0,     // in mW
        "l3": 0      // in mW
      },
      "CurtailmentSetpoint": {
        "total": 0,  // in mA
        "l1": 0,     // in mA
        "l2": 0,     // in mA
        "l3": 0      // in mA
      },
      "OverloadProtectionActive": true,  // boolean
      "GridPowerLimit": {
        "Active": false,  // boolean
        "Power": 0        // in W
      },
      "PVPowerLimit": {
        "Active": false,  // boolean
        "Power": 0        // in W
      }
    }
    ```  

## EVSE-Kostal Gerät
- Kurzbeschreibung: Abfrage des Bindungsstatus der EVSE-Kostal Schnittstellen.  
- **Methode:** GET  
- **Pfad:** `/api/evse-kostal/device`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "APP2": "bound"
    }
    ```  

## EVSE-Kostal EVSE Details
- Kurzbeschreibung: Abfrage der Geräte­details der einzelnen Wallbox.  
- **Methode:** GET  
- **Pfad:** `/api/evse-kostal/evse/<WALLBOX_ID>/details`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "serial": "<SERIAL_NUMBER>",               // Seriennummer anonymisiert
      "model": "ac-3_7_11",
      "version": "FW: 2023.21.11024-20; COM: 1.03",
      "hardware": "0003",
      "max_install_current": 63000,               // in mA
      "updateable": true,
      "phase_switching_option": 2,                // 3 und 1 Phase
      "supports_phase_switching": true
    }
    ```  

## Kostal Energyflow Konfiguration
- Kurzbeschreibung: Abfrage der aktuellen Energiefluss-Konfiguration des Kostal-Energieflussmoduls.  
- **Methode:** GET  
- **Pfad:** `/api/kostal-energyflow/configuration`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Response:**  
    ```json
    {
      "enabled": false,                     // boolean, Energiefluss-Modul aktiviert
      "selected_controller_type": "legacy", // string, gewählter Steuerungstyp
      "powerreduction": {
        "enabled": false,                   // boolean, Leistungsreduzierung aktiviert
        "limit": 0,                         // integer, Reduktionsgrenze (W)
        "interval": 1,                      // integer, Intervall zur Leistungsmessung (min)
        "avg_interval": 35,                 // integer, Intervall zur Mittelwertbildung (min)
        "avg_teridian": 15,                 // integer, Teridian-Intervall für Tagesmittel (min)
        "maxpower": 0                       // integer, maximale Leistung nach Reduzierung (W)
      },
      "batteryusage": true,                 // boolean, Batterienutzung erlaubt
      "version": 5                          // integer, Konfigurationsversion
    }
    ```

## Kostal Batterie-Nutzung bei Solar Pure
- Kurzbeschreibung: Aktivieren oder Deaktivieren der Batterienutzung im Solar Pure-Modus.  
- **Methode:** PUT  
- **Pfad:** `/api/kostal-energyflow/configuration/batteryusage`  
- **Header:**  
    `Authorization: Bearer <token>`  
- **Request Body:**  
    ```text
    true  // oder false
    ```  
- **Response:**  
    HTTP 204 No Content  






---
## WebSocket-Verbindung – Authentifizierung

Beim Aufbau der WebSocket-Verbindung muss
1. der **Token im HTTP-Header** (`Authorization: Bearer <token>`) gesendet werden
2. **direkt nach dem Verbindungsaufbau** eine Nachricht mit dem exakten Inhalt  
   `"Bearer <token>"`  
   (also als reiner String, **nicht** als JSON!)  
   an den Server geschickt werden.

---

**Schritte:**

1. **Verbindung aufbauen:**  
   - Sende HTTP-Header:  
     ```
     Authorization: Bearer <access_token>
     ```
2. **Direkt nach Verbindungsaufbau:**  
   - Sende als **erste Nachricht** über die WS-Verbindung:  
     ```
     Bearer <access_token>
     ```
     *(Ohne Anführungszeichen, exakt mit Leerzeichen dazwischen, reiner String!)*

3. **Nach erfolgreicher Authentifizierung:**  
   - Empfang der Event- oder Statusdaten als Protobuf (binary) oder JSON.

---

### Pseudocode

```text
1. Open WebSocket to ws://<host>/api/data-transfer/ws/protobuf/gdr/local/values/KSEM-001-WB01/evse
2. Send header: Authorization: Bearer <token>
3. After connect, send string: "Bearer <token>"
4. Wait for incoming data
````
## WebSocket: Wallbox Live-Werte

**Pfad:**  
`ws://<host>/api/data-transfer/ws/protobuf/gdr/local/values/+/evse`
### Beschreibung & Datenstruktur

- Die Verbindung liefert alle aktuellen Messwerte und Statusdaten der jeweiligen Wallbox(en) in **Protobuf-Binärformat**.
- Die Nachrichten werden nach Decodierung (im Frontend via `gdr.GDRs.decode(...)`) in einem **Dictionary `GDRs`** abgelegt.
- **Jede Wallbox (EVSE) wird als eigenes Objekt gespeichert, Key ist die UUID:**


```json
{
"GDRs": {
  "0b6bef8f-c578-4ab3-9ce2-a05418f7ca3": {
    "id": "0b6bef8f-c578-4ab3-9ce2-a05418f7fca3",      // Wallbox-UUID
    "status": 1,                                       // Statuscode (z. B. 1 = ready, 2 = charging, etc.)
    "timestamp": 1752254953,                           // Unix-Timestamp (Sekunden)
    "values": {                                        // Messwerte, meist OBIS-Code als Key
      "1-0:32.4.0*255": 229,                           // Beispiel: Spannung (V)
      "1-0:31.7.0*255": 16,                            // Beispiel: Strom (A)
      ...
    },
    "flexValues": {                                    // Spezialwerte, als Key meist Klartext-String
      "evse_error_code": {
        // Ggf. Fehlerdetails als Objekt, sonst leer bei kein Fehler
      },
      ...
    }
  },
  ...
}
}
```


## WebSocket: Wallbox State-Stream (JSON)

**Pfad:**  
`ws://<host>/api/data-transfer/ws/json/json/local/evse/+/state`
(`+` steht für die jeweilige Wallbox-UUID bei Plus werden alle gesendet)

---

### Beschreibung

- Überträgt Echtzeit-Statusänderungen der jeweiligen Wallbox(en) als kompaktes JSON-Objekt.
- Für jede State-Änderung oder bei bestimmten Ereignissen wird eine Nachricht gesendet.

---

### Beispiel für empfangene Nachricht

```json
{
  "topic": "json/local/evse/0b6bef8f-c578-4ab3-9ce3-a05418f7cc3/state",
  "msg": {
    "evse-id": "0b6bef8f-c578-4ab3-9ce3-a05418f7fcc3",
    "parentState": "",
    "state": "stateConnected"
  }
}
```

## WebSocket: Charge-Mode-Stream (Wallboxen)

**Pfad:**  
`ws://<host>/api/data-transfer/ws/json/json/local/config/e-mobility/chargemode`

### Beschreibung

- Dieser Stream überträgt in Echtzeit den aktuellen Lademodus und zugehörige Steuerparameter für die Wallbox(en).
- Eine Nachricht wird gesendet, wenn sich der Modus oder eine der Quoten-Einstellungen ändert (z. B. durch Benutzeraktion oder externe Steuerung).
- Der Channel liefert keine Messwerte, sondern ausschließlich die aktuell eingestellte Betriebsart und Steuerinformationen für den Lademodus.

### **Beispiel für empfangene Nachricht**

```json
{
  "topic": "json/local/config/e-mobility/chargemode",
  "msg": {
    "mode": "lock",
    "mincharginpowerquota": 0,
    "minpvpowerquota": 0,
    "lastminchargingpowerquota": 100,
    "lastminpvpowerquota": 30,
    "controlledby": 0
  }
}
