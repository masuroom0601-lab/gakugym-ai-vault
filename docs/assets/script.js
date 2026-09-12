// 学ジム 公式サイト 共通スクリプト(ナビ開閉+お問い合わせ文字数カウント)
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
  }

  const message = document.getElementById("message");
  const charCount = document.getElementById("char-count");
  if (message && charCount) {
    const max = 500;
    const update = () => {
      const remaining = Math.max(0, max - message.value.length);
      charCount.textContent = `残り${remaining}文字`;
    };
    message.addEventListener("input", update);
    update();
  }
});
