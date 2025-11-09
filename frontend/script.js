const backend_base_url = "http://localhost:8001";

// Default origination date to current day.
const origination_date_element = document.getElementById("origination_date");
origination_date_element.valueAsDate = new Date();

document.getElementById("analyze").addEventListener("click", async () => {
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
    "results"
  ).innerText = `Monthly: $${data.monthly_payment}, Total Interest: $${data.total_interest}`;

  const values = [data.principal, data.total_interest];
  const labels = ["Principal", "Interest"];

  const fig = {
    data: [{ type: "pie", values, labels, hole: 0.4 }],
    layout: { title: "Loan Breakdown" },
  };

  Plotly.newPlot("chart", fig.data, fig.layout);

  const schedule = data.schedule;
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
  Plotly.newPlot("amortization_schedule", [principal_trace, interest_trace], {
    title: "Principal vs Interest Over Time",
    xaxis: { title: "Month" },
    yaxis: { title: "Amount ($)" },
  });

  // Create table
  const table = document.getElementById("schedule_table");
  table.innerHTML = `
    <tr><th>Payment #</th><th>Due Date</th><th>Payment Date</th><th>Description</th><th>Payment Amount</th><th>Principal Portion</th><th>Interest Portion</th><th>Total Interest</th><th>Ending Balance</th><th>Resulting LTV%</th></tr>
    ${schedule
      .map(
        (row) => `
      <tr>
        <td>${row.payment_id}</td>
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
});

const container = document.getElementById("extra-container");
document.getElementById("add-extra").addEventListener("click", () => {
  const div = document.createElement("div");
  div.classList.add("extra-row");
  div.innerHTML = `
    <input type="date" class="extra-month">
    <input type="number" placeholder="Amount ($)" class="extra-amount">
    <button type="button" class="remove">×</button>
  `;
  div.querySelector(".remove").onclick = () => div.remove();
  container.appendChild(div);
});
