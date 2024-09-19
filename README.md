### Setup

1. Install dependencies: `pip install -r ./requirements.txt`
2. Install docker and setup `emqx` (MQTT server)
    - `docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 8084:8084 -p 8883:8883 -p 18083:18083  emqx:5.0.20`
    - open http://localhost:18083/ to setup admin account l: `admin` p: `public`
    - create user account (I am not sure whether it is needed, you can use admin account)
3. Connect your DJI Smart Controller to the same local network your PC is in (in case of laptop I recommend creating local hotspot).
4. Create a `.env` file with empty values for required env variables:
   ```bash
   echo "MQTT_HOST_ADDR=
   MQTT_USERNAME=
   MQTT_PASSWORD=
   DJI_LICENSE=
   DJI_APP_KEY=" > .env
   ```
5. Set values for all the veriables in `.env` file 
6. run `python3 cloud_api.http.py`
7. run `python3 cloud_api_mqtt.py`

### Connecting the controller

1. Open DJI Pilot App
2. Go to `Cloud Service` -> `Other platforms`
3. Write url `http://HOST_ADDR:5000/login` and connect
4. Press Login.
