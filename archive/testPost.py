#!/usr/bin/env python3
"""
Complete test script for Flask API with all fixes
Tests article_id and cluster_title support
Uses random IDs to avoid conflicts
"""

import requests
import json
import random
import time

BASE_URL = "http://localhost:5000"

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🎯 {title}")
    print(f"{'='*80}")

def print_subheader(title):
    print(f"\n{'-'*60}")
    print(f"📍 {title}")
    print(f"{'-'*60}")

def test_endpoint(method, endpoint, data, description):
    """Test an endpoint and show results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🚀 {method}: {description}")
    print(f"   URL: {url}")
    
    try:
        if method == "POST":
            response = requests.post(url, json=data)
        elif method == "GET":
            response = requests.get(url)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return None
        
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                print("   ✅ SUCCESS")
                
                # Show summary info
                if 'summary' in response_data:
                    summary = response_data['summary']
                    for key, value in summary.items():
                        print(f"   📊 {key}: {value}")
                
                if 'cluster' in response_data:
                    cluster = response_data['cluster']
                    cluster_id = cluster.get('cluster_id')
                    cluster_title = cluster.get('cluster_title', 'No title')
                    print(f"   📝 Created cluster {cluster_id}: {cluster_title}")
                
                if 'results' in response_data:
                    results = response_data['results']
                    print(f"   📝 Created {len(results)} cluster batches")
                    for i, result in enumerate(results):
                        c = result.get('cluster', {})
                        articles_count = result.get('articles_count', 0)
                        print(f"      Batch {i+1}: Cluster {c.get('cluster_id')} with {articles_count} articles")
                
                return response_data
            else:
                print("   ❌ FAILED")
                if 'error' in response_data:
                    print(f"   🔍 Error: {response_data['error']}")
                else:
                    print(f"   🔍 Response: {json.dumps(response_data, indent=6)}")
                return None
                
        except json.JSONDecodeError:
            print("   📄 Non-JSON response:")
            print(f"   {response.text}")
            if response.status_code in [200, 201]:
                print("   ✅ SUCCESS")
                return response.text
            else:
                print("   ❌ FAILED")
                return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ FAILED - Connection Error")
        print("   🔍 Is your Flask server running on http://localhost:5000?")
        return None
    except Exception as e:
        print(f"   ❌ FAILED - Error: {str(e)}")
        return None

def main():
    """Run comprehensive tests with all fixes"""
    print("🚀 COMPLETE FLASK API TEST SUITE")
    print("Testing all endpoints with article_id and cluster_title support")
    print(f"🌐 Target: {BASE_URL}")
    
    # Use random high numbers to avoid conflicts
    base_id = random.randint(8000, 9999)
    print(f"🎲 Using base ID: {base_id} to avoid conflicts")
    
    created_clusters = []
    
    # Test 1: Health check first
    print_header("BASIC CONNECTIVITY TESTS")
    test_endpoint("GET", "/health", None, "Health check")
    test_endpoint("GET", "/server", None, "Server status")
    
    # Test 2: Single cluster batch with all new fields
    print_header("SINGLE CLUSTER BATCH TEST")
    
    cluster_id_1 = base_id + 1
    single_cluster_data = {
        "cluster": {
            "cluster_id": cluster_id_1,
            "cluster_summary": "Technology and AI News - Latest developments in artificial intelligence and emerging technologies",
            "cluster_title": "Tech & AI News"
        },
        "articles": [
            {
                "article_id": base_id + 101,
                "title": "Revolutionary AI Model Breaks Performance Records Across Multiple Benchmarks",
                "text": "Researchers at leading AI institutions have developed a groundbreaking artificial intelligence model that has achieved unprecedented performance across multiple industry benchmarks. The model demonstrates significant improvements in natural language understanding, code generation, mathematical reasoning, and complex problem-solving tasks. Early testing shows performance gains of 25-40% over previous state-of-the-art models.",
                "article_summary": "New AI model achieves record-breaking performance with 25-40% improvements",
                "source": "AI Research Journal"
            },
            {
                "article_id": base_id + 102,
                "title": "Quantum Computing Milestone: First Practical Application Demonstrates Clear Advantage",
                "text": "Scientists have successfully demonstrated quantum advantage in a practical computing application for the first time, marking a major milestone in the field. The quantum computer solved a real-world optimization problem significantly faster than the most powerful classical computers, opening new possibilities for industries ranging from drug discovery to financial modeling.",
                "article_summary": "Quantum computing achieves first practical advantage over classical computers",
                "source": "Science & Technology Daily"
            },
            {
                "article_id": base_id + 103,
                "title": "Tech Giants Announce $75 Billion Investment in AI Infrastructure Development",
                "text": "Leading technology companies have announced a combined $75 billion investment in AI infrastructure over the next three years. The massive funding will focus on building advanced data centers, developing specialized AI chips, expanding cloud computing capabilities, and training the next generation of AI researchers and engineers.",
                "article_summary": "Tech companies commit $75B to AI infrastructure and talent development",
                "source": "Tech Business Weekly"
            }
        ]
    }
    
    result1 = test_endpoint("POST", "/api/clusters/batch", single_cluster_data, f"Create cluster {cluster_id_1} with 3 articles")
    if result1 and result1.get('success'):
        created_clusters.append(cluster_id_1)
    
    # Test 3: Multiple clusters bulk with comprehensive data
    print_header("BULK CLUSTERS TEST")
    
    cluster_id_2 = base_id + 2
    cluster_id_3 = base_id + 3
    cluster_id_4 = base_id + 4
    
    bulk_data = {
        "clusters": [
            {
                "cluster": {
                    "cluster_id": cluster_id_2,
                    "cluster_summary": "Sports News and Athletic Achievements - Coverage of major sporting events, championship results, and athletic milestones",
                    "cluster_title": "Sports & Athletics"
                },
                "articles": [
                    {
                        "article_id": base_id + 201,
                        "title": "World Championship Finals Break Global Viewership Records",
                        "text": "The world championship finals attracted a global television audience of over 2.1 billion viewers, breaking all previous records for sports broadcasting. The event showcased exceptional athleticism and sportsmanship, with dramatic moments that kept audiences engaged throughout the competition.",
                        "article_summary": "Championship finals set global viewership record with 2.1B viewers",
                        "source": "Global Sports Network"
                    },
                    {
                        "article_id": base_id + 202,
                        "title": "Olympic Training Centers Integrate AI-Powered Performance Analytics",
                        "text": "Olympic training facilities worldwide are incorporating cutting-edge AI-powered analytics and biomechanical analysis systems to help athletes optimize their performance and reduce injury risk. The technology provides real-time feedback and personalized training recommendations.",
                        "article_summary": "Olympic centers adopt AI analytics for athlete performance optimization",
                        "source": "Olympic Sports Magazine"
                    }
                ]
            },
            {
                "cluster": {
                    "cluster_id": cluster_id_3,
                    "cluster_summary": "Health and Medical Research - Breakthrough medical discoveries, clinical trials, and healthcare policy developments",
                    "cluster_title": "Health & Medicine"
                },
                "articles": [
                    {
                        "article_id": base_id + 301,
                        "title": "Gene Therapy Breakthrough Shows 95% Success Rate for Rare Genetic Diseases",
                        "text": "Clinical trials for a revolutionary gene therapy treatment have shown remarkable success rates of 95% in treating previously incurable rare genetic diseases. The therapy has demonstrated both exceptional safety and efficacy in phase 3 trials involving over 500 patients across multiple medical centers.",
                        "article_summary": "Gene therapy achieves 95% success rate in treating rare genetic diseases",
                        "source": "Medical Research Quarterly"
                    },
                    {
                        "article_id": base_id + 302,
                        "title": "Global Health Initiative Successfully Reduces Disease Prevalence by 45%",
                        "text": "A coordinated global health initiative has successfully reduced the prevalence of several infectious diseases by 45% over the past five years through improved vaccination programs, enhanced healthcare infrastructure, and community health education programs in developing regions.",
                        "article_summary": "Global health program reduces infectious disease prevalence by 45%",
                        "source": "World Health Organization Report"
                    }
                ]
            },
            {
                "cluster": {
                    "cluster_id": cluster_id_4,
                    "cluster_summary": "Environmental Science and Sustainability - Climate change research, renewable energy developments, and environmental conservation efforts",
                    "cluster_title": "Environment & Climate"
                },
                "articles": [
                    {
                        "article_id": base_id + 401,
                        "title": "Renewable Energy Sources Surpass Fossil Fuels in Global Electricity Generation",
                        "text": "For the first time in history, renewable energy sources have generated more electricity than fossil fuels globally, marking a historic transition in energy production. Solar, wind, and hydroelectric power now account for 52% of global electricity generation, driven by technological advances and decreasing costs.",
                        "article_summary": "Renewable energy surpasses fossil fuels in global electricity generation for first time",
                        "source": "Environmental Energy Report"
                    }
                ]
            }
        ]
    }
    
    result2 = test_endpoint("POST", "/api/data/bulk", bulk_data, f"Create 3 clusters with articles")
    if result2 and result2.get('success'):
        created_clusters.extend([cluster_id_2, cluster_id_3, cluster_id_4])
    
    # Test 4: Add articles to existing cluster
    print_header("ADD ARTICLES TO EXISTING CLUSTER TEST")
    
    if created_clusters:
        target_cluster = created_clusters[0]  # Use first created cluster
        additional_articles = {
            "articles": [
                {
                    "article_id": base_id + 501,
                    "title": "Tech Industry Embraces Comprehensive Sustainability Practices",
                    "text": "Major technology companies are implementing comprehensive sustainability programs to reduce their environmental impact. These initiatives include carbon-neutral data centers, renewable energy adoption, sustainable manufacturing processes, and circular economy principles in product design.",
                    "article_summary": "Tech industry adopts comprehensive sustainability measures across operations",
                    "source": "Green Technology News"
                },
                {
                    "article_id": base_id + 502,
                    "title": "Innovation in Battery Technology Revolutionizes Renewable Energy Storage",
                    "text": "Engineers have developed breakthrough battery technology that could revolutionize renewable energy storage capabilities. The new solid-state batteries offer 300% higher energy density, faster charging times, and significantly longer lifespans compared to current lithium-ion technology.",
                    "article_summary": "New battery technology offers 300% higher density for renewable energy storage",
                    "source": "Energy Innovation Weekly"
                },
                {
                    "article_id": base_id + 503,
                    "title": "AI Ethics Framework Adopted by Leading Technology Organizations",
                    "text": "A comprehensive AI ethics framework developed through collaboration between leading technology companies, academic institutions, and policy organizations has been formally adopted. The framework addresses key concerns about algorithmic bias, transparency, accountability, and the responsible development of AI systems.",
                    "article_summary": "Comprehensive AI ethics framework adopted by major tech organizations",
                    "source": "AI Ethics Consortium"
                }
            ]
        }
        
        test_endpoint("POST", f"/api/clusters/{target_cluster}/articles/batch", additional_articles, f"Add 3 articles to cluster {target_cluster}")
    else:
        print("   ⚠️  No clusters created successfully, skipping add articles test")
    
    # Test 5: Comprehensive data verification
    print_header("DATA VERIFICATION TESTS")
    
    print_subheader("Get All Data")
    clusters_result = test_endpoint("GET", "/api/clusters", None, "Get all clusters")
    articles_result = test_endpoint("GET", "/api/articles", None, "Get all articles")
    
    print_subheader("Get Specific Clusters")
    for cluster_id in created_clusters[:3]:  # Test first 3
        test_endpoint("GET", f"/api/clusters/{cluster_id}", None, f"Get cluster {cluster_id} details")
    
    print_subheader("Get Articles by Cluster")
    for cluster_id in created_clusters[:3]:  # Test first 3
        test_endpoint("GET", f"/api/clusters/{cluster_id}/articles", None, f"Get articles for cluster {cluster_id}")
    
    # Test 6: Error handling
    print_header("ERROR HANDLING TESTS")
    
    test_endpoint("GET", "/api/clusters/99999", None, "Get non-existent cluster (should return 404)")
    test_endpoint("GET", "/api/articles/99999", None, "Get non-existent article (should return 404)")
    test_endpoint("GET", "/api/clusters/99999/articles", None, "Get articles for non-existent cluster (should return 404)")
    
    # Final summary
    print_header("TEST SUMMARY")
    
    if clusters_result and articles_result:
        total_clusters = len(clusters_result.get('clusters', []))
        total_articles = len(articles_result.get('articles', []))
        
        print(f"📊 Database Contents:")
        print(f"   Total clusters: {total_clusters}")
        print(f"   Total articles: {total_articles}")
        print(f"   Clusters created in this test: {len(created_clusters)}")
        print(f"   Created cluster IDs: {created_clusters}")
    
    print(f"\n🎯 What Was Tested:")
    print(f"   ✅ Single cluster batch creation")
    print(f"   ✅ Multi-cluster bulk creation")
    print(f"   ✅ Adding articles to existing clusters")
    print(f"   ✅ All GET endpoints for data retrieval")
    print(f"   ✅ Error handling for non-existent resources")
    print(f"   ✅ article_id and cluster_title field support")
    
    print(f"\n🔍 Next Steps:")
    print(f"   1. Check your Supabase dashboard to see all created data")
    print(f"   2. Verify article_id and cluster_title fields are populated")
    print(f"   3. Test with your own real data using this structure")
    print(f"   4. Use these cluster IDs as examples: {created_clusters[:3]}")
    
    print(f"\n🌐 Quick Links to Test:")
    for cluster_id in created_clusters[:2]:
        print(f"   - http://localhost:5000/api/clusters/{cluster_id}")
        print(f"   - http://localhost:5000/api/clusters/{cluster_id}/articles")

if __name__ == "__main__":
    main()