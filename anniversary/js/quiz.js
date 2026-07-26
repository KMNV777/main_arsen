const STORAGE_KEY = "anniversary-quiz-v1";

const quarters = {
  1: [
    {
      text: "Где мы впервые почувствовали, что это «не просто так»?",
      options: [
        "На длинной прогулке без плана",
        "В шумном кафе среди чужих разговоров",
        "В переписке до самого утра",
        "Когда просто молчали рядом",
      ],
      correct: 0,
      feedback: "Именно тогда воздух стал другим — тише и ближе.",
    },
    {
      text: "Что чаще всего выдавало наши чувства в начале?",
      options: [
        "Случайные улыбки",
        "Глупые шутки",
        "Взгляд, который слишком долго держался",
        "Всё сразу",
      ],
      correct: 3,
      feedback: "Мы ещё притворялись спокойными — безуспешно.",
    },
    {
      text: "Какой маленький ритуал появился у нас в первом квартале?",
      options: [
        "Доброе утро обязательно",
        "Общий плейлист",
        "«Как ты?» без повода",
        "Фото на память почти каждый раз",
      ],
      correct: 2,
      feedback: "Этот вопрос стал нашей нежностью по умолчанию.",
    },
    {
      text: "Что мы поняли друг о друге быстрее всего?",
      options: [
        "Любимый вкус и запах",
        "Как успокоить, когда тяжело",
        "Кто первый начинает обнимать",
        "Что рядом можно быть собой",
      ],
      correct: 3,
      feedback: "Самое важное открытие — безопасность быть настоящими.",
    },
  ],
  2: [
    {
      text: "Какая наша привычка стала самой домашней?",
      options: [
        "Готовить вместе и спорить о специях",
        "Смотреть «ещё одну серию»",
        "Делиться мелочами дня",
        "Засыпать, держась за руку",
      ],
      correct: 2,
      feedback: "Именно мелочи сшили дни в общую жизнь.",
    },
    {
      text: "Кто обычно выбирает, куда пойти вечером?",
      options: [
        "Ты",
        "Я",
        "Мы спорим, а потом смеёмся",
        "Идём туда, где теплее сердцу",
      ],
      correct: 2,
      feedback: "Даже выбор маршрута у нас — маленькое приключение.",
    },
    {
      text: "Что тебя в нас удивляет до сих пор?",
      options: [
        "Как легко мы находим общий язык",
        "Как быстро миримся",
        "Как много можем молчать и всё понимать",
        "Как каждый день чуть-чуть влюбляемся заново",
      ],
      correct: 3,
      feedback: "Вот оно — настоящее чудо второго сезона.",
    },
    {
      text: "Какое наше «мы» звучит точнее всего?",
      options: [
        "Команда",
        "Приключение",
        "Тихая гавань",
        "Любовь с характером",
      ],
      correct: 3,
      feedback: "С характером — и от этого ещё роднее.",
    },
  ],
  3: [
    {
      text: "Какое совместное приключение запомнилось ярче всего?",
      options: [
        "Поездка, где всё пошло не по плану",
        "Вечер, который растянулся на всю ночь",
        "Место, куда хочется вернуться",
        "День, когда смеялись без причины",
      ],
      correct: 0,
      feedback: "Лучшие истории начинаются с «а помнишь, как всё пошло не так?»",
    },
    {
      text: "Что мы берём с собой почти в любую поездку?",
      options: [
        "Любимую музыку",
        "Запас нежности",
        "Фотоаппарат или телефон наготове",
        "Всё перечисленное — и ещё шоколад",
      ],
      correct: 3,
      feedback: "Снаряжение настоящей пары: любовь и перекус.",
    },
    {
      text: "Какой наш общий «суперсила» в третьем квартале?",
      options: [
        "Поддерживать в трудный день",
        "Превращать обычное в праздник",
        "Находить красоту в мелочах",
        "Держаться крепче, когда мир качает",
      ],
      correct: 1,
      feedback: "С тобой даже вторник умеет быть особенным.",
    },
    {
      text: "Что ты хочешь повторить из этого сезона снова и снова?",
      options: [
        "Долгие разговоры",
        "Новые места",
        "Тихие вечера только вдвоём",
        "Всё, где есть мы",
      ],
      correct: 3,
      feedback: "Правильный ответ всегда один: где есть мы.",
    },
  ],
  4: [
    {
      text: "Чем для тебя стал этот год рядом?",
      options: [
        "Домом",
        "Школой нежности",
        "Лучшим приключением",
        "Доказательством, что любовь — это выбор каждый день",
      ],
      correct: 3,
      feedback: "И ты выбираешь — снова и снова. Я тоже.",
    },
    {
      text: "Какая фраза лучше описывает нас сейчас?",
      options: [
        "Мы только начинаем",
        "Мы уже своя история",
        "Мы — привычка и чудо одновременно",
        "Мы — навсегда в работе",
      ],
      correct: 2,
      feedback: "Привычка греть, чудо — не приедаться.",
    },
    {
      text: "Что ты ценишь во мне больше всего за этот год?",
      options: [
        "Заботу",
        "Юмор",
        "Верность мелочам",
        "То, как я смотрю на тебя",
      ],
      correct: 0,
      feedback: "Забота — наш тихий язык любви.",
    },
    {
      text: "Какое желание на следующий год самое важное?",
      options: [
        "Больше путешествий",
        "Больше тишины вдвоём",
        "Больше смелости мечтать вместе",
        "Просто быть рядом — и не отпускать",
      ],
      correct: 3,
      feedback: "Главное желание уже сбывается: мы вместе.",
    },
  ],
};

