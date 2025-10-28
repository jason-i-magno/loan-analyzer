const backendUrl = "http://localhost:8001/analyze";

document.getElementById("analyze").addEventListener("click", async () => {
  const annual_interest_percentage = parseFloat(document.getElementById("annual_interest_percentage").value);
  const closing_costs = parseFloat(document.getElementById("closing_costs").value);
  const down_payment_percentage = parseFloat(document.getElementById("down_payment_percentage").value);
  const purchase_price = parseFloat(document.getElementById("purchase_price").value);
  const term_years = parseInt(document.getElementById("term_years").value);

  const response = await fetch(backendUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ annual_interest_percentage, closing_costs, down_payment_percentage, purchase_price, term_years }),
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
