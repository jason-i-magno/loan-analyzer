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
  const annual_interest_percentage = parseFloat(
    document.getElementById("annual_interest_percentage").value
  );
  const closing_costs = parseFloat(
    document.getElementById("closing_costs").value
  );
  const down_payment_percentage = parseFloat(
    document.getElementById("down_payment_percentage").value
  );
  const monthly_extra_payment = parseFloat(
    document.getElementById("monthly_extra_payment").value
  );
  const origination_date = document.getElementById("origination_date").value;
  const purchase_price = parseFloat(
    document.getElementById("purchase_price").value
  );
  const term_years = parseInt(document.getElementById("term_years").value);

  // One time extra payments.
  const extras = {};
  document.querySelectorAll(".extra-row").forEach((row) => {
    console.log("Found row");
    const month = row.querySelector(".extra-month").value;
    const amount = parseFloat(row.querySelector(".extra-amount").value);
    if (month && !isNaN(amount)) extras[month] = amount;
  });

  const response = await fetch(`${backend_base_url}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      annual_interest_percentage,
      closing_costs,
      down_payment_percentage,
      monthly_extra_payment,
      origination_date,
      purchase_price,
      term_years,
      one_time_extras: extras,
    }),
  });

  const data = await response.json();

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
        <input datepicker datepicker-format="mm/dd/yyyy" id="origination_date" type="text" class="extra-month ps-9" placeholder="mm/dd/yyy" required />
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
