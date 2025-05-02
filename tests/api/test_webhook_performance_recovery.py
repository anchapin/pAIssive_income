"""
Performance recovery tests for webhook system.

This module tests the recovery mechanisms of the webhook system:
1. Delivery recovery after system overload
2. Backpressure handling mechanisms
3. Webhook queue prioritization
4. Exponential backoff retry logic
5. Delivery timeout handling
6. Queue persistence across service restarts
7. Dead letter queue processing
"""

import pytest
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from api.services.webhook_service import WebhookService
from api.schemas.webhook import WebhookEventType, WebhookDeliveryStatus


class TestDeliveryRecovery:
    """Tests for delivery recovery after system overload."""
    
    @pytest.mark.asyncio
    async def test_recovery_after_overload(self):
        """Test that the system can recover after being overloaded."""
        # Create a webhook service with limited queue size
        service = WebhookService(max_queue_size=10, max_workers=2)
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a mock response that takes time to process
            slow_response = AsyncMock()
            slow_response.status = 200
            slow_response.text = AsyncMock(return_value="OK")
            
            # Patch the httpx.AsyncClient.post method to simulate slow responses
            with patch("httpx.AsyncClient.post", side_effect=lambda *args, **kwargs: asyncio.sleep(0.5).then(lambda: slow_response)):
                # Generate many events to overload the queue
                events = []
                for i in range(20):
                    event_data = {
                        "user_id": f"user-{i}",
                        "username": f"testuser{i}",
                        "email": f"test{i}@example.com"
                    }
                    events.append(event_data)
                
                # Try to deliver all events (some will be rejected due to queue size)
                delivery_ids = []
                for event_data in events:
                    try:
                        delivery = await service.queue_event(
                            webhook_id=webhook["id"],
                            event_type=WebhookEventType.USER_CREATED,
                            event_data=event_data
                        )
                        if delivery:
                            delivery_ids.append(delivery["id"])
                    except Exception:
                        # Queue full exception expected
                        pass
                
                # Wait for the queue to process some events
                await asyncio.sleep(2)
                
                # Check that some events were processed
                processed_count = 0
                for delivery_id in delivery_ids:
                    delivery = await service.get_delivery(delivery_id)
                    if delivery and delivery["status"] == WebhookDeliveryStatus.SUCCESS:
                        processed_count += 1
                
                # Verify that the system processed some events despite overload
                assert processed_count > 0
                
                # Now try to deliver more events after the system has recovered
                recovery_events = []
                for i in range(5):
                    event_data = {
                        "user_id": f"recovery-user-{i}",
                        "username": f"recoveryuser{i}",
                        "email": f"recovery{i}@example.com"
                    }
                    recovery_events.append(event_data)
                
                # Deliver recovery events
                recovery_delivery_ids = []
                for event_data in recovery_events:
                    delivery = await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event_data
                    )
                    recovery_delivery_ids.append(delivery["id"])
                
                # Wait for recovery events to be processed
                await asyncio.sleep(3)
                
                # Check that recovery events were processed
                recovery_processed_count = 0
                for delivery_id in recovery_delivery_ids:
                    delivery = await service.get_delivery(delivery_id)
                    if delivery and delivery["status"] == WebhookDeliveryStatus.SUCCESS:
                        recovery_processed_count += 1
                
                # Verify that the system recovered and processed new events
                assert recovery_processed_count == len(recovery_events)
        
        finally:
            # Stop the service
            await service.stop()


class TestBackpressureHandling:
    """Tests for backpressure handling mechanisms."""
    
    @pytest.mark.asyncio
    async def test_backpressure_handling(self):
        """Test that the system applies backpressure when overloaded."""
        # Create a webhook service with limited queue size
        service = WebhookService(max_queue_size=5, max_workers=1)
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a mock response that takes time to process
            slow_response = AsyncMock()
            slow_response.status = 200
            slow_response.text = AsyncMock(return_value="OK")
            
            # Patch the httpx.AsyncClient.post method to simulate slow responses
            with patch("httpx.AsyncClient.post", side_effect=lambda *args, **kwargs: asyncio.sleep(1).then(lambda: slow_response)):
                # Fill the queue
                for i in range(5):
                    event_data = {
                        "user_id": f"user-{i}",
                        "username": f"testuser{i}",
                        "email": f"test{i}@example.com"
                    }
                    await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event_data
                    )
                
                # Try to add one more event, which should be rejected due to backpressure
                with pytest.raises(Exception, match="Queue full"):
                    event_data = {
                        "user_id": "overflow-user",
                        "username": "overflowuser",
                        "email": "overflow@example.com"
                    }
                    await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event_data
                    )
        
        finally:
            # Stop the service
            await service.stop()


