import { useState } from 'react';
import LandingHero from './components/LandingHero';
import ResearchInterface from './components/ResearchInterface';

function App() {
  const [showResearch, setShowResearch] = useState(false);

  if (showResearch) {
    return <ResearchInterface onBack={() => setShowResearch(false)} />;
  }

  return (
    <div className="min-h-screen">
      <LandingHero onStart={() => setShowResearch(true)} />
    </div>
  );
}

export default App;
