import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import PaperGenerator from './pages/PaperGenerator';
import PaperDetail from './pages/PaperDetail';
import QuestionBank from './pages/QuestionBank';
import DocumentIngestion from './pages/DocumentIngestion';
import TemplateStudio from './pages/TemplateStudio';
import ValidationStudio from './pages/ValidationStudio';
import AnalyticsView from './pages/AnalyticsView';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [activePaperId, setActivePaperId] = useState(null);

  const handleSelectPaper = (paperId) => {
    setActivePaperId(paperId);
    setCurrentTab('paper_detail');
  };

  const handleNavigate = (tab) => {
    setCurrentTab(tab);
    if (tab !== 'paper_detail') {
      setActivePaperId(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar onNavigate={handleNavigate} />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar currentTab={currentTab} onNavigate={handleNavigate} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
          {currentTab === 'dashboard' && (
            <Dashboard 
              onNavigate={handleNavigate} 
              onSelectPaper={handleSelectPaper} 
            />
          )}

          {currentTab === 'generate' && (
            <PaperGenerator 
              onSelectPaper={handleSelectPaper} 
            />
          )}

          {currentTab === 'paper_detail' && (
            <PaperDetail 
              paperId={activePaperId} 
              onBack={() => handleNavigate('dashboard')} 
            />
          )}

          {currentTab === 'questions' && (
            <QuestionBank />
          )}

          {currentTab === 'documents' && (
            <DocumentIngestion />
          )}

          {currentTab === 'templates' && (
            <TemplateStudio />
          )}

          {currentTab === 'validation' && (
            <ValidationStudio onSelectPaper={handleSelectPaper} />
          )}

          {currentTab === 'analytics' && (
            <AnalyticsView />
          )}
        </main>
      </div>
    </div>
  );
}