const scoreMessages = [
  {
    min: 14,
    title: "Ты знаешь нас наизусть",
    message:
      "Шестнадцать вопросов — и почти все ответы из самого сердца. Я так тебя люблю.",
  },
  {
    min: 10,
    title: "Ты чувствуешь нашу историю",
    message:
      "Мы говорим на одном языке даже тогда, когда выбираем разные слова. Это и есть мы.",
  },
  {
    min: 6,
    title: "Главное ты помнишь точно",
    message:
      "Не в баллах дело — в том, что каждый вопрос про нас настоящих. С праздником, любовь моя.",
  },
  {
    min: 0,
    title: "Любовь важнее правильных ответов",
    message:
      "Пусть викторина пошутила — а год вместе сказал всё сам. Я выбираю тебя снова.",
  },
];

/** @type {Map<string, { selected: number, correct: boolean }>} */
const answers = new Map();
let sectionObserver = null;
let confettiStarted = false;

function loadSaved() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    Object.entries(data).forEach(([id, value]) => {
      answers.set(id, value);
    });
  } catch {
    /* ignore broken storage */
  }
}

function saveAnswers() {
  const data = Object.fromEntries(answers.entries());
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function renderQuizzes() {
  document.querySelectorAll(".quiz").forEach((container) => {
    const quarter = Number(container.dataset.quarter);
    const questions = quarters[quarter] || [];

    container.innerHTML = questions
      .map((q, index) => {
        const id = `q${quarter}-${index}`;
        const saved = answers.get(id);
        const options = q.options
          .map((label, optionIndex) => {
            const classes = ["option"];
            let disabled = "";
            if (saved) {
              disabled = "disabled";
              if (optionIndex === q.correct) classes.push("is-correct");
              if (optionIndex === saved.selected) classes.push("is-selected");
              if (
                optionIndex === saved.selected &&
                optionIndex !== q.correct
              ) {
                classes.push("is-wrong");
              }
            }
            return `
            <button
              type="button"
              class="${classes.join(" ")}"
              data-question="${id}"
              data-option="${optionIndex}"
              data-correct="${q.correct}"
              ${disabled}
            >${label}</button>`;
          })
          .join("");

        const feedbackText = saved
          ? saved.correct
            ? q.feedback
            : `Почти! ${q.feedback}`
          : "";

        return `
          <article class="question" data-id="${id}">
            <h3 class="question__text">${index + 1}. ${q.text}</h3>
            <div class="options">${options}</div>
            <p class="question__feedback${saved ? " is-show" : ""}"${
              saved ? "" : " hidden"
            }>${feedbackText}</p>
          </article>`;
      })
      .join("");
  });
}

function quarterAnsweredCount(quarter) {
  let count = 0;
  for (let i = 0; i < 4; i += 1) {
    if (answers.has(`q${quarter}-${i}`)) count += 1;
  }
  return count;
}

function updateQuarterUi() {
  for (let quarter = 1; quarter <= 4; quarter += 1) {
    const count = quarterAnsweredCount(quarter);
    const counter = document.querySelector(`[data-count-for="${quarter}"]`);
    const next = document.querySelector(`[data-unlock="${quarter}"]`);
    if (counter) {
      counter.textContent = `${count} / 4`;
      counter.classList.toggle("is-done", count === 4);
    }
    if (next) {
      const unlocked = count === 4;
      const wasLocked = next.classList.contains("is-locked");
      next.classList.toggle("is-locked", !unlocked);
      if (unlocked) {
        next.classList.add("is-unlocked");
        if (wasLocked) {
          next.classList.remove("is-unlocked");
          // reflow to retrigger animation
          void next.offsetWidth;
          next.classList.add("is-unlocked");
        }
      }
    }
  }
}

function getScore() {
  return [...answers.values()].filter((item) => item.correct).length;
}

function animateScore(target) {
  const scoreValue = document.getElementById("scoreValue");
  const scoreBlock = scoreValue.parentElement;
  const start = Number(scoreValue.textContent) || 0;
  if (start === target) {
    scoreBlock.classList.add("is-pop");
    return;
  }

  const duration = 700;
  const started = performance.now();
  scoreBlock.classList.remove("is-pop");

  const tick = (now) => {
    const t = Math.min(1, (now - started) / duration);
    const eased = 1 - (1 - t) ** 3;
    scoreValue.textContent = String(Math.round(start + (target - start) * eased));
    if (t < 1) {
      requestAnimationFrame(tick);
    } else {
      scoreValue.textContent = String(target);
      scoreBlock.classList.add("is-pop");
    }
  };

  requestAnimationFrame(tick);
}

function updateScore(animate = false) {
  const score = getScore();
  const title = document.getElementById("finaleTitle");
  const message = document.getElementById("finaleMessage");
  const pack =
    scoreMessages.find((item) => score >= item.min) || scoreMessages.at(-1);

  title.textContent = pack.title;
  message.textContent = pack.message;

  if (animate) animateScore(score);
  else document.getElementById("scoreValue").textContent = String(score);
}

function applyAnswer(questionId, selected) {
  const [quarter, index] = questionId.slice(1).split("-").map(Number);
  const question = quarters[quarter][index];
  const article = document.querySelector(`[data-id="${questionId}"]`);
  if (!article) return;

  const correct = question.correct;
  const feedback = article.querySelector(".question__feedback");

  article.querySelectorAll(".option").forEach((option) => {
    option.disabled = true;
    const optionIndex = Number(option.dataset.option);
    option.classList.toggle("is-correct", optionIndex === correct);
    option.classList.toggle("is-selected", optionIndex === selected);
    option.classList.toggle(
      "is-wrong",
      optionIndex === selected && optionIndex !== correct
    );
  });

  answers.set(questionId, {
    selected,
    correct: selected === correct,
  });

  feedback.hidden = false;
  feedback.textContent =
    selected === correct ? question.feedback : `Почти! ${question.feedback}`;
  feedback.classList.add("is-show");

  saveAnswers();
  updateQuarterUi();
  updateScore(true);
}

function handleOptionClick(event) {
  const button = event.target.closest(".option");
  if (!button || button.disabled) return;
  applyAnswer(button.dataset.question, Number(button.dataset.option));
}

function observeSections() {
  if (sectionObserver) sectionObserver.disconnect();

  sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.28 }
  );

  document.querySelectorAll(".quarter").forEach((section) => {
    sectionObserver.observe(section);
  });
}

