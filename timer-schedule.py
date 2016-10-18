#! /usr/bin/python3
import datetime
from time import sleep
from datetime import datetime, time
import logging
import logging.config
import os
import sys
import signal
# Define Logging Settings
scriptFilename = os.path.basename(sys.argv[0]).replace(".py", ".log")

LOGGING_CONFIG = {
    'version': 1,  # required
    'disable_existing_loggers': True,  # this config overrides all other loggers
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s -- %(message)s'
        },
        'whenAndWhere': {
            'format': '%(asctime)s\t%(levelname)s -- %(processName)s(%(process)d) %(filename)s:%(lineno)s -- %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'whenAndWhere'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/home/pi/timer_schedule/timer_schedule.log',
            'mode': 'a',
            'formatter': 'whenAndWhere'
        }
    },
    'loggers': {
        '': {  # 'root' logger
            'level': 'INFO',
            'handlers': ['file']
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('')   # factory method

log.info('Process beginning...')

from RPi import GPIO

# Outlet pattern
#
# 1 | 3
# 2 | 4
#
# Match outlet with pin
# Outlet = Pin

outletPins = {"outlet1": 7, "outlet2": 11, "outlet3": 13, "outlet4": 15}

# List Schedule Defaults - 24hr times - 5pm = 17, 8pm = 20
scheduleA = {"Sunday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Monday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Tuesday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Wednesday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Thursday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Friday": {"on": time(17, 0, 0), "off": time(21, 30, 0)},
             "Saturday": {"on": time(17, 0, 0), "off": time(21, 30, 0)}}

scheduleB = {"Sunday": {"on": time(11, 0, 0), "off": time(21, 30, 0)},
             "Monday": {"on": time(14, 0, 0), "off": time(21, 30, 0)},
             "Tuesday": {"on": time(14, 0, 0), "off": time(21, 30, 0)},
             "Wednesday": {"on": time(14, 0, 0), "off": time(21, 30, 0)},
             "Thursday": {"on": time(14, 0, 0), "off": time(21, 30, 0)},
             "Friday": {"on": time(14, 0, 0), "off": time(21, 30, 0)},
             "Saturday": {"on": time(11, 0, 0), "off": time(21, 30, 0)}}

outletSchedule = {"outlet1": "scheduleA", "outlet2": "scheduleA", "outlet3": "scheduleB"}

# Log Start Script and Outlets
print("31:Script is starting...%s" % datetime.now())
logging.info("Script is starting...%s" % datetime.now())
# Set GPIO pins [outlets]

GPIO.setmode(GPIO.BOARD)

for outlet, pin in sorted(outletPins.items()):
    print("setup pin %s" % pin)
    logging.info("setup pin %s" % pin)
    GPIO.setup(pin, GPIO.OUT)


# error handling
def cleanup_pins():
    """cleanup everything we created with the GPIO"""
    print("[%s] cleaning up pins!" % datetime.now())
    logging.info("cleaning up pins!")
    GPIO.cleanup()


def sigterm_handler(_signo, _stack_frame):
    """When sysvinit sends the TERM signal, cleanup before exiting."""
    print("[%s] received signal {}, exiting...".format(_signo) % datetime.now())
    logging.info("received signal {}, exiting...".format(_signo))
    cleanup_pins()
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

# Begin looping the whole process
def theSchedule(outletpins):
    try:
        while True:
            # Today is...
            weekdayName = datetime.today().strftime("%A")
            now = datetime.now()
            now_time = now.time()

            # Check for override
            overrideStatus = 'NA'

            if overrideStatus == 'On' or overrideStatus == 'Off':
                # do nothing
                print("Override status = %s" % overrideStatus)
                logging.info("Override status = %s" % overrideStatus)
                sleep(3)
            else:
                # If today is
                if scheduleA[weekdayName]['on'] <= now.time() <= scheduleA[weekdayName]['off']:
                    # print("71:in schedule A time")
                    for outlet, schedule in sorted(outletSchedule.items()):
                        if schedule == 'scheduleA':
                            #rint("74:Check outlets for Schedule A:")
                            #print("75:Check outlet on:%s" % outlet)
                            if GPIO.input(outletPins[outlet]) == 1:
                                print("77:Pin %s of outlet %s is ON" % (outletPins[outlet], outlet))
                            else:
                                print("79:Pin %s of outlet %s is OFF" % (outletPins[outlet], outlet))
                                GPIO.output(outletPins[outlet], 1)
                                print("81:Set outlet %s to ON" % (outlet))
                                logging.info("Set outlet %s to ON at %s" % (outlet, now_time))
                                sleep(3)

                elif scheduleB[weekdayName]['on'] <= now.time() <= scheduleB[weekdayName]['off']:
                    # print("71:in schedule B time")
                    for outlet, schedule in sorted(outletSchedule.items()):
                        if schedule == 'scheduleB':
                            #rint("74:Check outlets for Schedule B:")
                            #print("75:Check outlet on:%s" % outlet)
                            if GPIO.input(outletPins[outlet]) == 1:
                                print("77:Pin %s of outlet %s is ON" % (outletPins[outlet], outlet))
                            else:
                                print("79:Pin %s of outlet %s is OFF" % (outletPins[outlet], outlet))
                                GPIO.output(outletPins[outlet], 1)
                                print("81:Set outlet %s to ON" % (outlet))
                                logging.info("Set outlet %s to ON at %s" % (outlet, now_time))
                                sleep(3)


                else:
                    #print("86:not schedule A time")
                    for outlet, schedule in sorted(outletSchedule.items()):
                        if schedule == 'scheduleA' or schedule == 'scheduleB':
                            #print("89:Check outlets for Schedule A:")
                            #print("90:Check outlet off:%s" % outlet)
                            if GPIO.input(outletPins[outlet]) == 1:
                                print("92:Pin %s of outlet %s is ON" % (outletPins[outlet], outlet))
                                GPIO.output(outletPins[outlet], 0)
                                print("94:Set outlet %s to OFF" % (outlet))
                                logging.info("Set outlet %s to OFF at %s" % (outlet, now_time))
                                sleep(3)
                            else:
                                print("98: Pin %s of outlet %s is OFF" % (outletPins[outlet], outlet))


        else:
            print("102: Having a hard time starting this script")

    except KeyboardInterrupt:
        cleanup_pins()

theSchedule(outletPins)