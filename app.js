(function () {
  const CAKES = [
    {
      id: 1,
      name: "Медовик сметанный",
      price: 3000,
      description: "Тонкие медовые коржи и нежный сметанный крем",
      image: "./images/01-medovik.jpg?v=2"
    },
    {
      id: 2,
      name: "Вишня шоколад",
      price: 3000,
      description: "Шоколадный бисквит с вишнёвой начинкой",
      image: "./images/02-vishnya-shokolad.png"
    },
    {
      id: 3,
      name: "Клубничный пломбир",
      price: 3000,
      description: "Клубника и воздушный сливочный пломбир",
      image: "./images/03-klubnika-plombir.png"
    },
    {
      id: 4,
      name: "Фисташка малина",
      price: 3000,
      description: "Фисташковый крем и свежая малина",
      image: "./images/04-fistashka-malina.png"
    },
    {
      id: 5,
      name: "Тирамису",
      price: 3000,
      description: "Маскарпоне, кофе и какао — классический вкус",
      image: "./images/05-tiramisu.jpg"
    },
    {
      id: 6,
      name: "Морковный",
      price: 3000,
      description: "Морковный бисквит с пряностями и крем-чизом",
      image: "./images/06-morkovnyy.jpg"
    },
    {
      id: 7,
      name: "Нутелла орехи",
      price: 3000,
      description: "Шоколад, фундук и крем с Нутеллой",
      image: "./images/07-nutella-orehi.png"
    },
    {
      id: 8,
      name: "Сникерс",
      price: 3000,
      description: "Солёная карамель, арахис и молочный шоколад",
      image: "./images/08-snikers.png"
    }
  ];

  const DESIGNS = [
    {
      id: "lambet",
      name: "Ламбет",
      hint: "Ровные грани, объёмный крем, рюши, классическая свадебная отделка",
      image: "./design-images/01-lambet.jpg"
    },
    {
      id: "waffle",
      name: "Вафельный",
      hint: "Вафельный декор по бокам торта",
      image: "./design-images/02-waffle.jpg"
    },
    {
      id: "italian",
      name: "Итальянский пирог",
      hint: "Низкий круглый пирог, крем и фрукты в итальянском стиле",
      image: "./design-images/03-italian.jpg"
    },
    {
      id: "oval-lambet",
      name: "Овальный ламбет",
      hint: "Овальная форма с ламбетной отделкой по контуру",
      image: "./design-images/04-oval-lambet.jpg"
    },
    {
      id: "custom",
      name: "Индивидуальный дизайн",
      hint: "Свой эскиз или идея — опишите в комментарии к заказу",
      image: "./design-images/05-custom.jpg"
    }
  ];

  const WEIGHT_OPTIONS_KG = [1, 1.5, 2, 2.5, 3, 4, 5];
  const DEFAULT_WEIGHT_KG = 1;

  function formatPrice(value) {
    return `${new Intl.NumberFormat("ru-RU").format(value)} руб.`;
  }

  function parseWeightKg(raw) {
    const w = Number(String(raw ?? "").replace(",", "."));
    if (WEIGHT_OPTIONS_KG.includes(w)) return w;
    return DEFAULT_WEIGHT_KG;
  }

  function formatWeightKg(kg) {
    const s = Number.isInteger(kg) ? String(kg) : String(kg).replace(".", ",");
    return `${s} кг`;
  }

  function cakeTotalPrice(cake, kg) {
    return Math.round(cake.price * kg);
  }

  function weightSelectHtml(selectedKg, attrs = "") {
    const options = WEIGHT_OPTIONS_KG.map(
      (w) =>
        `<option value="${w}"${w === selectedKg ? " selected" : ""}>${formatWeightKg(w)}</option>`
    ).join("");
    return `<select class="weight-select" ${attrs}>${options}</select>`;
  }

  function priceSummaryLabel(cake, kg) {
    return `${formatPrice(cake.price)} за кг · ${formatPrice(cakeTotalPrice(cake, kg))} итого`;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  /** Если .jpg/.png не откроется как картинка — подставить .svg с тем же именем. */
  function imageFallbackAttr(src) {
    if (!src || !/\.(jpe?g|png|webp)$/i.test(src)) return "";
    const svg = src.replace(/\.(jpe?g|png|webp)$/i, ".svg");
    if (svg === src) return "";
    return ` onerror="this.onerror=null;this.src='${escapeHtml(svg)}'"`;
  }

  function pluralCakes(n) {
    const m10 = n % 10;
    const m100 = n % 100;
    if (m100 >= 11 && m100 <= 14) return "тортов";
    if (m10 === 1) return "торт";
    if (m10 >= 2 && m10 <= 4) return "торта";
    return "тортов";
  }

  function initCatalog() {
    const searchInput = document.getElementById("searchInput");
    const sortSelect = document.getElementById("sortSelect");
    const cakeGrid = document.getElementById("cakeGrid");
    const metaText = document.getElementById("metaText");
    if (!searchInput || !sortSelect || !cakeGrid || !metaText) return;

    function getFilteredCakes() {
      const query = (searchInput.value || "").trim().toLowerCase();
      let items = CAKES.filter((cake) => {
        if (!query) return true;
        return (
          cake.name.toLowerCase().includes(query) ||
          cake.description.toLowerCase().includes(query)
        );
      });

      switch (sortSelect.value) {
        case "price-asc":
          items = [...items].sort((a, b) => a.price - b.price);
          break;
        case "price-desc":
          items = [...items].sort((a, b) => b.price - a.price);
          break;
        case "name-asc":
          items = [...items].sort((a, b) => a.name.localeCompare(b.name, "ru"));
          break;
        default:
          break;
      }

      return items;
    }

    function renderCatalog() {
      const items = getFilteredCakes();
      metaText.textContent = `Найдено: ${items.length} ${pluralCakes(items.length)}`;
      cakeGrid.innerHTML = "";

      if (!items.length) {
        cakeGrid.innerHTML =
          "<p class=\"empty-msg\">По вашему запросу ничего не найдено. Попробуйте другое слово.</p>";
        return;
      }

      items.forEach((cake) => {
        const card = document.createElement("article");
        card.className = "card";
        card.innerHTML = `
      <div class="card-photo">
        <img src="${escapeHtml(cake.image)}" alt="${escapeHtml(cake.name)}" loading="lazy" width="640" height="400"${imageFallbackAttr(cake.image)}>
      </div>
      <h3>${escapeHtml(cake.name)}</h3>
      <p class="desc">${escapeHtml(cake.description)}</p>
      <label class="card-weight">
        <span class="card-weight-label">Вес торта</span>
        ${weightSelectHtml(DEFAULT_WEIGHT_KG, `data-cake-id="${cake.id}" aria-label="Вес торта ${escapeHtml(cake.name)}"`)}
      </label>
      <div class="card-bottom">
        <div class="price-block">
          <span class="price">${formatPrice(cakeTotalPrice(cake, DEFAULT_WEIGHT_KG))}</span>
          <span class="price-per">${formatPrice(cake.price)} за кг</span>
        </div>
        <button class="order-btn" type="button" data-id="${cake.id}">Заказать</button>
      </div>
    `;
        cakeGrid.appendChild(card);
      });
    }

    function updateCardPrice(card, cake, kg) {
      const priceEl = card.querySelector(".price");
      if (priceEl) priceEl.textContent = formatPrice(cakeTotalPrice(cake, kg));
    }

    function handleOrderClick(event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("order-btn")) return;

      const id = Number(target.dataset.id);
      const cake = CAKES.find((item) => item.id === id);
      if (!cake) return;

      const card = target.closest(".card");
      const select = card?.querySelector(".weight-select");
      const weight = parseWeightKg(select?.value);

      window.location.href = `./design.html?id=${encodeURIComponent(String(cake.id))}&weight=${encodeURIComponent(String(weight))}`;
    }

    function handleWeightChange(event) {
      const select = event.target;
      if (!(select instanceof HTMLSelectElement) || !select.classList.contains("weight-select")) {
        return;
      }
      const card = select.closest(".card");
      const id = Number(select.dataset.cakeId);
      const cake = CAKES.find((item) => item.id === id);
      if (card && cake) updateCardPrice(card, cake, parseWeightKg(select.value));
    }

    searchInput.addEventListener("input", renderCatalog);
    sortSelect.addEventListener("change", renderCatalog);
    cakeGrid.addEventListener("click", handleOrderClick);
    cakeGrid.addEventListener("change", handleWeightChange);
    renderCatalog();
  }

  function initDesign() {
    const designGrid = document.getElementById("designGrid");
    if (!designGrid) return;

    let selectedDesignId = "";

    function getCakeIdFromQuery() {
      const params = new URLSearchParams(window.location.search);
      const raw = params.get("id");
      const id = raw === null || raw === "" ? NaN : Number(raw);
      return Number.isFinite(id) ? id : NaN;
    }

    function getWeightFromQuery() {
      const params = new URLSearchParams(window.location.search);
      return parseWeightKg(params.get("weight"));
    }

    function renderSummary(cake, weightKg) {
      const block = document.getElementById("cakeSummary");
      if (!block) return;
      block.hidden = false;
      block.innerHTML = `
    <div class="order-summary-inner">
      <div class="order-summary-photo">
        <img src="${escapeHtml(cake.image)}" alt="${escapeHtml(cake.name)}" width="120" height="75" loading="lazy"${imageFallbackAttr(cake.image)}>
      </div>
      <div class="order-summary-text">
        <p class="order-summary-label">Выбранная начинка</p>
        <p class="order-summary-name">${escapeHtml(cake.name)}</p>
        <label class="summary-weight">
          <span class="card-weight-label">Вес торта</span>
          ${weightSelectHtml(weightKg, 'id="designWeight" aria-label="Вес торта"')}
        </label>
        <p class="order-summary-meta" id="designPriceMeta">${escapeHtml(priceSummaryLabel(cake, weightKg))}</p>
      </div>
    </div>
  `;
      const weightSelect = document.getElementById("designWeight");
      const priceMeta = document.getElementById("designPriceMeta");
      if (weightSelect) {
        weightSelect.addEventListener("change", () => {
          const kg = parseWeightKg(weightSelect.value);
          if (priceMeta) priceMeta.textContent = priceSummaryLabel(cake, kg);
          selectedWeightKg = kg;
        });
      }
    }

    function renderDesignCards() {
      designGrid.innerHTML = "";

      DESIGNS.forEach((d) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "card design-card";
        btn.setAttribute("role", "radio");
        btn.setAttribute("aria-checked", "false");
        btn.dataset.designId = d.id;
        btn.setAttribute("aria-label", `${d.name}. ${d.hint}`);
        btn.innerHTML = `
      <div class="card-photo">
        <img src="${escapeHtml(d.image)}" alt="${escapeHtml(d.name)}" loading="lazy" width="640" height="400"${imageFallbackAttr(d.image)}>
      </div>
      <h3>${escapeHtml(d.name)}</h3>
      <p class="desc">${escapeHtml(d.hint)}</p>
    `;
        btn.addEventListener("click", () => selectDesign(d.id));
        designGrid.appendChild(btn);
      });
    }

    function selectDesign(id) {
      selectedDesignId = id;
      document.querySelectorAll(".design-card").forEach((el) => {
        const isSel = el.dataset.designId === id;
        el.classList.toggle("design-card--selected", isSel);
        el.setAttribute("aria-checked", isSel ? "true" : "false");
      });
      const continueBtn = document.getElementById("continueBtn");
      if (continueBtn) continueBtn.disabled = false;

      const toast = document.getElementById("designToast");
      if (toast) toast.hidden = true;
    }

    const cakeId = getCakeIdFromQuery();
    const cake = CAKES.find((c) => c.id === cakeId);
    let selectedWeightKg = getWeightFromQuery();

    const err = document.getElementById("designError");
    const section = document.getElementById("designSection");

    if (!cake) {
      if (err) err.hidden = false;
      return;
    }

    if (section) section.hidden = false;
    renderSummary(cake, selectedWeightKg);
    renderDesignCards();

    const continueBtn = document.getElementById("continueBtn");
    if (continueBtn) {
      continueBtn.addEventListener("click", () => {
        if (!selectedDesignId) return;
        const weightSelect = document.getElementById("designWeight");
        if (weightSelect) selectedWeightKg = parseWeightKg(weightSelect.value);
        window.location.href =
          `./order.html?id=${encodeURIComponent(String(cake.id))}&design=${encodeURIComponent(selectedDesignId)}&weight=${encodeURIComponent(String(selectedWeightKg))}`;
      });
    }
  }

  function initOrder() {
    const form = document.getElementById("orderForm");
    if (!form) return;

    const params = new URLSearchParams(window.location.search);
    const cakeId = Number(params.get("id"));
    const designId = params.get("design") || "";
    let orderWeightKg = parseWeightKg(params.get("weight"));
    const cake = CAKES.find((c) => c.id === cakeId);
    const design = DESIGNS.find((d) => d.id === designId);

    const err = document.getElementById("orderError");
    const section = document.getElementById("orderFormSection");
    const summary = document.getElementById("orderSummary");
    const backLink = document.getElementById("backToDesign");

    if (!cake || !design) {
      if (err) err.hidden = false;
      return;
    }

    if (backLink) {
      backLink.href = `./design.html?id=${encodeURIComponent(String(cake.id))}&weight=${encodeURIComponent(String(orderWeightKg))}`;
    }

    function renderOrderSummary(kg) {
      if (!summary) return;
      summary.hidden = false;
      summary.innerHTML = `
    <div class="order-summary-inner">
      <div class="order-summary-photo">
        <img src="${escapeHtml(cake.image)}" alt="${escapeHtml(cake.name)}" width="120" height="75" loading="lazy"${imageFallbackAttr(cake.image)}>
      </div>
      <div class="order-summary-text">
        <p class="order-summary-label">Ваш заказ</p>
        <p class="order-summary-name">${escapeHtml(cake.name)}</p>
        <p class="order-summary-meta">Стиль: ${escapeHtml(design.name)} · ${escapeHtml(formatWeightKg(kg))} · ${escapeHtml(priceSummaryLabel(cake, kg))}</p>
      </div>
    </div>
  `;
    }

    renderOrderSummary(orderWeightKg);

    const weightField = document.getElementById("orderWeight");
    if (weightField) {
      weightField.innerHTML = WEIGHT_OPTIONS_KG.map(
        (w) =>
          `<option value="${w}"${w === orderWeightKg ? " selected" : ""}>${formatWeightKg(w)}</option>`
      ).join("");
      weightField.addEventListener("change", () => {
        orderWeightKg = parseWeightKg(weightField.value);
        renderOrderSummary(orderWeightKg);
      });
    }

    if (section) section.hidden = false;

    const dateInput = document.getElementById("eventDate");
    if (dateInput) {
      const today = new Date();
      dateInput.min = today.toISOString().split("T")[0];
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const name = document.getElementById("customerName");
      const phone = document.getElementById("customerPhone");
      const email = document.getElementById("customerEmail");
      const eventDate = document.getElementById("eventDate");
      const comment = document.getElementById("orderComment");
      const sendError = document.getElementById("orderSendError");
      const submitBtn = form.querySelector(".order-submit");

      if (!name?.value.trim() || !phone?.value.trim() || !eventDate?.value) {
        form.reportValidity();
        return;
      }

      const weightInput = document.getElementById("orderWeight");
      if (weightInput) orderWeightKg = parseWeightKg(weightInput.value);

      const payload = {
        name: name.value.trim(),
        phone: phone.value.trim(),
        email: email?.value.trim() || "",
        eventDate: eventDate.value,
        comment: comment?.value.trim() || "",
        cakeName: cake.name,
        designName: design.name,
        weightLabel: formatWeightKg(orderWeightKg),
        priceLabel: priceSummaryLabel(cake, orderWeightKg),
      };

      if (sendError) {
        sendError.hidden = true;
        sendError.textContent = "";
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Отправляем…";
      }

      const formSection = document.getElementById("orderFormSection");
      const success = document.getElementById("orderSuccess");
      const successText = document.getElementById("orderSuccessText");

      try {
        const response = await fetch("/api/order", {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.ok) {
          throw new Error(result.error || "Не удалось отправить заявку");
        }

        if (formSection) formSection.hidden = true;
        if (summary) summary.hidden = true;

        if (success && successText) {
          const emailPart = payload.email ? ` Email: ${payload.email}.` : "";
          const commentPart = payload.comment
            ? ` Комментарий: ${payload.comment}`
            : "";
          successText.textContent =
            `Спасибо, ${payload.name}! Заявка отправлена в Telegram. Торт «${cake.name}» (${design.name}), ${payload.weightLabel}, ${payload.priceLabel}, дата ${payload.eventDate}. Телефон: ${payload.phone}.${emailPart}${commentPart} Менеджер kisura свяжется с вами.`;
          success.hidden = false;
          success.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      } catch (err) {
        if (sendError) {
          sendError.textContent =
            err instanceof Error
              ? err.message
              : "Ошибка отправки. Запустите сайт через: python3 server.py 8080";
          sendError.hidden = false;
        }
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Отправить заявку";
        }
      }
    });
  }

  initCatalog();
  initDesign();
  initOrder();
})();
