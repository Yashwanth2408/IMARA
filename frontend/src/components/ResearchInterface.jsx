import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ArrowLeft, Search, Loader2, CheckCircle, Clock,
    Bot, Code, FileSearch, PresentationIcon, Download,
    Sparkles, TrendingUp, Target, Activity
} from 'lucide-react';

const ResearchInterface = ({ onBack }) => {
    const [query, setQuery] = useState('');
    const [isResearching, setIsResearching] = useState(false);
    const [currentAgent, setCurrentAgent] = useState('');
    const [progress, setProgress] = useState(0);
    const [agentResults, setAgentResults] = useState({});
    const [finalReport, setFinalReport] = useState(null);
    const [metrics, setMetrics] = useState(null);
    const [routing, setRouting] = useState(null);
    const resultsRef = useRef(null);

    const agents = [
        { id: 'researcher', name: 'Researcher', icon: FileSearch, color: 'text-green-400' },
        { id: 'coder', name: 'Coder', icon: Code, color: 'text-orange-400' },
        { id: 'reviewer', name: 'Reviewer', icon: CheckCircle, color: 'text-red-400' },
        { id: 'presenter', name: 'Presenter', icon: PresentationIcon, color: 'text-purple-400' }
    ];

    const startResearch = async () => {
        if (!query.trim()) return;

        setIsResearching(true);
        setProgress(0);
        setAgentResults({});
        setFinalReport(null);
        setMetrics(null);
        setRouting(null);

        try {
            const ws = new WebSocket('ws://localhost:8000/ws/research');

            ws.onopen = () => {
                ws.send(JSON.stringify({ query }));
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                switch (data.type) {
                    case 'start':
                        setCurrentAgent('initializing');
                        break;

                    case 'routing':
                        setRouting(data.data);
                        break;

                    case 'agent_start':
                        setCurrentAgent(data.agent);
                        setProgress(data.progress || 0);
                        break;

                    case 'agent_complete':
                        setAgentResults(prev => ({
                            ...prev,
                            [data.agent]: data.data
                        }));
                        setProgress(data.progress || 0);

                        // Scroll to results
                        setTimeout(() => {
                            resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
                        }, 100);
                        break;

                    case 'complete':
                        setFinalReport(data.data);
                        setMetrics(data.data.metrics);
                        setProgress(100);
                        setIsResearching(false);
                        setCurrentAgent('');
                        ws.close();
                        break;

                    case 'error':
                        console.error('Research error:', data.message);
                        setIsResearching(false);
                        setCurrentAgent('');
                        break;
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setIsResearching(false);
                setCurrentAgent('');
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            setIsResearching(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !isResearching) {
            startResearch();
        }
    };

    return (
        <div className="min-h-screen px-4 py-8">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-8">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Home
                </button>

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Bot className="w-10 h-10 text-blue-400" />
                        <div>
                            <h1 className="text-3xl font-bold gradient-text">Research Assistant</h1>
                            <p className="text-slate-400">Enter your research topic below</p>
                        </div>
                    </div>

                    {routing && (
                        <div className="glass-card px-4 py-2">
                            <div className="text-sm text-slate-400">Route: <span className="text-white font-semibold">{routing.path}</span></div>
                            <div className="text-xs text-slate-500">Confidence: {(routing.confidence * 100).toFixed(0)}%</div>
                        </div>
                    )}
                </div>
            </div>

            {/* Search Input */}
            <div className="max-w-4xl mx-auto mb-12">
                <div className="glass-card p-6">
                    <div className="flex gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="e.g., Multi-agent reinforcement learning systems"
                                disabled={isResearching}
                                className="w-full pl-12 pr-4 py-4 bg-slate-800/50 border border-slate-700 rounded-lg 
                         text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 
                         transition-all disabled:opacity-50"
                            />
                        </div>
                        <button
                            onClick={startResearch}
                            disabled={isResearching || !query.trim()}
                            className="btn-primary px-8 disabled:opacity-50 disabled:cursor-not-allowed 
                       inline-flex items-center gap-2"
                        >
                            {isResearching ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Researching...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    Start Research
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            {isResearching && (
                <div className="max-w-4xl mx-auto mb-8">
                    <div className="glass-card p-6">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-sm text-slate-400">Research Progress</span>
                            <span className="text-sm font-semibold text-white">{progress}%</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                transition={{ duration: 0.5 }}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Agent Status Cards */}
            <div className="max-w-7xl mx-auto mb-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {agents.map((agent) => {
                        const isActive = currentAgent === agent.id;
                        const isComplete = agentResults[agent.id];
                        const Icon = agent.icon;

                        return (
                            <motion.div
                                key={agent.id}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className={`glass-card p-6 transition-all ${isActive ? 'ring-2 ring-blue-500 bg-blue-500/10' : ''
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <Icon className={`w-8 h-8 ${agent.color}`} />
                                    {isActive && <Loader2 className="w-5 h-5 animate-spin text-blue-400" />}
                                    {isComplete && <CheckCircle className="w-5 h-5 text-green-400" />}
                                    {!isActive && !isComplete && <Clock className="w-5 h-5 text-slate-600" />}
                                </div>
                                <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                                <p className="text-xs text-slate-400">
                                    {isActive && 'Processing...'}
                                    {isComplete && 'Completed'}
                                    {!isActive && !isComplete && 'Waiting'}
                                </p>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* Results Section */}
            <div ref={resultsRef} className="max-w-7xl mx-auto">
                <AnimatePresence>
                    {Object.keys(agentResults).length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-6"
                        >
                            {/* Metrics Dashboard */}
                            {metrics && (
                                <div className="glass-card p-6">
                                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                        <TrendingUp className="w-6 h-6 text-blue-400" />
                                        Research Quality Metrics
                                    </h2>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-green-400">{metrics.grade || 'N/A'}</div>
                                            <div className="text-sm text-slate-400">Grade</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-blue-400">{metrics.overall_score || 0}/10</div>
                                            <div className="text-sm text-slate-400">Overall Score</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-purple-400">{metrics.paper_count || 0}</div>
                                            <div className="text-sm text-slate-400">Papers Analyzed</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-orange-400">
                                                {routing ? `${(routing.confidence * 100).toFixed(0)}%` : 'N/A'}
                                            </div>
                                            <div className="text-sm text-slate-400">Confidence</div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Agent Results */}
                            {agentResults.researcher && (
                                <div className="glass-card p-6">
                                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                        <FileSearch className="w-6 h-6 text-green-400" />
                                        Research Findings
                                    </h2>
                                    <div className="prose prose-invert max-w-none">
                                        <p className="text-slate-300 whitespace-pre-wrap">{agentResults.researcher.summary}</p>
                                    </div>
                                </div>
                            )}

                            {agentResults.coder && (
                                <div className="glass-card p-6">
                                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                        <Code className="w-6 h-6 text-orange-400" />
                                        Generated Code
                                    </h2>
                                    <pre className="bg-slate-900 p-4 rounded-lg overflow-x-auto text-sm">
                                        <code className="text-slate-300">{agentResults.coder.code}</code>
                                    </pre>
                                </div>
                            )}

                            {agentResults.reviewer && (
                                <div className="glass-card p-6">
                                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                        <CheckCircle className="w-6 h-6 text-red-400" />
                                        Review Feedback
                                    </h2>
                                    <p className="text-slate-300 whitespace-pre-wrap">{agentResults.reviewer.review}</p>
                                </div>
                            )}

                            {/* Download Button */}
                            {finalReport && (
                                <div className="flex justify-center">
                                    <button
                                        onClick={() => {
                                            const blob = new Blob([JSON.stringify(finalReport, null, 2)], { type: 'application/json' });
                                            const url = URL.createObjectURL(blob);
                                            const a = document.createElement('a');
                                            a.href = url;
                                            a.download = 'imara-research-report.json';
                                            a.click();
                                        }}
                                        className="btn-primary inline-flex items-center gap-2"
                                    >
                                        <Download className="w-5 h-5" />
                                        Download Full Report
                                    </button>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default ResearchInterface;
