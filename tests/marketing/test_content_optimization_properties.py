"""
Property-based tests for content optimization algorithms.

This module tests properties that should hold true for content optimization algorithms
in the marketing.content_optimization module, using the Hypothesis framework for property-based testing.
"""

import pytest
import uuid
from datetime import datetime
from hypothesis import given, strategies as st, assume, settings, example
from hypothesis.strategies import composite

from marketing.content_optimization import (
    KeywordAnalyzer, ReadabilityAnalyzer, SEOAnalyzer
)

# Constants for generating test content
SAMPLE_WORDS = [
    "marketing", "content", "seo", "analysis", "keyword", "optimization", "strategy",
    "brand", "audience", "customer", "product", "service", "business", "value",
    "digital", "social", "media", "website", "online", "traffic", "conversion",
    "lead", "sale", "revenue", "growth", "analytics", "data", "metric", "performance",
    "quality", "engage", "target", "segment", "persona", "funnel", "campaign",
    "channel", "platform", "message", "communicate", "attract", "convert", "retain"
]

SIMPLE_WORDS = [
    "the", "and", "of", "to", "in", "is", "that", "it", "with", "as", "for", "was",
    "on", "are", "by", "be", "at", "this", "from", "but", "not", "or", "have", "an",
    "one", "all", "you", "new", "more", "use", "time", "than", "has", "they", "like"
]

COMPLEX_WORDS = [
    "established", "consequently", "opportunities", "fundamentally", "revolutionary",
    "comprehensive", "developmental", "methodologies", "differentiate", "approximately",
    "functionality", "organizational", "technological", "considerations", "accessibility"
]

TRANSITION_WORDS = [
    "additionally", "furthermore", "moreover", "similarly", "likewise", 
    "however", "nevertheless", "nonetheless", "therefore", "consequently",
    "specifically", "particularly", "especially", "generally", "overall",
    "finally", "meanwhile", "subsequently", "ultimately", "indeed"
]


