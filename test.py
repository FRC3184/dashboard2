import dashboard
import dashboard_server
from threading import Thread
from random import randint
from time import sleep
import math

server_thread = Thread(target=dashboard_server.run)
server_thread.daemon = True
server_thread.start()
dt = .2
t = dt

log = math.log(t)
sqrt = t**.5
sq = t**2

dashboard.graph("log(time)", lambda: log)
dashboard.graph("time", lambda: t)
dashboard.graph("sqrt(time)", lambda: sqrt)
dashboard.graph("time^2", lambda: sq)
dashboard.graph("Random", lambda: randint(-10, 10))

dashboard.chooser("Ice Cream", ["Chocolate", "Vanilla", "Neapolitan"])

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
