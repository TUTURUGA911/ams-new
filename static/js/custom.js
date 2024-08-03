(function() {
	'use strict';

	// Initialize the tiny slider
	function initTinySlider() {
		var sliders = document.querySelectorAll('.testimonial-slider');
		if (sliders.length > 0) {
			tns({
				container: '.testimonial-slider',
				items: 1,
				axis: "horizontal",
				controlsContainer: "#testimonial-nav",
				swipeAngle: false,
				speed: 700,
				nav: true,
				controls: true,
				autoplay: true,
				autoplayHoverPause: true,
				autoplayTimeout: 3500,
				autoplayButtonOutput: false
			});
		}
	}

	// Initialize the quantity control
	function initQuantityControls() {
		var quantityContainers = document.getElementsByClassName('quantity-container');

		for (var i = 0; i < quantityContainers.length; i++) {
			bindQuantityControlEvents(quantityContainers[i]);
		}

		function bindQuantityControlEvents(container) {
			var quantityAmount = container.getElementsByClassName('quantity-amount')[0];
			var increaseButton = container.getElementsByClassName('increase')[0];
			var decreaseButton = container.getElementsByClassName('decrease')[0];

			increaseButton.addEventListener('click', function() {
				updateQuantity(quantityAmount, 1);
			});

			decreaseButton.addEventListener('click', function() {
				updateQuantity(quantityAmount, -1);
			});
		}

		function updateQuantity(quantityElement, delta) {
			var value = parseInt(quantityElement.value, 10);
			value = isNaN(value) ? 0 : value;
			value += delta;
			if (value < 0) value = 0;
			quantityElement.value = value;
		}
	}

	// Initialize all functionalities
	function init() {
		initTinySlider();
		initQuantityControls();
	}

	// Run the initialization
	init();
})();
