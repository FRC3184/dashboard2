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


def deadzone(x, size=0.05):
    if abs(x) < size:
        return 0
    return x


def max_turn_radius(D, sensitivity=.01):
    return (1-sensitivity)*(sensitivity + D/2)/(sensitivity - D/2)


def real_root(x, pow):
    return sign(x) * abs(x)**pow


def radius_drive(robot_drive, pow, turn, robot_width, max_radius):
    """
    Turns at a constant turn radius at a given power
    :param robot_drive: wpilib.RobotDrive object
    :param pow: The power to drive at. [-1, 1]
    :param turn: The joystick turn value. [-1, 1]
    :param robot_width: The track width of the robot
    :param max_radius: The maximum turn radius of the robot, in units same as robot_width
    """
    D = robot_width
    if turn == 0:  # Special case to handle straight lines
        robot_drive.tankDrive(pow, pow)
        return
    turn = real_root(turn, 1/3)  # Shift turn to turn faster at lower powers
    radius = max_radius * (1 - abs(turn))  # Calculate the turn radius
    Vo = pow
    # Calculate the inner wheel power
    Vi = Vo * (radius - D/2) / (radius + D/2)

    # Apply the calculated power to the correct wheels for the direction
    if turn > 0:
        robot_drive.tankDrive(Vo, Vi)
    else:
        robot_drive.tankDrive(Vi, Vo)


def radius_turn(robot_drive, pow, radius, robot_width):
    D = robot_width
    Vo = pow
    # Calculate the inner wheel power
    Vi = Vo * (abs(radius) - D / 2) / (abs(radius) + D / 2)

    # Apply the calculated power to the correct wheels for the direction
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

        self.teleop = lambda: False

        dashboard2.graph("Forward", self.joystick.getY)
        dashboard2.graph("Turn", self.joystick.getX)
        dashboard2.graph("Talon Left", self.talon_left.get)
        dashboard2.graph("Talon Right", self.talon_right.get)
        dashboard2.chooser("Drive", ["Radius", "Arcade"])
        dashboard2.indicator("Teleop", self.teleop)
        simulbot.load(self.width, self.top_speed)

        self.time = 0

        dashboard2.run()

    def teleopInit(self):
        self.teleop = lambda: True

    def autonomousInit(self):
        self.teleop = lambda: False

    def disabledInit(self):
        self.teleop = lambda: False

    def disabledPeriodic(self):
        self.drive.tankDrive(0, 0)
        self.time += delta()
        dashboard2.update(self.time)

    def teleopPeriodic(self):

        turn = deadzone(self.joystick.getZ())
        forward = -deadzone(self.joystick.getY())
        if dashboard2.chooser_status['Drive'] in (None, "Radius"):
            radius_drive(self.drive, forward, turn, self.width, 200)
        else:
            self.drive.arcadeDrive(forward, -turn)

        simulbot.update(self.talon_left.get(), self.talon_right.get())
        self.time += delta()
        dashboard2.update(self.time)

    def autonomousPeriodic(self):
        radius_drive(self.drive, 1, 10, 2)
        simulbot.update(self.talon_left.get(), self.talon_right.get())
        self.time += delta()
        dashboard2.update(self.time)

if __name__ == '__main__':
    wpilib.run(MyRobot)
