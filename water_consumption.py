import subprocess
import logging
import time
import os
from pprint import pprint
import logging.config
import paho.mqtt.publish as publish
import json
import config

logging.config.dictConfig(config.LOGGING_CONFIG)
FNULL = open(os.devnull, 'w')

class WaterConsumption:
    expected_data = {
        'header': ['0x1c441486'],
        'constant_2': ['0411a0'],
        'unknown_1': ['0', '1'],
        'constant_3': ['8', 'c'],
        'unknown_2': ['0', '4', '1', 'c'],
        'constant_4': ['0030000000005ff0b'],
        'constant_5': ['0000']
    }
    def __init__(self):
        self.rtl_sdr = ["rtl_sdr", "-f", "868.9M", "-s", "1600000", "-"]
        self.rtl_wmbus = ["/root/rtl-wmbus/build/rtl_wmbus"]
        self.last_consumption = None
        self.last_time = None
    
    def get(self):
        if config.DEBUG:
            output = subprocess.Popen(self.rtl_wmbus, stdin=subprocess.PIPE, stdout=subprocess.PIPE)#, stderr=FNULL)
            sdr_data = subprocess.Popen(self.rtl_sdr, stdout=output.stdin)#stderr=FNULL,
        else:
            output = subprocess.Popen(self.rtl_wmbus, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=FNULL)
            sdr_data = subprocess.Popen(self.rtl_sdr, stdout=output.stdin, stderr=FNULL)
        time.sleep(2) # Wait to see if there is an error at startup
        error = False
        for proc in [sdr_data, output]:
            return_code = proc.poll()
            if return_code:
                error = True
                try:
                    proc.terminate()
                except:
                    pass
        if error:
            logging.error("ERROR")
            return None
        tstart = time.time()
        logging.debug("Collecting results")
        with output.stdout:
            for line in iter(output.stdout.readline, b''):
                if (time.time() - tstart) > config.MAX_TIME_SEC:
                    logging.info("Timeout")
                    for proc in [sdr_data, output]:
                        try:
                            proc.terminate()
                        except:
                            pass
                    return None
                data = line.split(";")
                if data[1] != "1" or data[2] != "1":
                    continue
                serial = data[6]
                data = data[7]
                logging.debug(serial + ' ' + data)
                data_d = {
                    # 'constant_1': serial,
                    # 'header': data[:10], # 0x1c441486
                    # 'serial_inv': data[10:18],# serial (inverse) ab941300
                    # 'constant_2': data[18:24], # 0411a0
                    'consumption': data[24:32], # inverse
                    # 'unknown_1': data[32], # 0 ou 1
                    # 'constant_3': data[33], # 8 ou c
                    # 'unknown_2': data[34], # 0 ou 4 ou 1 ou c
                    # 'constant_4': data[35:52], # 0030000000005ff0b
                    # 'unknown_3': data[52:56],
                    # 'constant_5': data[56:60], # 0000
                }
                consumption = int(data[30:32] + data[28:30] + data[26:28] + data[24:26], 16)
                consumption = config.CONSUMPTION_A*consumption + config.CONSUMPTION_B
                data_d["consumption"] = round(consumption)
                # pprint(data_d) 
                for k, v in data_d.iteritems():
                    if k in self.expected_data:
                        if not v in self.expected_data[k]:
                            logging.error("Unexpected value (%s, expected %s)"%(v, self.expected_data[k]))
                if serial == config.COUNTER_ID:
                    if self.last_consumption:
                        data_d['delta'] = round(consumption - self.last_consumption)
                        data_d['flow_rate'] = round(data_d['delta']/ ((time.time()-self.last_time)/60))
                    self.last_time = time.time()
                    self.last_consumption = consumption
                    logging.info("Got data, closing")
                    sdr_data.terminate()
                    sdr_data.wait()
                    output.terminate()
                    output.wait()
                    return data_d


if __name__ == '__main__':
    w = WaterConsumption()
    while True:
        data = w.get()
        
        if data:
            pprint(data)
            i = 0
            while True:
                try:
                    publish.single(config.MQTT_TOPIC+"/out", json.dumps(data), hostname=config.MQTT_SERVER)
                    break
                except Exception as e:
                    i+=1
                    if time > 3:
                        logging.exception("Failed to write to mqtt, not retrying : %s"%e)
                        break
                    logging.error("Got exception while writting to mqtt (attempt %s): %s"%(i, e))
                    time.sleep(10)
        else:
            logging.warning("Failed to get data")
        logging.info("All done")
        time.sleep(config.MONITOR_INTERVAL)

