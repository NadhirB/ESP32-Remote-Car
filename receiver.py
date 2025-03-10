from machine import Pin, PWM
import time
import network
import espnow

# Define the GPIO pin connected to the motors
frequency = 1000
motor_R1 = PWM(Pin(26), frequency)
motor_R2 = PWM(Pin(27), frequency)

motor_L1 = PWM(Pin(33), frequency)
motor_L2 = PWM(Pin(25), frequency)

# DEFINE SPEED LEVEL
max_speed_L = 1023
max_speed_R = 1023
mid_speed_L = 500
mid_speed_R = 500

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)
sta.disconnect()  # Because ESP8266 auto-connects to last Access Point

e = espnow.ESPNow()
e.active(True)


def msg_case(str_msg):
    """
    interprets the appropriate message from the controller and gives the command where to go
    :param str_msg: the received string
    :return: no return, prints the command
    """
    if str_msg == "Forward":
        print("FORWARD")
        go_forward()
    elif str_msg == "Left":
        print("Left")
        go_left()
    if str_msg == "Left Forward":
        print("LEFT FORWARD")
        go_left_forward()
    elif str_msg == "Right":
        print("RIGHT")
        go_right()
    elif str_msg == "Right Forward":
        print("Right Forward")
        go_right_forward()
    elif str_msg == "Back":
        print("BACK")
        go_back()
    elif str_msg == "Stop":
        print("BACK")
        stop()
    else:
        print("not match")

def go_forward():
    motor_L1.duty(max_speed_L)
    motor_L2.duty(0)

    motor_R1.duty(max_speed_R)
    motor_R2.duty(0)

def go_left():
    motor_L1.duty(0)
    motor_L2.duty(max_speed_L)

    motor_R1.duty(max_speed_R)
    motor_R2.duty(0)

def go_left_forward():
    motor_L1.duty(mid_speed_L)
    motor_L2.duty(0)

    motor_R1.duty(max_speed_R)
    motor_R2.duty(0)

def go_right():
    motor_L1.duty(max_speed_L)
    motor_L2.duty(0)

    motor_R1.duty(0)
    motor_R2.duty(max_speed_R)

def go_right_forward():
    motor_L1.duty(max_speed_L)
    motor_L2.duty(0)

    motor_R1.duty(mid_speed_R)
    motor_R2.duty(0)

def go_back():
    motor_L1.duty(0)
    motor_L2.duty(max_speed_L)

    motor_R1.duty(0)
    motor_R2.duty(max_speed_R)

def stop():
    motor_L1.duty(0)
    motor_L2.duty(0)

    motor_R1.duty(0)
    motor_R2.duty(0)

# Main Loop
def main():
    while True:
        host, msg = e.recv()
        if msg:  # msg == None if timeout in recv()
            print(msg)
            str_msg = msg.decode('utf-8')  # Decode the received message to a string
            msg_case(str_msg)

            if msg == b'end':
                break