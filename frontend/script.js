const backendBaseUrl = "http://localhost:8001";

document.getElementById("amortization").addEventListener("click", async () => {
  const annual_interest_percentage = parseFloat(
    document.getElementById("annual_interest_percentage").value
  );
  const closing_costs = parseFloat(
    document.getElementById("closing_costs").value
  );
  const down_payment_percentage = parseFloat(
    document.getElementById("down_payment_percentage").value
  );
  const purchase_price = parseFloat(
    document.getElementById("purchase_price").value
  );
  const term_years = parseInt(document.getElementById("term_years").value);

  const response = await fetch(`${backendBaseUrl}/amortization`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      annual_interest_percentage,
      closing_costs,
      down_payment_percentage,
      purchase_price,
      term_years,
    }),
  });

  const schedule = await response.json();

  // Plotly line chart
  const principal_trace = {
    x: schedule.map((row) => row.payment_id),
    y: schedule.map((row) => row.principal_portion),
    name: "Principal",
    type: "scatter",
    mode: "lines",
  };
  const interest_trace = {
    x: schedule.map((row) => row.payment_id),
    y: schedule.map((row) => row.interest_portion),
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
    <tr><th>Payment #</th><th>Payment Date</th><th>Payment Amount</th><th>Principal Portion</th><th>Interest Portion</th><th>Total Interest</th><th>Ending Balance</th><th>Resulting LTV%</th></tr>
    ${schedule
      .map(
        (row) => `
      <tr>
        <td>${row.payment_id}</td>
        <td>${row.payment_date}</td>
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
  const purchase_price = parseFloat(
    document.getElementById("purchase_price").value
  );
  const term_years = parseInt(document.getElementById("term_years").value);

  const response = await fetch(`${backendBaseUrl}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      annual_interest_percentage,
      closing_costs,
      down_payment_percentage,
      purchase_price,
      term_years,
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
});
