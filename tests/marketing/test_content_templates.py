"""
Tests for the content templates components in the Marketing module.
"""



from marketing.content_templates import (
    BlogPostTemplate,
    ContentTemplate,
    EmailNewsletterTemplate,
    SocialMediaTemplate,
)


def test_content_template_init():
    """Test ContentTemplate initialization."""
    template = ContentTemplate(
        name="Test Template", description="A test content template"
    )

    # Check that the template has the expected attributes
    assert template.name == "Test Template"
    assert template.description == "A test content template"
    assert hasattr(template, "id")
    assert hasattr(template, "created_at")
    assert hasattr(template, "updated_at")
    assert hasattr(template, "sections")
    assert isinstance(template.sections, list)


def test_content_template_add_section():
    """Test add_section method of ContentTemplate."""
    template = ContentTemplate(
        name="Test Template", description="A test content template"
    )

    # Add a section
    section = template.add_section(
        name="Introduction",
        description="The introduction section",
        content_type="text",
        placeholder="Write an engaging introduction here...",
        required=True,
    )

    # Check that the section was added
    assert len(template.sections) == 1
    assert template.sections[0] == section

    # Check that the section has the expected attributes
    assert "id" in section
    assert section["name"] == "Introduction"
    assert section["description"] == "The introduction section"
    assert section["content_type"] == "text"
    assert section["placeholder"] == "Write an engaging introduction here..."
    assert section["required"] is True


def test_content_template_generate_content():
    """Test generate_content method of ContentTemplate."""
    template = ContentTemplate(
        name="Test Template",
        description="A test content template",
        key_points=[
            "Productivity benefits",
            "Cost savings",
            "Implementation strategies",
        ],
    )

    # Add sections
    template.add_section(
        name="Introduction",
        description="The introduction section",
        content_type="text",
        placeholder="Write an engaging introduction here...",
        required=True,
    )

    template.add_section(
        name="Main Content",
        description="The main content section",
        content_type="text",
        placeholder="Write the main content here...",
        required=True,
    )

    template.add_section(
        name="Conclusion",
        description="The conclusion section",
        content_type="text",
        placeholder="Write a compelling conclusion here...",
        required=True,
    )

    # Generate content
    content = template.generate_content(
        topic="AI Tools for Small Businesses",
        target_audience="Small business owners",
        tone="informative",
        keywords=["AI", "small business", "productivity", "automation"],
    )

    # Check that the content has the expected attributes
    assert "id" in content
    assert "template_id" in content
    assert "topic" in content
    assert "target_audience" in content
    assert "tone" in content
    assert "keywords" in content
    assert "sections" in content
    assert "created_at" in content

    # Check specific values
    assert content["template_id"] == template.id
    assert content["topic"] == "AI Tools for Small Businesses"
    assert content["target_audience"] == "Small business owners"
    assert content["tone"] == "informative"
    assert content["keywords"] == ["AI", "small business", "productivity", "automation"]
    assert isinstance(content["sections"], list)
    assert len(content["sections"]) == 3

    # Check that each section has content
    for section in content["sections"]:
        assert "id" in section
        assert "name" in section
        assert "content" in section
        assert isinstance(section["content"], str)
        assert len(section["content"]) > 0


def test_blog_post_template_init():
    """Test BlogPostTemplate initialization."""
    template = BlogPostTemplate(
        name="Test Blog Post Template", description="A test blog post template"
    )

    # Check that the template has the expected attributes
    assert template.name == "Test Blog Post Template"
    assert template.description == "A test blog post template"
    assert hasattr(template, "id")
    assert hasattr(template, "created_at")
    assert hasattr(template, "updated_at")
    assert hasattr(template, "sections")
    assert isinstance(template.sections, list)

    # Check that the default sections were added
    section_names = [section["name"] for section in template.sections]
    assert "Title" in section_names
    assert "Introduction" in section_names
    assert "Main Content" in section_names
    assert "Conclusion" in section_names
    assert "Call to Action" in section_names


def test_blog_post_template_generate_blog_post():
    """Test generate_blog_post method of BlogPostTemplate."""
    template = BlogPostTemplate(
        name="Test Blog Post Template",
        description="A test blog post template",
        key_points=[
            "Productivity benefits",
            "Cost savings",
            "Implementation strategies",
        ],
    )

    # Generate a blog post
    blog_post = template.generate_blog_post(
        topic="AI Tools for Small Businesses",
        target_audience="Small business owners",
        tone="informative",
        keywords=["AI", "small business", "productivity", "automation"],
        word_count=1000,
        include_images=True,
    )

    # Check that the blog post has the expected attributes
    assert "id" in blog_post
    assert "template_id" in blog_post
    assert "topic" in blog_post
    assert "target_audience" in blog_post
    assert "tone" in blog_post
    assert "keywords" in blog_post
    assert "word_count" in blog_post
    assert "include_images" in blog_post
    assert "sections" in blog_post
    assert "created_at" in blog_post

    # Check specific values
    assert blog_post["template_id"] == template.id
    assert blog_post["topic"] == "AI Tools for Small Businesses"
    assert blog_post["target_audience"] == "Small business owners"
    assert blog_post["tone"] == "informative"
    assert blog_post["keywords"] == [
        "AI",
        "small business",
        "productivity",
        "automation",
    ]
    assert blog_post["word_count"] == 1000
    assert blog_post["include_images"] is True
    assert isinstance(blog_post["sections"], list)

    # Check that each section has content
    for section in blog_post["sections"]:
        assert "id" in section
        assert "name" in section
        assert "content" in section
        assert isinstance(section["content"], str)
        assert len(section["content"]) > 0


