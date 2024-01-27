let currentIndex = 0;
let totalSlides = document.querySelectorAll(".carousel-slide").length;

function updateCarousel() {
  const carouselWrapper = document.getElementById("carouselWrapper");
  carouselWrapper.style.transform = `translateX(${-currentIndex * 10}%)`;
}

function updateTotalSlides() {
  totalSlides = document.querySelectorAll(".carousel-slide").length;
}

function nextSlide() {
  currentIndex = (currentIndex + 1) % totalSlides;
  updateCarousel();
}

function prevSlide() {
  currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
  updateCarousel();
}
