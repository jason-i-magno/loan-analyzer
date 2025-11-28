var themeToggleDarkIcon = document.getElementById("theme-toggle-dark-icon");
var themeToggleLightIcon = document.getElementById("theme-toggle-light-icon");

// Change the icons inside the button based on previous settings
if (
  localStorage.getItem("color-theme") === "dark" ||
  (!("color-theme" in localStorage) &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  themeToggleLightIcon.classList.remove("hidden");
} else {
  themeToggleDarkIcon.classList.remove("hidden");
}

var themeToggleBtn = document.getElementById("theme-toggle");
var analyzeButton = document.getElementById("analyze");
var errorContainer = document.getElementById("form-errors");

themeToggleBtn.addEventListener("click", function () {
  // toggle icons inside button
  themeToggleDarkIcon.classList.toggle("hidden");
  themeToggleLightIcon.classList.toggle("hidden");

  // if set via local storage previously
  if (localStorage.getItem("color-theme")) {
    if (localStorage.getItem("color-theme") === "light") {
      document.documentElement.classList.add("dark");
      localStorage.setItem("color-theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("color-theme", "light");
    }

    // if NOT set via local storage previously
  } else {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("color-theme", "light");
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("color-theme", "dark");
    }
  }

  analyzeLoan();
});

function clearErrors() {
  document
    .querySelectorAll("input")
    .forEach((el) =>
      el.classList.remove(
        "border-red-500",
        "focus:border-red-500",
        "focus:ring-red-500"
      )
    );
  document.querySelectorAll(".error-msg").forEach((el) => el.remove());
  errorContainer.textContent = "";
  errorContainer.classList.add("hidden");
}

function addFieldError(inputId, message) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.classList.add(
    "border-red-500",
    "focus:border-red-500",
    "focus:ring-red-500"
  );
  const msg = document.createElement("div");
  msg.className = "error-msg text-red-600 dark:text-red-400 text-xs mt-1";
  msg.textContent = message;
  input.insertAdjacentElement("afterend", msg);
}

function showGeneralError(message) {
  errorContainer.textContent = message;
  errorContainer.classList.remove("hidden");
}

function setLoading(isLoading) {
  if (!analyzeButton) return;
  analyzeButton.disabled = isLoading;
  analyzeButton.textContent = isLoading ? "Analyzing..." : "Analyze";
}

function parseNumber(id, { min = null, max = null, integer = false } = {}) {
  const raw = document.getElementById(id)?.value ?? "";
  const value = integer ? parseInt(raw, 10) : parseFloat(raw);
  if (Number.isNaN(value)) return { error: "Must be a number." };
  if (!Number.isFinite(value)) return { error: "Must be finite." };
  if (min !== null && value < min) return { error: `Must be >= ${min}.` };
  if (max !== null && value > max) return { error: `Must be <= ${max}.` };
  if (integer && !Number.isInteger(value))
    return { error: "Must be an integer." };
  return { value };
}

function parseDateValue(id) {
  const raw = document.getElementById(id)?.value;
  if (!raw) return { error: "Date is required." };
  const ts = Date.parse(raw);
  if (Number.isNaN(ts)) return { error: "Invalid date." };
  return { value: new Date(ts).toISOString().slice(0, 10) };
}

// Plotly Charts
const plotlyLightTheme = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "#f1f5f9", // slate-100
  font: { color: "#1f2937" }, // gray-800
  xaxis: { gridcolor: "#e5e7eb" }, // gray-200
  yaxis: { gridcolor: "#e5e7eb" },
};

const plotlyDarkTheme = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "#1e293b", // slate-800
  font: { color: "#f1f5f9" }, // slate-100
  xaxis: { gridcolor: "#334155" }, // slate-700
  yaxis: { gridcolor: "#334155" },
};

function isDarkMode() {
  return document.documentElement.classList.contains("dark");
}

function getPlotlyTheme() {
  return isDarkMode() ? plotlyDarkTheme : plotlyLightTheme;
}

function drawPlotlyCharts(data) {
  const values = [data.principal, data.total_interest];
  const labels = ["Principal", "Interest"];

  const fig = {
    data: [{ type: "pie", values, labels, hole: 0.4 }],
    layout: {
      ...getPlotlyTheme(),
      title: "Loan Breakdown",
    },
  };

  Plotly.newPlot("chart", fig.data, fig.layout);

  const aggregated = data.aggregated;

  // Plotly line chart
  const principal_trace = {
    x: aggregated.map((row) => row.due_date),
    y: aggregated.map((row) => row.principal_portion),
    name: "Principal",
    type: "scatter",
    mode: "lines",
  };
  const interest_trace = {
    x: aggregated.map((row) => row.due_date),
    y: aggregated.map((row) => row.interest_portion),
    name: "Interest",
    type: "scatter",
    mode: "lines",
  };
  Plotly.newPlot("payment_portion_graph", [principal_trace, interest_trace], {
    ...getPlotlyTheme(),
    title: "Principal vs Interest Over Time",
    xaxis: { title: "Month" },
    yaxis: { title: "Amount ($)" },
  });
}

const backend_base_url = "http://localhost:8001";

