import dashboard
from threading import Thread
from random import random
from time import sleep
import math

server_thread = Thread(target=dashboard.app.run)
server_thread.start()
dt = .05
t = dt

log = math.log(t)
sqrt = t**.5
sq = t**2

dashboard.graph("log(time)", lambda: log)
dashboard.graph("time", lambda: t)
dashboard.graph("sqrt(time)", lambda: sqrt)
dashboard.graph("time^2", lambda: sq)

try:
    while True:
        log = math.log(t)
        sqrt = t**.5
        sq = t**2

        dashboard.update(t)
        sleep(dt)
        t += dt
finally:
    pass
