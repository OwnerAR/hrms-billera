# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe


def execute():
	"""
	Fix duplicate account numbers in Chart of Accounts
	This patch handles the issue with duplicate account numbers in Indonesia COA
	"""
	frappe.logger().info("Running patch to fix duplicate account numbers...")
	
	# Get all companies
	companies = frappe.get_all("Company", pluck="name")
	
	for company in companies:
		fix_duplicate_account_numbers_for_company(company)


def fix_duplicate_account_numbers_for_company(company):
	"""Fix duplicate account numbers for a specific company"""
	try:
		# Find accounts with duplicate account numbers
		duplicate_query = """
			SELECT account_number, COUNT(*) as count
			FROM `tabAccount`
			WHERE company = %s AND account_number IS NOT NULL AND account_number != ''
			GROUP BY account_number
			HAVING count > 1
		"""
		duplicates = frappe.db.sql(duplicate_query, (company,), as_dict=True)
		
		if duplicates:
			frappe.logger().info(f"Found {len(duplicates)} duplicate account numbers in company {company}")
			
			for dup in duplicates:
				account_number = dup.account_number
				# Get all accounts with this duplicate number
				accounts = frappe.db.sql(
					"""
					SELECT name, account_name, account_number
					FROM `tabAccount`
					WHERE company = %s AND account_number = %s
					ORDER BY creation
				""",
					(company, account_number),
					as_dict=True,
				)
				
				# Keep the first one, clear account_number for the rest
				for idx, account in enumerate(accounts):
					if idx > 0:  # Skip first account
						frappe.db.set_value(
							"Account", account.name, "account_number", None, update_modified=False
						)
						frappe.logger().info(
							f"Cleared duplicate account number {account_number} from account {account.name} ({account.account_name})"
						)
			
			frappe.db.commit()
			frappe.logger().info(f"Fixed duplicate account numbers for company {company}")
		else:
			frappe.logger().info(f"No duplicate account numbers found in company {company}")
			
	except Exception as e:
		frappe.logger().error(f"Error fixing duplicate account numbers for company {company}: {str(e)}")
		frappe.log_error(f"Failed to fix duplicate account numbers for company {company}")

