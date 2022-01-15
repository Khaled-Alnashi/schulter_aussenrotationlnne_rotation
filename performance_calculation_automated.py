import math
import json
import paho.mqtt.client as mqttclient
import cv2
import numpy as np
import pyttsx3 as pyttsx3
import Pose_Module as pm
import os

path_current = os.path.abspath(os.getcwd())

# Reading video
# capture by your own camera
cap = cv2.VideoCapture(0)

hasFrame, framee = cap.read()
frameeWidth = framee.shape[1]
frameeHeight = framee.shape[0]
os.path.abspath(os.getcwd())
detector = pm.poseDetector()
count = 0
dir = 0
count1 = 0
dir1 = 0
pTime = 0
# If hand = 0, it means left arm or hand = 1, it means right arm
hand = 0
g = 1
time1, time2, time3, time4, time5, time6 = 80, 80, 80, 80, 80, 80

# MQTT connection
broker_address = "localhost"
port = 1883
user = "mqtt"
password = "test"


# is the conversion of an object from one data type to another data type
def convert(data1):
    text_speech = pyttsx3.init()
    text_speech.say(data1)
    text_speech.runAndWait()


# Connection check
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("client is connected")
        global connected
        connected = True
    else:
        print("client is error")


# Called when composing and sending a message
def on_message(client, userdata, message):
    print("message recieved = " + str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    convert(message.payload.decode("utf-8"))


Messagerecieved = False
connected = False
client = mqttclient.Client("MQTT")
client.on_message = on_message
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.connect(broker_address, port=port)

client.loop_start()
client.subscribe("test/#")

########################################################################################################################
while True:
    success, img = cap.read()
    img = cv2.resize(img, (1280, 720))
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    if len(lmList) != 0:
        ############################## left arm ##############################
        if hand == 0:
            angle, difference = detector.findAngle(img, 12, 11, 13)
           
            value_min = 140
           
           
            value_max = 70
           

            # bar for left arm
            per1 = np.interp(angle, (value_max, value_min), (100, 0))
            bar1 = np.interp(angle, (value_max, value_min), (100, 650))
            # Check for the curl
            color = (255, 0, 255)
            if per1 == 0:
                color = (0, 255, 0)
                if dir1 == 0:
                    count1 += 0.5
                    dir1 = 1
            if per1 == 100:
                color = (0, 255, 0)
                if dir1 == 1:
                    count1 += 0.5
                    dir1 = 0

            # Conditions for giving instructions related to the movement in the form
            # of text and voice messages to complete it successfully
            if 75 < angle < 135 and g == 1:
                # text messages
                cv2.putText(img, str("Bewegen Sie Ihren Oberarm nach aussen und hinten."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                # voice messages
                if time1 > 79:
                    client.publish("test", "Bewegen Sie Ihren Oberarm nach aussen und hinten.")
                    time1 = 0
                else:
                    # This is in order to create a time of approximately 3 seconds between the message
                    # and the message that follow
                    time1 = time1 + 1
                    print(time1)
                    time2, time3, time4, time5, time6 = 80, 80, 80, 80, 80

            elif 140 < angle < 145:
                cv2.putText(img, str("Zuruck weit vor Ihren Koerper."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 0

                if time2 > 79:
                    client.publish("test", "Zuruck weit vor Ihren Koerper.")
                    time2 = 0
                else:
                    time2 = time2 + 1
                    print(time2)
                    time1, time3, time4, time5, time6 = 80, 80, 80, 80, 80

            elif angle > 150 or angle < 62:
                cv2.putText(img, str("Nicht so viel, das reichte schon."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 0

                if time3 > 79:
                    client.publish("test", "Nicht so viel, das reichte schon.")
                    time3 = 0
                else:
                    time3 = time3 + 1
                    print(time3)
                    time1, time2, time4, time5, time6 = 80, 80, 80, 80, 80

            elif 65 < angle < 74:
                cv2.putText(img, str("Sehr gut geschafft,Machen Sie dass nochmals."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 1

                if time4 > 79:
                    client.publish("test", "Sehr gut geschafft,Machen Sie dass nochmals.")
                    time4 = 0
                else:
                    time4 = time4 + 1
                    print(time4)
                    time1, time2, time3, time5, time6 = 80, 80, 80, 80, 80

            elif 76 < angle < 134 and g == 0:
                cv2.putText(img, str("Das ist nicht genug, bitte machen Sie wieterhin"), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 0

                if time5 > 79:
                    client.publish("test", "Das ist nicht genug, bitte machen Sie wieterhin")
                    time5 = 0
                else:
                    time5 = time5 + 1
                    print(time5)
                    time1, time2, time3, time4, time6 = 80, 80, 80, 80, 80

            # Draw Bar link
            cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
            cv2.rectangle(img, (1100, int(bar1)), (1175, 650), color, cv2.FILLED)
            cv2.putText(img, f'{int(per1)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 2,
                        color, 4)

            # Draw Curl Count link
            cv2.putText(img, "L: " + str(int(count1)), (1050, 720), cv2.FONT_HERSHEY_PLAIN, 5,
                        (255, 0, 0), 5)
            # calculate the z axis i.s. the posture of the hand angle
            if difference > 1.25:
                img = cv2.applyColorMap(img, cv2.COLORMAP_AUTUMN)
                cv2.putText(img, str("Bitte korrigiere haltung"), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
                            (255, 0, 0), 5)
                cv2.imshow("Image", img)
                if time6 > 79:
                    client.publish("test", "Bitte korrigiere haltung")
                    time6 = 0
                else:
                    time6 = time6 + 1
                    print(time6)
                    time1, time2, time3, time4, time5 = 80, 80, 80, 80, 80

            else:

                cv2.imshow("Image", img)
            cv2.imshow("Image", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        ##################################################################################
        ################################# Right ARM ######################################
        else:
            angle, difference = detector.findAngle(img, 11, 12,
            value_min = 140
            value_max = 70
            

            # bar for right arm
            per = np.interp(angle, (value_max, value_min), (100, 0))
            bar = np.interp(angle, (value_max, value_min), (100, 650))
            print(value_max, value_min, bar)

            # Check for the curls
            color = (255, 0, 255)
            if per == 0:
                color = (0, 255, 0)
                if dir == 0:
                    count += 0.5
                    dir = 1
            if per == 100:
                color = (0, 255, 0)
                if dir == 1:
                    count += 0.5
                    dir = 0

            # Conditions for giving instructions related to the movement in the form
            # of text and voice messages to complete it successfully
            if 75 < angle < 135 and g == 1:
                # text messages
                cv2.putText(img, str("Bewegen Sie Ihren Oberarm nach aussen und hinten."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                # voice messages
                if time1 > 79:
                    client.publish("test", "Bewegen Sie Ihren Oberarm nach aussen und hinten.")
                    time1 = 0
                else:
                    # This is in order to create a time of approximately 3 seconds between the message
                    # and the message that follow
                    time1 = time1 + 1
                    print(time1)
                    time2, time3, time4, time5, time6 = 80, 80, 80, 80, 80

            elif 140 < angle < 145:
                cv2.putText(img, str("Zuruck weit vor Ihren Koerper."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 0

                if time2 > 79:
                    client.publish("test", "Zuruck weit vor Ihren Koerper.")
                    time2 = 0
                else:
                    time2 = time2 + 1
                    print(time2)
                    time1, time3, time4, time5, time6 = 80, 80, 80, 80, 80

            elif angle > 150 or angle < 62:
                cv2.putText(img, str("Nicht so viel, das reichte schon."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 1

                if time3 > 79:
                    client.publish("test", "Nicht so viel, das reichte schon.")
                    time3 = 0
                else:
                    time3 = time3 + 1
                    print(time3)
                    time1, time2, time4, time5, time6 = 80, 80, 80, 80, 80

            elif 65 < angle < 74:
                cv2.putText(img, str("Sehr gut geschafft,Machen Sie dass nochmals."), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 1

                if time4 > 79:
                    client.publish("test", "Sehr gut geschafft,Machen Sie dass nochmals.")
                    time4 = 0
                else:
                    time4 = time4 + 1
                    print(time4)
                    time1, time2, time3, time5, time6 = 80, 80, 80, 80, 80

            elif 76 < angle < 134 and g == 0:
                cv2.putText(img, str("Das ist nicht genug, bitte machen Sie wieterhin"), (20, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2.4,
                            (255, 0, 0), 3)
                g = 0

                if time5 > 79:
                    client.publish("test", "Das ist nicht genug, bitte machen Sie wieterhin")
                    time5 = 0
                else:
                    time5 = time5 + 1
                    print(time5)
                    time1, time2, time3, time4, time6 = 80, 80, 80, 80, 80

            # Draw Bar Right
            cv2.rectangle(img, (100, 100), (175, 650), color, 3)
            cv2.rectangle(img, (100, int(bar)), (175, 650), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (100, 75), cv2.FONT_HERSHEY_PLAIN, 2,
                        color, 4)

            # Draw Curl Count
            cv2.putText(img, "R: " + str(int(count)), (45, 720), cv2.FONT_HERSHEY_PLAIN, 5,
                        (255, 0, 0), 5)
            # calculate the z axis i.s. the posture of the hand angle
            if difference > 1.25:
                img = cv2.applyColorMap(img, cv2.COLORMAP_AUTUMN)
                cv2.putText(img, str("Bitte korrigiere haltung"), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
                            (255, 0, 0), 5)
                cv2.imshow("Image", img)
                if time6 > 79:
                    client.publish("test", "Bitte korrigiere haltung")
                    time6 = 0
                else:
                    time6 = time6 + 1
                    print(time6)
                    time1, time2, time3, time4, time5 = 80, 80, 80, 80, 80
            else:
                cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
cap.release()
cv2.destroyAllWindows()
########################################################################################################################