function bindProgress() {
  const bar = document.getElementById("progressBar");
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const value = max > 0 ? (window.scrollY / max) * 100 : 0;
    bar.style.width = `${value}%`;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function bindDots() {
  const links = [...document.querySelectorAll(".dots__item")];
  const sections = links
    .map((link) => document.getElementById(link.dataset.target))
    .filter(Boolean);

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((link) => {
          link.classList.toggle(
            "is-active",
            link.dataset.target === entry.target.id
          );
        });
      });
    },
    { threshold: 0.45 }
  );

  sections.forEach((section) => observer.observe(section));
}

function burstConfetti() {
  const canvas = document.getElementById("confetti");
  if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  const ctx = canvas.getContext("2d");
  const resize = () => {
    canvas.width = canvas.clientWidth * devicePixelRatio;
    canvas.height = canvas.clientHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  };
  resize();

  const colors = ["#d4a574", "#c45c6a", "#f7ebe3", "#7db88a", "#e8b4b8"];
  const pieces = Array.from({ length: 70 }, () => ({
    x: Math.random() * canvas.clientWidth,
    y: -20 - Math.random() * canvas.clientHeight * 0.4,
    r: 3 + Math.random() * 4,
    vy: 1.4 + Math.random() * 2.4,
    vx: -1 + Math.random() * 2,
    rot: Math.random() * Math.PI,
    vr: -0.08 + Math.random() * 0.16,
    color: colors[Math.floor(Math.random() * colors.length)],
  }));

  let frames = 0;
  const draw = () => {
    frames += 1;
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
    pieces.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.rot += p.vr;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.r, -p.r * 0.4, p.r * 2, p.r * 0.8);
      ctx.restore();
    });
    if (frames < 180) requestAnimationFrame(draw);
    else ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  };

  window.addEventListener("resize", resize, { once: true });
  requestAnimationFrame(draw);
}

