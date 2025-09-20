// src/App.tsx
import { useState, useEffect } from 'react'

// Import your existing components with camelCase
import forceGraph, { GraphData } from './components/forceGraph'
import trendingTopics from './components/trendingTopics'
import datasetSwitcher, { Dataset } from './components/datasetSwitcher'
import networkStats from './components/networkStats'
import loadingSpinner from './components/loadingSpinner'
import errorMessage from './components/errorMessage'

// Import your sample data
import { availableDatasets } from './data/sampleDatasets'

function App(): JSX.Element {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [trendingTopics, setTrendingTopics] = useState<string[]>([])
  const [currentDataset, setCurrentDataset] = useState<string>('Sports')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTrendingNews()
  }, [])

  const fetchTrendingNews = async (): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      
      // Use your existing datasets from the data file
      const sportsDataset = availableDatasets.find(d => d.name === 'Sports')
      if (sportsDataset) {
        setGraphData(sportsDataset.data)
        setTrendingTopics(['NFL', 'NBA', 'World Cup', 'Olympics', 'Tennis'])
        setCurrentDataset('Sports')
      }
      
      setError(null)
      
    } catch (err) {
      console.error('Error fetching news:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleDatasetChange = (dataset: Dataset): void => {
    setGraphData(dataset.data)
    setCurrentDataset(dataset.name)
    
    const topicMap: { [key: string]: string[] } = {
      'Sports': ['NFL', 'NBA', 'World Cup', 'Olympics', 'Tennis'],
      'Technology': ['ChatGPT', 'AI Ethics', 'Cryptocurrency', 'Quantum Computing'],
      'Politics': ['Trump', 'Biden', 'Economy', 'Healthcare', 'Foreign Policy'],
      'Entertainment': ['Taylor Swift', 'Netflix', 'Marvel', 'Gaming', 'TikTok']
    }
    
    setTrendingTopics(topicMap[dataset.name] || [])
  }

  const handleRefresh = (): void => {
    fetchTrendingNews()
  }

  const handleTopicClick = (topic: string): void => {
    console.log('Topic clicked:', topic)
  }

  const handleRetry = (): void => {
    setError(null)
    fetchTrendingNews()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              News Trends Visualizer
            </h1>
            <p className="text-lg text-gray-600 mb-4">
              Real-time trending news topics and connections
            </p>
            <button 
              onClick={handleRefresh} 
              disabled={loading}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
            >
              {loading ? 'Loading...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-8">
            <errorMessage 
              error={error}
              onRetry={handleRetry}
              title="Error Loading Data"
            />
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center min-h-96">
            <loadingSpinner 
              message="Loading trending news data..."
              size="large"
            />
          </div>
        ) : (
          <div className="space-y-8">
            
            {/* Dataset Selection */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <datasetSwitcher 
                datasets={availableDatasets}
                onDatasetChange={handleDatasetChange}
                currentDataset={currentDataset}
              />
            </div>

            {/* Trending Topics */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <trendingTopics 
                topics={trendingTopics}
                title="Trending Topics"
                onTopicClick={handleTopicClick}
              />
            </div>

            {/* Force Graph */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {currentDataset} Network
                </h2>
              </div>
              {graphData && (
                <div className="flex justify-center">
                  <forceGraph 
                    data={graphData}
                    width={928}
                    height={600}
                  />
                </div>
              )}
            </div>

            {/* Network Statistics */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <networkStats 
                data={graphData}
                title="Network Summary"
              />
            </div>

          </div>
        )}
      </main>
    </div>
  )
}

export default App