COUNTER_ID = "001394FA"
MAX_TIME_SEC = 500
# Conversion function : consumption (L) = A*x + B
CONSUMPTION_A = 0.3311
CONSUMPTION_B = 17
#
MONITOR_INTERVAL = 600
WATCHDOG_KILL_TIME = 500
DEBUG = False
MQTT_SERVER = "mymqttserver.com"
MQTT_TOPIC = "waterconsumption"
LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)-15s - %(process)d [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 10*1024*1024,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': { 
            # 'handlers': ['default', 'file'],
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
    } 
}



import os
import ast
for var in locals().keys():
    if var in os.environ.keys():
        env_value = os.environ[var]
        if ("PASS" in var) or ("KEY" in var) or ("PW" in var):
            env_value_dbg = "****"
            secret = True
        else:
            env_value_dbg = env_value
            secret = False
        print "Raw %s=%s(%s)"%(var, env_value_dbg, type(env_value))
        env_value = ast.literal_eval(os.environ[var])
        if not secret:
            env_value_dbg = env_value
        print "After casting %s=%s(%s)"%(var, env_value_dbg, type(env_value))
        locals()[var] = env_value

##
# Ex of env variables :
#   Bool : TOTO="True"
#   Int : TOTO="123"
#   Str :  TOTO = "'strubg'"
#   List : TOTO = "['an','ii']"
##