function bindFinale() {
  const finale = document.getElementById("finale");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || confettiStarted) return;
        if (answers.size < 16) return;
        confettiStarted = true;
        updateScore(true);
        burstConfetti();
      });
    },
    { threshold: 0.5 }
  );
  observer.observe(finale);
}

async function shareResult() {
  const score = getScore();
  const title = document.getElementById("finaleTitle").textContent;
  const text = `${title}\nРезультат: ${score}/16\nС праздником, любовь моя 💛`;
  const btn = document.getElementById("shareBtn");

  try {
    await navigator.clipboard.writeText(text);
    const prev = btn.textContent;
    btn.textContent = "Скопировано";
    setTimeout(() => {
      btn.textContent = prev;
    }, 1600);
  } catch {
    btn.textContent = "Не удалось скопировать";
  }
}

function restartQuiz() {
  answers.clear();
  localStorage.removeItem(STORAGE_KEY);
  confettiStarted = false;
  renderQuizzes();
  updateQuarterUi();
  updateScore(false);
  document
    .querySelectorAll(".quarter")
    .forEach((section) => section.classList.remove("is-visible"));
  observeSections();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function init() {
  loadSaved();
  renderQuizzes();
  updateQuarterUi();
  updateScore(false);
  observeSections();
  bindProgress();
  bindDots();
  bindFinale();

  document.addEventListener("click", handleOptionClick);
  document.getElementById("restartBtn").addEventListener("click", restartQuiz);
  document.getElementById("shareBtn").addEventListener("click", shareResult);
}

init();
