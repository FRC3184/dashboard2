var robotConnected = false;
var arm_len = 288;

function rotateArm(angle, to_rotate) {
	var rads = angle * Math.PI/180;
	var y_change = (-1*Math.round(Math.sin(rads)*arm_len/2)) -30;
	var x_change = Math.round(Math.cos(rads)*arm_len/2) + 57;
	var transform = "translate(" +x_change+ "px, " +y_change+ "px)" + " rotate(" + (-angle) + "deg)";
	//console.log(transform);
	to_rotate.css({"transform": transform});
}
function rotateDisplay(angle, display, offset) {
	display.text((Math.round(angle*10)/10) + String.fromCharCode(176));
	var rads = angle * Math.PI/180;
	var x = Math.round(Math.cos(rads)*(arm_len+offset)) + (arm_len+offset)*(3/4);
	var y = -Math.round(Math.sin(rads)*(arm_len+offset));
	var transform = "translate(" + x + "px, " + y + "px)";
	//console.log(transform);
	display.css({"transform": transform});
}

function animateArm(arm, display, init) {
	var deg = init;
	var dir = 1;
	return setInterval(function() {
		rotateArm(deg, arm);
		rotateDisplay(deg, display);
		deg += dir*1;
		if (deg == 115 || deg == -15) {
			dir *= -1;
		}
	}, 50);
}

$(document).ready(function() {
var arm_real = $("#arm-real");
var display_real = $("#real-angle");
var arm_fake = $("#arm-fake");
var display_fake = $("#fake-angle");
rotateArm(0, arm_real);
rotateArm(30, arm_fake);
rotateDisplay(0, display_real, 0);
rotateDisplay(30, display_fake, 30);
//animateArm(arm_fake, display_fake, 30);
//animateArm(arm_real, display_real, 0);

attachRobotConnectionIndicator("#jesse-ventura")

NetworkTables.addWsConnectionListener(function() {
	NetworkTables.addKeyListener("/SmartDashboard/Articulate Angle", function(key, value, isNew) {
		rotateArm(value, arm_real);
		rotateDisplay(value, display_real);
	});
	NetworkTables.addKeyListener("/SmartDashboard/Articulate Set Angle", function(key, value, isNew) {
		rotateArm(value, arm_fake);
		rotateDisplay(value, display_fake);
	});
    NetworkTables.addGlobalListener(function(key, value, isNew){
        console.log(key + " : " + value);
    }, true);
});


});