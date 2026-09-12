// 学ジム 公式サイト 共通スクリプト(ナビ開閉+ヒーロースライドショー)
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
  }

  const slides = document.querySelectorAll(".hero-slide");
  const dots = document.querySelectorAll(".hero-dots button");
  if (slides.length > 1) {
    let current = 0;
    const show = (i) => {
      slides.forEach((s, idx) => s.classList.toggle("active", idx === i));
      dots.forEach((d, idx) => d.classList.toggle("active", idx === i));
      current = i;
    };
    dots.forEach((d, idx) => d.addEventListener("click", () => show(idx)));
    setInterval(() => show((current + 1) % slides.length), 5000);
  }
});
