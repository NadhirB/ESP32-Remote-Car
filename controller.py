from machine import Pin, ADC
import machine, math, time, neopixel, network, espnow

# Set Up section:

# X and Y inputs
vrx = ADC(Pin(32))
vrx.atten(ADC.ATTN_11DB)
vry = ADC(Pin(35))
vry.atten(ADC.ATTN_11DB)

# Switch input
sw = Pin(34, Pin.IN, Pin.PULL_UP)

# NeoPixel Wheel input
np = neopixel.NeoPixel(machine.Pin(18), 24)

# ESPNOW setup
# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\xA0\xDD\x6C\x03\x7F\xE0'   # MAC address of peer's wifi interface
e.add_peer(peer)       # Must add_peer() before send()


# Functions:

def send_direction(pos, amount):
    """
    This function is responsible for sending direction commands to the receiver ESP32
    :param pos: the position of the direction using numbers ranging from 0 to 6 or -5
    :param amount: TODO implement reaction to different amount of power
    :return: returns the command that was sent for debugging
    """

    if pos == 0:
        e.send(peer, "Forward")
        dest = "Forward"
    elif pos == 1:
        e.send(peer, "Right Forward")
        dest = "Right Forward"
    elif pos == -1:
        e.send(peer, "Left Forward")
        dest = "Left Forward"
    elif pos == 3:
        e.send(peer, "Right")
        dest = "Right"
    elif pos == -3:
        e.send(peer, "Left")
        dest = "Left"
    elif pos == 4 or pos == 5 or pos == -4 or pos == -5 or pos == 6 or pos == -6:
        e.send(peer, "Back")
        dest = "Back"
    else:
        e.send(peer, "Stop")
        dest = "Stop"
    return dest

def calibrate(num):
    """
    Calibrates the input from the joystick. changes (65535 , 29000) to (100, 0) and (28900, 0) to (0, -100). Values in
    between will be automatically sent to 0. The calibration is based on a linear transformation
    :param num: the given value
    :return: calibrated value with the given parameters
    """
    m1 = 0.002737 # for the upper range
    m2 = 0.0034602 # for the lower range
    if num >= 29000:
        cal_num = int(m1 * num - 79.3759)
    elif num <= 28900:
        cal_num = int(m2 * num - 100)
    else:
        cal_num = 0
    return cal_num

def position(r, theta):
    """
    Returns the position of the input from the joystick, from the polar coordinates. They are divided by 6 to each side
    where 0 is the front and +-6 is the back. 3 is right and -3 is left.
    :param r:
    :param theta: the given angle ranging from 180 to -180 degrees
    :return: the appropriate position based on the calculations, 100 represents the center position
    """
    if r == 0:
        pos = 100
    else:
        pos = int((theta * 6) / 180) #returns whole numbers
    return pos

def polar_coor(x, y):
    """
    Calculates the polar coordinates of the input from the joystick.
    """
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)

    deg = 360*(theta/2/math.pi)

    #setting the different values for r, can be changed according to preference and joystick sensitivity
    if r <= 0.25:
        r = 0
    elif  0.25 < r <= 0.5:
        r = 1
    elif 0.5 < r <= 0.9:
        r = 2
    else:
        r = 3

    return r, int(deg)

def update_colour(pos, r):
    """
    Updates the colour of the LED wheel according to the input from the joystick.
    :param pos: the given position
    :param r: the "intensity"
    """
    np.fill((0, 0, 0)) #resetting the colour of all LED's to 0

    lum = r*60 #setting the intensity according to the input

    if pos == 100:
        np.fill((0, 0, 30))
    else:
        if pos == 0:
            np[23] = np[0] = np[1] = (lum, 0, 0) #Forward
        elif pos == 1:
            np[2] = np[3] = np[4] = (lum, 0, 0) #Right Forward
        elif pos == 2 or pos == 3:
            np[5] = np[6] = np[7] = (lum, 0, 0) #Right
        elif pos == 4:
            np[8] = np[9] = np[10] = (lum, 0, 0) #Right Back
        elif pos == 5 or pos == -5 or pos == 6 or pos == -6:
            np[11] = np[12] = np[13] = (lum, 0, 0) #Back
        elif pos == -4:
            np[14] = np[15] = np[16] = (lum, 0, 0) #Left Back
        elif pos == -2 or pos == -3:
            np[17] = np[18] = np[19] = (lum, 0, 0) #Left
        elif pos == -1:
            np[20] = np[21] = np[22] = (lum, 0, 0) #Left Forward
    np.write()

# Main Loop:

def main():

    while True:
        #getting the x and y values:
        x_value = vrx.read_u16()
        y_value = vry.read_u16()

        #calibrating to range (-100, 100) and converting to polar
        cal_x = calibrate(x_value)
        cal_y = calibrate(y_value)
        r, angle = polar_coor(cal_x/100, cal_y/100)

        #position Assignment
        pos = position(r, angle)

        #color wheel:
        update_colour(pos, r)

        #send directions to esp
        direction = send_direction(pos, r)

        #print values to the consol for error and calibration
        print(f"X:{x_value}, {cal_x}, Y:{y_value}, {cal_y},  R:{r}, theta:{angle}, position:{pos}, direction:{direction}")

        time.sleep(0.1) # small delay, not strictly necessary