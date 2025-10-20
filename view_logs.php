<?php
include('config.php'); // includes both MySQL + SQLite connections

// --- Handle Delete Single Log ---
if (isset($_GET['delete'])) {
  $id = intval($_GET['delete']);
  $sqlite->exec("DELETE FROM logs WHERE id = $id");
  header("Location: view_logs.php");
  exit();
}

// --- Handle Delete All Logs ---
if (isset($_GET['delete_all'])) {
  $sqlite->exec("DELETE FROM logs");
  header("Location: view_logs.php");
  exit();
}

// --- Handle Export to CSV ---
if (isset($_GET['export'])) {
  $filename = "logs_export_" . date("Y-m-d_H-i-s") . ".csv";
  header("Content-Type: text/csv");
  header("Content-Disposition: attachment; filename=$filename");

  $output = fopen("php://output", "w");
  fputcsv($output, ["ID", "Action", "Email", "Timestamp"]);

  $results = $sqlite->query("SELECT * FROM logs ORDER BY id DESC");
  while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
    fputcsv($output, $row);
  }
  fclose($output);
  exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Admin Activity Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://kit.fontawesome.com/a2e0ad1c6d.js" crossorigin="anonymous"></script>
  <style>
    body {
      background-color: #f8f9fa;
    }
    .card {
      border-radius: 1rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .table-container {
      max-height: 500px;
      overflow-y: auto;
    }
    .badge {
      font-size: 0.9em;
    }
  </style>
</head>
<body>

<div class="container mt-5">
  <div class="card">
    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
      <h4 class="mb-0"><i class="fa-solid fa-clipboard-list"></i> Activity Logs</h4>
      <div>
        <a href="login.php" class="btn btn-outline-light btn-sm"><i class="fa-solid fa-door-open"></i> Back to Login</a>
      </div>
    </div>

    <div class="card-body">
      <!-- Control Buttons -->
      <div class="d-flex justify-content-between mb-3">
        <div>
          <a href="?export=true" class="btn btn-success btn-sm">
            <i class="fa-solid fa-file-export"></i> Export CSV
          </a>
          <a href="?delete_all=true" onclick="return confirm('Delete ALL logs?')" class="btn btn-danger btn-sm">
            <i class="fa-solid fa-trash"></i> Delete All
          </a>
        </div>
        <input type="text" id="searchInput" class="form-control w-25" placeholder="Search..." onkeyup="searchLogs()">
      </div>

      <!-- Logs Table -->
      <div class="table-container">
        <table class="table table-hover align-middle text-center">
          <thead class="table-dark sticky-top">
            <tr>
              <th>ID</th>
              <th>Action</th>
              <th>User Email</th>
              <th>Timestamp</th>
              <th>Delete</th>
            </tr>
          </thead>
          <tbody>
            <?php
            $results = $sqlite->query("SELECT * FROM logs ORDER BY id DESC");
            if ($results) {
              while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
                echo "<tr>
                        <td>{$row['id']}</td>
                        <td><span class='badge bg-primary'>{$row['action']}</span></td>
                        <td>{$row['email']}</td>
                        <td>{$row['timestamp']}</td>
                        <td>
                          <a href='?delete={$row['id']}' class='btn btn-sm btn-outline-danger' onclick='return confirm(\"Delete this log?\")'>
                            <i class='fa-solid fa-trash'></i>
                          </a>
                        </td>
                      </tr>";
              }
            } else {
              echo "<tr><td colspan='5'>No logs found.</td></tr>";
            }
            ?>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- JavaScript Search Function -->
<script>
function searchLogs() {
  let input = document.getElementById('searchInput').value.toLowerCase();
  let rows = document.querySelectorAll('tbody tr');

  rows.forEach(row => {
    let text = row.textContent.toLowerCase();
    row.style.display = text.includes(input) ? '' : 'none';
  });
}
</script>

</body>
</html>
