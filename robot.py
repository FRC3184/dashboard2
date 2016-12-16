import wpilib
from dashboard import dashboard2 as dashboard
import time


__last_time = time.time()

simulbot_js = """
var robot_x = 0;
var robot_y = 0;
var robot_theta = 0
var robot_max_wheel_speed = 10
var robot_width = 2;

var last_time = Date.now();

source.addEventListener('simulbot', function(event) {

    var delta = Date.now() - last_time;
    last_time += delta;

    var data = JSON.parse(event.data);
    var left_dist = data.left * robot_max_wheel_speed * delta / 1000;
    var right_dist = data.right * robot_max_wheel_speed * delta / 1000;
    var dist = (left_dist + right_dist) / 2;
    robot_x += dist * Math.cos(robot_theta);
    robot_y += dist * Math.sin(robot_theta);
    robot_theta += (right_dist - left_dist) / robot_width


    var element = $("#simulbot");
    var canvas = element.get(0).getContext("2d");
    var h = element.height();
    var w = element.width();
    var SCALE = 1;
    var r_w = robot_width * 12;
    var r_h = 60 - r_w;
    r_w *= SCALE;
    r_h *= SCALE;

    canvas.clearRect(0, 0, 400, 400);
    canvas.beginPath();

    canvas.save();
    canvas.setTransform(1, 0, 0, 1, 0, 0);
    canvas.strokeStyle = "#000";
    canvas.translate(w/2, h/2);
    canvas.rotate(robot_theta + Math.PI / 2);

    canvas.rect(-r_w/2, -r_h/2, r_w, r_h);
    canvas.moveTo(0, 0);
    canvas.lineTo(0, -r_h/2);
    canvas.stroke();
    canvas.restore();

    canvas.save();
    canvas.setTransform(1, 0, 0, 1, 0, 0);
    canvas.strokeStyle = "#000";
    canvas.translate(w/2 -robot_x, h/2 -robot_y);
    canvas.moveTo(0, 150);
    canvas.lineTo(150, -75);
    canvas.lineTo(-150, -75);
    canvas.lineTo(0, 150);
    canvas.stroke();
    canvas.restore();


}, false);
"""


def delta():
    global __last_time
    now = time.time()
    dt = now - __last_time
    __last_time = now
    return dt


class MyRobot(wpilib.IterativeRobot):
    def __init__(self):
        super().__init__()
        self.talon_left = wpilib.Talon(0)
        self.talon_right = wpilib.Talon(1)
        self.drive = wpilib.RobotDrive(self.talon_left, self.talon_right)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearLeft, False)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearRight, True)
        self.joystick = wpilib.Joystick(0)

        dashboard.graph("Forward", self.joystick.getY)
        dashboard.graph("Turn", self.joystick.getX)
        dashboard.graph("Talon Left", self.talon_left.get)
        dashboard.graph("Talon Right", self.talon_right.get)

        dashboard.extension("Simulbot", "<canvas id='simulbot' width='400' height='400'></canvas>", simulbot_js, "")

        self.time = 0

        dashboard.run()

    def disabledPeriodic(self):
        self.time += delta()
        dashboard.update(self.time)

    def teleopPeriodic(self):
        turn = self.joystick.getX()
        forward = self.joystick.getY()
        dashboard.send_message({"left": self.talon_left.get(), "right": self.talon_right.get()}, "simulbot")
        self.drive.arcadeDrive(forward, turn)
        self.time += delta()
        dashboard.update(self.time)

if __name__ == '__main__':
    wpilib.run(MyRobot)
