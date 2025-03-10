# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

import controller , receiver
controller.main() # change name of file according to esp you are installing on:
                        # Receiver: 'receiver.main()'
                        # Controller: 'controller.main()'