class TestQueuePrioritization:
    """Tests for webhook queue prioritization."""
    
    @pytest.mark.asyncio
    async def test_queue_prioritization(self):
        """Test that high-priority events are processed before low-priority events."""
        # Create a webhook service
        service = WebhookService()
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [
                    WebhookEventType.USER_CREATED,
                    WebhookEventType.PAYMENT_RECEIVED,
                    WebhookEventType.SUBSCRIPTION_CREATED
                ],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            
            # Track the order of processed events
            processed_events = []
            
            # Patch the _deliver_webhook method to track the order
            original_deliver = service._deliver_webhook
            
            async def mock_deliver_webhook(webhook_obj, delivery):
                # Call the original method
                result = await original_deliver(webhook_obj, delivery)
                # Record the event type
                processed_events.append(delivery["event_type"])
                return result
            
            with patch.object(service, "_deliver_webhook", mock_deliver_webhook):
                with patch("httpx.AsyncClient.post", return_value=mock_response):
                    # Queue events with different priorities
                    # Assume PAYMENT_RECEIVED is high priority, USER_CREATED is medium, SUBSCRIPTION_CREATED is low
                    
                    # Queue low priority event first
                    await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.SUBSCRIPTION_CREATED,
                        event_data={"subscription_id": "sub-123"},
                        priority=0  # Low priority
                    )
                    
                    # Queue medium priority event
                    await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data={"user_id": "user-123"},
                        priority=1  # Medium priority
                    )
                    
                    # Queue high priority event
                    await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.PAYMENT_RECEIVED,
                        event_data={"payment_id": "payment-123"},
                        priority=2  # High priority
                    )
                    
                    # Wait for all events to be processed
                    await asyncio.sleep(1)
                    
                    # Verify that events were processed in order of priority (high to low)
                    assert processed_events[0] == WebhookEventType.PAYMENT_RECEIVED
                    assert processed_events[1] == WebhookEventType.USER_CREATED
                    assert processed_events[2] == WebhookEventType.SUBSCRIPTION_CREATED
        
        finally:
            # Stop the service
            await service.stop()