// Analyze loan
async function analyzeLoan() {
  clearErrors();
  setLoading(true);
  try {
    const errors = [];

    const rate = parseNumber("annual_interest_percentage", { min: 0 });
    if (rate.error) {
      errors.push("Rate " + rate.error);
      addFieldError("annual_interest_percentage", rate.error);
    }

    const closing = parseNumber("closing_costs", { min: 0 });
    if (closing.error) {
      errors.push("Closing costs " + closing.error);
      addFieldError("closing_costs", closing.error);
    }

    const down = parseNumber("down_payment_percentage", { min: 0, max: 100 });
    if (down.error) {
      errors.push("Down payment " + down.error);
      addFieldError("down_payment_percentage", down.error);
    }

    const extra = parseNumber("monthly_extra_payment", { min: 0 });
    if (extra.error) {
      errors.push("Monthly extra " + extra.error);
      addFieldError("monthly_extra_payment", extra.error);
    }

    const price = parseNumber("purchase_price", { min: 0.01 });
    if (price.error) {
      errors.push("Purchase price " + price.error);
      addFieldError("purchase_price", price.error);
    }

    const term = parseNumber("term_years", { min: 1, integer: true });
    if (term.error) {
      errors.push("Term years " + term.error);
      addFieldError("term_years", term.error);
    }

    const origDate = parseDateValue("origination_date");
    if (origDate.error) {
      errors.push("Origination date " + origDate.error);
      addFieldError("origination_date", origDate.error);
    }

    const extras = {};
    document.querySelectorAll(".extra-row").forEach((row) => {
      const monthRaw = row.querySelector(".extra-month")?.value;
      const amountRaw = row.querySelector(".extra-amount")?.value;
      if (!monthRaw && !amountRaw) return;
      const parsedDate = Date.parse(monthRaw);
      const amount = parseFloat(amountRaw);
      if (Number.isNaN(parsedDate)) {
        errors.push("Extra payment date is invalid.");
        row.querySelector(".extra-month")?.classList.add("border-red-500");
        return;
      }
      if (Number.isNaN(amount) || amount < 0) {
        errors.push("Extra payment amount must be a non-negative number.");
        row.querySelector(".extra-amount")?.classList.add("border-red-500");
        return;
      }
      const iso = new Date(parsedDate).toISOString().slice(0, 10);
      extras[iso] = amount;
    });

    if (errors.length) {
      showGeneralError("Please fix the highlighted fields.");
      return;
    }

    const response = await fetch(`${backend_base_url}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        annual_interest_percentage: rate.value,
        closing_costs: closing.value,
        down_payment_percentage: down.value,
        monthly_extra_payment: extra.value,
        origination_date: origDate.value,
        purchase_price: price.value,
        term_years: term.value,
        one_time_extras: extras,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      const errMsg =
        (data && data.errors && data.errors.join("; ")) ||
        data?.detail ||
        "Request failed.";
      showGeneralError(errMsg);
      return;
    }

    document.getElementById(
      "monthly_payment"
    ).innerText = `$${data.monthly_payment}`;

    document.getElementById(
      "total_interest"
    ).innerText = `$${data.total_interest}`;

    // Plotly Charts
    drawPlotlyCharts(data);

    // Create amortization table
    const schedule = data.schedule;
    const table_body = document.getElementById("schedule_table_body");
    table_body.innerHTML = `
      ${schedule
        .map(
          (row) => `
          <tr>
            <th scope="row">${row.payment_id}</th>
            <td>${row.due_date}</td>
            <td>${row.payment_date}</td>
            <td>${row.description}</td>
            <td>${row.payment_amount}</td>
            <td>${row.principal_portion}</td>
            <td>${row.interest_portion}</td>
            <td>${row.total_interest}</td>
            <td>${row.ending_balance}</td>
            <td>${row.resulting_ltv}</td>
          </tr>
        `
        )
        .join("")}
    `;
  } catch (err) {
    console.error(err);
    showGeneralError("Something went wrong. Please try again.");
  } finally {
    setLoading(false);
  }
}

document.getElementById("analyze").addEventListener("click", async () => {
  analyzeLoan();
});

const container = document.getElementById("extra-payments");
document.getElementById("add-extra").addEventListener("click", () => {
  const div = document.createElement("div");
  div.classList.add("extra-row");
  div.classList.add("mb-6");
  div.classList.add("grid");
  div.classList.add("grid-cols-3");
  div.classList.add("gap-4");
  div.innerHTML = `
    <div class="col-span-1 sm:col-span-1">
      <div class="relative">
        <div class="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3.5">
          <svg class="h-4 w-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                      fill="currentColor" viewBox="0 0 24 24">
            <path
              fill-rule="evenodd"
              d="M5 5a1 1 0 0 0 1-1 1 1 0 1 1 2 0 1 1 0 0 0 1 1h1a1 1 0 0 0 1-1 1 1 0 1 1 2 0 1 1 0 0 0 1 1h1a1 1 0 0 0 1-1 1 1 0 1 1 2 0 1 1 0 0 0 1 1 2 2 0 0
                 1 2 2v1a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a2 2 0 0 1 2-2ZM3 19v-7a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Zm6.01-6a1 1 0 1
                 0-2 0 1 1 0 0 0 2 0Zm2 0a1 1 0 1 1 2 0 1 1 0 0 1-2 0Zm6 0a1 1 0 1 0-2 0 1 1 0 0 0 2 0Zm-10 4a1 1 0 1 1 2 0 1 1 0 0 1-2 0Zm6 0a1 1 0 1 0-2 0 1
                 1 0 0 0 2 0Zm2 0a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <input id="origination_date" type="date" class="extra-month ps-9" placeholder="mm/dd/yyy" required />
      </div>
    </div>

    <div class="col-span-1 sm:col-span-1">
      <div class="relative">
        <div class="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3.5">
          <span class="text-gray-500 dark:text-gray-400">$</span>
        </div>
        <input type="text" id="purchase_price" class="extra-amount ps-7 " placeholder="0" required />
      </div>
    </div>
    <div class="col-span-1 sm:col-span-1">
      <button type="button" class="remove flex w-min items-center justify-center">X</button>
    </div>
  `;
  div.querySelector(".remove").onclick = () => div.remove();
  container.appendChild(div);
});
