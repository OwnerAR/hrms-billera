# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _

from erpnext.accounts.doctype.account.account import Account


class CustomAccount(Account):
	"""Custom Account class to handle duplicate account numbers"""
	
	def validate_account_number(self):
		"""
		Override to handle duplicate account numbers gracefully
		This fixes the issue with duplicate account numbers in Indonesia COA template
		"""
		if not self.account_number:
			return
			
		# Check for existing account with same account number
		existing_account = frappe.db.get_value(
			"Account",
			{
				"account_number": self.account_number,
				"company": self.company,
				"name": ["!=", self.name],
			},
			["name", "account_name"],
			as_dict=True,
		)
		
		if existing_account:
			# Instead of throwing error, clear the account number and log a warning
			frappe.logger().warning(
				f"Duplicate account number {self.account_number} found. "
				f"Clearing account number from {self.name} ({self.account_name}). "
				f"Already used by {existing_account.name} ({existing_account.account_name})"
			)
			
			# Clear the duplicate account number
			self.account_number = None
			
			# Optionally, you can show a message to user (but don't throw error)
			frappe.msgprint(
				_(
					"Account Number {0} is already used in account {1}. "
					"Account number has been cleared for {2}."
				).format(
					frappe.bold(self.account_number or ""),
					frappe.bold(f"{existing_account.name} - {existing_account.account_name}"),
					frappe.bold(self.account_name),
				),
				indicator="orange",
				alert=True,
			)

