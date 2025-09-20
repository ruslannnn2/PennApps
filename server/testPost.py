#!/usr/bin/env python3
"""
Complete workflow test: POST data then GET it back to verify
Tests all POST endpoints then retrieves data using all GET endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

class APITester:
    def __init__(self):
        self.created_clusters = []
        self.created_articles = []
        self.test_results = {
            "posts": {"success": 0, "failed": 0},
            "gets": {"success": 0, "failed": 0}
        }
    
    def print_header(self, title, char="="):
        print(f"\n{char*80}")
        print(f"🎯 {title}")
        print(f"{char*80}")
    
    def print_subheader(self, title):
        print(f"\n{'-'*60}")
        print(f"📍 {title}")
        print(f"{'-'*60}")
    
    def post_request(self, endpoint, data, description):
        """Make a POST request and track results"""
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🚀 POST: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, json=data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS")
                self.test_results["posts"]["success"] += 1
                
                try:
                    result = response.json()
                    
                    # Track created items for later GET tests
                    if 'cluster' in result:
                        cluster = result['cluster']
                        cluster_id = cluster.get('cluster_id')
                        if cluster_id:
                            self.created_clusters.append(cluster_id)
                            print(f"   📝 Tracked cluster_id: {cluster_id}")
                    
                    if 'article' in result:
                        article = result['article']
                        article_id = article.get('id')  # or whatever ID field you use
                        if article_id:
                            self.created_articles.append(article_id)
                            print(f"   📝 Tracked article_id: {article_id}")
                    
                    if 'results' in result:  # For bulk operations
                        for batch_result in result['results']:
                            if 'cluster' in batch_result:
                                cluster_id = batch_result['cluster'].get('cluster_id')
                                if cluster_id:
                                    self.created_clusters.append(cluster_id)
                            if 'articles' in batch_result:
                                for article in batch_result['articles']:
                                    article_id = article.get('id')
                                    if article_id:
                                        self.created_articles.append(article_id)
                    
                    # Show summary info
                    if 'summary' in result:
                        summary = result['summary']
                        for key, value in summary.items():
                            print(f"   📊 {key}: {value}")
                    
                    return result
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response: {response.text}")
                    return response.text
            else:
                print(f"   ❌ FAILED")
                self.test_results["posts"]["failed"] += 1
                try:
                    error_data = response.json()
                    print(f"   🔍 Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   🔍 Raw error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            self.test_results["posts"]["failed"] += 1
            return None
    
    def get_request(self, endpoint, description, expected_status=200):
        """Make a GET request and show results"""
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 GET: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ SUCCESS")
                self.test_results["gets"]["success"] += 1
                
                try:
                    result = response.json()
                    
                    # Show summary of what we got back
                    if isinstance(result, dict):
                        if 'clusters' in result:
                            print(f"   📊 Retrieved {len(result['clusters'])} clusters")
                        if 'articles' in result:
                            print(f"   📊 Retrieved {len(result['articles'])} articles")
                        if 'cluster' in result:
                            cluster = result['cluster']
                            print(f"   📊 Cluster: ID={cluster.get('cluster_id')}, Title='{cluster.get('cluster_title', cluster.get('cluster_summary', ''))[:30]}...'")
                        if 'article' in result:
                            article = result['article']
                            print(f"   📊 Article: Title='{article.get('title', '')[:40]}...', Cluster={article.get('cluster_id')}")
                        if 'cluster_id' in result and 'article_count' in result:
                            print(f"   📊 Cluster {result['cluster_id']} has {result['article_count']} articles")
                    
                    return result
                    
                except json.JSONDecodeError:
                    print(f"   📄 Non-JSON response: {response.text}")
                    return response.text
            else:
                print(f"   ❌ FAILED (Expected {expected_status})")
                self.test_results["gets"]["failed"] += 1
                return None
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            self.test_results["gets"]["failed"] += 1
            return None
    
    def run_post_tests(self):
        """Run all POST tests to create data"""
        self.print_header("PHASE 1: CREATING DATA WITH POST REQUESTS")
        
        # Test 1: Single cluster with articles
        self.print_subheader("Single Cluster Batch")
        single_cluster_data = {
            "cluster": {
                "cluster_id": 1,
                "cluster_summary": "Technology and AI News - Latest developments in artificial intelligence"
            },
            "articles": [
                {
                    "title": "Revolutionary AI Model Breaks Performance Records",
                    "text": "A new artificial intelligence model has achieved unprecedented performance across multiple benchmarks, setting new standards for machine learning capabilities.",
                    "article_summary": "New AI model achieves record-breaking performance",
                    "source": "AI Research Journal"
                },
                {
                    "title": "Tech Giants Announce Major AI Infrastructure Investment",
                    "text": "Leading technology companies have announced a combined $50 billion investment in AI infrastructure over the next three years.",
                    "article_summary": "Tech companies invest $50B in AI infrastructure",
                    "source": "Tech Business Weekly"
                }
            ]
        }
        
        self.post_request("/api/clusters/batch", single_cluster_data, "Create cluster 1 with 2 articles")
        
        # Test 2: Multiple clusters bulk
        self.print_subheader("Multiple Clusters Bulk")
        bulk_data = {
            "clusters": [
                {
                    "cluster": {
                        "cluster_id": 2,
                        "cluster_summary": "Sports News - Coverage of major sporting events"
                    },
                    "articles": [
                        {
                            "title": "World Cup Finals Draw Record Viewership",
                            "text": "The World Cup finals attracted a global audience of over 1.5 billion viewers, breaking previous records.",
                            "article_summary": "World Cup finals break viewership records",
                            "source": "Sports Global Network"
                        },
                        {
                            "title": "Olympic Training Centers Embrace New Technology",
                            "text": "Olympic training facilities are incorporating AI-powered analytics to help athletes optimize performance.",
                            "article_summary": "Olympic centers use AI for athlete optimization",
                            "source": "Olympic Sports Magazine"
                        }
                    ]
                },
                {
                    "cluster": {
                        "cluster_id": 3,
                        "cluster_summary": "Health and Medicine - Medical breakthroughs and health policy"
                    },
                    "articles": [
                        {
                            "title": "Gene Therapy Shows Promise for Rare Diseases",
                            "text": "Clinical trials for a new gene therapy treatment have shown remarkable success in treating rare genetic diseases.",
                            "article_summary": "Gene therapy shows success for rare diseases",
                            "source": "Medical Research Quarterly"
                        }
                    ]
                }
            ]
        }
        
        self.post_request("/api/data/bulk", bulk_data, "Create clusters 2 & 3 with articles")
        
        # Test 3: Individual cluster
        self.print_subheader("Individual Items")
        individual_cluster = {
            "cluster_id": 4,
            "cluster_summary": "Environmental Science - Climate change research and sustainability"
        }
        
        self.post_request("/api/clusters", individual_cluster, "Create individual cluster 4")
        
        # Test 4: Individual article
        individual_article = {
            "cluster_id": 4,
            "title": "Renewable Energy Surpasses Fossil Fuels",
            "text": "For the first time, renewable energy sources have generated more electricity than fossil fuels in several major markets.",
            "article_summary": "Renewable energy surpasses fossil fuels in generation",
            "source": "Environmental Energy Report"
        }
        
        self.post_request("/api/articles", individual_article, "Create individual article for cluster 4")
        
        # Test 5: Add articles to existing cluster
        self.print_subheader("Add to Existing Cluster")
        additional_articles = {
            "articles": [
                {
                    "title": "AI Ethics Guidelines Updated by Industry Leaders",
                    "text": "Major technology companies have collaborated to update comprehensive AI ethics guidelines.",
                    "article_summary": "Tech industry updates AI ethics guidelines",
                    "source": "AI Ethics Council"
                },
                {
                    "title": "Quantum Computing Achieves New Milestone",
                    "text": "Researchers have demonstrated quantum advantage in a practical application for the first time.",
                    "article_summary": "Quantum computing demonstrates practical advantage",
                    "source": "Quantum Research Institute"
                }
            ]
        }
        
        self.post_request("/api/clusters/1/articles/batch", additional_articles, "Add 2 articles to existing cluster 1")
        
        # Test 6: Bulk articles
        self.print_subheader("Bulk Articles")
        bulk_articles = {
            "articles": [
                {
                    "cluster_id": 3,
                    "title": "Mental Health Apps Gain Medical Recognition",
                    "text": "Several mental health applications have received FDA approval as medical devices.",
                    "article_summary": "Mental health apps receive FDA approval",
                    "source": "Digital Health News"
                },
                {
                    "cluster_id": 3,
                    "title": "Global Health Initiative Reduces Disease Prevalence",
                    "text": "A coordinated global health initiative has successfully reduced disease prevalence by 40%.",
                    "article_summary": "Global health initiative reduces disease by 40%",
                    "source": "World Health Organization"
                }
            ]
        }
        
        self.post_request("/api/articles/bulk", bulk_articles, "Bulk create 2 articles for cluster 3")
    
    def run_get_tests(self):
        """Run all GET tests to retrieve the data we created"""
        self.print_header("PHASE 2: RETRIEVING DATA WITH GET REQUESTS")
        
        # Basic endpoints
        self.print_subheader("Basic Server Tests")
        self.get_request("/server", "Server home endpoint")
        self.get_request("/health", "Health check")
        
        # Get all data
        self.print_subheader("Get All Data")
        self.get_request("/api/clusters", "Get all clusters")
        self.get_request("/api/articles", "Get all articles")
        
        # Get specific clusters
        self.print_subheader("Get Specific Clusters")
        unique_clusters = list(set(self.created_clusters))  # Remove duplicates
        for cluster_id in unique_clusters[:5]:  # Test first 5
            self.get_request(f"/api/clusters/{cluster_id}", f"Get cluster {cluster_id}")
        
        # Get articles by cluster
        self.print_subheader("Get Articles by Cluster")
        for cluster_id in unique_clusters[:5]:
            self.get_request(f"/api/clusters/{cluster_id}/articles", f"Get articles for cluster {cluster_id}")
        
        # Get specific articles (if we have IDs)
        if self.created_articles:
            self.print_subheader("Get Specific Articles")
            unique_articles = list(set(self.created_articles))
            for article_id in unique_articles[:5]:  # Test first 5
                self.get_request(f"/api/articles/{article_id}", f"Get article {article_id}")
        
        # Test some error cases
        self.print_subheader("Error Cases")
        self.get_request("/api/clusters/99999", "Get non-existent cluster", 404)
        self.get_request("/api/articles/99999", "Get non-existent article", 404)
        self.get_request("/api/clusters/99999/articles", "Get articles for non-existent cluster", 404)
    
    def run_verification(self):
        """Verify the data integrity"""
        self.print_header("PHASE 3: DATA VERIFICATION")
        
        print("\n🔍 Verifying data integrity...")
        
        # Get all clusters and articles
        clusters_response = self.get_request("/api/clusters", "Get all clusters for verification")
        articles_response = self.get_request("/api/articles", "Get all articles for verification")
        
        if clusters_response and articles_response:
            clusters = clusters_response.get('clusters', [])
            articles = articles_response.get('articles', [])
            
            print(f"\n📊 VERIFICATION RESULTS:")
            print(f"   Total clusters in database: {len(clusters)}")
            print(f"   Total articles in database: {len(articles)}")
            print(f"   Clusters we tracked: {len(set(self.created_clusters))}")
            print(f"   Articles we tracked: {len(set(self.created_articles))}")
            
            # Count articles per cluster
            cluster_article_counts = {}
            for article in articles:
                cluster_id = article.get('cluster_id')
                if cluster_id:
                    cluster_article_counts[cluster_id] = cluster_article_counts.get(cluster_id, 0) + 1
            
            print(f"\n📈 Articles per cluster:")
            for cluster in clusters:
                cluster_id = cluster.get('cluster_id')
                article_count = cluster_article_counts.get(cluster_id, 0)
                summary = cluster.get('cluster_summary', '')[:50]
                print(f"   Cluster {cluster_id}: {article_count} articles - {summary}...")
            
            # Check for orphaned articles
            orphaned = [a for a in articles if not a.get('cluster_id')]
            if orphaned:
                print(f"\n⚠️  Found {len(orphaned)} articles without cluster assignment")
            else:
                print(f"\n✅ All articles are properly assigned to clusters")
        
    def show_final_summary(self):
        """Show final test summary"""
        self.print_header("FINAL TEST SUMMARY")
        
        total_posts = self.test_results["posts"]["success"] + self.test_results["posts"]["failed"]
        total_gets = self.test_results["gets"]["success"] + self.test_results["gets"]["failed"]
        
        print(f"📊 POST OPERATIONS:")
        print(f"   Successful: {self.test_results['posts']['success']}")
        print(f"   Failed: {self.test_results['posts']['failed']}")
        print(f"   Total: {total_posts}")
        print(f"   Success Rate: {(self.test_results['posts']['success']/total_posts*100):.1f}%" if total_posts > 0 else "   Success Rate: N/A")
        
        print(f"\n📊 GET OPERATIONS:")
        print(f"   Successful: {self.test_results['gets']['success']}")
        print(f"   Failed: {self.test_results['gets']['failed']}")
        print(f"   Total: {total_gets}")
        print(f"   Success Rate: {(self.test_results['gets']['success']/total_gets*100):.1f}%" if total_gets > 0 else "   Success Rate: N/A")
        
        print(f"\n🎯 CREATED DATA:")
        print(f"   Unique clusters: {len(set(self.created_clusters))}")
        print(f"   Total articles: {len(set(self.created_articles))}")
        
        overall_success = (self.test_results['posts']['success'] + self.test_results['gets']['success'])
        overall_total = total_posts + total_gets
        
        if overall_total > 0:
            success_rate = (overall_success / overall_total) * 100
            print(f"\n🏆 OVERALL SUCCESS RATE: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT! Your API is working great!")
            elif success_rate >= 75:
                print("👍 GOOD! Minor issues to address")
            else:
                print("⚠️  NEEDS ATTENTION! Several issues found")
        
        print(f"\n🔍 Next Steps:")
        print(f"   1. Check your Supabase dashboard to see all the data")
        print(f"   2. Review any failed operations above")
        print(f"   3. Test with your own real data")
        print(f"   4. Consider adding authentication if needed")

def main():
    """Run the complete workflow test"""
    print("🚀 COMPLETE API WORKFLOW TEST")
    print("This will POST data then GET it back to verify everything works!")
    print(f"🌐 Target: {BASE_URL}")
    
    tester = APITester()
    
    try:
        # Phase 1: Create data
        tester.run_post_tests()
        
        # Small delay to ensure data is persisted
        print("\n⏳ Waiting 2 seconds for data to be persisted...")
        time.sleep(2)
        
        # Phase 2: Retrieve data
        tester.run_get_tests()
        
        # Phase 3: Verify data integrity
        tester.run_verification()
        
        # Show summary
        tester.show_final_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        tester.show_final_summary()
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        tester.show_final_summary()

if __name__ == "__main__":
    main()