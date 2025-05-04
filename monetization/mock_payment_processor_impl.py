"""
"""
Concrete implementation of the PaymentProcessor for testing.
Concrete implementation of the PaymentProcessor for testing.


This module provides a concrete implementation of the PaymentProcessor
This module provides a concrete implementation of the PaymentProcessor
abstract base class for testing purposes.
abstract base class for testing purposes.
"""
"""




from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .payment_processor import PaymentProcessor
from .payment_processor import PaymentProcessor




class MockPaymentProcessorImpl:
    class MockPaymentProcessorImpl:
    from .payment_processor import get_payment_gateway
    from .payment_processor import get_payment_gateway


    self.payment_gateway
    self.payment_gateway


    (PaymentProcessor):
    (PaymentProcessor):
    """
    """
    Concrete implementation of PaymentProcessor for testing.
    Concrete implementation of PaymentProcessor for testing.
    """
    """


    def __init__(self, config: Dict[str, Any] = None):
    def __init__(self, config: Dict[str, Any] = None):
    """
    """
    Initialize the mock payment processor.
    Initialize the mock payment processor.


    Args:
    Args:
    config: Configuration for the payment processor
    config: Configuration for the payment processor
    """
    """
    super().__init__(config or {})
    super().__init__(config or {})
    self.customers = {}
    self.customers = {}
    self.payment_methods = {}
    self.payment_methods = {}
    self.payments = {}
    self.payments = {}
    self.subscriptions = {}
    self.subscriptions = {}
    self.plans = {}
    self.plans = {}
    self.refunds = {}
    self.refunds = {}


    # Set up the payment gateway
    # Set up the payment gateway
    self.payment_gateway = None
    self.payment_gateway = None
    try:
    try:
    = get_payment_gateway()
    = get_payment_gateway()
