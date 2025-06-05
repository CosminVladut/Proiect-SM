import time
import board
import adafruit_dht
import datetime
from RPi import GPIO
from threading import Thread, Lock
from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---- PINS ----

PUMP_PIN = 2
DC_MOTOR_PIN = 3
TEMP_SENSOR_READ_PIN = board.D4
DISTANCE_SENSOR_TRIG_PIN = 17
DISTANCE_SENSOR_ECHO_READ_PIN = 27
FIRE_SENSOR_READ_PIN = 22
GAS_SENSOR_READ_PIN = 10
MOTION_SENSOR_READ_PIN = 9
BUZZER_PIN = 11

# ---- SETUP THE PINS AND SENSORS-----

GPIO.setup([PUMP_PIN, DC_MOTOR_PIN, DISTANCE_SENSOR_TRIG_PIN, BUZZER_PIN], GPIO.OUT, initial = GPIO.LOW)
GPIO.setup([DISTANCE_SENSOR_ECHO_READ_PIN, FIRE_SENSOR_READ_PIN, GAS_SENSOR_READ_PIN, MOTION_SENSOR_READ_PIN], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

sensor = adafruit_dht.DHT11(TEMP_SENSOR_READ_PIN)

# ---- STATE VARIABLE FOR THE OPTIONS -----

state = {
        "motor_mode" : "auto", # manual
        "home_mode" : "home", # away
        "manual_motor_start" : False,
        "fire_detected" : False,
        "intruder_detected" : False,
        "temp" : 0,
        "selected_maximum_temp" : 30,
        "selected_should_be_distance" : 15,
        "humidity" : "0%",
        "receiver_email" : "vladutcosmin321@outlook.com"
        }

lock = Lock()

# ----- GATHER DATA -----

def read_temp_and_humidity():
    global sensor
    try:
        if sensor.temperature is not None and sensor.humidity is not None:
            return round(sensor.temperature, 2), str(round(sensor.humidity, 2)) + "%"
        else:
            return -100, -100
    except Exception as error:
        print(error.args[0])
        return -100, -100

def read_distance():
    GPIO.output(DISTANCE_SENSOR_TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(DISTANCE_SENSOR_TRIG_PIN, False)

    start = time.time()
    while GPIO.input(DISTANCE_SENSOR_ECHO_READ_PIN) == 0:
        start = time.time()
    while GPIO.input(DISTANCE_SENSOR_ECHO_READ_PIN) == 1:
        stop = time.time()

    duration = stop - start
    distance = round(duration * 17150, 2)
    return distance

# ----- SEND EMAIL -----

def send_alert_email(subject, body, receiver_email):
    sender_email = "cosminspanu464@gmail.com"
    password = "otqxyjbonzllvpuq"  

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

# ----- MONITOR -----

def monitor():
    prev_fire_detected = False
    prev_intruder_detected = False

    while 1:
        with lock:
            state["temp"], state["humidity"] = read_temp_and_humidity()
            distance = read_distance()
 
            state["fire_detected"] = GPIO.input(FIRE_SENSOR_READ_PIN) == GPIO.LOW and GPIO.input(GAS_SENSOR_READ_PIN) == GPIO.LOW
            GPIO.output(PUMP_PIN, state["fire_detected"])
            
            state["intruder_detected"] = state["home_mode"] == "away" and (GPIO.input(MOTION_SENSOR_READ_PIN) == GPIO.HIGH or distance < state["selected_should_be_distance"])
            GPIO.output(BUZZER_PIN, state["intruder_detected"])

            if state["temp"] <= -100:
                continue
            
            GPIO.output(DC_MOTOR_PIN, state["temp"] > state["selected_maximum_temp"] if state["motor_mode"] == "auto" else state["manual_motor_start"])
        
        if state["fire_detected"] and not prev_fire_detected:
            send_alert_email(
                subject="🔥 Fire Alert Detected!",
                body=f"Fire has been detected at {datetime.datetime.now().isoformat()}",
                receiver_email=state["receiver_email"]
            )
        if state["intruder_detected"] and not prev_intruder_detected:
            send_alert_email(
                subject="🚨 Intruder Alert Detected!",
                body=f"Intruder has been detected at {datetime.datetime.now().isoformat()}",
                receiver_email=state["receiver_email"]
            )

        prev_fire_detected = state["fire_detected"]
        prev_intruder_detected = state["intruder_detected"]

        time.sleep(1)


# ----- FLASK SERVER -----

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set', methods=['POST'])
def set_state():
    updated = False
    with lock:
        data = request.json
        if "motor_mode" in data and data["motor_mode"] != state["motor_mode"]:
            state["motor_mode"] = data["motor_mode"]
            updated = True
        if "home_mode" in data and data["home_mode"] != state["home_mode"]:
            state["home_mode"] = data["home_mode"]
            updated = True
        if "manual_motor_start" in data and data["manual_motor_start"] != state["manual_motor_start"]:
            state["manual_motor_start"] = data["manual_motor_start"]
            updated = True
        if "selected_maximum_temp" in data and data["selected_maximum_temp"] != state["selected_maximum_temp"]:
            state["selected_maximum_temp"] = data["selected_maximum_temp"]
            updated = True
        if "selected_should_be_distance" in data and data["selected_should_be_distance"] != state["selected_should_be_distance"]:
            state["selected_should_be_distance"] = data["selected_should_be_distance"]
            updated = True
        if "receiver_email" in data and data["receiver_email"] != state["receiver_email"]:
            state["receiver_email"] = data["receiver_email"]
            updated = True

    response = {"status": "success"}
    if updated:
        response["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return jsonify(response), 200

@app.route('/status', methods=['GET'])
def get_status():
    response = {}
    with lock:
        response["temp"] = state["temp"]
        response["humidity"] = state["humidity"]
        response["fire_detected"] = state["fire_detected"]
        response["intruder_detected"] =  state["intruder_detected"]
        response["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return jsonify(response)

def start_server():
    app.run(host = "0.0.0.0", port = 5000, debug=False, use_reloader=False)

# ------ MAIN -----
if __name__ == '__main__':
    Thread(target = monitor, daemon = True).start()
    start_server()
