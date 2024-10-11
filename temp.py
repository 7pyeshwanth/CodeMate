import json
import streamlit as st
import streamlit.components.v1 as components

# Load contest data from contests.json
with open('contests.json', 'r') as f:
  contest_data = json.load(f)

# Generate HTML, CSS, and JavaScript from the loaded data
html_code = f"""
<style>
  /* Style the table */
  * {{
      color: white;
  }}
  table {{
    width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
    padding: 0.5em;
        text-align: left;
      }}
</style>

<table border="1" >
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>Type</th>
      <th>Phase</th>
      <th>Duration</th>
      <th>Start Time</th>
      <th>Countdown</th>
    </tr>
  </thead>
  <tbody id="contestTable">
    <!-- Rows will be inserted here dynamically -->
  </tbody>
</table>

<script>
// Contest data from contests.json
const contestData = {json.dumps(contest_data)};

// Helper function to format time
function formatTime(seconds) {{
  const d = Math.floor(seconds / (3600 * 24));
  const h = Math.floor((seconds % (3600 * 24)) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);

  let timeString = "";

  if (d > 0) {{
    timeString += `${{d}}d `;
  }}
  if (h > 0 || d > 0) {{  // Show hours only if days > 0 or if hours > 0
    timeString += `${{h}}h `;
  }}
  if (m > 0 || h > 0 || d > 0) {{  // Show minutes if hours > 0 or days > 0
    timeString += `${{m}}m `;
  }}
  if (s >= 0) {{  // Always show seconds
    timeString += `${{s}}s`;
  }}

  return timeString.trim();  // Remove trailing space
}}

// Function to update the countdown and table
function updateTable() {{
  const tableBody = document.getElementById("contestTable");
  tableBody.innerHTML = ""; // Clear previous rows

  const currentTimeSeconds = Math.floor(Date.now() / 1000);

  contestData.forEach(contest => {{
    const row = document.createElement("tr");

    // Create table cells
    const idCell = document.createElement("td");
    idCell.textContent = contest.id;

    const nameCell = document.createElement("td");
    nameCell.textContent = contest.name;

    const typeCell = document.createElement("td");
    typeCell.textContent = contest.type;

    const phaseCell = document.createElement("td");
    phaseCell.textContent = contest.phase;

    const durationCell = document.createElement("td");
    durationCell.textContent = `${{Math.floor(contest.durationSeconds / 3600)}}h ${{Math.floor((contest.durationSeconds % 3600) / 60)}}m`;

    const startTimeCell = document.createElement("td");
    const startTime = new Date(contest.startTimeSeconds * 1000);
    startTimeCell.textContent = startTime.toLocaleString();

    const countdownCell = document.createElement("td");
    const remainingTime = contest.startTimeSeconds - currentTimeSeconds;

    // Check if the contest has already started
    if (remainingTime > 0) {{
      countdownCell.textContent = formatTime(remainingTime);
    }} else {{
      countdownCell.textContent = "Started";
      countdownCell.style.color = "#5cb85c"; // Green color if started
    }}

    // Append cells to the row
    row.appendChild(idCell);
    row.appendChild(nameCell);
    row.appendChild(typeCell);
    row.appendChild(phaseCell);
    row.appendChild(durationCell);
    row.appendChild(startTimeCell);
    row.appendChild(countdownCell);

    // Append the row to the table body
    tableBody.appendChild(row);
  }});
}}

// Update the table every second
setInterval(updateTable, 1000);
</script>
"""

# Embed the HTML content in Streamlit
components.html(html_code, height=600)
