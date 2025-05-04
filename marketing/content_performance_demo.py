"""
Demo script for the content performance analytics module.

This script demonstrates how to track and analyze the performance of marketing content
across different channels using the ContentPerformanceAnalyzer.
"""

import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from marketing.content_performance import ContentPerformanceAnalyzer


def create_demo_storage():
    ():
    """Create a directory for demo storage if it doesn't exist."""
    storage_dir = Path("./demo_storage")
    if not storage_dir.exists():
    storage_dir.mkdir()
    return storage_dir


    def create_demo_content():
    """Create sample content for demonstration."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Create a blog post
    blog_post = analyzer.track_content(
    content_id="blog-001",
    content_type="blog_post",
    title="10 Ways AI Can Boost Your Marketing ROI",
    channels=["website", "social_media"],
    metadata={
    "author": "Marketing Team",
    "word_count": 1200,
    "tags": ["AI", "marketing", "ROI"],
    },
    )

    # Create a social media post
    social_post = analyzer.track_content(
    content_id="social-001",
    content_type="social_media",
    title="Maximize your marketing efficiency with our AI tools",
    channels=["twitter", "linkedin", "facebook"],
    metadata={
    "author": "Social Media Manager",
    "tags": ["AI", "marketing", "efficiency"],
    "has_image": True,
    },
    )

    # Create an email newsletter
    email_newsletter = analyzer.track_content(
    content_id="email-001",
    content_type="email",
    title="Monthly Marketing AI Update - June Edition",
    channels=["email"],
    metadata={
    "author": "Email Marketing Team",
    "recipient_count": 5000,
    "tags": ["newsletter", "AI", "monthly update"],
    },
    )

    # Create a video
    video = analyzer.track_content(
    content_id="video-001",
    content_type="video",
    title="How to Set Up Your First AI Marketing Campaign",
    channels=["youtube", "website"],
    metadata={
    "author": "Video Production Team",
    "duration_seconds": 360,
    "tags": ["tutorial", "AI", "marketing campaign"],
    },
    )

    print(f"Created {len(analyzer.content)} content items for tracking")
    return {
    "blog_post": blog_post,
    "social_post": social_post,
    "email_newsletter": email_newsletter,
    "video": video,
    }


    def generate_demo_engagements(content: Dict[str, Any]):
    """Generate sample engagement data for the demo content."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Get the current date and time
    now = datetime.now()

    # Generate engagement data for the blog post over the past 7 days
    blog_id = content["blog_post"]["content_id"]
    for day in range(7):
    date = now - timedelta(days=day)

    # Views
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="view",
    channel="website",
    count=random.randint(50, 200),
    timestamp=date,
    )

    # Clicks
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="click",
    channel="website",
    count=random.randint(5, 30),
    timestamp=date,
    )

    # Comments
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="comment",
    channel="website",
    count=random.randint(0, 5),
    timestamp=date,
    )

    # Shares
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="share",
    channel="website",
    count=random.randint(1, 10),
    timestamp=date,
    )

    # Social media views
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="view",
    channel="social_media",
    count=random.randint(100, 300),
    timestamp=date,
    )

    # Conversions
    analyzer.record_engagement(
    content_id=blog_id,
    engagement_type="lead",
    channel="website",
    count=random.randint(1, 5),
    timestamp=date,
    )

    # Generate engagement data for the social media post
    social_id = content["social_post"]["content_id"]
    for channel in ["twitter", "linkedin", "facebook"]:
    for day in range(5):
    date = now - timedelta(days=day)

    # Impressions
    analyzer.record_engagement(
    content_id=social_id,
    engagement_type="impression",
    channel=channel,
    count=random.randint(200, 500),
    timestamp=date,
    )

    # Likes
    analyzer.record_engagement(
    content_id=social_id,
    engagement_type="like",
    channel=channel,
    count=random.randint(5, 50),
    timestamp=date,
    )

    # Comments
    analyzer.record_engagement(
    content_id=social_id,
    engagement_type="comment",
    channel=channel,
    count=random.randint(0, 10),
    timestamp=date,
    )

    # Shares
    analyzer.record_engagement(
    content_id=social_id,
    engagement_type="share",
    channel=channel,
    count=random.randint(1, 15),
    timestamp=date,
    )

    # Clicks
    analyzer.record_engagement(
    content_id=social_id,
    engagement_type="click",
    channel=channel,
    count=random.randint(10, 30),
    timestamp=date,
    )

    # Generate engagement data for the email newsletter
    email_id = content["email_newsletter"]["content_id"]

    # Opens
    analyzer.record_engagement(
    content_id=email_id,
    engagement_type="view",
    channel="email",
    count=1250,  # 25% open rate
    timestamp=now - timedelta(days=2),
    )

    # Clicks
    analyzer.record_engagement(
    content_id=email_id,
    engagement_type="click",
    channel="email",
    count=150,  # 3% click rate
    timestamp=now - timedelta(days=2),
    )

    # Generate engagement data for the video
    video_id = content["video"]["content_id"]
    for day in range(5):
    date = now - timedelta(days=day)

    # Views on YouTube
    analyzer.record_engagement(
    content_id=video_id,
    engagement_type="view",
    channel="youtube",
    count=random.randint(50, 200),
    timestamp=date,
    )

    # Likes on YouTube
    analyzer.record_engagement(
    content_id=video_id,
    engagement_type="like",
    channel="youtube",
    count=random.randint(5, 20),
    timestamp=date,
    )

    # Comments on YouTube
    analyzer.record_engagement(
    content_id=video_id,
    engagement_type="comment",
    channel="youtube",
    count=random.randint(0, 5),
    timestamp=date,
    )

    # Shares on YouTube
    analyzer.record_engagement(
    content_id=video_id,
    engagement_type="share",
    channel="youtube",
    count=random.randint(1, 8),
    timestamp=date,
    )

    # Views on website
    analyzer.record_engagement(
    content_id=video_id,
    engagement_type="view",
    channel="website",
    count=random.randint(20, 100),
    timestamp=date,
    )

    print("Generated engagement data for all content items")
    return analyzer.engagements


    def demo_content_analysis():
    """Demonstrate content performance analysis."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Analyze blog post performance
    blog_analysis = analyzer.analyze_performance("blog-001")

    print("\n=== Blog Post Performance Analysis ===")
    print(f"Title: {blog_analysis['title']}")
    print(
    f"Overall Performance Score: {blog_analysis['overall_performance_score']:.2f}"
    )
    print(f"Rating: {blog_analysis['performance_rating']}")
    print(
    f"Engagement Rate: {blog_analysis['engagement_metrics']['engagement_rate']:.2f}%"
    )
    print(
    f"Conversion Rate: {blog_analysis['engagement_metrics']['conversion_rate']:.2f}%"
    )

    print("\nEngagement Metrics:")
    for metric, value in blog_analysis["metrics"].items():
    if metric in blog_analysis["performance"]:
    benchmark = blog_analysis["performance"][metric]["benchmark"]
    performance = blog_analysis["performance"][metric]["performance_percentage"]
    print(f"  {metric}: {value} ({performance:.2f}% of benchmark {benchmark})")
    else:
    print(f"  {metric}: {value}")

    print("\nInsights:")
    for insight in blog_analysis["insights"]:
    print(f"  [{insight['type']}] {insight['message']}")


    def demo_content_comparison():
    """Demonstrate content comparison."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Compare all content items
    comparison = analyzer.compare_content(
    ["blog-001", "social-001", "email-001", "video-001"]
    )

    print("\n=== Content Performance Comparison ===")
    print("Performance Ranking:")
    for i, item in enumerate(comparison["performance_ranking"]):
    print(f"  {i+1}. {item['title']} (Score: {item['performance_score']:.2f})")

    print("\nMetric Comparison (Views):")
    metric_data = comparison["metrics_comparison"].get("view", {})
    if metric_data:
    for content_id, value in metric_data["content_values"].items():
    title = comparison["content_info"][content_id]["title"]
    print(f"  {title}: {value} views")

    print(f"  Average: {metric_data['average_value']:.2f} views")

    if metric_data["highest_value"]["content_id"]:
    best_id = metric_data["highest_value"]["content_id"]
    best_title = comparison["content_info"][best_id]["title"]
    print(
    f"  Best performing: {best_title} with {metric_data['highest_value']['value']} views"
    )


    def demo_identify_top_content():
    """Demonstrate identifying top-performing content."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Identify top performing content by views
    top_content = analyzer.identify_top_performing_content(
    engagement_metric="view", limit=3
    )

    print("\n=== Top Performing Content by Views ===")
    for i, content in enumerate(top_content):
    print(f"{i+1}. {content['title']} ({content['metric_value']} views)")
    print(f"   Content Type: {content['content_type']}")
    print(f"   Channels: {', '.join(content['channels'])}")
    print(
    f"   Key metrics: {', '.join([f'{k}: {v}' for k, v in list(content['metrics'].items())[:3]])}"
    )
    print()


    def demo_content_reports():
    """Demonstrate generating content reports."""
    analyzer = ContentPerformanceAnalyzer(storage_path="./demo_storage")

    # Generate a summary report for the social post
    social_report = analyzer.generate_content_report(
    content_id="social-001", report_type="summary"
    )

    print("\n=== Social Media Post Summary Report ===")
    print(f"Title: {social_report['title']}")
    print(f"Generated: {social_report['generated_at']}")
    print(
    f"Time Period: {social_report['time_period']['start']} to {social_report['time_period']['end']}"
    )

    summary = social_report["performance_summary"]
    print(f"Overall Score: {summary['overall_score']:.2f}")
    print(f"Rating: {summary['rating']}")
    print(f"Engagement Rate: {summary['engagement_rate']:.2f}%")
    print(f"Conversion Rate: {summary['conversion_rate']:.2f}%")

    print("\nTop Metrics:")
    for metric in summary["top_metrics"]:
    print(
    f"  {metric['name']}: {metric['value']} ({metric['performance']:.2f}% of benchmark)"
    )

    print("\nInsights:")
    for insight in summary["insights"]:
    print(f"  [{insight['type']}] {insight['message']}")

    # Generate a channel report for the video
    video_report = analyzer.generate_content_report(
    content_id="video-001", report_type="channel"
    )

    print("\n=== Video Channel Report ===")
    print(f"Title: {video_report['title']}")

    print("\nChannel Performance:")
    for channel, data in video_report["channel_performance"].items():
    print(f"  {channel}: {data['total_engagements']} total engagements")
    for metric, value in data["metrics"].items():
    print(f"    {metric}: {value}")

    print("\nChannel Recommendations:")
    for rec in video_report["channel_recommendations"]:
    print(f"  [{rec['type']}] {rec['message']}")


    if __name__ == "__main__":
    print("=== Content Performance Analytics Demo ===")

    # Create demo storage directory
    storage_dir = create_demo_storage()
    print(f"Demo storage directory: {storage_dir}")

    # Create demo content
    content = create_demo_content()

    # Generate demo engagements
    engagements = generate_demo_engagements(content)

    # Demonstrate content analysis
    demo_content_analysis()

    # Demonstrate content comparison
    demo_content_comparison()

    # Demonstrate identifying top content
    demo_identify_top_content()

    # Demonstrate content reports
    demo_content_reports()

    print("\nDemo completed!")