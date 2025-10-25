#!/bin/bash

# Fix Duplicate Account Numbers Script
# Usage: ./fix_account_numbers.sh [site_name]

SITE_NAME=${1:-"hrms.localhost"}

echo "=========================================="
echo "Fix Duplicate Account Numbers"
echo "Site: $SITE_NAME"
echo "=========================================="
echo ""

# Check if bench exists
if ! command -v bench &> /dev/null; then
    echo "Error: bench command not found"
    echo "Please run this script from frappe-bench directory or ensure bench is in PATH"
    exit 1
fi

# Check if site exists
if ! bench --site "$SITE_NAME" list-apps &> /dev/null; then
    echo "Error: Site $SITE_NAME not found"
    exit 1
fi

echo "Step 1: Checking for duplicate account numbers..."
bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.connect()

duplicates = frappe.db.sql("""
    SELECT company, account_number, COUNT(*) as count
    FROM \`tabAccount\`
    WHERE account_number IS NOT NULL AND account_number != ''
    GROUP BY company, account_number
    HAVING count > 1
""", as_dict=True)

if duplicates:
    print(f"\nFound {len(duplicates)} duplicate account numbers:")
    for dup in duplicates:
        print(f"  - Company: {dup.company}, Account Number: {dup.account_number}, Count: {dup.count}")
else:
    print("\nNo duplicate account numbers found!")
EOF

echo ""
echo "Step 2: Running fix patch..."
bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.connect()

from hrms.patches.post_install.fix_duplicate_account_numbers import execute

print("\nExecuting fix...")
execute()
print("Fix completed!")
EOF

echo ""
echo "Step 3: Verifying fix..."
bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.connect()

duplicates = frappe.db.sql("""
    SELECT company, account_number, COUNT(*) as count
    FROM \`tabAccount\`
    WHERE account_number IS NOT NULL AND account_number != ''
    GROUP BY company, account_number
    HAVING count > 1
""", as_dict=True)

if duplicates:
    print(f"\nWarning: Still found {len(duplicates)} duplicate account numbers")
    print("Please check manually")
else:
    print("\n✓ Success! All duplicate account numbers have been fixed")
EOF

echo ""
echo "Step 4: Clearing cache..."
bench --site "$SITE_NAME" clear-cache

echo ""
echo "=========================================="
echo "Fix process completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart bench: bench restart"
echo "2. Try setup wizard again"
echo ""

