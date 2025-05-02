import pytest
from agent_team.agent_profiles.researcher import ResearchAgent

def test_researcher_attribute_validation():
    """Test that ResearchAgent properly validates attributes"""
    agent = ResearchAgent(name="test_agent")
    
    # Test safe attribute access
    assert agent._name == "test_agent"
    
    # Test invalid attribute access
    with pytest.raises(AttributeError):
        agent.__dict__  # Should block direct dict access
        
    with pytest.raises(AttributeError):
        agent._protected_attr = "test"  # Should block setting new protected attrs

def test_researcher_input_validation():
    """Test input validation for researcher methods"""
    agent = ResearchAgent(name="test_agent")
    
    # Test with invalid inputs
    with pytest.raises(ValueError):
        agent.analyze_topic("")  # Empty string
        
    with pytest.raises(ValueError):
        agent.analyze_topic("a" * 1001)  # Too long
        
    with pytest.raises(TypeError):
        agent.analyze_topic(123)  # Wrong type

    # Test with valid input
    result = agent.analyze_topic("valid topic")
    assert isinstance(result, dict)

def test_diskcache_json_handling():
    """Test DiskCache JSON serialization security"""
    from ai_models.caching.cache_backends.disk_cache import DiskCache
    
    cache = DiskCache()
    test_data = {"key": "value", "number": 42}
    
    # Test JSON serialization
    cache.set("test_key", test_data)
    retrieved = cache.get("test_key")
    
    assert retrieved == test_data
    assert isinstance(retrieved, dict)
    
    # Test invalid data rejection
    with pytest.raises(TypeError):
        cache.set("invalid", lambda x: x)  # Functions shouldn't be serializable

def test_network_timeouts():
    """Test network timeout implementation"""
    from monetization.invoice_delivery import InvoiceDelivery
    import pytest
    
    delivery = InvoiceDelivery()
    
    # Test timeout enforcement
    with pytest.raises(TimeoutError):
        delivery.send_invoice("test", timeout=0.1)  # Should timeout quickly

def test_hash_operations():
    """Test secure hash operations"""
    from niche_analysis.niche_analyzer import NicheAnalyzer
    
    analyzer = NicheAnalyzer()
    
    # Test hash creation with usedforsecurity=False
    result = analyzer.generate_niche_hash("test_niche")
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex string length
