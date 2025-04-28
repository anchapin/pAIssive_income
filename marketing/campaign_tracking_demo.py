"""
Demonstration of campaign tracking functionality.

This script demonstrates how to:
- Create marketing campaigns
- Record campaign metrics
- Analyze campaign performance
- Generate campaign reports
- Compare multiple campaigns
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import random

from marketing.campaign_tracking import CampaignTracker, MetricGroup

# Create a campaign tracker with storage in the current directory
tracker = CampaignTracker(storage_path="./campaign_data")

def create_sample_campaigns() -> List[str]:
    """Create sample marketing campaigns and return their IDs."""
    
    # Create a social media campaign
    social_campaign = tracker.create_campaign(
        name="Spring Product Launch - Social Media",
        description="Social media campaign for spring product launch",
        channels=["facebook", "instagram", "twitter"],
        goals=[
            {
                "name": "Increase brand awareness",
                "description": "Increase visibility and brand recognition",
                "metrics": ["impressions", "reach", "brand_mentions"]
            },
            {
                "name": "Drive website traffic",
                "description": "Send users to product landing pages",
                "metrics": ["clicks", "website_visits"]
            },
            {
                "name": "Generate leads",
                "description": "Collect contact information for potential customers",
                "metrics": ["new_leads", "email_signups"]
            }
        ],
        target_metrics={
            "impressions": 100000,
            "reach": 50000,
            "clicks": 5000,
            "website_visits": 4000,
            "new_leads": 500,
            "email_signups": 300,
            "brand_mentions": 200
        },
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now() + timedelta(days=60),
        budget=5000,
        tags=["social_media", "product_launch", "spring_campaign"]
    )
    
    # Create an email marketing campaign
    email_campaign = tracker.create_campaign(
        name="Spring Product Launch - Email",
        description="Email marketing campaign for spring product launch",
        channels=["email"],
        goals=[
            {
                "name": "Nurture leads",
                "description": "Nurture leads through the sales funnel",
                "metrics": ["email_opens", "clicks"]
            },
            {
                "name": "Drive conversions",
                "description": "Convert leads to customers",
                "metrics": ["conversions", "revenue"]
            }
        ],
        target_metrics={
            "email_opens": 5000,
            "clicks": 1000,
            "conversions": 200,
            "revenue": 10000
        },
        start_date=datetime.now() - timedelta(days=15),
        end_date=datetime.now() + timedelta(days=45),
        budget=3000,
        tags=["email", "product_launch", "spring_campaign"]
    )
    
    # Create a content marketing campaign
    content_campaign = tracker.create_campaign(
        name="Spring Product Launch - Content",
        description="Content marketing campaign for spring product launch",
        channels=["blog", "youtube"],
        goals=[
            {
                "name": "Establish thought leadership",
                "description": "Position the brand as a thought leader in the industry",
                "metrics": ["page_views", "time_on_page", "shares"]
            },
            {
                "name": "Generate organic traffic",
                "description": "Drive organic traffic through SEO",
                "metrics": ["website_visits", "new_leads"]
            }
        ],
        target_metrics={
            "page_views": 20000,
            "time_on_page": 180,  # seconds
            "shares": 500,
            "website_visits": 10000,
            "new_leads": 300
        },
        start_date=datetime.now() - timedelta(days=45),
        end_date=datetime.now() + timedelta(days=45),
        budget=7000,
        tags=["content", "product_launch", "spring_campaign"]
    )
    
    print(f"Created social media campaign with ID: {social_campaign['id']}")
    print(f"Created email campaign with ID: {email_campaign['id']}")
    print(f"Created content campaign with ID: {content_campaign['id']}")
    
    return [social_campaign["id"], email_campaign["id"], content_campaign["id"]]

def generate_sample_metrics(campaign_ids: List[str]) -> None:
    """Generate sample metrics for campaigns."""
    
    now = datetime.now()
    
    # Metrics for social media campaign
    social_id = campaign_ids[0]
    social_campaign = tracker.get_campaign(social_id)
    social_start = datetime.fromisoformat(social_campaign["start_date"])
    
    # Generate daily metrics for social media campaign
    for day in range((now - social_start).days + 1):
        date = social_start + timedelta(days=day)
        
        # Generate random metrics with growth over time
        growth_factor = min(1.0, (day / 30) * 1.5)
        
        # Record impressions
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="impressions",
            value=random.randint(1000, 3000) * (1 + growth_factor),
            timestamp=date,
            channel="facebook",
            metadata={"ad_set": "spring_launch_awareness"}
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="impressions",
            value=random.randint(800, 2500) * (1 + growth_factor),
            timestamp=date,
            channel="instagram",
            metadata={"ad_set": "spring_launch_awareness"}
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="impressions",
            value=random.randint(500, 1500) * (1 + growth_factor),
            timestamp=date,
            channel="twitter",
            metadata={"ad_set": "spring_launch_awareness"}
        )
        
        # Record reach
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="reach",
            value=random.randint(500, 1500) * (1 + growth_factor),
            timestamp=date,
            channel="facebook"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="reach",
            value=random.randint(400, 1200) * (1 + growth_factor),
            timestamp=date,
            channel="instagram"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="reach",
            value=random.randint(300, 900) * (1 + growth_factor),
            timestamp=date,
            channel="twitter"
        )
        
        # Record clicks
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="clicks",
            value=random.randint(50, 200) * (1 + growth_factor),
            timestamp=date,
            channel="facebook"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="clicks",
            value=random.randint(40, 160) * (1 + growth_factor),
            timestamp=date,
            channel="instagram"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="clicks",
            value=random.randint(30, 100) * (1 + growth_factor),
            timestamp=date,
            channel="twitter"
        )
        
        # Record website visits
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="website_visits",
            value=random.randint(40, 180) * (1 + growth_factor),
            timestamp=date,
            channel="facebook"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="website_visits",
            value=random.randint(30, 140) * (1 + growth_factor),
            timestamp=date,
            channel="instagram"
        )
        
        tracker.record_metric(
            campaign_id=social_id,
            metric_name="website_visits",
            value=random.randint(20, 90) * (1 + growth_factor),
            timestamp=date,
            channel="twitter"
        )
        
        # Record new leads - lower numbers
        if day % 2 == 0:  # Every other day
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="new_leads",
                value=random.randint(5, 20) * (1 + growth_factor),
                timestamp=date,
                channel="facebook"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="new_leads",
                value=random.randint(4, 16) * (1 + growth_factor),
                timestamp=date,
                channel="instagram"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="new_leads",
                value=random.randint(3, 10) * (1 + growth_factor),
                timestamp=date,
                channel="twitter"
            )
        
        # Record email signups - lower numbers
        if day % 2 == 1:  # Alternate days
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="email_signups",
                value=random.randint(4, 15) * (1 + growth_factor),
                timestamp=date,
                channel="facebook"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="email_signups",
                value=random.randint(3, 12) * (1 + growth_factor),
                timestamp=date,
                channel="instagram"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="email_signups",
                value=random.randint(2, 8) * (1 + growth_factor),
                timestamp=date,
                channel="twitter"
            )
        
        # Record brand mentions - fewer, random days
        if day % 4 == 0:
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="brand_mentions",
                value=random.randint(2, 10) * (1 + growth_factor),
                timestamp=date,
                channel="facebook"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="brand_mentions",
                value=random.randint(3, 12) * (1 + growth_factor),
                timestamp=date,
                channel="instagram"
            )
            
            tracker.record_metric(
                campaign_id=social_id,
                metric_name="brand_mentions",
                value=random.randint(5, 15) * (1 + growth_factor),
                timestamp=date,
                channel="twitter"
            )
    
    # Email campaign metrics
    email_id = campaign_ids[1]
    email_campaign = tracker.get_campaign(email_id)
    email_start = datetime.fromisoformat(email_campaign["start_date"])
    
    # Email blasts every 7 days
    email_days = []
    current_day = 0
    while (email_start + timedelta(days=current_day)) <= now:
        email_days.append(current_day)
        current_day += 7
    
    for day in email_days:
        date = email_start + timedelta(days=day)
        
        # Email campaign grows more slowly
        growth_factor = min(0.8, (day / 30) * 0.9)
        
        # Record email metrics for different segments
        segments = ["new_subscribers", "existing_customers", "leads"]
        for segment in segments:
            # Different base values for different segments
            if segment == "new_subscribers":
                base_opens = random.randint(300, 500)
                base_clicks = random.randint(50, 100)
                base_conversions = random.randint(5, 15)
            elif segment == "existing_customers":
                base_opens = random.randint(400, 600)
                base_clicks = random.randint(80, 150)
                base_conversions = random.randint(10, 25)
            else:  # leads
                base_opens = random.randint(200, 400)
                base_clicks = random.randint(30, 80)
                base_conversions = random.randint(3, 10)
            
            # Email opens
            tracker.record_metric(
                campaign_id=email_id,
                metric_name="email_opens",
                value=base_opens * (1 + growth_factor),
                timestamp=date,
                channel="email",
                metadata={"segment": segment, "email_type": "product_launch"}
            )
            
            # Clicks from email
            tracker.record_metric(
                campaign_id=email_id,
                metric_name="clicks",
                value=base_clicks * (1 + growth_factor),
                timestamp=date,
                channel="email",
                metadata={"segment": segment, "email_type": "product_launch"}
            )
            
            # Conversions from email (leads to customers)
            tracker.record_metric(
                campaign_id=email_id,
                metric_name="conversions",
                value=base_conversions * (1 + growth_factor),
                timestamp=date,
                channel="email",
                metadata={"segment": segment, "email_type": "product_launch"}
            )
            
            # Revenue from conversions
            avg_order = random.randint(40, 60)
            tracker.record_metric(
                campaign_id=email_id,
                metric_name="revenue",
                value=base_conversions * (1 + growth_factor) * avg_order,
                timestamp=date,
                channel="email",
                metadata={"segment": segment, "email_type": "product_launch"}
            )
    
    # Content marketing metrics
    content_id = campaign_ids[2]
    content_campaign = tracker.get_campaign(content_id)
    content_start = datetime.fromisoformat(content_campaign["start_date"])
    
    # Content pieces published weekly
    content_publish_days = []
    current_day = 0
    while (content_start + timedelta(days=current_day)) <= now:
        if current_day % 7 == 0:  # Weekly blog post
            content_publish_days.append((current_day, "blog"))
        if current_day % 14 == 0:  # Bi-weekly YouTube video
            content_publish_days.append((current_day, "youtube"))
        current_day += 1
    
    # Track metrics for each content piece
    for pub_day, channel in content_publish_days:
        # Each content piece gets metrics for 14 days after publishing
        for day in range(min(14, (now - (content_start + timedelta(days=pub_day))).days + 1)):
            date = content_start + timedelta(days=pub_day + day)
            
            # Content performance tends to be highest at first, then decays
            decay_factor = 1 - (day / 20)  # Slower decay
            
            # Base values differ by channel
            if channel == "blog":
                base_views = random.randint(200, 500)
                base_time = random.randint(120, 240)  # seconds
                base_shares = random.randint(5, 20)
                base_visits = random.randint(150, 400)
                base_leads = random.randint(3, 15)
            else:  # YouTube
                base_views = random.randint(300, 800)
                base_time = random.randint(180, 360)  # seconds
                base_shares = random.randint(8, 30)
                base_visits = random.randint(100, 300)
                base_leads = random.randint(2, 10)
            
            # Page views / video views
            tracker.record_metric(
                campaign_id=content_id,
                metric_name="page_views",
                value=base_views * decay_factor,
                timestamp=date,
                channel=channel,
                metadata={"content_id": f"{channel}_content_{pub_day}"}
            )
            
            # Time on page / watch time
            tracker.record_metric(
                campaign_id=content_id,
                metric_name="time_on_page",
                value=base_time * decay_factor,
                timestamp=date,
                channel=channel,
                metadata={"content_id": f"{channel}_content_{pub_day}"}
            )
            
            # Social shares
            if day % 2 == 0:  # Not every day gets shares
                tracker.record_metric(
                    campaign_id=content_id,
                    metric_name="shares",
                    value=base_shares * decay_factor,
                    timestamp=date,
                    channel=channel,
                    metadata={"content_id": f"{channel}_content_{pub_day}"}
                )
            
            # Website visits from content
            tracker.record_metric(
                campaign_id=content_id,
                metric_name="website_visits",
                value=base_visits * decay_factor,
                timestamp=date,
                channel=channel,
                metadata={"content_id": f"{channel}_content_{pub_day}"}
            )
            
            # New leads from content
            if day % 3 == 0:  # Less frequent lead generation
                tracker.record_metric(
                    campaign_id=content_id,
                    metric_name="new_leads",
                    value=base_leads * decay_factor,
                    timestamp=date,
                    channel=channel,
                    metadata={"content_id": f"{channel}_content_{pub_day}"}
                )
    
    print("Generated sample metrics for all campaigns")

def analyze_campaigns(campaign_ids: List[str]) -> None:
    """Analyze campaign performance and print results."""
    
    # Analyze social media campaign
    social_id = campaign_ids[0]
    social_analysis = tracker.analyze_performance(social_id)
    
    print("\n=== Social Media Campaign Performance Analysis ===")
    print(f"Overall Performance: {social_analysis['overall_performance']:.2f}%")
    print("\nMetric Performance:")
    
    for metric, data in social_analysis["metrics_performance"].items():
        print(f"  {metric}: {data['current']:.2f}/{data['target']} ({data['achievement_percentage']:.2f}%)")
    
    print("\nPerformance by Group:")
    for group, data in social_analysis["groups_performance"].items():
        print(f"  {group}: {data['average_achievement']:.2f}%")
    
    # Get detailed metrics for social media campaign by channel
    social_metrics = tracker.get_metrics(
        campaign_id=social_id,
        group_by="channel"
    )
    
    print("\nPerformance by Channel:")
    for channel, metrics in social_metrics.get("grouped_data", {}).items():
        print(f"  {channel}:")
        for metric_name, value in metrics.items():
            print(f"    {metric_name}: {value:.2f}")
    
    # Compare all campaigns
    comparison = tracker.compare_campaigns(campaign_ids)
    
    print("\n=== Campaign Comparison ===")
    print("Overall Ranking:")
    for rank, campaign in enumerate(comparison["overall_ranking"]):
        print(f"  {rank + 1}. {campaign['name']} - {campaign['performance']:.2f}%")
    
    # Generate a report for the top performing campaign
    top_campaign_id = comparison["overall_ranking"][0]["campaign_id"]
    report = tracker.generate_report(top_campaign_id, report_type="summary")
    
    print(f"\n=== Performance Report for {report['campaign_name']} ===")
    print(f"Overall Performance: {report['performance_summary']['overall_performance']:.2f}%")
    
    print("\nTop Performing Metrics:")
    for metric in report["performance_summary"]["top_metrics"]:
        print(f"  {metric['name']}: {metric['achievement']:.2f}% ({metric['current']:.2f}/{metric['target']})")
    
    print("\nBottom Performing Metrics:")
    for metric in report["performance_summary"]["bottom_metrics"]:
        print(f"  {metric['name']}: {metric['achievement']:.2f}% ({metric['current']:.2f}/{metric['target']})")

if __name__ == "__main__":
    # Create campaigns if they don't exist
    if not tracker.list_campaigns():
        campaign_ids = create_sample_campaigns()
        generate_sample_metrics(campaign_ids)
    else:
        # Use existing campaigns
        campaigns = tracker.list_campaigns()
        campaign_ids = [c["id"] for c in campaigns]
        print(f"Using {len(campaigns)} existing campaigns")
    
    # Analyze campaign performance
    analyze_campaigns(campaign_ids)