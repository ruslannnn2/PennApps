// src/data/sampleDatasets.ts
import { GraphData } from '../components/ForceGraph';
import { Dataset } from '../components/DatasetSwitcher';

export const politicalNewsData: GraphData = {
  nodes: [
    { id: "Trump", group: 1 },
    { id: "Biden", group: 1 },
    { id: "Congress", group: 2 },
    { id: "Supreme Court", group: 2 },
    { id: "Immigration", group: 3 },
    { id: "Healthcare", group: 3 },
    { id: "Economy", group: 3 },
    { id: "Climate Policy", group: 3 },
    { id: "Foreign Policy", group: 4 },
    { id: "China", group: 4 },
    { id: "Russia", group: 4 },
    { id: "Ukraine", group: 4 },
    { id: "NATO", group: 4 },
    { id: "Trade War", group: 5 },
    { id: "Inflation", group: 5 },
    { id: "Jobs Report", group: 5 }
  ],
  links: [
    { source: "Trump", target: "Immigration", value: 8 },
    { source: "Biden", target: "Climate Policy", value: 7 },
    { source: "Congress", target: "Healthcare", value: 6 },
    { source: "Supreme Court", target: "Healthcare", value: 5 },
    { source: "Economy", target: "Inflation", value: 9 },
    { source: "Economy", target: "Jobs Report", value: 7 },
    { source: "Foreign Policy", target: "China", value: 8 },
    { source: "Foreign Policy", target: "Russia", value: 6 },
    { source: "Ukraine", target: "Russia", value: 10 },
    { source: "Ukraine", target: "NATO", value: 7 },
    { source: "China", target: "Trade War", value: 8 },
    { source: "Trump", target: "Trade War", value: 6 },
    { source: "Biden", target: "Foreign Policy", value: 5 },
    { source: "Congress", target: "Economy", value: 4 }
  ]
};

export const techNewsData: GraphData = {
  nodes: [
    { id: "ChatGPT", group: 1 },
    { id: "OpenAI", group: 1 },
    { id: "Google AI", group: 1 },
    { id: "Meta AI", group: 1 },
    { id: "Tesla", group: 2 },
    { id: "SpaceX", group: 2 },
    { id: "Neuralink", group: 2 },
    { id: "Apple", group: 3 },
    { id: "iPhone", group: 3 },
    { id: "Vision Pro", group: 3 },
    { id: "Cryptocurrency", group: 4 },
    { id: "Bitcoin", group: 4 },
    { id: "Ethereum", group: 4 },
    { id: "AI Ethics", group: 5 },
    { id: "Job Automation", group: 5 },
    { id: "Regulation", group: 5 },
    { id: "Quantum Computing", group: 6 },
    { id: "5G", group: 6 },
    { id: "Cybersecurity", group: 7 }
  ],
  links: [
    { source: "ChatGPT", target: "OpenAI", value: 10 },
    { source: "OpenAI", target: "AI Ethics", value: 7 },
    { source: "Google AI", target: "AI Ethics", value: 6 },
    { source: "Meta AI", target: "AI Ethics", value: 5 },
    { source: "Tesla", target: "SpaceX", value: 8 },
    { source: "Tesla", target: "Neuralink", value: 6 },
    { source: "Apple", target: "iPhone", value: 9 },
    { source: "Apple", target: "Vision Pro", value: 7 },
    { source: "Bitcoin", target: "Cryptocurrency", value: 10 },
    { source: "Ethereum", target: "Cryptocurrency", value: 8 },
    { source: "AI Ethics", target: "Job Automation", value: 8 },
    { source: "AI Ethics", target: "Regulation", value: 7 },
    { source: "Quantum Computing", target: "Cybersecurity", value: 6 },
    { source: "5G", target: "Cybersecurity", value: 5 },
    { source: "ChatGPT", target: "Job Automation", value: 6 }
  ]
};

