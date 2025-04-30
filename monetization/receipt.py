"""
Receipt generation for the pAIssive Income project.

This module provides classes for generating and managing receipts for transactions.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import copy

from common_utils import to_json, write_file


class ReceiptItem:
    """
    Class representing an item on a receipt.

    This class provides a structured way to represent a line item on a receipt,
    including the item description, quantity, unit price, and any discounts.
    """

    def __init__(
        self,
        description: str,
        quantity: float = 1.0,
        unit_price: float = 0.0,
        discount: float = 0.0,
        tax_rate: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a receipt item.

        Args:
            description: Description of the item
            quantity: Quantity of the item
            unit_price: Unit price of the item
            discount: Discount amount for the item
            tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
            metadata: Additional metadata for the item
        """
        self.id = str(uuid.uuid4())
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount
        self.tax_rate = tax_rate
        self.metadata = metadata or {}

    def get_subtotal(self) -> float:
        """
        Get the subtotal for this item (quantity * unit_price).

        Returns:
            Subtotal amount
        """
        return self.quantity * self.unit_price

    def get_discount_amount(self) -> float:
        """
        Get the discount amount for this item.

        Returns:
            Discount amount
        """
        return self.discount

    def get_taxable_amount(self) -> float:
        """
        Get the taxable amount for this item (subtotal - discount).

        Returns:
            Taxable amount
        """
        return max(0, self.get_subtotal() - self.get_discount_amount())

    def get_tax_amount(self) -> float:
        """
        Get the tax amount for this item.

        Returns:
            Tax amount
        """
        return self.get_taxable_amount() * self.tax_rate

    def get_total(self) -> float:
        """
        Get the total for this item (taxable amount + tax amount).

        Returns:
            Total amount
        """
        return self.get_taxable_amount() + self.get_tax_amount()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the receipt item to a dictionary.

        Returns:
            Dictionary representation of the receipt item
        """
        return {
            "id": self.id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "discount": self.discount,
            "tax_rate": self.tax_rate,
            "subtotal": self.get_subtotal(),
            "discount_amount": self.get_discount_amount(),
            "taxable_amount": self.get_taxable_amount(),
            "tax_amount": self.get_tax_amount(),
            "total": self.get_total(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReceiptItem":
        """
        Create a receipt item from a dictionary.

        Args:
            data: Dictionary with receipt item data

        Returns:
            ReceiptItem instance
        """
        item = cls(
            description=data["description"],
            quantity=data["quantity"],
            unit_price=data["unit_price"],
            discount=data["discount"],
            tax_rate=data["tax_rate"],
            metadata=data.get("metadata", {}),
        )

        item.id = data["id"]

        return item

    def __str__(self) -> str:
        """String representation of the receipt item."""
        return f"{self.description}: {self.quantity} x ${self.unit_price:.2f} = ${self.get_total():.2f}"


class Receipt:
    """
    Class for generating and managing receipts.

    This class provides methods for creating, formatting, and managing
    receipts for transactions.
    """

    def __init__(
        self,
        transaction_id: str,
        customer_id: str,
        date: Optional[datetime] = None,
        currency: str = "USD",
        items: Optional[List[ReceiptItem]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a receipt.

        Args:
            transaction_id: ID of the transaction
            customer_id: ID of the customer
            date: Date of the receipt
            currency: Currency code (e.g., USD)
            items: List of receipt items
            metadata: Additional metadata for the receipt
        """
        self.id = str(uuid.uuid4())
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.date = date or datetime.now()
        self.currency = currency
        self.items = items or []
        self.metadata = metadata or {}

        # Initialize other properties
        self.company_name = self.metadata.get("company_name", "")
        self.company_address = self.metadata.get("company_address", "")
        self.company_email = self.metadata.get("company_email", "")
        self.company_phone = self.metadata.get("company_phone", "")
        self.company_website = self.metadata.get("company_website", "")
        self.company_logo_url = self.metadata.get("company_logo_url", "")

        self.customer_name = self.metadata.get("customer_name", "")
        self.customer_email = self.metadata.get("customer_email", "")
        self.customer_address = self.metadata.get("customer_address", "")

        self.payment_method = self.metadata.get("payment_method", "")
        self.payment_id = self.metadata.get("payment_id", "")

        self.notes = self.metadata.get("notes", "")
        self.terms = self.metadata.get("terms", "")

        self.tax_name = self.metadata.get("tax_name", "Tax")
        self.discount_name = self.metadata.get("discount_name", "Discount")

        self.additional_fees = self.metadata.get("additional_fees", [])
        self.custom_fields = self.metadata.get("custom_fields", {})

    def add_item(
        self,
        description: str,
        quantity: float = 1.0,
        unit_price: float = 0.0,
        discount: float = 0.0,
        tax_rate: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReceiptItem:
        """
        Add an item to the receipt.

        Args:
            description: Description of the item
            quantity: Quantity of the item
            unit_price: Unit price of the item
            discount: Discount amount for the item
            tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
            metadata: Additional metadata for the item

        Returns:
            The created receipt item
        """
        item = ReceiptItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tax_rate=tax_rate,
            metadata=metadata,
        )

        self.items.append(item)

        return item

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the receipt.

        Args:
            item_id: ID of the item to remove

        Returns:
            True if the item was removed, False otherwise
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                return True

        return False

    def get_item(self, item_id: str) -> Optional[ReceiptItem]:
        """
        Get an item from the receipt.

        Args:
            item_id: ID of the item

        Returns:
            The receipt item or None if not found
        """
        for item in self.items:
            if item.id == item_id:
                return item

        return None

    def get_items(self) -> List[ReceiptItem]:
        """
        Get all items on the receipt.

        Returns:
            List of receipt items
        """
        return self.items

    def set_company_info(
        self,
        name: str,
        address: str = "",
        email: str = "",
        phone: str = "",
        website: str = "",
        logo_url: str = "",
    ) -> None:
        """
        Set company information for the receipt.

        Args:
            name: Company name
            address: Company address
            email: Company email
            phone: Company phone
            website: Company website
            logo_url: URL to company logo
        """
        self.company_name = name
        self.company_address = address
        self.company_email = email
        self.company_phone = phone
        self.company_website = website
        self.company_logo_url = logo_url

        # Update metadata
        self.metadata["company_name"] = name
        self.metadata["company_address"] = address
        self.metadata["company_email"] = email
        self.metadata["company_phone"] = phone
        self.metadata["company_website"] = website
        self.metadata["company_logo_url"] = logo_url

    def set_customer_info(self, name: str, email: str = "", address: str = "") -> None:
        """
        Set customer information for the receipt.

        Args:
            name: Customer name
            email: Customer email
            address: Customer address
        """
        self.customer_name = name
        self.customer_email = email
        self.customer_address = address

        # Update metadata
        self.metadata["customer_name"] = name
        self.metadata["customer_email"] = email
        self.metadata["customer_address"] = address

    def set_payment_info(self, method: str, payment_id: str = "") -> None:
        """
        Set payment information for the receipt.

        Args:
            method: Payment method
            payment_id: Payment ID
        """
        self.payment_method = method
        self.payment_id = payment_id

        # Update metadata
        self.metadata["payment_method"] = method
        self.metadata["payment_id"] = payment_id

    def add_custom_field(self, name: str, value: Any) -> None:
        """
        Add a custom field to the receipt.

        Args:
            name: Field name
            value: Field value
        """
        self.custom_fields[name] = value
        self.metadata["custom_fields"] = self.custom_fields

    def add_additional_fee(
        self, name: str, amount: float, is_percentage: bool = False
    ) -> None:
        """
        Add an additional fee to the receipt.

        Args:
            name: Fee name
            amount: Fee amount
            is_percentage: Whether the fee is a percentage of the subtotal
        """
        fee = {"name": name, "amount": amount, "is_percentage": is_percentage}

        self.additional_fees.append(fee)
        self.metadata["additional_fees"] = self.additional_fees

    def set_notes(self, notes: str) -> None:
        """
        Set notes for the receipt.

        Args:
            notes: Receipt notes
        """
        self.notes = notes
        self.metadata["notes"] = notes

    def set_terms(self, terms: str) -> None:
        """
        Set terms and conditions for the receipt.

        Args:
            terms: Terms and conditions
        """
        self.terms = terms
        self.metadata["terms"] = terms

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the receipt to a dictionary.

        Returns:
            Dictionary representation of the receipt
        """
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "date": self.date.isoformat(),
            "currency": self.currency,
            "items": [item.to_dict() for item in self.items],
            "company_name": self.company_name,
            "company_address": self.company_address,
            "company_email": self.company_email,
            "company_phone": self.company_phone,
            "company_website": self.company_website,
            "company_logo_url": self.company_logo_url,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_address": self.customer_address,
            "payment_method": self.payment_method,
            "payment_id": self.payment_id,
            "notes": self.notes,
            "terms": self.terms,
            "tax_name": self.tax_name,
            "discount_name": self.discount_name,
            "additional_fees": self.additional_fees,
            "custom_fields": self.custom_fields,
            "subtotal": self.get_subtotal(),
            "discount_total": self.get_discount_total(),
            "tax_total": self.get_tax_total(),
            "additional_fees_total": self.get_additional_fees_total(),
            "total": self.get_total(),
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the receipt to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the receipt
        """
        return to_json(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Receipt":
        """
        Create a receipt from a dictionary.

        Args:
            data: Dictionary with receipt data

        Returns:
            Receipt instance
        """
        # Create receipt
        receipt = cls(
            transaction_id=data["transaction_id"],
            customer_id=data["customer_id"],
            date=datetime.fromisoformat(data["date"]),
            currency=data["currency"],
            metadata=data.get("metadata", {}),
        )

        # Set receipt ID
        receipt.id = data["id"]

        # Add items
        for item_data in data["items"]:
            item = ReceiptItem.from_dict(item_data)
            receipt.items.append(item)

        # Set other properties
        receipt.company_name = data.get("company_name", "")
        receipt.company_address = data.get("company_address", "")
        receipt.company_email = data.get("company_email", "")
        receipt.company_phone = data.get("company_phone", "")
        receipt.company_website = data.get("company_website", "")
        receipt.company_logo_url = data.get("company_logo_url", "")

        receipt.customer_name = data.get("customer_name", "")
        receipt.customer_email = data.get("customer_email", "")
        receipt.customer_address = data.get("customer_address", "")

        receipt.payment_method = data.get("payment_method", "")
        receipt.payment_id = data.get("payment_id", "")

        receipt.notes = data.get("notes", "")
        receipt.terms = data.get("terms", "")

        receipt.tax_name = data.get("tax_name", "Tax")
        receipt.discount_name = data.get("discount_name", "Discount")

        receipt.additional_fees = data.get("additional_fees", [])
        receipt.custom_fields = data.get("custom_fields", {})

        return receipt

    def get_subtotal(self) -> float:
        """
        Get the subtotal for all items on the receipt.

        Returns:
            Subtotal amount
        """
        return sum(item.get_subtotal() for item in self.items)

    def get_discount_total(self) -> float:
        """
        Get the total discount amount for all items on the receipt.

        Returns:
            Total discount amount
        """
        return sum(item.get_discount_amount() for item in self.items)

    def get_taxable_amount(self) -> float:
        """
        Get the total taxable amount for all items on the receipt.

        Returns:
            Total taxable amount
        """
        return sum(item.get_taxable_amount() for item in self.items)

    def get_tax_total(self) -> float:
        """
        Get the total tax amount for all items on the receipt.

        Returns:
            Total tax amount
        """
        return sum(item.get_tax_amount() for item in self.items)

    def get_additional_fees_total(self) -> float:
        """
        Get the total amount for all additional fees on the receipt.

        Returns:
            Total additional fees amount
        """
        total = 0.0
        subtotal = self.get_subtotal()

        for fee in self.additional_fees:
            if fee["is_percentage"]:
                total += subtotal * fee["amount"] / 100.0
            else:
                total += fee["amount"]

        return total

    def get_total(self) -> float:
        """
        Get the total amount for the receipt.

        Returns:
            Total amount
        """
        return (
            self.get_taxable_amount()
            + self.get_tax_total()
            + self.get_additional_fees_total()
        )

    def format_amount(self, amount: float) -> str:
        """
        Format an amount with currency symbol.

        Args:
            amount: Amount to format

        Returns:
            Formatted amount with currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }

        symbol = currency_symbols.get(self.currency, self.currency)

        if self.currency == "JPY":
            # JPY doesn't use decimal places
            return f"{symbol}{int(amount):,}"
        else:
            return f"{symbol}{amount:,.2f}"

    def to_text(self) -> str:
        """
        Format the receipt as plain text.

        Returns:
            Plain text representation of the receipt
        """
        lines = []

        # Add company information
        if self.company_name:
            lines.append(self.company_name)

        if self.company_address:
            lines.append(self.company_address)

        if self.company_phone or self.company_email:
            contact_info = []

            if self.company_phone:
                contact_info.append(f"Phone: {self.company_phone}")

            if self.company_email:
                contact_info.append(f"Email: {self.company_email}")

            lines.append(" | ".join(contact_info))

        if self.company_website:
            lines.append(f"Website: {self.company_website}")

        lines.append("")

        # Add receipt information
        lines.append(f"Receipt: {self.id}")
        lines.append(f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.transaction_id:
            lines.append(f"Transaction: {self.transaction_id}")

        lines.append("")

        # Add customer information
        if self.customer_name or self.customer_email or self.customer_address:
            lines.append("Customer Information:")

            if self.customer_name:
                lines.append(f"Name: {self.customer_name}")

            if self.customer_email:
                lines.append(f"Email: {self.customer_email}")

            if self.customer_address:
                lines.append(f"Address: {self.customer_address}")

            lines.append("")

        # Add payment information
        if self.payment_method or self.payment_id:
            lines.append("Payment Information:")

            if self.payment_method:
                lines.append(f"Method: {self.payment_method}")

            if self.payment_id:
                lines.append(f"Payment ID: {self.payment_id}")

            lines.append("")

        # Add items
        lines.append("Items:")
        lines.append("-" * 80)
        lines.append(
            f"{'Description':<40} {'Quantity':>10} {'Unit Price':>15} {'Discount':>15} {'Total':>15}"
        )
        lines.append("-" * 80)

        for item in self.items:
            lines.append(
                f"{item.description:<40} "
                f"{item.quantity:>10.2f} "
                f"{self.format_amount(item.unit_price):>15} "
                f"{self.format_amount(item.discount):>15} "
                f"{self.format_amount(item.get_total()):>15}"
            )

        lines.append("-" * 80)

        # Add totals
        lines.append(f"{'Subtotal:':<65} {self.format_amount(self.get_subtotal()):>15}")

        if self.get_discount_total() > 0:
            lines.append(
                f"{self.discount_name+'s:':<65} {self.format_amount(self.get_discount_total()):>15}"
            )

        if self.get_tax_total() > 0:
            lines.append(
                f"{self.tax_name+'es:':<65} {self.format_amount(self.get_tax_total()):>15}"
            )

        # Add additional fees
        for fee in self.additional_fees:
            fee_name = fee["name"]

            if fee["is_percentage"]:
                fee_name += f" ({fee['amount']}%)"
                fee_amount = self.get_subtotal() * fee["amount"] / 100.0
            else:
                fee_amount = fee["amount"]

            lines.append(f"{fee_name+'s:':<65} {self.format_amount(fee_amount):>15}")

        lines.append("-" * 80)
        lines.append(f"{'Total:':<65} {self.format_amount(self.get_total()):>15}")
        lines.append("-" * 80)

        # Add notes
        if self.notes:
            lines.append("")
            lines.append("Notes:")
            lines.append(self.notes)

        # Add terms
        if self.terms:
            lines.append("")
            lines.append("Terms and Conditions:")
            lines.append(self.terms)

        # Add custom fields
        if self.custom_fields:
            lines.append("")
            lines.append("Additional Information:")

            for name, value in self.custom_fields.items():
                lines.append(f"{name}: {value}")

        return "\n".join(lines)

    def to_html(self) -> str:
        """
        Format the receipt as HTML.

        Returns:
            HTML representation of the receipt
        """
        html = []

        # Start HTML document
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append(f"<title>Receipt {self.id}</title>")
        html.append("<style>")
        html.append(
            "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
        )
        html.append(
            ".receipt { max-width: 800px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }"
        )
        html.append(".header { text-align: center; margin-bottom: 20px; }")
        html.append(".company-name { font-size: 24px; font-weight: bold; }")
        html.append(".receipt-info { margin-bottom: 20px; }")
        html.append(".customer-info { margin-bottom: 20px; }")
        html.append(".payment-info { margin-bottom: 20px; }")
        html.append(
            ".items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }"
        )
        html.append(".items th, .items td { padding: 8px; text-align: right; }")
        html.append(
            ".items th:first-child, .items td:first-child { text-align: left; }"
        )
        html.append(".items th { background-color: #f2f2f2; }")
        html.append(".items tr:nth-child(even) { background-color: #f9f9f9; }")
        html.append(".totals { width: 100%; margin-bottom: 20px; }")
        html.append(".totals td { padding: 8px; text-align: right; }")
        html.append(".totals td:first-child { text-align: left; }")
        html.append(".total-row { font-weight: bold; }")
        html.append(".notes, .terms, .custom-fields { margin-top: 20px; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")

        # Receipt container
        html.append('<div class="receipt">')

        # Header with company information
        html.append('<div class="header">')

        if self.company_logo_url:
            html.append(
                f'<img src="{self.company_logo_url}" alt="{self.company_name}" style="max-height: 100px; margin-bottom: 10px;">'
            )

        if self.company_name:
            html.append(f'<div class="company-name">{self.company_name}</div>')

        if self.company_address:
            html.append(f"<div>{self.company_address}</div>")

        contact_info = []

        if self.company_phone:
            contact_info.append(f"Phone: {self.company_phone}")

        if self.company_email:
            contact_info.append(f"Email: {self.company_email}")

        if contact_info:
            html.append(f'<div>{" | ".join(contact_info)}</div>')

        if self.company_website:
            html.append(f"<div>Website: {self.company_website}</div>")

        html.append("</div>")  # End header

        # Receipt information
        html.append('<div class="receipt-info">')
        html.append(f"<div><strong>Receipt:</strong> {self.id}</div>")
        html.append(
            f'<div><strong>Date:</strong> {self.date.strftime("%Y-%m-%d %H:%M:%S")}</div>'
        )

        if self.transaction_id:
            html.append(
                f"<div><strong>Transaction:</strong> {self.transaction_id}</div>"
            )

        html.append("</div>")  # End receipt info

        # Customer information
        if self.customer_name or self.customer_email or self.customer_address:
            html.append('<div class="customer-info">')
            html.append("<h3>Customer Information</h3>")

            if self.customer_name:
                html.append(f"<div><strong>Name:</strong> {self.customer_name}</div>")

            if self.customer_email:
                html.append(f"<div><strong>Email:</strong> {self.customer_email}</div>")

            if self.customer_address:
                html.append(
                    f"<div><strong>Address:</strong> {self.customer_address}</div>"
                )

            html.append("</div>")  # End customer info

        # Payment information
        if self.payment_method or self.payment_id:
            html.append('<div class="payment-info">')
            html.append("<h3>Payment Information</h3>")

            if self.payment_method:
                html.append(
                    f"<div><strong>Method:</strong> {self.payment_method}</div>"
                )

            if self.payment_id:
                html.append(
                    f"<div><strong>Payment ID:</strong> {self.payment_id}</div>"
                )

            html.append("</div>")  # End payment info

        # Items
        html.append('<table class="items">')
        html.append("<tr>")
        html.append("<th>Description</th>")
        html.append("<th>Quantity</th>")
        html.append("<th>Unit Price</th>")
        html.append("<th>Discount</th>")
        html.append("<th>Total</th>")
        html.append("</tr>")

        for item in self.items:
            html.append("<tr>")
            html.append(f"<td>{item.description}</td>")
            html.append(f"<td>{item.quantity:.2f}</td>")
            html.append(f"<td>{self.format_amount(item.unit_price)}</td>")
            html.append(f"<td>{self.format_amount(item.discount)}</td>")
            html.append(f"<td>{self.format_amount(item.get_total())}</td>")
            html.append("</tr>")

        html.append("</table>")

        # Totals
        html.append('<table class="totals">')
        html.append(
            f"<tr><td>Subtotal:</td><td>{self.format_amount(self.get_subtotal())}</td></tr>"
        )

        if self.get_discount_total() > 0:
            html.append(
                f"<tr><td>{self.discount_name}s:</td><td>{self.format_amount(self.get_discount_total())}</td></tr>"
            )

        if self.get_tax_total() > 0:
            html.append(
                f"<tr><td>{self.tax_name}es:</td><td>{self.format_amount(self.get_tax_total())}</td></tr>"
            )

        # Additional fees
        for fee in self.additional_fees:
            fee_name = fee["name"]

            if fee["is_percentage"]:
                fee_name += f" ({fee['amount']}%)"
                fee_amount = self.get_subtotal() * fee["amount"] / 100.0
            else:
                fee_amount = fee["amount"]

            html.append(
                f"<tr><td>{fee_name}:</td><td>{self.format_amount(fee_amount)}</td></tr>"
            )

        html.append(
            f'<tr class="total-row"><td>Total:</td><td>{self.format_amount(self.get_total())}</td></tr>'
        )
        html.append("</table>")

        # Notes
        if self.notes:
            html.append('<div class="notes">')
            html.append("<h3>Notes</h3>")
            html.append(f"<p>{self.notes}</p>")
            html.append("</div>")

        # Terms
        if self.terms:
            html.append('<div class="terms">')
            html.append("<h3>Terms and Conditions</h3>")
            html.append(f"<p>{self.terms}</p>")
            html.append("</div>")

        # Custom fields
        if self.custom_fields:
            html.append('<div class="custom-fields">')
            html.append("<h3>Additional Information</h3>")
            html.append("<ul>")

            for name, value in self.custom_fields.items():
                html.append(f"<li><strong>{name}:</strong> {value}</li>")

            html.append("</ul>")
            html.append("</div>")

        html.append("</div>")  # End receipt container
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def save_to_file(self, file_path: str, format: str = "text") -> None:
        """
        Save the receipt to a file.

        Args:
            file_path: Path to save the file
            format: Format of the file (text, html, json)
        """
        if format == "text":
            content = self.to_text()
        elif format == "html":
            content = self.to_html()
        elif format == "json":
            content = self.to_json()
        else:
            raise ValueError(f"Unsupported format: {format}")

        write_file(file_path, content, encoding="utf-8")

    def __str__(self) -> str:
        """String representation of the receipt."""
        return f"Receipt({self.id}, {self.date.strftime('%Y-%m-%d')}, {self.format_amount(self.get_total())})"
