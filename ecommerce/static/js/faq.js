// Seleciona todos os itens de FAQ
document.addEventListener("DOMContentLoaded", function () {
  const faqItems = document.querySelectorAll(".faq-item");

  faqItems.forEach(item => {
      const question = item.querySelector(".faq-question");

      // Adiciona um evento de clique para cada pergunta
      question.addEventListener("click", function () {
          // Alterna a classe 'active' para expandir ou recolher
          item.classList.toggle("active");
      });
  });
});
