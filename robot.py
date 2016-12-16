import wpilib
from dashboard import dashboard2 as dashboard
import time


__last_time = time.time()


def delta():
    global __last_time
    now = time.time()
    dt = now - __last_time
    __last_time = now
    return dt


class MyRobot(wpilib.IterativeRobot):
    def __init__(self):
        super().__init__()
        talon_left = wpilib.Talon(0)
        talon_right = wpilib.Talon(1)
        self.drive = wpilib.RobotDrive(talon_left, talon_right)
        self.joystick = wpilib.Joystick(0)

        dashboard.graph("Forward", self.joystick.getY)
        dashboard.graph("Turn", self.joystick.getX)
        dashboard.graph("Talon Left", talon_left.get)
        dashboard.graph("Talon Right", talon_right.get)

        self.time = 0

        dashboard.run()

    def disabledPeriodic(self):
        self.time += delta()
        dashboard.update(self.time)

    def teleopPeriodic(self):
        turn = self.joystick.getX()
        forward = self.joystick.getY()
        self.drive.arcadeDrive(forward, turn)
        self.time += delta()
        dashboard.update(self.time)

if __name__ == '__main__':
    wpilib.run(MyRobot)
