# Cash Flow Minimizer — Multi-Mode DAA Project

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install flask
```

### 2. Run the app
```bash
cd cash-flow-minimizer
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## 🌐 Pages

| URL | Mode | Algorithm |
|-----|------|-----------|
| `/` | Landing Page | Animation |
| `/dashboard` | Greedy Mode | Greedy + Merge Sort |
| `/priority` | Priority Mode | Sorting + Greedy |
| `/paths` | Path Explorer | Graph + DFS/Backtracking |
| `/zero-sum` | Zero-Sum Groups | DP-style Subset Search |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/minimize` | POST | Greedy cash flow minimization |
| `/api/priority` | POST | Priority-sorted settlement |
| `/api/paths` | POST | DFS settlement path exploration |
| `/api/zero-sum` | POST | Zero-sum group detection |

### Request format (all endpoints):
```json
{
  "participants": ["Alice", "Bob", "Carol"],
  "transactions": [
    {"debtor": "Alice", "creditor": "Bob", "amount": 100},
    {"debtor": "Bob", "creditor": "Carol", "amount": 50}
  ]
}
```

---

## 🗂 Project Structure

```
cash-flow-minimizer/
├── app.py                  ← Flask backend (all 4 modes)
├── templates/
│   ├── index.html          ← Landing page with animation
│   ├── dashboard.html      ← Mode 1: Greedy
│   ├── priority.html       ← Mode 2: Priority
│   ├── paths.html          ← Mode 3: Path Explorer
│   └── zero_sum.html       ← Mode 4: Zero-Sum Groups
├── static/
│   └── css/
│       └── base.css
└── README.md
```

---

## 🧠 Algorithm Summary

| Mode | Focus | Core Algorithm |
|------|-------|----------------|
| Greedy | Minimize transaction count | Greedy + Merge Sort |
| Priority | Who should pay/receive first | Sorting by magnitude |
| Path Explorer | All possible settlement chains | DFS + Backtracking |
| Zero-Sum | Self-settling subgroups | Subset enumeration (DP-style) |
