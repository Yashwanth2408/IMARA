import { motion } from 'framer-motion';
import { Bot, Sparkles, ArrowRight, Github, Zap, Target, Shield } from 'lucide-react';

const LandingHero = ({ onStart }) => {
    const features = [
        {
            icon: Bot,
            title: "4 Specialized Agents",
            desc: "Researcher, Coder, Reviewer, Presenter"
        },
        {
            icon: Zap,
            title: "Real-time ArXiv Search",
            desc: "Academic papers in seconds"
        },
        {
            icon: Target,
            title: "Quality Scoring",
            desc: "4D metrics for research quality"
        },
        {
            icon: Shield,
            title: "100% Local & Private",
            desc: "No data sent externally"
        }
    ];

    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 relative overflow-hidden">
            {/* Animated background */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -top-48 -left-48 animate-pulse-slow" />
                <div className="absolute w-96 h-96 bg-purple-500/20 rounded-full blur-3xl -bottom-48 -right-48 animate-pulse-slow" />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto text-center">
                {/* Logo & Title */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="mb-8"
                >
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <Bot className="w-16 h-16 text-blue-400" />
                        <h1 className="text-7xl font-bold gradient-text">IMARA</h1>
                    </div>
                    <p className="text-2xl text-slate-300 mb-2">
                        Intelligent Multi-Agent Research Assistant
                    </p>
                    <p className="text-slate-400 flex items-center justify-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Powered by Llama 3.2 • LangGraph • ArXiv API
                    </p>
                </motion.div>

                {/* Feature Cards */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12"
                >
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.3 + index * 0.1 }}
                            className="glass-card p-6 hover:bg-white/15 transition-all"
                        >
                            <feature.icon className="w-10 h-10 text-blue-400 mb-3 mx-auto" />
                            <h3 className="font-semibold mb-2">{feature.title}</h3>
                            <p className="text-sm text-slate-400">{feature.desc}</p>
                        </motion.div>
                    ))}
                </motion.div>

                {/* CTA Button */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6 }}
                >
                    <button
                        onClick={onStart}
                        className="btn-primary text-lg inline-flex items-center gap-2 group"
                    >
                        Start Research
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                </motion.div>

                {/* Stats */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="mt-16 flex justify-center gap-12 text-sm text-slate-400"
                >
                    <div>
                        <div className="text-2xl font-bold text-white">100%</div>
                        <div>Open Source</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-white">4</div>
                        <div>AI Agents</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-white">&lt;60s</div>
                        <div>Average Time</div>
                    </div>
                </motion.div>

                {/* Footer Links */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="mt-12 flex justify-center gap-6"
                >
                    <a
                        href="https://github.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        <Github className="w-6 h-6" />
                    </a>
                    <a
                        href="#"
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        <Bot className="w-6 h-6" />
                    </a>
                </motion.div>
            </div>
        </div>
    );
};

export default LandingHero;