@composite
def content_dict_strategy(draw, with_keywords=True):
    """Strategy for generating valid content dictionaries."""
    
    # Generate title with keyword inclusion if requested
    include_keyword = with_keywords and draw(st.booleans())
    keyword_candidates = SAMPLE_WORDS if include_keyword else []
    
    # Title generation
    title_words = draw(st.lists(
        st.sampled_from(SAMPLE_WORDS + SIMPLE_WORDS + keyword_candidates), 
        min_size=3, 
        max_size=15
    ))
    title = " ".join(title_words).capitalize()
    
    # Meta description generation
    meta_desc_words = draw(st.lists(
        st.sampled_from(SAMPLE_WORDS + SIMPLE_WORDS + keyword_candidates),
        min_size=5,
        max_size=30
    ))
    meta_description = " ".join(meta_desc_words).capitalize() + "."
    
    # Generate sections
    num_sections = draw(st.integers(min_value=1, max_value=5))
    sections = []
    
    for _ in range(num_sections):
        # Section title
        section_title_words = draw(st.lists(
            st.sampled_from(SAMPLE_WORDS + SIMPLE_WORDS + keyword_candidates),
            min_size=2,
            max_size=10
        ))
        section_title = " ".join(section_title_words).capitalize()
        
        # Section content with paragraphs
        num_paragraphs = draw(st.integers(min_value=1, max_value=3))
        paragraphs = []
        
        for _ in range(num_paragraphs):
            # Choose words for this paragraph
            word_pool = SAMPLE_WORDS + SIMPLE_WORDS
            if draw(st.booleans()):  # Add some complex words
                word_pool += COMPLEX_WORDS
            if draw(st.booleans()):  # Add some transition words
                word_pool += TRANSITION_WORDS
            
            # Generate sentences for this paragraph
            num_sentences = draw(st.integers(min_value=1, max_value=5))
            sentences = []
            
            for _ in range(num_sentences):
                # Create a sentence
                sentence_words = draw(st.lists(
                    st.sampled_from(word_pool + keyword_candidates if include_keyword else word_pool),
                    min_size=3,
                    max_size=20
                ))
                sentence = " ".join(sentence_words).capitalize() + "."
                sentences.append(sentence)
            
            paragraph = " ".join(sentences)
            paragraphs.append(paragraph)
        
        section_content = "\n\n".join(paragraphs)
        
        sections.append({
            "title": section_title,
            "content": section_content
        })
    
    # Generate introduction
    intro_paragraphs = draw(st.integers(min_value=1, max_value=2))
    intro_sentences = []
    
    for _ in range(intro_paragraphs * 3):  # 3 sentences per paragraph on average
        intro_words = draw(st.lists(
            st.sampled_from(SAMPLE_WORDS + SIMPLE_WORDS + keyword_candidates if include_keyword else SAMPLE_WORDS + SIMPLE_WORDS),
            min_size=5,
            max_size=15
        ))
        sentence = " ".join(intro_words).capitalize() + "."
        intro_sentences.append(sentence)
    
    introduction = " ".join(intro_sentences)
    
    # Generate conclusion
    conclusion_sentences = []
    for _ in range(draw(st.integers(min_value=2, max_value=4))):
        conclusion_words = draw(st.lists(
            st.sampled_from(SAMPLE_WORDS + SIMPLE_WORDS),
            min_size=5,
            max_size=15
        ))
        sentence = " ".join(conclusion_words).capitalize() + "."
        conclusion_sentences.append(sentence)
    
    conclusion = " ".join(conclusion_sentences)
    
    # Create SEO data including URL slug
    seo_data = None
    if with_keywords and draw(st.booleans()):
        slug_words = draw(st.lists(
            st.sampled_from(SAMPLE_WORDS + keyword_candidates),
            min_size=2,
            max_size=6
        ))
        seo_data = {
            "slug": "-".join(slug_words).lower(),
            "canonical_url": f"https://example.com/{'-'.join(slug_words)}/",
            "robots": "index,follow"
        }
    
    # Build the content dictionary
    content = {
        "id": str(uuid.uuid4()),
        "title": title,
        "meta_description": meta_description,
        "introduction": introduction,
        "sections": sections,
        "conclusion": conclusion,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add SEO data if generated
    if seo_data:
        content["seo_data"] = seo_data
    
    return content


@composite
def keywords_strategy(draw):
    """Strategy for generating keyword lists."""
    num_keywords = draw(st.integers(min_value=1, max_value=5))
    keywords = []
    
    for _ in range(num_keywords):
        # Generate keyword (can be single word or phrase)
        keyword_length = draw(st.integers(min_value=1, max_value=3))
        keyword_words = draw(st.lists(
            st.sampled_from(SAMPLE_WORDS),
            min_size=keyword_length,
            max_size=keyword_length
        ))
        keyword = " ".join(keyword_words)
        keywords.append(keyword)
    
    return keywords


@composite
def keyword_analyzer_config_strategy(draw):
    """Strategy for generating valid keyword analyzer configs."""
    # Generate min/max keyword density with min <= max
    min_density = draw(st.floats(min_value=0.005, max_value=0.05))
    max_density = draw(st.floats(min_value=min_density, max_value=0.1))
    
    # Generate min/max word counts with min <= optimal
    min_word_count = draw(st.integers(min_value=100, max_value=1000))
    optimal_word_count = draw(st.integers(min_value=min_word_count, max_value=2000))
    
    # Generate min/max title length with min <= max
    min_title_length = draw(st.integers(min_value=20, max_value=40))
    max_title_length = draw(st.integers(min_value=min_title_length, max_value=70))
    
    # Generate min/max meta description length with min <= max
    min_meta_desc_length = draw(st.integers(min_value=50, max_value=120))
    max_meta_desc_length = draw(st.integers(min_value=min_meta_desc_length, max_value=160))
    
    return {
        "min_keyword_density": min_density,
        "max_keyword_density": max_density,
        "min_word_count": min_word_count,
        "optimal_word_count": optimal_word_count,
        "min_title_length": min_title_length,
        "max_title_length": max_title_length,
        "min_meta_description_length": min_meta_desc_length,
        "max_meta_description_length": max_meta_desc_length,
        "min_heading_count": draw(st.integers(min_value=1, max_value=5)),
        "min_internal_links": draw(st.integers(min_value=0, max_value=5)),
        "min_external_links": draw(st.integers(min_value=0, max_value=3)),
        "max_paragraph_length": draw(st.integers(min_value=100, max_value=500)),
        "check_keyword_in_title": draw(st.booleans()),
        "check_keyword_in_headings": draw(st.booleans()),
        "check_keyword_in_first_paragraph": draw(st.booleans()),
        "check_keyword_in_url": draw(st.booleans()),
        "check_keyword_in_meta_description": draw(st.booleans())
    }


@composite
def readability_analyzer_config_strategy(draw):
    """Strategy for generating valid readability analyzer configs."""
    # Generate target reading level
    reading_level = draw(st.sampled_from(["beginner", "intermediate", "advanced"]))
    
    # Generate min/max sentence lengths
    min_sentence_length = draw(st.integers(min_value=3, max_value=8))
    max_sentence_length = draw(st.integers(min_value=min_sentence_length + 5, max_value=35))
    
    # Generate min/max paragraph lengths
    min_paragraph_length = draw(st.integers(min_value=20, max_value=50))
    max_paragraph_length = draw(st.integers(min_value=min_paragraph_length + 30, max_value=200))
    
    # Generate maximum percentages
    max_passive_voice = draw(st.floats(min_value=0.05, max_value=0.3))
    max_complex_word = draw(st.floats(min_value=0.05, max_value=0.3))
    
    # Generate readability score thresholds
    min_flesch_reading_ease = draw(st.floats(min_value=30.0, max_value=80.0))
    
    # Grade level thresholds
    max_grade_level = draw(st.floats(min_value=6.0, max_value=16.0))
    
    return {
        "target_reading_level": reading_level,
        "max_sentence_length": max_sentence_length,
        "min_sentence_length": min_sentence_length,
        "max_paragraph_length": max_paragraph_length,
        "min_paragraph_length": min_paragraph_length,
        "max_passive_voice_percentage": max_passive_voice,
        "max_complex_word_percentage": max_complex_word,
        "min_flesch_reading_ease": min_flesch_reading_ease,
        "max_flesch_kincaid_grade": max_grade_level,
        "max_smog_index": max_grade_level,
        "max_coleman_liau_index": max_grade_level,
        "max_automated_readability_index": max_grade_level,
        "max_gunning_fog_index": max_grade_level,
        "check_transition_words": draw(st.booleans()),
        "check_sentence_beginnings": draw(st.booleans()),
        "check_adverb_usage": draw(st.booleans()),
        "check_passive_voice": draw(st.booleans()),
        "check_consecutive_sentences": draw(st.booleans())
    }


class TestKeywordAnalyzerProperties:
    """Property-based tests for the KeywordAnalyzer class."""
    
    @given(
        content=content_dict_strategy(),
        keywords=keywords_strategy(),
        config=keyword_analyzer_config_strategy()
    )
    def test_keyword_density_bounds(self, content, keywords, config):
        """Test that keyword density values are bounded between 0 and 1."""
        analyzer = KeywordAnalyzer(content, keywords, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Check that all keyword densities are between 0 and 1
            for keyword, data in results["keyword_density"]["keywords"].items():
                assert 0.0 <= data["density"] <= 1.0
                
            # Check that the overall score is between 0 and 1
            assert 0.0 <= results["overall_score"] <= 1.0
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        keywords=keywords_strategy(),
        config=keyword_analyzer_config_strategy()
    )
    def test_keyword_placement_consistency(self, content, keywords, config):
        """Test that keyword placement analysis is consistent with content."""
        analyzer = KeywordAnalyzer(content, keywords, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # For each keyword, check that placement checks are consistent with content
            for keyword, placement in results["keyword_placement"].items():
                # If keyword is in title, the keyword should be in the content title
                if placement["in_title"]:
                    assert keyword.lower() in content["title"].lower()
                
                # If keyword is in meta description, it should be in the meta description
                if placement["in_meta_description"] and "meta_description" in content:
                    assert keyword.lower() in content["meta_description"].lower()
                
                # If keyword is in URL, it should be in the slug
                if placement["in_url"] and "seo_data" in content and "slug" in content["seo_data"]:
                    assert keyword.lower().replace(" ", "-") in content["seo_data"]["slug"].lower()
                    
                # Verify score is average of placement checks
                expected_score = sum([
                    1 if placement["in_title"] else 0,
                    1 if placement["in_headings"] else 0,
                    1 if placement["in_first_paragraph"] else 0,
                    1 if placement["in_meta_description"] else 0,
                    1 if placement["in_url"] else 0
                ]) / 5.0
                assert placement["score"] == pytest.approx(expected_score)
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        keywords=keywords_strategy(),
        config=keyword_analyzer_config_strategy()
    )
    def test_recommendations_consistency(self, content, keywords, config):
        """Test that recommendations are consistent with analysis results."""
        analyzer = KeywordAnalyzer(content, keywords, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Check that recommendations are provided for non-optimal keyword density
            for keyword, data in results["keyword_density"]["keywords"].items():
                if not data["is_optimal"]:
                    # Should find at least one recommendation for this keyword's density
                    density_recommendations = [
                        r for r in results["recommendations"]
                        if r["type"] == "keyword_density" and r["keyword"] == keyword
                    ]
                    assert len(density_recommendations) > 0
                    
                    # The recommendation should mention the keyword
                    assert all(keyword in r["message"] for r in density_recommendations)
                    
                    # The recommendation should include a suggestion
                    assert all(len(r["suggestion"]) > 0 for r in density_recommendations)
            
            # Check that recommendations are provided for suboptimal keyword placement
            for keyword, placement in results["keyword_placement"].items():
                # For each placement check that's False and has a corresponding config check enabled
                if not placement["in_title"] and config.get("check_keyword_in_title", True):
                    title_recommendations = [
                        r for r in results["recommendations"]
                        if r["type"] == "keyword_placement" and r["keyword"] == keyword and "title" in r["message"].lower()
                    ]
                    assert len(title_recommendations) > 0
                
                # Similar checks could be added for headings, first paragraph, etc.
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        keywords=keywords_strategy(),
        config=keyword_analyzer_config_strategy()
    )
    def test_score_reflects_density_and_placement(self, content, keywords, config):
        """Test that the overall score reflects both density and placement."""
        analyzer = KeywordAnalyzer(content, keywords, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Calculate expected score components
            density_scores = []
            for keyword, data in results["keyword_density"]["keywords"].items():
                if data["is_optimal"]:
                    density_scores.append(1.0)
                else:
                    # Calculate how close the density is to the optimal range
                    density = data["density"]
                    min_density = data["optimal_range"]["min"]
                    max_density = data["optimal_range"]["max"]
                    
                    if density < min_density:
                        # Score based on how close to min_density
                        density_scores.append(density / min_density)
                    else:  # density > max_density
                        # Score based on how close to max_density
                        density_scores.append(max_density / density)
            
            density_score = sum(density_scores) / len(density_scores) if density_scores else 0
            
            placement_scores = [data["score"] for keyword, data in results["keyword_placement"].items()]
            placement_score = sum(placement_scores) / len(placement_scores) if placement_scores else 0
            
            # Calculate expected overall score (50% density, 50% placement)
            expected_score = (density_score * 0.5) + (placement_score * 0.5)
            
            # Check that the actual score matches the expected score
            assert results["overall_score"] == pytest.approx(expected_score)
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        keywords=keywords_strategy()
    )
    def test_default_config_validation(self, content, keywords):
        """Test that the default config is valid."""
        analyzer = KeywordAnalyzer(content, keywords)
        
        # Validate the default config
        is_valid, errors = analyzer.validate_config()
        assert is_valid, f"Default config is not valid: {errors}"


class TestReadabilityAnalyzerProperties:
    """Property-based tests for the ReadabilityAnalyzer class."""
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_readability_score_bounds(self, content, config):
        """Test that readability scores are bounded appropriately."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Check that the Flesch Reading Ease score is between 0 and 100
            flesch_score = results["readability_scores"]["flesch_reading_ease"]["score"]
            assert 0.0 <= flesch_score <= 100.0
            
            # Check that grade level scores are non-negative
            grade_level_scores = [
                results["readability_scores"]["flesch_kincaid_grade"]["score"],
                results["readability_scores"]["smog_index"]["score"],
                results["readability_scores"]["coleman_liau_index"]["score"],
                results["readability_scores"]["automated_readability_index"]["score"],
                results["readability_scores"]["gunning_fog_index"]["score"]
            ]
            
            for score in grade_level_scores:
                assert score >= 0.0
                
            # Check that the overall score is between 0 and 1
            assert 0.0 <= results["overall_score"] <= 1.0
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_reading_level_consistency(self, content, config):
        """Test that reading level is consistent with Flesch Reading Ease score."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Get the Flesch Reading Ease score and reading level
            flesch_score = results["readability_scores"]["flesch_reading_ease"]["score"]
            reading_level = results["readability_scores"]["reading_level"]
            
            # Check that the reading level is consistent with the Flesch score
            if flesch_score >= 80:
                assert reading_level == "beginner"
            elif flesch_score >= 50:
                assert reading_level == "intermediate"
            else:
                assert reading_level == "advanced"
                
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_text_statistics_consistency(self, content, config):
        """Test that text statistics are internally consistent."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Get text statistics
            stats = results["text_statistics"]
            
            # Check that num_complex_words <= num_words
            assert stats["num_complex_words"] <= stats["num_words"]
            
            # Check that complex_word_percentage = num_complex_words / num_words
            expected_percentage = stats["num_complex_words"] / stats["num_words"] if stats["num_words"] > 0 else 0
            assert stats["complex_word_percentage"] == pytest.approx(expected_percentage)
            
            # Check that avg_words_per_sentence = num_words / num_sentences
            expected_avg = stats["num_words"] / stats["num_sentences"] if stats["num_sentences"] > 0 else 0
            assert stats["avg_words_per_sentence"] == pytest.approx(expected_avg)
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_sentence_analysis_consistency(self, content, config):
        """Test that sentence analysis is internally consistent."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Get sentence analysis
            sentence_analysis = results["sentence_analysis"]
            
            # Check that the sum of sentence counts by length equals total sentence count
            sentence_count = sentence_analysis["sentence_count"]
            short_count = sentence_analysis["sentence_length"]["short_count"]
            long_count = sentence_analysis["sentence_length"]["long_count"]
            optimal_count = sentence_analysis["sentence_length"]["optimal_count"]
            
            assert short_count + long_count + optimal_count == sentence_count
            
            # Check that percentages add up to 1.0
            short_pct = sentence_analysis["sentence_length"]["short_percentage"]
            long_pct = sentence_analysis["sentence_length"]["long_percentage"]
            optimal_pct = sentence_analysis["sentence_length"]["optimal_percentage"]
            
            assert pytest.approx(short_pct + long_pct + optimal_pct) == 1.0
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_recommendations_consistency(self, content, config):
        """Test that recommendations are consistent with analysis results."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Check that recommendations exist for non-optimal Flesch Reading Ease
            if not results["readability_scores"]["flesch_reading_ease"]["is_optimal"]:
                flesch_recommendations = [
                    r for r in results["recommendations"]
                    if r["type"] == "readability_score"
                ]
                assert len(flesch_recommendations) > 0
            
            # Check that recommendations exist for non-optimal grade level
            if not results["readability_scores"]["flesch_kincaid_grade"]["is_optimal"]:
                grade_recommendations = [
                    r for r in results["recommendations"]
                    if r["type"] == "grade_level"
                ]
                assert len(grade_recommendations) > 0
                
            # Check that recommendations exist for non-optimal sentence length
            if not results["sentence_analysis"]["sentence_length"]["is_optimal"]:
                sentence_recommendations = [
                    r for r in results["recommendations"]
                    if r["type"] == "sentence_length"
                ]
                assert len(sentence_recommendations) > 0
                
            # Check that recommendations exist for non-optimal paragraph length
            if not results["paragraph_analysis"]["paragraph_length"]["is_optimal"]:
                paragraph_recommendations = [
                    r for r in results["recommendations"]
                    if r["type"] == "paragraph_length"
                ]
                assert len(paragraph_recommendations) > 0
                
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy(),
        config=readability_analyzer_config_strategy()
    )
    def test_readability_score_calculation(self, content, config):
        """Test that the overall readability score is calculated correctly."""
        analyzer = ReadabilityAnalyzer(content, config)
        
        try:
            # Validate content before analyzing
            is_valid, _ = analyzer.validate_content()
            assume(is_valid)
            
            # Perform the analysis
            results = analyzer.analyze()
            
            # Calculate expected score components
            readability_score = 0.0
            
            # Score based on Flesch Reading Ease
            if results["readability_scores"]["flesch_reading_ease"]["is_optimal"]:
                readability_score += 0.2
            else:
                # Calculate partial score based on how close to optimal
                flesch_score = results["readability_scores"]["flesch_reading_ease"]["score"]
                min_flesch = config["min_flesch_reading_ease"]
                readability_score += 0.2 * (flesch_score / min_flesch) if min_flesch > 0 else 0
            
            # Score based on grade level
            target_grade = config["max_flesch_kincaid_grade"]
            actual_grade = results["readability_scores"]["grade_level"]
            
            if actual_grade <= target_grade:
                readability_score += 0.2
            else:
                # Calculate partial score based on how close to target
                readability_score += 0.2 * (target_grade / actual_grade) if actual_grade > 0 else 0
            
            # Score based on sentence structure
            sentence_score = 0.0
            
            if results["sentence_analysis"]["sentence_length"]["is_optimal"]:
                sentence_score += 0.33
            
            if results["sentence_analysis"]["sentence_beginnings"]["is_optimal"]:
                sentence_score += 0.33
            
            if results["sentence_analysis"]["sentence_variety"]["is_optimal"]:
                sentence_score += 0.34
            
            readability_score += 0.2 * sentence_score
            
            # Score based on paragraph structure
            paragraph_score = 0.0
            
            if results["paragraph_analysis"]["paragraph_length"]["is_optimal"]:
                paragraph_score += 0.5
            
            if results["paragraph_analysis"]["paragraph_variety"]["is_optimal"]:
                paragraph_score += 0.5
            
            readability_score += 0.2 * paragraph_score
            
            # Score based on writing style
            style_score = 0.0
            
            if results["style_analysis"]["passive_voice"]["is_optimal"]:
                style_score += 0.33
            
            if results["style_analysis"]["adverb_usage"]["is_optimal"]:
                style_score += 0.33
            
            if results["style_analysis"]["complex_words"]["is_optimal"]:
                style_score += 0.34
            
            readability_score += 0.2 * style_score
            
            # Check that the actual score matches the expected score
            assert results["overall_score"] == pytest.approx(readability_score)
            
        except ValueError:
            # If content is not valid, skip the test
            assume(False)
    
    @given(
        content=content_dict_strategy()
    )
    def test_default_config_validation(self, content):
        """Test that the default config is valid."""
        analyzer = ReadabilityAnalyzer(content)
        
        # Validate the default config
        is_valid, errors = analyzer.validate_config()
        assert is_valid, f"Default config is not valid: {errors}"