class TestExponentialBackoff:
    """Tests for exponential backoff retry logic."""
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that retries use exponential backoff."""
        # Create a webhook service
        service = WebhookService()
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a sequence of failing responses
            fail_response = AsyncMock()
            fail_response.status = 500
            fail_response.text = AsyncMock(return_value="Internal Server Error")
            
            # Track retry times
            retry_times = []
            
            # Patch time.time to track when retries happen
            original_time = time.time
            
            def mock_time():
                current_time = original_time()
                retry_times.append(current_time)
                return current_time
            
            with patch("time.time", mock_time):
                with patch("httpx.AsyncClient.post", return_value=fail_response):
                    # Deliver an event that will fail and trigger retries
                    event_data = {
                        "user_id": "user-123",
                        "username": "testuser",
                        "email": "test@example.com"
                    }
                    
                    # Set max_attempts to 4 (initial + 3 retries)
                    delivery = await service.deliver_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event_data,
                        max_attempts=4
                    )
                    
                    # Wait for all retries to complete
                    await asyncio.sleep(5)
                    
                    # Verify that delivery failed after max attempts
                    assert delivery["status"] == WebhookDeliveryStatus.MAX_RETRIES_EXCEEDED
                    assert len(delivery["attempts"]) == 4
                    
                    # Calculate time differences between retries
                    time_diffs = []
                    for i in range(1, len(retry_times)):
                        time_diffs.append(retry_times[i] - retry_times[i-1])
                    
                    # Verify that each retry took longer than the previous one (exponential backoff)
                    for i in range(1, len(time_diffs)):
                        assert time_diffs[i] > time_diffs[i-1]
        
        finally:
            # Stop the service
            await service.stop()


class TestDeliveryTimeout:
    """Tests for delivery timeout handling."""
    
    @pytest.mark.asyncio
    async def test_delivery_timeout_handling(self):
        """Test that the system handles delivery timeouts properly."""
        # Create a webhook service
        service = WebhookService()
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a mock that times out
            async def mock_timeout(*args, **kwargs):
                await asyncio.sleep(11)  # Sleep longer than the timeout
                mock_response = AsyncMock()
                mock_response.status = 200
                return mock_response
            
            # Patch the httpx.AsyncClient.post method to simulate a timeout
            with patch("httpx.AsyncClient.post", side_effect=asyncio.TimeoutError):
                # Deliver an event
                event_data = {
                    "user_id": "user-123",
                    "username": "testuser",
                    "email": "test@example.com"
                }
                
                delivery = await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=event_data,
                    timeout=10  # 10 second timeout
                )
                
                # Verify that delivery failed due to timeout
                assert delivery["status"] == WebhookDeliveryStatus.FAILED
                assert len(delivery["attempts"]) == 1
                assert "timeout" in delivery["attempts"][0]["error_message"].lower()
        
        finally:
            # Stop the service
            await service.stop()


class TestQueuePersistence:
    """Tests for queue persistence across service restarts."""
    
    @pytest.mark.asyncio
    async def test_queue_persistence(self):
        """Test that the queue persists across service restarts."""
        # Create a webhook service with persistence enabled
        service = WebhookService(persist_queue=True, queue_file="test_queue.json")
        await service.start()
        
        webhook_id = None
        delivery_ids = []
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            webhook_id = webhook["id"]
            
            # Create a mock response that will be used after restart
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            
            # Queue some events
            for i in range(5):
                event_data = {
                    "user_id": f"user-{i}",
                    "username": f"testuser{i}",
                    "email": f"test{i}@example.com"
                }
                
                # Patch the _deliver_webhook method to prevent immediate delivery
                with patch.object(service, "_deliver_webhook", side_effect=Exception("Simulated failure")):
                    delivery = await service.queue_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event_data
                    )
                    delivery_ids.append(delivery["id"])
            
            # Stop the service (simulating a restart)
            await service.stop()
            
            # Start a new service instance that should load the persisted queue
            new_service = WebhookService(persist_queue=True, queue_file="test_queue.json")
            await new_service.start()
            
            try:
                # Patch the httpx.AsyncClient.post method to return success
                with patch("httpx.AsyncClient.post", return_value=mock_response):
                    # Wait for the queue to be processed
                    await asyncio.sleep(3)
                    
                    # Check that the events were delivered after restart
                    for delivery_id in delivery_ids:
                        delivery = await new_service.get_delivery(delivery_id)
                        assert delivery is not None
                        assert delivery["status"] == WebhookDeliveryStatus.SUCCESS
            
            finally:
                # Stop the new service
                await new_service.stop()
        
        finally:
            # Clean up
            import os
            if os.path.exists("test_queue.json"):
                os.remove("test_queue.json")


class TestDeadLetterQueue:
    """Tests for dead letter queue processing."""
    
    @pytest.mark.asyncio
    async def test_dead_letter_queue_processing(self):
        """Test that failed deliveries are moved to the dead letter queue."""
        # Create a webhook service with dead letter queue enabled
        service = WebhookService(use_dead_letter_queue=True)
        await service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True
            }
            webhook = await service.register_webhook(webhook_data)
            
            # Create a failing response
            fail_response = AsyncMock()
            fail_response.status = 500
            fail_response.text = AsyncMock(return_value="Internal Server Error")
            
            # Patch the httpx.AsyncClient.post method to always fail
            with patch("httpx.AsyncClient.post", return_value=fail_response):
                # Deliver an event that will fail
                event_data = {
                    "user_id": "user-123",
                    "username": "testuser",
                    "email": "test@example.com"
                }
                
                # Set max_attempts to 3 (initial + 2 retries)
                delivery = await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=event_data,
                    max_attempts=3
                )
                
                # Wait for all retries to complete
                await asyncio.sleep(3)
                
                # Verify that delivery failed after max attempts
                assert delivery["status"] == WebhookDeliveryStatus.MAX_RETRIES_EXCEEDED
                
                # Check that the delivery was moved to the dead letter queue
                dead_letter_items = await service.list_dead_letter_queue()
                assert len(dead_letter_items) == 1
                assert dead_letter_items[0]["delivery_id"] == delivery["id"]
                assert dead_letter_items[0]["webhook_id"] == webhook["id"]
                assert dead_letter_items[0]["event_type"] == WebhookEventType.USER_CREATED
                
                # Test reprocessing from dead letter queue with a successful response
                success_response = AsyncMock()
                success_response.status = 200
                success_response.text = AsyncMock(return_value="OK")
                
                with patch("httpx.AsyncClient.post", return_value=success_response):
                    # Reprocess the dead letter queue
                    reprocessed = await service.reprocess_dead_letter_queue()
                    
                    # Verify that the item was reprocessed
                    assert reprocessed == 1
                    
                    # Check that the dead letter queue is now empty
                    dead_letter_items = await service.list_dead_letter_queue()
                    assert len(dead_letter_items) == 0
                    
                    # Check that the delivery status was updated
                    updated_delivery = await service.get_delivery(delivery["id"])
                    assert updated_delivery["status"] == WebhookDeliveryStatus.SUCCESS
        
        finally:
            # Stop the service
            await service.stop()
