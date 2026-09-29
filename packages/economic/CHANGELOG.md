# Changelog

## 0.1.0

First release. Read-only e-conomic REST client: agreement identity check,
invoices (booked/paid/unpaid/overdue/not-due) with consistency issues, customers,
accounts, accounting years, and entries per year or per account. Integer
minor-unit money with Z3-proved base-currency conversion (int64-bounded),
settlement partition and pay state. Injection-safe filter builder with a proved
field/operator boundary. Proved pagination planning, budgeted walks that are
complete or an error. Smoke test runs offline against captured demo fixtures and
live against e-conomic's public demo agreement.