export const sportsData: GraphData = {
  nodes: [
    { id: "NFL", group: 1 },
    { id: "Super Bowl", group: 1 },
    { id: "Patrick Mahomes", group: 1 },
    { id: "Chiefs", group: 1 },
    { id: "NBA", group: 2 },
    { id: "Lakers", group: 2 },
    { id: "LeBron James", group: 2 },
    { id: "Stephen Curry", group: 2 },
    { id: "World Cup", group: 3 },
    { id: "Messi", group: 3 },
    { id: "Argentina", group: 3 },
    { id: "Olympics", group: 4 },
    { id: "Paris 2024", group: 4 },
    { id: "Tennis", group: 5 },
    { id: "Wimbledon", group: 5 },
    { id: "Novak Djokovic", group: 5 }
  ],
  links: [
    { source: "NFL", target: "Super Bowl", value: 10 },
    { source: "Super Bowl", target: "Patrick Mahomes", value: 8 },
    { source: "Patrick Mahomes", target: "Chiefs", value: 9 },
    { source: "NBA", target: "Lakers", value: 7 },
    { source: "Lakers", target: "LeBron James", value: 8 },
    { source: "NBA", target: "Stephen Curry", value: 7 },
    { source: "World Cup", target: "Messi", value: 9 },
    { source: "Messi", target: "Argentina", value: 8 },
    { source: "Olympics", target: "Paris 2024", value: 9 },
    { source: "Tennis", target: "Wimbledon", value: 8 },
    { source: "Tennis", target: "Novak Djokovic", value: 7 },
    { source: "Wimbledon", target: "Novak Djokovic", value: 6 }
  ]
};

export const entertainmentData: GraphData = {
  nodes: [
    { id: "Taylor Swift", group: 1 },
    { id: "Eras Tour", group: 1 },
    { id: "Travis Kelce", group: 1 },
    { id: "Netflix", group: 2 },
    { id: "Stranger Things", group: 2 },
    { id: "Wednesday", group: 2 },
    { id: "Marvel", group: 3 },
    { id: "Avengers", group: 3 },
    { id: "Disney", group: 3 },
    { id: "Star Wars", group: 3 },
    { id: "TikTok", group: 4 },
    { id: "Instagram", group: 4 },
    { id: "YouTube", group: 4 },
    { id: "Gaming", group: 5 },
    { id: "PlayStation", group: 5 },
    { id: "Xbox", group: 5 },
    { id: "Nintendo", group: 5 }
  ],
  links: [
    { source: "Taylor Swift", target: "Eras Tour", value: 10 },
    { source: "Taylor Swift", target: "Travis Kelce", value: 8 },
    { source: "Netflix", target: "Stranger Things", value: 9 },
    { source: "Netflix", target: "Wednesday", value: 7 },
    { source: "Marvel", target: "Avengers", value: 8 },
    { source: "Disney", target: "Marvel", value: 7 },
    { source: "Disney", target: "Star Wars", value: 8 },
    { source: "TikTok", target: "Taylor Swift", value: 6 },
    { source: "Instagram", target: "Taylor Swift", value: 5 },
    { source: "YouTube", target: "Gaming", value: 7 },
    { source: "Gaming", target: "PlayStation", value: 8 },
    { source: "Gaming", target: "Xbox", value: 7 },
    { source: "Gaming", target: "Nintendo", value: 8 }
  ]
};

export const availableDatasets: Dataset[] = [
  {
    name: 'Sports',
    data: sportsData,
    emoji: '🏈',
    description: 'Sports news and athlete connections'
  },
  {
    name: 'Technology',
    data: techNewsData,
    emoji: '🤖',
    description: 'AI, tech companies, and innovation'
  },
  {
    name: 'Politics',
    data: politicalNewsData,
    emoji: '🏛️',
    description: 'Political figures and policy topics'
  },
  {
    name: 'Entertainment',
    data: entertainmentData,
    emoji: '📺',
    description: 'Pop culture, celebrities, and media'
  }
];