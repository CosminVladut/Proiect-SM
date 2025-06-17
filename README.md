# Smart Home – Sistem integrat de monitorizare și control

**Student:** Spînu Cosmin-Vlăduț  
**Grupa:** 1311A  
**Email:** cosmin-vladut.spinu@student.tuiasi.ro

## Motivația alegerii temei

Locuințele inteligente sunt tot mai populare, iar integrarea senzorilor și automatizarea funcțiilor precum ventilația, detecția incendiilor sau a intrușilor aduce un plus de siguranță și confort. Acest proiect combină electronica, programarea și dezvoltarea web într-un sistem extensibil și aplicabil în scenarii reale.

## Rezumat

Sistem bazat pe **Raspberry Pi Zero** care monitorizează și controlează în timp real:

- Temperatură și umiditate (DHT11)
- Incendii (senzor flacără + MQ135 pentru calitate aer)
- Intruziuni (HC-SR04 + PIR)
- Actuatori: motor DC (ventilare), pompă de apă (stingere), buzzer (alarmă)

Include o **interfață web (Flask)** pentru:

- Vizualizare stări senzori
- Configurare parametri: temperatură maximă, distanță prag, mod motor, email alertă

## Cerințe

### Funcționale:
- Măsurare continuă temperatură și umiditate
- Control motor DC (auto/manual)
- Detecție incendiu și activare pompă
- Detecție intruși și activare buzzer
- Alerte email
- Interfață web interactivă

### Non-funcționale:
- Stabilitate comunicație senzori-actuatori
- Răspuns în timp real
- Securitate minimă Flask + email
- Ușurință utilizare UI

## Hardware

| Componentă               | Funcție                          | Pin GPIO |
|--------------------------|----------------------------------|----------|
| Raspberry Pi             | Control principal                | -        |
| DHT11                    | Temperatură + Umiditate          | D4       |
| Motor DC                 | Ventilație                       | 3        |
| Pompă de apă             | Stingere incendiu                | 2        |
| Senzor flacără           | Detecție foc                     | 22       |
| MQ135 (calitate aer)     | Detecție gaz/fum                 | 10       |
| HC-SR04 (ultrasonic)     | Distanță/intruziuni              | TRIG 17, ECHO 27 |
| PIR (mișcare)            | Detecție mișcare                 | 9        |
| Buzzer                   | Alarmă sonoră                    | 11       |

## Software

- **Python 3**, **Flask** – backend web
- **RPi.GPIO**, **adafruit_dht** – GPIO control
- **smtplib**, **email.mime** – alerte email
- **JavaScript (fetch API)** – UI dinamic

## Arhitectură

- Thread principal `monitor()` – citește senzori, actualizează stare, controlează actuatoare, trimite emailuri
- Server Flask – servește UI + API `/status` și `/set`
- Stare salvată într-un dicționar `state` (temp, umiditate, mod motor etc.)

## Interfață Web (Dashboard)

- **HTML**: valori senzori, formular configurare
- **JavaScript**: actualizare UI la 500ms, POST la `/set` cu noile setări

## Scenarii de Test

1. **Ventilare auto/manual**:
    - În modul auto, motorul pornește automat peste temperatura setată
    - În manual, poate fi pornit cu checkbox

2. **Incendiu**:
    - Simulare foc → pompă activată + email „🔥 Fire Alert Detected!”

3. **Intruziune**:
    - Mișcare sau obiect detectat → buzzer + email „🚨 Intruder Alert Detected!”

## Probleme întâmpinate

- **Blocaje DHT11**: retry & timeout + valori default
- **Fals pozitiv incendiu**: verificare dublă (flacără + gaz)

## Ce înveți replicând

- Programare GPIO & threading în Python
- Citire senzori & debounce hardware
- Dezvoltare web cu Flask + JS
- Trimitere emailuri SMTP cu MIME
- Arhitectură completă IoT + UI

## Bibliografie

- [Adafruit DHT11 Guide](https://learn.adafruit.com/dht)
- [RPi.GPIO Examples](https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/)
- Miguel Grinberg – *Flask Web Development*
- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html)
- [HC-SR04 Tutorial](https://thepihut.com/blogs/raspberry-pi-tutorials/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi)
