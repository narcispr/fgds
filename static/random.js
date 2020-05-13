// Global variable
var img = null,
	needle = null,
	ctx = null,
	degrees = 0;
	counter = 0;
	limit = 0;
	compas_int = null;

function dice() {
    var d2 = Math.floor(Math.random() * 2) + 1;
    document.getElementById('d2').innerHTML = d2.toString();
    var d6 = Math.floor(Math.random() * 6) + 1;
    document.getElementById('d6').innerHTML = d6.toString();
    var d20 = Math.floor(Math.random() * 20) + 1;
    document.getElementById('d20').innerHTML = d20.toString();
    var dx = Math.floor(Math.random() * parseInt(document.getElementById('dx_input').value)) + 1;
    document.getElementById('dx').innerHTML = dx.toString();
}

function initiative() {
    var p1 = Math.floor(Math.random() * 20) + 1;
    var results = Array(p1);
    var p2 = getD20NotInValues(results);
    results.push(p2);
    var p3 = getD20NotInValues(results);
    results.push(p3);
    var p4 = getD20NotInValues(results);
    
    document.getElementById('p1_dice').innerHTML = p1.toString();
    document.getElementById('p2_dice').innerHTML = p2.toString();
    document.getElementById('p3_dice').innerHTML = p3.toString();
    document.getElementById('p4_dice').innerHTML = p4.toString();
}

function getD20NotInValues(values) {
    var d20 = Math.floor(Math.random() * 20) + 1;
    while (values.includes(d20)) {
        d20 = Math.floor(Math.random() * 20) + 1;
    }
    return d20;
}

function moveCompass() {
	startAnimation();
	counter = 0;
	limit = 360 + Math.floor(Math.random() * 359);
}

function clearCanvas() {
	 // clear canvas
	ctx.clearRect(0, 0, 200, 200);
}

function draw() {

	clearCanvas();

	// Draw the compass onto the canvas
	ctx.drawImage(img, 0, 0);

	// Save the current drawing state
	ctx.save();

	// Now move across and down half the 
	ctx.translate(100, 100);

	// Rotate around this point
	ctx.rotate(degrees * (Math.PI / 180));

	// Draw the image back and up
	ctx.drawImage(needle, -100, -100);

	// Restore the previous drawing state
	ctx.restore();

	// Increment the angle of the needle by 5 degrees until max
	if (counter <= limit){
		degrees += 2;
		counter += 2;
	}
	if ((counter > limit) && (limit > 0)){
		clearTimeout(compas_int);
	}
}

function startAnimation() {
	// Image loaded event complete.  Start the timer
	clearTimeout(compas_int);
	compas_int = setInterval(draw, 5);
}

function init_compass() {
	// Grab the compass element
	var canvas = document.getElementById('compass');

	// Canvas supported?
	if (canvas.getContext('2d')) {
		ctx = canvas.getContext('2d');

		// Load the needle image
		needle = new Image();
		needle.src = '../static/needle.png';

		// Load the compass image
		img = new Image();
		img.src = '../static/compass.png';
		img.onload = draw;
		
	} else {
		alert("Canvas not supported!");
	}
}