def test_social_media_template_init():
    """Test SocialMediaTemplate initialization."""
    template = SocialMediaTemplate(
        name="Test Social Media Template",
        description="A test social media template",
        platform="instagram",
    )

    # Check that the template has the expected attributes
    assert template.name == "Test Social Media Template"
    assert template.description == "A test social media template"
    assert template.platform == "instagram"
    assert hasattr(template, "id")
    assert hasattr(template, "created_at")
    assert hasattr(template, "updated_at")
    assert hasattr(template, "sections")
    assert isinstance(template.sections, list)

    # Check that the default sections were added
    section_names = [section["name"] for section in template.sections]
    assert "Caption" in section_names
    assert "Hashtags" in section_names


def test_social_media_template_generate_post():
    """Test generate_post method of SocialMediaTemplate."""
    template = SocialMediaTemplate(
        name="Test Social Media Template",
        description="A test social media template",
        platform="instagram",
        key_points=[
            "Productivity benefits",
            "Cost savings",
            "Implementation strategies",
        ],
    )

    # Generate a social media post
    post = template.generate_post(
        topic="AI Tools for Small Businesses",
        target_audience="Small business owners",
        tone="conversational",
        include_hashtags=True,
        include_emoji=True,
        include_call_to_action=True,
    )

    # Check that the post has the expected attributes
    assert "id" in post
    assert "template_id" in post
    assert "platform" in post
    assert "topic" in post
    assert "target_audience" in post
    assert "tone" in post
    assert "include_hashtags" in post
    assert "include_emoji" in post
    assert "include_call_to_action" in post
    assert "sections" in post
    assert "created_at" in post

    # Check specific values
    assert post["template_id"] == template.id
    assert post["platform"] == "instagram"
    assert post["topic"] == "AI Tools for Small Businesses"
    assert post["target_audience"] == "Small business owners"
    assert post["tone"] == "conversational"
    assert post["include_hashtags"] is True
    assert post["include_emoji"] is True
    assert post["include_call_to_action"] is True
    assert isinstance(post["sections"], list)

    # Check that each section has content
    for section in post["sections"]:
        assert "id" in section
        assert "name" in section
        assert "content" in section
        assert isinstance(section["content"], str)
        assert len(section["content"]) > 0


def test_email_newsletter_template_init():
    """Test EmailNewsletterTemplate initialization."""
    template = EmailNewsletterTemplate(
        name="Test Email Newsletter Template",
        description="A test email newsletter template",
    )

    # Check that the template has the expected attributes
    assert template.name == "Test Email Newsletter Template"
    assert template.description == "A test email newsletter template"
    assert hasattr(template, "id")
    assert hasattr(template, "created_at")
    assert hasattr(template, "updated_at")
    assert hasattr(template, "sections")
    assert isinstance(template.sections, list)

    # Check that the default sections were added
    section_names = [section["name"] for section in template.sections]
    assert "Subject Line" in section_names
    assert "Preheader" in section_names
    assert "Greeting" in section_names
    assert "Main Content" in section_names
    assert "Call to Action" in section_names
    assert "Footer" in section_names


def test_email_newsletter_template_generate_newsletter():
    """Test generate_newsletter method of EmailNewsletterTemplate."""
    template = EmailNewsletterTemplate(
        name="Test Email Newsletter Template",
        description="A test email newsletter template",
        key_points=[
            "Productivity benefits",
            "Cost savings",
            "Implementation strategies",
        ],
    )

    # Generate an email newsletter
    newsletter = template.generate_newsletter(
        topic="AI Tools for Small Businesses",
        target_audience="Small business owners",
        tone="friendly",
        include_images=True,
        include_personalization=True,
        include_call_to_action=True,
    )

    # Check that the newsletter has the expected attributes
    assert "id" in newsletter
    assert "template_id" in newsletter
    assert "topic" in newsletter
    assert "target_audience" in newsletter
    assert "tone" in newsletter
    assert "include_images" in newsletter
    assert "include_personalization" in newsletter
    assert "include_call_to_action" in newsletter
    assert "sections" in newsletter
    assert "created_at" in newsletter

    # Check specific values
    assert newsletter["template_id"] == template.id
    assert newsletter["topic"] == "AI Tools for Small Businesses"
    assert newsletter["target_audience"] == "Small business owners"
    assert newsletter["tone"] == "friendly"
    assert newsletter["include_images"] is True
    assert newsletter["include_personalization"] is True
    assert newsletter["include_call_to_action"] is True
    assert isinstance(newsletter["sections"], list)

    # Check that each section has content
    for section in newsletter["sections"]:
        assert "id" in section
        assert "name" in section
        assert "content" in section
        assert isinstance(section["content"], str)
        assert len(section["content"]) > 0