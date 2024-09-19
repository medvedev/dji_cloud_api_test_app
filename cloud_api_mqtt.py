import os
import json
import threading
import time
import uuid

import paho
import paho.mqtt.client as mqtt

import tkinter as tk

from dotenv import load_dotenv

from dji_error_codes import DjiErrorCodes

load_dotenv()

ui_window = tk.Tk()
ui_window.title("Manage DJI Mavic 3E")
text_status_replies = tk.Text(ui_window)

rc_sn_value = tk.StringVar(value="RC S\\N:")
uav_sn_value = tk.StringVar(value="UAV S\\N:")
gw_sn = ""
uav_sn = ""

error_codes = DjiErrorCodes()


def on_connect(c, userdata, flags, rc, _):
    print("Connected with result code " + str(rc))
    c.subscribe("sys/#")
    c.subscribe("thing/#")


def handle_osd_message(message: dict):
    data = message["data"]
    data.pop("wireless_link", None)
    data.pop("wireless_link_state", None)
    print(data)


# The callback for when a PUBLISH message is received from the server.
def on_message(c: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    print("📨Got msg: " + msg.topic)
    message = json.loads(msg.payload.decode("utf-8"))
    message_data_ = message["data"]
    if msg.topic.endswith("_reply"):
        print(json.dumps(message))
        if "method" in message:
            text_status_replies.insert(tk.END, "method: " + message["method"] + "\n")
        text_status_replies.insert(tk.END, "topic: " + msg.topic + "\n")
        text_status_replies.insert(tk.END, "data: " + json.dumps(message_data_) + "\n")
        if "result" in message_data_:
            error_text = error_codes[message_data_["result"]]
            if error_text:
                text_status_replies.insert(tk.END, error_text + "\n")
        text_status_replies.insert(tk.END, "\n")


    global uav_sn, gw_sn
    if msg.topic.endswith("status"):
        if message["method"] != "update_topo":
            return

        if len(message_data_["sub_devices"]) == 0:
            uav_sn_value.set(f"UAV S\\N:")
        else:
            uav_sn = message_data_["sub_devices"][0]["sn"]
            uav_sn_value.set(f"UAV S\\N: {uav_sn}")

        response = {
            "tid": message["tid"],
            "bid": message["bid"],
            "timestamp": message["timestamp"] + 2,
            "data": {"result": 0},
        }
        c.publish(msg.topic + "_reply", payload=json.dumps(response))
        print("✅published")
    elif msg.topic.endswith("osd") and msg.topic.startswith("thing"):
        topic_sn = msg.topic.split('/')[2]
        gw_sn = json.loads(msg.payload)['gateway']
        if gw_sn == topic_sn:
            rc_sn_value.set(f"RC S\\N: {topic_sn}")
        else:
            uav_sn = topic_sn
            uav_sn_value.set(f"UAV S\\N: {uav_sn}")
        handle_osd_message(message)


client = mqtt.Client(paho.mqtt.enums.CallbackAPIVersion.VERSION2, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.environ["MQTT_HOST_ADDR"], 1883, 60)

mq_thread = threading.Thread(target=lambda: client.loop_forever(), daemon=True)
mq_thread.start()


def publish(method, data):
    request = {
        "tid": str(uuid.uuid4()),
        "bid": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "method": method,
        "data": data,
    }
    client.publish(f"thing/product/{gw_sn}/services", json.dumps(request))


def request_control():
    global gw_sn
    if gw_sn:
        publish("cloud_control_auth_request",
                {"user_id": 1, "user_callsign": "Slavko", "control_keys": ["flight"]})


def release_control():
    global gw_sn
    if gw_sn:
        publish("cloud_control_release",
                {"control_keys": ["flight"]})


def start_stream():
    global gw_sn, uav_sn
    if gw_sn and uav_sn:
        publish("live_start_push",
                {
                    "url": "rtmp://192.168.1.74/live/vd",
                    "url_type": 1,
                    "video_id": f"{uav_sn}/66-0-0/zoom-0",
                    "video_quality": 0
                },
                )


def stop_stream():
    global gw_sn, uav_sn
    if gw_sn and uav_sn:
        publish("live_stop_push",
                {
                    "video_id": f"{uav_sn}/66-0-0/zoom-0",
                },
                )


def take_photo():
    global gw_sn
    if gw_sn:
        publish("camera_photo_take", {
            "payload_index": "66-0-0",
        }, )


# GUI

frame_buttons = tk.Frame(ui_window)
frame_buttons.pack(pady=10)

button_request_control = tk.Button(frame_buttons, text="Request control", command=request_control)
button_release_control = tk.Button(frame_buttons, text="Release control", command=release_control)
button_take_photo = tk.Button(frame_buttons, text="Take photo", command=take_photo)
button_start_stream = tk.Button(frame_buttons, text="Start stream", command=start_stream)
button_stop_stream = tk.Button(frame_buttons, text="Stop stream", command=stop_stream)

label_frame = tk.Frame(ui_window)
label_frame.pack(side=tk.TOP, pady=10)

label_rc_sn = tk.Label(label_frame, textvariable=rc_sn_value)
label_uav_sn = tk.Label(label_frame, textvariable=uav_sn_value)

scroll = tk.Scrollbar(ui_window)
text_status_replies.configure(yscrollcommand=scroll.set)
text_status_replies.pack(side=tk.LEFT)

scroll.config(command=text_status_replies.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

button_request_control.pack(side=tk.LEFT, padx=10)
button_release_control.pack(side=tk.LEFT, padx=10)
button_take_photo.pack(side=tk.LEFT, padx=10)
button_start_stream.pack(side=tk.LEFT, padx=10)
button_stop_stream.pack(side=tk.LEFT, padx=10)

label_rc_sn.pack(side=tk.TOP, padx=10, pady=5)
label_uav_sn.pack(side=tk.TOP, padx=10, pady=5)

ui_window.mainloop()
