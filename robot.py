import wpilib
from dashboard import dashboard2
from dashboard.extensions import simulbot
import time


__last_time = time.time()


def delta():
    global __last_time
    now = time.time()
    dt = now - __last_time
    __last_time = now
    return dt


def sign(x):
    return x/abs(x) if x != 0 else 0


def deadzone(x):
    if abs(x) < 0.05:
        return 0
    return x


def radius_turn(robot_drive, pow, turn, robot_width, max_radius):
    D = robot_width
    if turn == 0:
        robot_drive.tankDrive(pow, pow)
        return
    elif pow == 0:
        turn_pow = turn
        robot_drive.tankDrive(turn_pow, -turn_pow)
        return
    radius = sign(turn) * max_radius * (1 - abs(turn))
    Vo = pow
    Vi = Vo*abs(radius)/(abs(radius) + D)

    if radius > 0:
        robot_drive.tankDrive(Vo, Vi)
    else:
        robot_drive.tankDrive(Vi, Vo)


class MyRobot(wpilib.IterativeRobot):
    def __init__(self):
        super().__init__()
        self.talon_left = wpilib.Talon(0)
        self.talon_right = wpilib.Talon(1)
        self.drive = wpilib.RobotDrive(self.talon_left, self.talon_right)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearLeft, False)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearRight, True)
        self.joystick = wpilib.Joystick(0)

        self.width = 2
        self.top_speed = 15

        dashboard2.graph("Forward", self.joystick.getY)
        dashboard2.graph("Turn", self.joystick.getX)
        dashboard2.graph("Talon Left", self.talon_left.get)
        dashboard2.graph("Talon Right", self.talon_right.get)
        dashboard2.chooser("Drive", ["Radius", "Arcade"])
        simulbot.load(self.width, self.top_speed)

        self.time = 0

        dashboard2.run()

    def disabledPeriodic(self):
        self.drive.tankDrive(0, 0)
        self.time += delta()
        dashboard2.update(self.time)

    def teleopPeriodic(self):
        max_turn = 20

        turn = deadzone(self.joystick.getZ())
        forward = -deadzone(self.joystick.getY())
        if dashboard2.chooser_status['Drive'] in (None, "Radius"):
            radius_turn(self.drive, forward, turn, self.width, max_turn)
        else:
            self.drive.arcadeDrive(forward, -turn)

        simulbot.update(self.talon_left.get(), self.talon_right.get())
        self.time += delta()
        dashboard2.update(self.time)

    def autonomousPeriodic(self):
        radius_turn(self.drive, 1, 10, 2, 10)
        simulbot.update(self.talon_left.get(), self.talon_right.get())
        self.time += delta()
        dashboard2.update(self.time)

if __name__ == '__main__':
    wpilib.run(MyRobot)