except (ImportError, AttributeError):
except (ImportError, AttributeError):
    pass
    pass


    def process_payment(
    def process_payment(
    self,
    self,
    amount: float,
    amount: float,
    currency: str,
    currency: str,
    payment_method_id: str,
    payment_method_id: str,
    description: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Process a payment.
    Process a payment.


    Args:
    Args:
    amount: Amount to charge
    amount: Amount to charge
    currency: Currency code (e.g., USD)
    currency: Currency code (e.g., USD)
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    description: Description of the payment
    description: Description of the payment
    metadata: Additional metadata for the payment
    metadata: Additional metadata for the payment


    Returns:
    Returns:
    Dictionary with payment result
    Dictionary with payment result
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.create_payment(
    return self.payment_gateway.create_payment(
    amount=amount,
    amount=amount,
    currency=currency,
    currency=currency,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    description=description,
    description=description,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Generate a payment ID
    # Generate a payment ID
    payment_id = f"pay_{len(self.payments) + 1}"
    payment_id = f"pay_{len(self.payments) + 1}"


    # Create payment
    # Create payment
    payment = {
    payment = {
    "id": payment_id,
    "id": payment_id,
    "amount": amount,
    "amount": amount,
    "currency": currency,
    "currency": currency,
    "payment_method_id": payment_method_id,
    "payment_method_id": payment_method_id,
    "description": description,
    "description": description,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "status": "succeeded",
    "status": "succeeded",
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store payment
    # Store payment
    self.payments[payment_id] = payment
    self.payments[payment_id] = payment


    return payment
    return payment


    def refund_payment(
    def refund_payment(
    self,
    self,
    payment_id: str,
    payment_id: str,
    amount: Optional[float] = None,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Refund a payment.
    Refund a payment.


    Args:
    Args:
    payment_id: ID of the payment to refund
    payment_id: ID of the payment to refund
    amount: Amount to refund (if None, refund the full amount)
    amount: Amount to refund (if None, refund the full amount)
    reason: Reason for the refund
    reason: Reason for the refund
    metadata: Additional metadata for the refund
    metadata: Additional metadata for the refund


    Returns:
    Returns:
    Dictionary with refund information
    Dictionary with refund information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.refund_payment(
    return self.payment_gateway.refund_payment(
    payment_id=payment_id, amount=amount, reason=reason, metadata=metadata
    payment_id=payment_id, amount=amount, reason=reason, metadata=metadata
    )
    )


    # Check if payment exists
    # Check if payment exists
    if payment_id not in self.payments:
    if payment_id not in self.payments:
    raise ValueError(f"Payment not found: {payment_id}")
    raise ValueError(f"Payment not found: {payment_id}")


    payment = self.payments[payment_id]
    payment = self.payments[payment_id]


    # Determine refund amount
    # Determine refund amount
    refund_amount = amount if amount is not None else payment["amount"]
    refund_amount = amount if amount is not None else payment["amount"]


    # Generate a refund ID
    # Generate a refund ID
    refund_id = f"ref_{len(self.refunds) + 1}"
    refund_id = f"ref_{len(self.refunds) + 1}"


    # Create refund
    # Create refund
    refund = {
    refund = {
    "id": refund_id,
    "id": refund_id,
    "payment_id": payment_id,
    "payment_id": payment_id,
    "amount": refund_amount,
    "amount": refund_amount,
    "reason": reason,
    "reason": reason,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "status": "succeeded",
    "status": "succeeded",
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store refund
    # Store refund
    self.refunds[refund_id] = refund
    self.refunds[refund_id] = refund


    return refund
    return refund


    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a payment.
    Get information about a payment.


    Args:
    Args:
    payment_id: ID of the payment
    payment_id: ID of the payment


    Returns:
    Returns:
    Dictionary with payment information
    Dictionary with payment information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.get_payment(payment_id)
    return self.payment_gateway.get_payment(payment_id)


    # Check if payment exists
    # Check if payment exists
    if payment_id not in self.payments:
    if payment_id not in self.payments:
    raise ValueError(f"Payment not found: {payment_id}")
    raise ValueError(f"Payment not found: {payment_id}")


    return self.payments[payment_id]
    return self.payments[payment_id]


    def list_payments(
    def list_payments(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List payments.
    List payments.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_date: Start date for payments
    start_date: Start date for payments
    end_date: End date for payments
    end_date: End date for payments
    limit: Maximum number of payments to return
    limit: Maximum number of payments to return


    Returns:
    Returns:
    List of payments
    List of payments
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.list_payments(
    return self.payment_gateway.list_payments(
    customer_id=customer_id,
    customer_id=customer_id,
    start_date=start_date,
    start_date=start_date,
    end_date=end_date,
    end_date=end_date,
    limit=limit,
    limit=limit,
    )
    )


    # Filter payments
    # Filter payments
    payments = list(self.payments.values())
    payments = list(self.payments.values())


    # Apply filters
    # Apply filters
    if customer_id:
    if customer_id:
    payments = [p for p in payments if p.get("customer_id") == customer_id]
    payments = [p for p in payments if p.get("customer_id") == customer_id]


    # Apply limit
    # Apply limit
    payments = payments[:limit]
    payments = payments[:limit]


    return payments
    return payments


    def create_customer(
    def create_customer(
    self,
    self,
    email: str,
    email: str,
    name: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a customer.
    Create a customer.


    Args:
    Args:
    email: Email of the customer
    email: Email of the customer
    name: Name of the customer
    name: Name of the customer
    metadata: Additional metadata for the customer
    metadata: Additional metadata for the customer


    Returns:
    Returns:
    Dictionary with customer information
    Dictionary with customer information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.create_customer(
    return self.payment_gateway.create_customer(
    email=email, name=name, metadata=metadata
    email=email, name=name, metadata=metadata
    )
    )


    # Generate a customer ID
    # Generate a customer ID
    customer_id = f"cus_{len(self.customers) + 1}"
    customer_id = f"cus_{len(self.customers) + 1}"


    # Create customer
    # Create customer
    customer = {
    customer = {
    "id": customer_id,
    "id": customer_id,
    "email": email,
    "email": email,
    "name": name,
    "name": name,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store customer
    # Store customer
    self.customers[customer_id] = customer
    self.customers[customer_id] = customer


    return customer
    return customer


    def get_customer(self, customer_id: str) -> Dict[str, Any]:
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a customer.
    Get information about a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    Dictionary with customer information
    Dictionary with customer information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.get_customer(customer_id)
    return self.payment_gateway.get_customer(customer_id)


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    return self.customers[customer_id]
    return self.customers[customer_id]


    def update_customer(
    def update_customer(
    self,
    self,
    customer_id: str,
    customer_id: str,
    email: Optional[str] = None,
    email: Optional[str] = None,
    name: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a customer.
    Update a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    email: New email for the customer
    email: New email for the customer
    name: New name for the customer
    name: New name for the customer
    metadata: New metadata for the customer
    metadata: New metadata for the customer


    Returns:
    Returns:
    Dictionary with updated customer information
    Dictionary with updated customer information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.update_customer(
    return self.payment_gateway.update_customer(
    customer_id=customer_id, email=email, name=name, metadata=metadata
    customer_id=customer_id, email=email, name=name, metadata=metadata
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    customer = self.customers[customer_id]
    customer = self.customers[customer_id]


    # Update customer
    # Update customer
    if email:
    if email:
    customer["email"] = email
    customer["email"] = email
    if name:
    if name:
    customer["name"] = name
    customer["name"] = name
    if metadata:
    if metadata:
    customer["metadata"].update(metadata)
    customer["metadata"].update(metadata)


    return customer
    return customer


    def delete_customer(self, customer_id: str) -> bool:
    def delete_customer(self, customer_id: str) -> bool:
    """
    """
    Delete a customer.
    Delete a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    True if the customer was deleted, False otherwise
    True if the customer was deleted, False otherwise
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.delete_customer(customer_id)
    return self.payment_gateway.delete_customer(customer_id)


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    return False
    return False


    # Delete customer
    # Delete customer
    del self.customers[customer_id]
    del self.customers[customer_id]


    return True
    return True


    def create_payment_method(
    def create_payment_method(
    self,
    self,
    customer_id: str,
    customer_id: str,
    payment_type: str,
    payment_type: str,
    payment_details: Dict[str, Any],
    payment_details: Dict[str, Any],
    set_as_default: bool = False,
    set_as_default: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a payment method.
    Create a payment method.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment method (e.g., card, bank_account)
    payment_type: Type of payment method (e.g., card, bank_account)
    payment_details: Details of the payment method
    payment_details: Details of the payment method
    set_as_default: Whether to set this as the default payment method
    set_as_default: Whether to set this as the default payment method
    metadata: Additional metadata for the payment method
    metadata: Additional metadata for the payment method


    Returns:
    Returns:
    Dictionary with payment method information
    Dictionary with payment method information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    # The MockPaymentGateway doesn't have set_as_default parameter
    # The MockPaymentGateway doesn't have set_as_default parameter
    return self.payment_gateway.create_payment_method(
    return self.payment_gateway.create_payment_method(
    customer_id=customer_id,
    customer_id=customer_id,
    payment_type=payment_type,
    payment_type=payment_type,
    payment_details=payment_details,
    payment_details=payment_details,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Generate a payment method ID
    # Generate a payment method ID
    payment_method_id = f"pm_{len(self.payment_methods) + 1}"
    payment_method_id = f"pm_{len(self.payment_methods) + 1}"


    # Create payment method
    # Create payment method
    payment_method = {
    payment_method = {
    "id": payment_method_id,
    "id": payment_method_id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "type": payment_type,
    "type": payment_type,
    "details": payment_details,
    "details": payment_details,
    "is_default": set_as_default,
    "is_default": set_as_default,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store payment method
    # Store payment method
    self.payment_methods[payment_method_id] = payment_method
    self.payment_methods[payment_method_id] = payment_method


    return payment_method
    return payment_method


    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a payment method.
    Get information about a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method


    Returns:
    Returns:
    Dictionary with payment method information
    Dictionary with payment method information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.get_payment_method(payment_method_id)
    return self.payment_gateway.get_payment_method(payment_method_id)


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    return self.payment_methods[payment_method_id]
    return self.payment_methods[payment_method_id]


    def update_payment_method(
    def update_payment_method(
    self,
    self,
    payment_method_id: str,
    payment_method_id: str,
    payment_details: Optional[Dict[str, Any]] = None,
    payment_details: Optional[Dict[str, Any]] = None,
    set_as_default: Optional[bool] = None,
    set_as_default: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a payment method.
    Update a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    payment_details: New details for the payment method
    payment_details: New details for the payment method
    set_as_default: Whether to set this as the default payment method
    set_as_default: Whether to set this as the default payment method
    metadata: New metadata for the payment method
    metadata: New metadata for the payment method


    Returns:
    Returns:
    Dictionary with updated payment method information
    Dictionary with updated payment method information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.update_payment_method(
    return self.payment_gateway.update_payment_method(
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    payment_details=payment_details,
    payment_details=payment_details,
    set_as_default=set_as_default,
    set_as_default=set_as_default,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    payment_method = self.payment_methods[payment_method_id]
    payment_method = self.payment_methods[payment_method_id]


    # Update payment method
    # Update payment method
    if payment_details:
    if payment_details:
    payment_method["details"].update(payment_details)
    payment_method["details"].update(payment_details)
    if set_as_default is not None:
    if set_as_default is not None:
    payment_method["is_default"] = set_as_default
    payment_method["is_default"] = set_as_default
    if metadata:
    if metadata:
    payment_method["metadata"].update(metadata)
    payment_method["metadata"].update(metadata)


    return payment_method
    return payment_method


    def delete_payment_method(self, payment_method_id: str) -> bool:
    def delete_payment_method(self, payment_method_id: str) -> bool:
    """
    """
    Delete a payment method.
    Delete a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method


    Returns:
    Returns:
    True if the payment method was deleted, False otherwise
    True if the payment method was deleted, False otherwise
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.delete_payment_method(payment_method_id)
    return self.payment_gateway.delete_payment_method(payment_method_id)


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    return False
    return False


    # Delete payment method
    # Delete payment method
    del self.payment_methods[payment_method_id]
    del self.payment_methods[payment_method_id]


    return True
    return True


    def list_payment_methods(
    def list_payment_methods(
    self, customer_id: str, payment_type: Optional[str] = None
    self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List payment methods for a customer.
    List payment methods for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment methods to list
    payment_type: Type of payment methods to list


    Returns:
    Returns:
    List of payment methods
    List of payment methods
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.list_payment_methods(
    return self.payment_gateway.list_payment_methods(
    customer_id=customer_id, payment_type=payment_type
    customer_id=customer_id, payment_type=payment_type
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Filter payment methods
    # Filter payment methods
    payment_methods = [
    payment_methods = [
    pm
    pm
    for pm in self.payment_methods.values()
    for pm in self.payment_methods.values()
    if pm["customer_id"] == customer_id
    if pm["customer_id"] == customer_id
    and (payment_type is None or pm["type"] == payment_type)
    and (payment_type is None or pm["type"] == payment_type)
    ]
    ]


    return payment_methods
    return payment_methods


    def create_subscription(
    def create_subscription(
    self,
    self,
    customer_id: str,
    customer_id: str,
    plan_id: str,
    plan_id: str,
    payment_method_id: str,
    payment_method_id: str,
    trial_period_days: Optional[int] = None,
    trial_period_days: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a subscription.
    Create a subscription.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    plan_id: ID of the plan
    plan_id: ID of the plan
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    trial_period_days: Number of days for the trial period
    trial_period_days: Number of days for the trial period
    metadata: Additional metadata for the subscription
    metadata: Additional metadata for the subscription


    Returns:
    Returns:
    Dictionary with subscription information
    Dictionary with subscription information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.create_subscription(
    return self.payment_gateway.create_subscription(
    customer_id=customer_id,
    customer_id=customer_id,
    plan_id=plan_id,
    plan_id=plan_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    trial_period_days=trial_period_days,
    trial_period_days=trial_period_days,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Check if plan exists
    # Check if plan exists
    if plan_id not in self.plans:
    if plan_id not in self.plans:
    raise ValueError(f"Plan not found: {plan_id}")
    raise ValueError(f"Plan not found: {plan_id}")


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Generate a subscription ID
    # Generate a subscription ID
    subscription_id = f"sub_{len(self.subscriptions) + 1}"
    subscription_id = f"sub_{len(self.subscriptions) + 1}"


    # Create subscription
    # Create subscription
    subscription = {
    subscription = {
    "id": subscription_id,
    "id": subscription_id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "plan_id": plan_id,
    "plan_id": plan_id,
    "payment_method_id": payment_method_id,
    "payment_method_id": payment_method_id,
    "status": "active",
    "status": "active",
    "trial_period_days": trial_period_days,
    "trial_period_days": trial_period_days,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store subscription
    # Store subscription
    self.subscriptions[subscription_id] = subscription
    self.subscriptions[subscription_id] = subscription


    return subscription
    return subscription


    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a subscription.
    Get information about a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription


    Returns:
    Returns:
    Dictionary with subscription information
    Dictionary with subscription information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.get_subscription(subscription_id)
    return self.payment_gateway.get_subscription(subscription_id)


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    return self.subscriptions[subscription_id]
    return self.subscriptions[subscription_id]


    def update_subscription(
    def update_subscription(
    self,
    self,
    subscription_id: str,
    subscription_id: str,
    plan_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a subscription.
    Update a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    plan_id: New plan ID for the subscription
    plan_id: New plan ID for the subscription
    payment_method_id: New payment method ID for the subscription
    payment_method_id: New payment method ID for the subscription
    metadata: New metadata for the subscription
    metadata: New metadata for the subscription


    Returns:
    Returns:
    Dictionary with updated subscription information
    Dictionary with updated subscription information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.update_subscription(
    return self.payment_gateway.update_subscription(
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    plan_id=plan_id,
    plan_id=plan_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Update subscription
    # Update subscription
    if plan_id:
    if plan_id:
    # Check if plan exists
    # Check if plan exists
    if plan_id not in self.plans:
    if plan_id not in self.plans:
    raise ValueError(f"Plan not found: {plan_id}")
    raise ValueError(f"Plan not found: {plan_id}")
    subscription["plan_id"] = plan_id
    subscription["plan_id"] = plan_id
    if payment_method_id:
    if payment_method_id:
    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")
    subscription["payment_method_id"] = payment_method_id
    subscription["payment_method_id"] = payment_method_id
    if metadata:
    if metadata:
    subscription["metadata"].update(metadata)
    subscription["metadata"].update(metadata)


    return subscription
    return subscription


    def cancel_subscription(
    def cancel_subscription(
    self, subscription_id: str, cancel_at_period_end: bool = False
    self, subscription_id: str, cancel_at_period_end: bool = False
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Cancel a subscription.
    Cancel a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    cancel_at_period_end: Whether to cancel at the end of the billing period
    cancel_at_period_end: Whether to cancel at the end of the billing period


    Returns:
    Returns:
    Dictionary with updated subscription information
    Dictionary with updated subscription information
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.cancel_subscription(
    return self.payment_gateway.cancel_subscription(
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    cancel_at_period_end=cancel_at_period_end,
    cancel_at_period_end=cancel_at_period_end,
    )
    )


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Update subscription
    # Update subscription
    if cancel_at_period_end:
    if cancel_at_period_end:
    subscription["cancel_at_period_end"] = True
    subscription["cancel_at_period_end"] = True
    else:
    else:
    subscription["status"] = "canceled"
    subscription["status"] = "canceled"
    subscription["canceled_at"] = datetime.now().isoformat()
    subscription["canceled_at"] = datetime.now().isoformat()


    return subscription
    return subscription


    def list_subscriptions(
    def list_subscriptions(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List subscriptions.
    List subscriptions.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    status: Status of subscriptions to list
    status: Status of subscriptions to list
    limit: Maximum number of subscriptions to return
    limit: Maximum number of subscriptions to return


    Returns:
    Returns:
    List of subscriptions
    List of subscriptions
    """
    """
    if self.payment_gateway:
    if self.payment_gateway:
    return self.payment_gateway.list_subscriptions(
    return self.payment_gateway.list_subscriptions(
    customer_id=customer_id, status=status, limit=limit
    customer_id=customer_id, status=status, limit=limit
    )
    )


    # Filter subscriptions
    # Filter subscriptions
    subscriptions = list(self.subscriptions.values())
    subscriptions = list(self.subscriptions.values())


    # Apply filters
    # Apply filters
    if customer_id:
    if customer_id:
    subscriptions = [
    subscriptions = [
    s for s in subscriptions if s["customer_id"] == customer_id
    s for s in subscriptions if s["customer_id"] == customer_id
    ]
    ]
    if status:
    if status:
    subscriptions = [s for s in subscriptions if s["status"] == status]
    subscriptions = [s for s in subscriptions if s["status"] == status]


    # Apply limit
    # Apply limit
    subscriptions = subscriptions[:limit]
    subscriptions = subscriptions[:limit]


    return subscriptions
    return subscriptions